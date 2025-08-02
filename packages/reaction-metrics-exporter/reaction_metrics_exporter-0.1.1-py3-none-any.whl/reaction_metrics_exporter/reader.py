from abc import ABC, abstractmethod
import asyncio
from collections.abc import AsyncGenerator
from contextlib import closing
from datetime import datetime
from typing import Any

import aiofiles
import aionotify
import structlog
from systemd import journal
from systemd.journal import Reader

from .models.config import Config
from .models.log import Log, LogLevel

logger = structlog.get_logger()
config = Config.get_config()


class UnsupportedLine(Exception):
    pass


class LogReader(ABC):
    """
    Asynchonously yield reaction logs.

    path is "abstract" (e.g. it is the unit to be read specific to subclasses).
    """

    @abstractmethod
    def __init__(self, path: str) -> None:
        self._path = path

    @abstractmethod
    def logs(self, follow: bool) -> AsyncGenerator[Log]:
        """
        yield either from the beginning (follow = False) or from now then (follow = True).
        """
        pass


class FileReader(LogReader):
    def __init__(self, path: str) -> None:
        super().__init__(path)

    async def logs(self, follow: bool) -> AsyncGenerator[Log]:
        async with aiofiles.open(self._path, "r") as file:
            n = 0
            if not follow:
                # consume all existing lines
                async for line in file:
                    logger.debug(f"read line: {line.strip()}")
                    yield self._to_log(line)
                    n += 1
                logger.info(f"{n} lines read in file {self._path}")

            # wait for lines forever
            else:
                with closing(aionotify.Watcher()) as watcher:
                    # register inotify watcher
                    watcher.watch(self._path, flags=aionotify.Flags.MODIFY)
                    await watcher.setup()
                    while True:
                        # watch for changes
                        _ = await watcher.get_event()
                        # consume new lines
                        async for line in file:
                            yield self._to_log(line)

    def _to_log(self, line: str) -> Log:
        line = line.lstrip()
        # split only first space
        level, _ = line.split(" ", 1)
        try:
            loglevel: LogLevel = LogLevel[level]
            # note that loglevel is part of the message
            return Log(datetime.now(), loglevel, line.strip())
        except ValueError as e:
            raise UnsupportedLine(f"unrecognized loglevel {level} found in line {line}: {e}")


class JournalReader(LogReader):
    def __init__(self, path: str):
        super().__init__(path)
        # when mounting in Docker, without the path logs are not read because
        # they come from "another" computer. in that case the path points
        # mounted journal files, otherwise None will be transparent
        self._jd: Reader = journal.Reader(path=config.journal)
        self._jd.log_level(journal.LOG_INFO)
        # no nice way to check for existence, but no exception if it doesn't
        self._jd.add_match(_SYSTEMD_UNIT=path)

    async def logs(self, follow: bool) -> AsyncGenerator[Log]:
        if not follow:
            n = 0
            for entry in self._jd:
                yield self._to_log(entry)
                n += 1
            logger.info(f"{n} lines read in journal")
        else:
            self._jd.seek_realtime(datetime.now())
            while True:
                # evaluate to true when a new entry (at least) appears
                if await self._wait_entries() == journal.APPEND:
                    for entry in self._jd:
                        yield self._to_log(entry)

    async def _wait_entries(self) -> int:
        # Reader.wait() is synchronous, execute in another thread
        loop = asyncio.get_running_loop()
        # back to polling with 1s non-blocking timeout
        res: int = await loop.run_in_executor(None, self._jd.wait, 1)
        return res

    def _to_log(self, entry: dict[str, Any]) -> Log:
        # timestamp is already a datetime object
        return Log(entry["__REALTIME_TIMESTAMP"], entry["PRIORITY"], entry["MESSAGE"].strip())
