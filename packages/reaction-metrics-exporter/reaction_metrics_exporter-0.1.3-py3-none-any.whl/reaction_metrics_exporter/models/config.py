from collections import OrderedDict
from functools import cache
import os
import re
from typing import Any, Self

from dateutil.relativedelta import relativedelta
from ruamel.yaml import YAML
from schema import And, Optional, Or, Schema, Use
import structlog

logger = structlog.get_logger()


class Config:
    """
    singleton-ish holding the exporter's configuration.
    does validation and expose most of its configuration as public attributes.
    """

    _inst: Self | None = None
    _reader = YAML()

    # forget is written "\d+{d,w,m,y,H,M}, e.g. 12w or 12H"
    _REGEX_DURATION = re.compile(r"(?P<unit>\d+)(?P<kind>\w)")
    # to call timedelta constructor
    _DELTA_MAP = {
        "u": "microseconds",
        "S": "seconds",
        "M": "minutes",
        "H": "hours",
        "d": "days",
        "w": "weeks",
        "m": "months",
        "y": "years",
    }

    _listen_schema = Schema(
        {
            Optional("address", default="127.0.0.1"): str,
            Optional("port", default=8080): int,
        }
    )

    _reaction_schema = Schema(
        {
            Optional("config", default="/etc/reaction"): os.path.exists,
            # choose systemd by default, and accept only one of "systemd" or "file" key
            Optional("logs", default={"systemd": "reaction.service"}): Or(
                {  # pyright: ignore[reportArgumentType]
                    Optional("systemd", default="reaction.service"): And(
                        # a way to set default value if key exists but value is None.
                        Use(lambda v: "reaction.service" if v is None else v),  # pyright: ignore[reportArgumentType]
                        str,
                    )
                },
                {  # pyright: ignore[reportArgumentType]
                    Optional("file", default="/var/log/reaction.log"): And(
                        Use(lambda v: "/var/log/reaction.log" if v is None else v), str  # pyright: ignore[reportArgumentType]
                    )
                },
            ),
            Optional("socket", default="/run/reaction/reaction.sock"): str,
        }
    )
    _persistence_schema = Schema(
        {
            Optional("folder", default=f"/var/lib/reaction-metrics-exporter"): str,
            Optional("interval", default=600): Or(float, int),
            Optional("forget", default="10y"): str,
        }
    )

    # a bit complex because we want to handle keys whose presence acts as bool,
    # so they cannot have a default value and can contains additionnal dictionaries with defaults
    _extra_schema = And(
        # set default value if None, then validate
        Use(lambda d: {"extra": True} if d is None else d),  # pyright: ignore[reportArgumentType]
        {Optional("extra", default=True): bool},  # pyright: ignore[reportArgumentType]
    )
    _metrics_schema = Schema(
        {
            Optional("all", default={}): Or({str: Or(str, None)}, {}),  # pyright: ignore[reportArgumentType]
            Optional("for", default={}): Or({str: {str: {str: Or(str, None)}}}, {}),  # pyright: ignore[reportArgumentType]
            Optional("export", default={}): {
                Optional("matches"): _extra_schema,
                Optional("actions"): _extra_schema,
                Optional("pending"): _extra_schema,
                Optional("internals"): Or(bool, None),  # pyright: ignore[reportArgumentType]
            },
        }
    )
    # Schema is made of subschema, allowing for complex default values
    _schema = Schema(
        {
            Optional("loglevel", default="INFO"): And(
                str,
                lambda s: s.upper() in ["DEBUG", "INFO", "WARNING", "ERROR"],
            ),
            Optional("persist", default=_persistence_schema.validate({})): _persistence_schema,
            Optional("listen", default=_listen_schema.validate({})): _listen_schema,
            Optional("reaction", default=_reaction_schema.validate({})): _reaction_schema,
            Optional("metrics", default=_metrics_schema.validate({})): _metrics_schema,
        }
    )

    def __init__(self):
        self._conf = OrderedDict()
        # internal setting controlled by main app
        # how many seconds to ignore actions when starting
        self.max_ignore_actions: int = 120
        # how many seconds left
        self.ignore_actions: int = 0

    @classmethod
    def get_config(cls) -> Self:
        # use defaults
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    @classmethod
    def from_file(cls, config_path: str) -> Self:
        inst = cls.get_config()
        logger.debug(f"using config file: {config_path}")
        with open(config_path, "r") as file:
            content = cls._reader.load(file.read())
            if not content:
                # to get default values
                content = {}
        inst._set_conf(content)
        return inst

    @classmethod
    def from_default(cls) -> Self:
        inst = cls.get_config()
        logger.debug(f"using no config file")
        inst._set_conf({})
        return inst

    def _set_conf(self, content: dict[str, Any]) -> None:
        logger.debug(f"initial configuration: {content}")
        self._conf: OrderedDict[str, Any] = self._schema.validate(content)
        logger.info(f"using configuration: {self._conf}")
        logger.debug(
            f"will export: matches: {self.matches} (labels: {self.matches_extra}); actions: {self.actions} (labels: {self.actions_extra}); pending: {self.pending} (labels: {self.pending_extra})"
        )

    @property
    def listen(self) -> tuple[str, int]:
        return (
            self._conf["listen"]["address"],
            self._conf["listen"]["port"],
        )

    @property
    def log_level(self) -> str:
        return self._conf["loglevel"]

    @property
    def socket(self) -> str:
        return self._conf["reaction"]["socket"]

    @property
    def reaction_config(self) -> str:
        return self._conf["reaction"]["config"]

    @property
    def type(self) -> str:
        return list(self._conf["reaction"]["logs"])[0]

    @property
    def path(self) -> str:
        return self._conf["reaction"]["logs"][self.type]

    @property
    def persist_directory(self) -> str:
        return self._conf["persist"]["folder"]

    @property
    def persist_interval(self) -> int:
        return self._conf["persist"]["interval"]

    @property
    def forget(self) -> relativedelta:
        return self._parse_duration(self._conf["persist"]["forget"])

    @property
    def actions(self) -> bool:
        return self._use_metric("actions")

    @property
    def actions_extra(self) -> bool:
        return self._use_labels("actions")

    @property
    def matches(self) -> bool:
        return self._use_metric("matches")

    @property
    def matches_extra(self) -> bool:
        return self._use_labels("matches")

    @property
    def pending(self) -> bool:
        return self._use_metric("pending")

    @property
    def pending_extra(self) -> bool:
        return self._use_labels("pending")

    @property
    def internals(self) -> bool:
        return self._use_metric("internals")

    @property
    def journal(self) -> str | None:
        # specific usage for Docker where user needs to specify
        # the mounted location of host journal files
        return os.environ.get("JOURNAL", None)

    @cache
    def transforms(self, stream: str, filter: str) -> dict[str, str]:
        """
        returns patterns that should be kept as labels, and how should matches be rendered.
        """
        all = self._conf["metrics"]["all"]
        locals = self._conf["metrics"]["for"]
        # if duplicate key first one is overriden (i.e. global transform is overwriten)
        merge: dict[str, str | None] = all | locals.get(stream, {}).get(filter, {})
        res: dict[str, str] = {}
        for pattern, value in merge.items():
            # i.e. use match as-is
            if value is None:
                res[pattern] = "{{ " + pattern + " }}"
            else:
                res[pattern] = value
        return res

    def __repr__(self) -> str:
        # useful for pytest
        return str(self._conf)

    def _use_metric(self, metric: str):
        return metric in self._conf["metrics"]["export"]

    def _use_labels(self, metric: str) -> bool:
        return self._use_metric(metric) and (
            # by default, we export labels
            self._conf["metrics"]["export"][metric] is None
            or self._conf["metrics"]["export"][metric].get("extra")
        )

    def _parse_duration(self, duration: str) -> relativedelta:
        """
        only supports days (1d), weeks (1w), months (1m) or years (1y).
        """
        if match := self._REGEX_DURATION.match(duration):
            groups: dict[str, str] = match.groupdict()
            try:
                delta: dict[str, int] = {self._DELTA_MAP[groups["kind"]]: int(groups["unit"])}
            except KeyError:
                raise ValueError(f"could not parse duration {duration}: unit must be one of {self._DELTA_MAP}")
            reldelta = relativedelta(**delta)  # pyright: ignore[reportArgumentType] : bad unpacking guess
            logger.debug(f"parsed duration {duration} to {reldelta}")
            return reldelta

        logger.warn(f"unmatched duration: {duration}; default to 10y")
        return relativedelta(years=10)
