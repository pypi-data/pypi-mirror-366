from collections import OrderedDict
from typing import Any

from asyncio_simple_http_server import HttpHeaders, HttpResponse, uri_mapping
import prometheus_client
from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    Metric,
    REGISTRY,
)
from prometheus_client.registry import Collector
import structlog

from reaction_metrics_exporter import __version__

from .models.config import Config
from .models.metric import FutureAction, ReactionMetrics
from .reaction import Reaction

logger = structlog.get_logger()
config = Config.get_config()


class MetricsHandler:
    HEADERS = HttpHeaders().set("Content-Type", "text/plain; charset=UTF-8")

    def __init__(self, metrics: ReactionMetrics):
        self._collector = ReactionCollector(metrics)
        # registry is a singleton holding multiple collector

        if not config.internals:
            REGISTRY._collector_to_names = {}
        REGISTRY.register(self._collector)

    @uri_mapping("/metrics")
    def metrics(self):
        # calls collect on every collector
        logger.debug("got a request on /metrics")
        openmetrics = prometheus_client.generate_latest(REGISTRY)
        return HttpResponse(200, self.HEADERS, openmetrics)


class ReactionCollector(Collector):
    def __init__(self, metrics: ReactionMetrics) -> None:
        self._metrics = metrics
        self._prev_matches = self._metrics.n_matches
        self._prev_actions = self._metrics.n_actions

    def collect(self) -> tuple[prometheus_client.Metric, ...]:
        logger.debug("start metrics collection")

        collected: list[Metric] = []
        # handle reset
        if self._metrics.n_matches < self._prev_matches:
            self._prev_matches = 0
        if self._metrics.n_actions < self._prev_actions:
            self._prev_actions = 0

        # all the metrics we are going to export
        # they do not accumulate: one object per collection
        build_info = GaugeMetricFamily(
            "reaction_exporter_build_info",
            "A metric with a constant '1' value labeled by version of the reaction_metrics_exporter.",
            labels=("version",),
        )
        collected.append(build_info)

        build_info.add_metric((__version__,), 1.0)
        # matches are not collected if configuration says so,
        # but could be around due to previous configuration and persistence
        if config.matches:
            match_total = CounterMetricFamily(
                "reaction_match_total",
                "Total number of matched logs.",
            )
            collected.append(match_total)
            # labels can vary with patterns and action names
            # we need to change global setting everytime because
            # the way the prometheus lib is made (and because
            # labels should not have high cardinality in general)
            for match, count in self._metrics.matches.items():
                match_total._labelnames = match.labels
                match_total.add_metric(match.values, count)
        if config.actions:
            action_total = CounterMetricFamily(
                "reaction_action_total",
                "Total number of matched logs.",
            )
            collected.append(action_total)
            for action, count in self._metrics.actions.items():
                action_total._labelnames = action.labels
                action_total.add_metric(action.values, count)

        n_pending = 0
        if config.pending:

            pending_count = GaugeMetricFamily(
                "reaction_pending_count",
                "Current number of pending actions.",
            )
            collected.append(pending_count)
            # pending actions cannot easily be inferred from logs: use `reaction show`
            for metric, count in self._collect_pending():
                pending_count._labelnames = metric.labels
                # multiple pending actions is possible
                pending_count.add_metric(metric.values, count)
                n_pending += count

        logger.info(
            f"end collecting metrics; {self._metrics.n_matches - self._prev_matches} new matches; {self._metrics.n_actions - self._prev_actions} new actions; {n_pending} pending actions"
        )
        self._prev_matches = self._metrics.n_matches
        self._prev_actions = self._metrics.n_actions

        return tuple(collected)

    def _collect_pending(self):
        show: OrderedDict[str, Any] = Reaction.show()
        for stream, filters in show.items():
            for filter, state in filters.items():
                for matches, data in state.items():
                    # i.e. action pending for this (stream, filter)
                    if "actions" in data:
                        for action, _ in data["actions"].items():
                            metric = FutureAction.from_show(stream, filter, matches, action)
                            yield metric, len(data["actions"])
