from collections import defaultdict
import copy
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from typing import Self

import jinja2
import structlog

from ..models.config import Config
from ..reaction import Reaction
from .event import Action, LogEvent, Match

logger = structlog.get_logger()
config = Config.get_config()


class UnmatchedAction(Exception):
    pass


class UnmatchedPattern(Exception):
    pass


@dataclass(frozen=True)
class BaseMetric:
    """
    each metric is identified by a unique set of labels and filters.
    meant to be used e.g. in a dict to aggregate new metrics fast.
    """

    stream: str
    filter: str

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter")

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter)


@dataclass(frozen=True)
class MatchMetric(BaseMetric):
    # each element of pattern has its match at same index in matches
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    # to render matches values
    _env = jinja2.Environment()

    @property
    def labels(self) -> tuple[str, ...]:
        return super().labels + self.patterns

    @property
    def values(self) -> tuple[str, ...]:
        return super().values + self.matches

    @classmethod
    def from_match(cls, match: Match) -> Self:
        # for now we need patterns from matches for actions
        if config.matches_extra or config.actions_extra:
            patterns, matches = cls._filtermatches(match.stream, match.filter, match.matches)
        else:
            patterns, matches = (), ()
        logger.debug(f"new match: stream {match.stream}, filter {match.filter}, patterns {patterns}, matches {matches}")
        return cls(match.stream, match.filter, patterns, matches)

    @classmethod
    @cache
    def _filtermatches(cls, stream: str, filter: str, matches: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """
        logs contains matches but not pattern names, but they are sorted according pattern names.
        get pattern names from config and then filter matches according the exporter's configuration.
        """
        final_patterns: list[str] = []
        final_matches: list[str] = []
        try:
            patterns: tuple[str, ...] = Reaction.patterns(stream, filter)
        except KeyError as e:
            raise UnmatchedPattern(f"cannot find patterns at {stream}.{filter} (key {e}) for matches {matches}: has config changed?")

        if len(patterns) != len(matches):
            raise UnmatchedPattern(f"different number of matches ({matches}) and patterns ({patterns})")

        transforms = config.transforms(stream, filter)
        # (match, pattern) side by side
        for pattern, match in zip(patterns, matches):
            # i.e. if pattern is configured to be a label
            if template := transforms.get(pattern):
                # pattern name is usable is the template, pass the match value
                try:
                    value = cls._env.from_string(template, {pattern: match}).render()
                    final_patterns.append(pattern)
                    final_matches.append(value)
                except jinja2.exceptions.TemplateSyntaxError as e:
                    logger.warn(f"cannot use match {match} for pattern {pattern} with template {template}: {e}")

        return tuple(final_patterns), tuple(final_matches)


@dataclass(frozen=True)
class ActionMetric(MatchMetric):
    action: str

    @property
    def labels(self) -> tuple[str, ...]:
        return (*super().labels, "action")

    @property
    def values(self) -> tuple[str, ...]:
        return (*super().values, self.action)

    @classmethod
    def from_action(cls, action: Action, match: MatchMetric | None = None) -> Self:
        """
        match is expected to be the match which triggered the action.
        """
        if not match or not config.actions_extra:
            patterns, matches = tuple(), tuple()
        else:
            patterns, matches = match.patterns, match.matches
        logger.debug(f"new action: stream {action.stream}, filter {action.filter}, action {action.action}, patterns {patterns}, matches {matches}")
        return cls(action.stream, action.filter, patterns, matches, action.action)


@dataclass(frozen=True)
# a FutureAction has matches and future action name.
# in logs we don't have matches for actions, so it may
# be useful to record at least those ones.
# for multiple heritage in dataclasses attributes are added
# backwards, so that we need to pass matches before action in constructor.
# ---
# it uses ActionMetric for `labels` and `values`
class FutureAction(ActionMetric, MatchMetric):
    @classmethod
    def from_show(cls, stream: str, filter: str, matches_str: str, action: str):
        if config.pending_extra:
            # reaction show uses space to delimitate matches
            # won't work if space in match
            matches: tuple[str, ...] = tuple(matches_str.split(" "))
            patterns, matches = cls._filtermatches(stream, filter, matches)
        else:
            patterns, matches = (), ()
        return cls(stream, filter, patterns, matches, action)


class ReactionMetrics:
    def __init__(self) -> None:
        # meant to be monotonic counters
        self.matches: dict[MatchMetric, int] = defaultdict(int)
        self.actions: dict[ActionMetric, int] = defaultdict(int)

        # holds the last match for the given (stream, filter) pair.
        # the next action for (stream, filter) is considered to be
        # triggered by match. this is true if the logs are well-ordered.
        self.last_match: dict[tuple[str, str], MatchMetric] = {}

        # counters can be reset if they become too large while still working with some query functions,
        # e.g. https://prometheus.io/docs/prometheus/latest/querying/functions/#increase
        # also on VictoriaMetrics, `running_sum(increase(<counter>))` approximates monotonicity on a given range
        # individual Grafana panels can only have their own relative time (e.g. 1y)
        # ---
        # note that unpickling does not trigger constructor, so the date stays the same
        self.start: datetime = datetime.now()

    def add(self, event: LogEvent):
        match event:
            case Action():
                # get last corresponding match to know matches and patterns
                if config.actions:
                    last_match: MatchMetric | None = self.last_match.get((event.stream, event.filter))
                    if last_match is None:
                        raise UnmatchedAction(
                            f"action {event.action} triggered for stream {event.stream} and filter {event.filter} but not previous match found; ignoring."
                        )
                    self.actions[ActionMetric.from_action(event, last_match)] += 1
            case Match():
                metric = MatchMetric.from_match(event)
                if config.matches:
                    if not config.matches_extra:
                        # we don't want to save extra info in matches, but we
                        # need to keep this info in last matches to feed corresponding actions
                        event = copy.deepcopy(event)
                        event.matches = ()
                        match = MatchMetric.from_match(event)
                    else:
                        match = metric
                    self.matches[match] += 1
                # actions need matches anyway
                self.last_match[(event.stream, event.filter)] = metric
            case _:
                raise TypeError(f"unsupported event type: {type(event)}")

    @property
    def n_matches(self) -> int:
        return sum(self.matches.values())

    @property
    def n_actions(self) -> int:
        return sum(self.actions.values())

    def clear(self):
        # reset metrics af if is was first launch
        self.matches.clear()
        self.actions.clear()
        self.last_match.clear()
        self.start = datetime.now()

    def __repr__(self):
        return str(self.__dict__)
