from abc import ABC
from ast import literal_eval
import re

import structlog

from .models.event import Action, Event, Match
from .models.log import Log

logger = structlog.get_logger()


class UnsupportedLog(Exception):
    pass


class Transformer(ABC):
    REGEX = re.compile(
        r"""
        INFO (?P<stream>.+?)
        \.
        (?P<filter>.+?)
        (?P<sep>\.)? # optional dot if event is an action (in which case we have filter.action)
        (?(sep)(?P<action>.+?)) # if dot found, match action name
        :\s(?P<type>match|run) # back to generic match
        \s(?P<params>\[.+?\])""",
        re.VERBOSE,
    )

    @classmethod
    def to_event(cls, log: Log) -> Event:
        m = cls.REGEX.match(log.message.strip())
        if not m:
            raise UnsupportedLog(f"unmatched: {log.message.strip()}")

        groups: dict[str, str] = m.groupdict()
        stream_name: str = groups["stream"].strip()
        filter_name: str = groups["filter"].strip()
        action_name: str = groups["action"]
        event_type: str = groups["type"].strip()
        params: str = groups["params"].strip()

        logger.debug(f'parsed log at "{log.time}"; got {stream_name=}, {filter_name=}, {action_name=}, {event_type=}, {params=}')
        # run = action
        if event_type == "run":
            # command format is is ["cmd" "arg0"...] with no commas
            # transform to array manually
            cmd_line: str = params.lstrip('["').rstrip('"]')
            command: tuple[str, ...] = tuple([part for part in cmd_line.split('" "')])

            action = Action(log.time, stream_name, filter_name, action_name, command)
            return action

        if event_type == "match":
            # expected format is ["match1", "match2"]
            # not perfectly safe (can e.g. overload memory) but not subject to eval-like stuff
            try:
                matches: tuple[str] = tuple(literal_eval(params))
                return Match(log.time, stream_name, filter_name, matches)
            except SyntaxError as e:
                raise UnsupportedLog(f"cannot parse matches {params}: {e}")

        raise UnsupportedLog(f"type: {event_type}")
