from abc import ABC
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event(ABC):
    """
    Describe events as shown in the logs
    """

    time: datetime
    stream: str
    filter: str


@dataclass
class Match(Event):
    matches: tuple[str, ...]


@dataclass
class Action(Event):
    action: str
    command: tuple[str, ...]
