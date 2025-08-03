import asyncio
from datetime import datetime
import fcntl
import os
import pickle
import signal
import sys

import structlog

from .models.config import Config
from .models.metric import ReactionMetrics

logger = structlog.get_logger()
config = Config.get_config()


class PersistenceManager:
    _PERSIST_FILE = "metrics.pickle"
    # which signals means terminate for us
    _SIGNALS = ["SIGINT", "SIGTERM"]

    def __init__(self) -> None:
        # ensure paths are writable
        self._path = f"{config.persist_directory}/{self._PERSIST_FILE}"
        self._backup_path = f"{self._path}.bkp"
        self._check_writable()

        # open files for the whole process and lock them, to avoid another instance erasing them
        try:
            # r+ means read and write with cursor initially at the beginning
            self._persist_file = open(self._path, "r+b")
            # LOCK_EX is blocking; with LOCK_NB if we cannot acquire lock an exception is raised
            fcntl.flock(self._persist_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._backup_file = open(self._backup_path, "r+b")
            fcntl.flock(self._backup_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.debug("successfully acquired exclusive lock on persistence files")
            logger.debug(f"will persist metrics at {self._path}")
            logger.debug(f"will perform backups at {self._backup_path}")
        except OSError as e:
            logger.error("cannot acquire lock on persistence files: is another instance running?")
            raise e

        # start with no metrics
        self.metrics = ReactionMetrics()
        self._launch()

    def load(self) -> None:
        # load metrics from disk and replace old ones
        # see https://docs.python.org/3/library/pickle.html#handling-stateful-objects
        # the day we need to change the attributes of ReactionMetrics
        try:
            # in case we already read it
            self._persist_file.seek(0)
            self.metrics: ReactionMetrics = pickle.loads(self._persist_file.read())
            logger.info(f"loaded metrics from {self._path}; {self._describe_metrics()}")
        # probably first launch
        except FileNotFoundError as e:
            self.metrics = ReactionMetrics()
        except EOFError as e:
            logger.warn(f"the persistence file exists but appears to be empty: check everything is ok ({e})")
            self.metrics = ReactionMetrics()
        except pickle.PickleError as e:
            raise RuntimeError(f"corrupted file {self._path}: {e}")

    def persist(self, backup: bool = False) -> None:
        # synchronous so exiting can be done without recursive waits
        file = self._persist_file
        if backup:
            file = self._backup_file
            logger.info(
                f"making a backup at {file.name}; will be overwritten if the exporter is running at the next forget date: {self.metrics.start + config.forget}"
            )

        # reset cursor at the beginning to that writes overwrite the content
        file.seek(0)
        file.write(pickle.dumps(self.metrics))
        logger.info(f"persisted metrics in {file.name}; {self._describe_metrics()}")

    def forget(self):
        # first metrics are older than threshold: reset
        if self.metrics.start < datetime.now() - config.forget:
            logger.info(f"detected metrics older than {datetime.now() - config.forget}: clearing all metrics")
            self.persist(True)
            self.metrics.clear()
            self.persist()
        else:
            logger.debug(f"forget metrics not due yet (due at {self.metrics.start + config.forget})")

    def clear(self, remove_backup: bool):
        """
        clear persisted metrics
        """
        if remove_backup:
            logger.debug("clearing metrics and backup")
            self.metrics.clear()
            self.persist()
            self.persist(True)
        else:
            logger.debug("clearing metrics and making a backup")
            self.persist(True)
            self.metrics.clear()
            self.persist()

    def has_metrics(self) -> bool:
        return self.metrics.n_actions + self.metrics.n_matches > 0

    def __del__(self):
        # close fd; check if not too early or an exception has been raised
        if hasattr(self, "_persist_file"):
            self._persist_file.close()
        if hasattr(self, "_backup_file"):
            self._backup_file.close()

    def _launch(self) -> None:
        """
        runs an infinite saving/forget loop for aggregated metrics in `metrics`,
        and save just before the program terminates.
        """
        asyncio.create_task(self._persist_loop())
        for sig in self._SIGNALS:
            asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), lambda sig=sig: self._quit(sig))
        logger.debug(f"installed handlers for signals {self._SIGNALS}")

    async def _persist_loop(self):
        while True:
            await asyncio.sleep(config.persist_interval)
            self.persist()
            self.forget()

    def _quit(self, sig: str):
        try:
            logger.info(f"signal {sig} catched, persisting before exiting...")
            self.persist()
            logger.info("exiting.")
        except Exception as e:
            # catch anything so process can exit
            logger.exception(e)
        finally:
            sys.exit(0)

    def _check_writable(self) -> None:
        """
        check than persistence directory is writable
        """
        dir = config.persist_directory
        if not os.path.isdir(dir):
            logger.info(f"persistence directory does not exist: {dir}; creating it")
            os.mkdir(dir)
        for file in [self._path, self._backup_path]:
            if os.path.isfile(file):
                if not os.access(file, os.W_OK):
                    raise ValueError(f"file exists but is not writable: {file}")
            else:
                if not os.access(dir, os.W_OK):
                    raise ValueError(f"persistence directory is not writable: {dir}")
                # don't bother logging for inexisting backup because backup
                # should happen rarely
                if file == self._path:
                    logger.debug(f"missing file {os.path.basename(file)}: first launch?")
                # create if not exists
                open(file, "a").close()

    def _describe_metrics(self) -> str:
        return f"{len(self.metrics.matches)} set of matches ({self.metrics.n_matches} total); {len(self.metrics.actions)} set of actions ({self.metrics.n_actions} total)"
