from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class State(Enum):
    START = auto()
    STOP = auto()


@dataclass
class Event(ABC):
    """
    Describe events as shown in the logs
    """

    time: datetime


@dataclass
class StartEvent(Event):
    command: tuple[str]


@dataclass
class StopEvent(Event):
    command: tuple[str]


@dataclass
class LogEvent(Event):
    """
    Describe something done by reaction regarding logs
    """

    stream: str
    filter: str


@dataclass
class Match(LogEvent):
    matches: tuple[str, ...]


@dataclass
class Action(LogEvent):
    action: str
    command: tuple[str, ...]
