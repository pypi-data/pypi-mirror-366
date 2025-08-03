from abc import ABC
from ast import literal_eval
from datetime import datetime
import json
import re

import structlog

from .models.config import Config

from .models.event import Action, Event, LogEvent, Match, StartEvent, StopEvent
from .models.log import Log

logger = structlog.get_logger()
config = Config.get_config()


class ActionIgnored(Exception):
    pass


class UnsupportedLog(Exception):
    pass


class Transformer(ABC):
    REGEX_EVENT = re.compile(
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

    REGEX_CHANGE = re.compile(
        r"""
        INFO\s(?P<state>.+?)
        \scommand:\srun\s
        (?P<command>\[.+?\])""",
        re.VERBOSE,
    )

    @classmethod
    def to_event(cls, log: Log) -> Event:
        message = log.message.strip()
        # test different type of logs
        m = cls.REGEX_EVENT.match(message)
        if m:
            event = cls._to_log_event(log.time, m)
            # is there time left before recording actions?
            if config.ignore_actions > 0 and isinstance(event, Action):
                raise ActionIgnored(log)
            return event
        m = cls.REGEX_CHANGE.match(message)
        if m:
            return cls._to_reaction_event(log.time, m)
        raise UnsupportedLog(f"unmatched: {log.message.strip()}")

    @classmethod
    def _to_log_event(cls, t: datetime, m: re.Match[str]) -> LogEvent:
        groups: dict[str, str] = m.groupdict()
        stream_name: str = groups["stream"].strip()
        filter_name: str = groups["filter"].strip()
        action_name: str = groups["action"]
        event_type: str = groups["type"].strip()
        params: str = groups["params"].strip()

        logger.debug(f'parsed log at "{t}"; got {stream_name=}, {filter_name=}, {action_name=}, {event_type=}, {params=}')
        # run = action
        if event_type == "run":
            # command format is is ["cmd" "arg0"...] with no commas
            # transform to array manually
            cmd_line: str = params.lstrip('["').rstrip('"]')
            command: tuple[str, ...] = tuple([part for part in cmd_line.split('" "')])

            action = Action(t, stream_name, filter_name, action_name, command)
            return action

        if event_type == "match":
            # expected format is ["match1", "match2"]
            # not perfectly safe (can e.g. overload memory) but not subject to eval-like stuff
            try:
                matches: tuple[str] = tuple(json.loads(params))
                return Match(t, stream_name, filter_name, matches)
            except json.JSONDecodeError as e:
                raise UnsupportedLog(f"cannot parse matches {params}: {e}")

        raise UnsupportedLog(f"type: {event_type}")

    @classmethod
    def _to_reaction_event(cls, t: datetime, m: re.Match[str]) -> Event:
        groups = m.groupdict()
        state = groups["state"]
        command = groups["command"]
        match state:
            case "start":
                event_class = StartEvent
            case "stop":
                event_class = StopEvent
            case _:
                raise UnsupportedLog(f"state: {state}")
        try:
            command_args = tuple(literal_eval(command))
        except SyntaxError as e:
            raise UnsupportedLog(f"cannot parse command {command}: {e}")
        return event_class(t, command_args)
