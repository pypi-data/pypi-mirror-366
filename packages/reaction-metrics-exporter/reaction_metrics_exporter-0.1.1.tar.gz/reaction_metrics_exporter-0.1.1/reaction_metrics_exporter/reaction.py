import asyncio
from collections import OrderedDict
from functools import cache
import os
import re
import subprocess
from typing import Any, Never, Self

from ruamel.yaml import YAML
import structlog

from .models.config import Config


class ReactionCommandFailed(Exception):
    pass


logger = structlog.get_logger()
config = Config.get_config()


class Reaction:
    _inst = None
    _reader = YAML()

    # patterns are written as <name> in regexps
    PATTERN_REGEXP = re.compile(r"<(?P<pattern>\w+)>")

    def __init__(self):
        if not os.path.exists(config.socket):
            logger.warn(f"socket {config.socket} does not exist, is reaction running?")
        # ensure config is known after initialization
        self._set_config()
        # launch background task to watch for config changes
        asyncio.get_running_loop().create_task(self._poll_config())

    @classmethod
    def init(cls) -> Self:
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    @classmethod
    def config(cls) -> OrderedDict[str, Any]:
        return cls.init()._conf

    @classmethod
    def show(cls) -> OrderedDict[str, Any]:
        try:
            stdout = subprocess.run(
                ["reaction", "show", "--socket", config.socket],
                check=True,
                capture_output=True,
            ).stdout
            return cls._reader.load(stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"error while invoking `reaction show`: {e}. stderr: {e.stderr}")
            # not a fatal error: new pending actions will not be exported
            return OrderedDict()

    @classmethod
    @cache
    def patterns(cls, stream: str, filter: str) -> tuple[str, ...]:
        """Get unique and sorted patterns which are involved in all the regexps of a filter"""
        conf = cls.config()
        patterns: set[str] = set()
        for regex in conf["streams"][stream]["filters"][filter]["regex"]:
            for pattern in re.findall(cls.PATTERN_REGEXP, regex):
                patterns.add(pattern)
        return tuple(sorted(patterns))

    async def _poll_config(self) -> Never:
        # refresh configuration every 10 seconds
        while True:
            await asyncio.sleep(10)
            await self._async_set_config()

    async def _async_set_config(self):
        stdout = await self._exec_async_command(f'reaction test-config -c "{config.reaction_config}"')
        logger.debug("reaction's configuration updated successfully")
        conf = self._reader.load(stdout)
        if conf == self._conf:
            return
        self._conf = conf
        self.patterns.cache_clear()

    def _set_config(self):
        # synchronous so initialization and checks can be done outside of async contexts
        stdout = subprocess.run(
            ["reaction", "test-config", "-c", config.reaction_config],
            check=True,
            capture_output=True,
        ).stdout
        logger.debug("reaction's configuration updated successfully")
        self._conf = self._reader.load(stdout)

    @staticmethod
    async def _exec_async_command(cmd: str):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ReactionCommandFailed(f"reaction failed to execute command {cmd}: {stderr}")
        return stdout
