import argparse
import asyncio
import json
import logging
import textwrap
from time import sleep

import asyncio_simple_http_server
from asyncio_simple_http_server import HttpServer
import structlog

from .models.event import LogEvent, StartEvent, StopEvent

from .handler import MetricsHandler
from .models.config import Config
from .models.metric import UnmatchedAction, UnmatchedPattern
from .persister import PersistenceManager
from .reaction import Reaction
from .reader import FileReader, JournalReader, UnsupportedLine
from .transformer import ActionIgnored, Transformer, UnsupportedLog

config = Config.get_config()
logger = structlog.get_logger()
# dirty hack so that we don't have ill-formatted debug messages
asyncio_simple_http_server.server.logger.setLevel(logging.WARNING)

parser = argparse.ArgumentParser(
    prog=f"python -m {__package__}",
    epilog=textwrap.dedent(
        """
    command:
        init: read all existing logs, compute metrics, save on disk and exit
        start: continuously read **new** logs, compute and save metrics; serve HTTP endpoint
        clear: make a backup delete all existing metrics (-f to force)
        defaults: print the default configuration in json
        test-config: validate and output configuration in json
        """
    ),
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument("command", help="mode of operation; see below", choices=["init", "start", "clear", "defaults", "test-config"])
parser.add_argument("-c", "--config", help="path to the configuration file (JSON or YAML)", required=False)
parser.add_argument(
    "-f",
    "--force",
    help="force clear even if backup is impossible, then delete backup",
    required=False,
    action="store_true",
)
parser.add_argument("-y", "--yes", help="disable interaction. caution with init and clear", required=False, action="store_true")


class ExporterApp:
    def __init__(self, yes: bool) -> None:
        self.manager = PersistenceManager()
        self.yes = yes

        match config.type:
            case "file":
                reader_class = FileReader
            case "systemd":
                reader_class = JournalReader
            case _:
                raise TypeError(f"unknown log type: {config.type}")

        # path is either a filepath or a unit name
        self.reader: FileReader | JournalReader = reader_class(config.path)

    async def start(self):
        """
        command start: consume new metrics, serve them, etc.
        """
        # fetch reaction configuration
        Reaction.init()
        self.manager.load()
        # executes in a background task
        await self._run_webserver()
        # ignore actions if needed
        asyncio.create_task(self._wait_ignore_actions())
        # executes until stream is closed
        await self._consume_logs(True)

    async def init(self) -> None:
        """
        command init: read existing logs, save metrics (overwriting old ones) and exit.
        """
        # fetch reaction configuration
        Reaction.init()
        if self.clear(False):
            await self._consume_logs(False)
            self.manager.persist()

    def clear(self, force: bool) -> bool:
        """
        command clear: erase existing metrics and exit.
        return True if metrics (would) have been deleted.
        """
        ans = True
        if not force:
            self.manager.load()
            if self.manager.has_metrics():
                ans = self._yesno(
                    "are you sure you want to clear metrics? this will reset counters; read the documentation if unsure.",
                    self.yes,
                )
                if ans:
                    self.manager.clear(False)
                    logger.info("metrics deleted.")
                else:
                    logger.info("no metrics deleted.")
            else:
                logger.debug("no existing metrics would have been overwritten.")
        else:
            logger.info("running in force mode: not trying to load previous metrics; deleting backup")
            self.manager.clear(True)
            logger.info("metrics and backup deleted.")
        return ans

    def defaults(self) -> None:
        """
        command defaults: dumps pretty-print default configuration.
        """
        print(json.dumps(config._schema.validate({}), sort_keys=True, indent=4))

    def test_config(self) -> None:
        """
        command test_config: validates and dumps configuration.
        """
        logger.info("valid config. dumping with added defaults...")
        print(json.dumps(config._conf, sort_keys=True, indent=4))

    @classmethod
    async def run(cls):
        args = parser.parse_args()
        # fetch exporter configuration
        if args.config is None:
            logger.warn(f"running without configuration file is not recommended: use your own")
            config.from_default()
        else:
            config.from_file(args.config)

        cls._configure_logger()

        inst = cls(args.yes)

        # run command
        logger.debug(f"running with command {args.command}")
        match args.command:
            case "init":
                await inst.init()
            case "start":
                await inst.start()
            case "clear":
                inst.clear(args.force)
            case "defaults":
                inst.defaults()
            case "test-config":
                inst.test_config()
            case _:
                raise ValueError(f"unknown command: {args.command}")

    async def _consume_logs(self, follow: bool):
        # never stops while async generator does not stop
        try:
            async for log in self.reader.logs(follow):
                try:
                    event = Transformer.to_event(log)
                    match event:
                        case StartEvent():
                            if config.ignore_actions < config.max_ignore_actions:
                                config.ignore_actions = config.max_ignore_actions
                                logger.info(f"start command detected, ignoring actions for {config.ignore_actions} seconds")
                        case LogEvent():
                            self.manager.metrics.add(event)
                        case _:
                            pass

                except ActionIgnored:
                    logger.info(f"reaction is starting, ignoring action: {log}")
                # do not quit for a bad formatted log
                except (UnsupportedLog, UnsupportedLine, UnmatchedAction, UnmatchedPattern) as e:
                    logger.warning(f"{e.__class__.__name__}: {e}; ignoring line")
        except UnsupportedLog as e:
            logger.warning(f"cannot parse line: {e}")

    async def _run_webserver(self):
        http_server = HttpServer()
        http_server.add_handler(MetricsHandler(self.manager.metrics))
        address, port = config.listen
        await http_server.start(address, port)
        logger.info(f"web server listens on http://{address}:{port}/metrics")
        asyncio.create_task(http_server.serve_forever())

    async def _wait_ignore_actions(self):
        """continuously decrease the ignore action counter if > 0"""
        while True:
            if config.ignore_actions > 0:
                config.ignore_actions -= 1
            await asyncio.sleep(1)

    @staticmethod
    def _configure_logger():
        colors = structlog.dev.ConsoleRenderer.get_default_level_styles()
        colors["info"] = structlog.dev.BLUE
        colors["warn"] = structlog.dev.YELLOW
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
                structlog.dev.ConsoleRenderer(level_styles=colors),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, config.log_level)),
        )

    @staticmethod
    def _yesno(question: str, yes: bool) -> bool:
        prompt = f"{question} ? (y/N): "
        if not yes:
            ans = input(prompt).strip().lower()
        else:
            logger.info("non-interactive mode, yes choosen.")
            ans = "y"
        if ans not in ["y", "n", ""]:
            print(f"{ans} is invalid, please try again")
            return ExporterApp._yesno(question, yes)
        if ans == "y":
            return True
        return False
