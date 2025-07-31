import copy
import logging
from collections import defaultdict
from types import MappingProxyType
from typing import Any, DefaultDict, Dict, List, Mapping, Optional, Tuple

from crystallize.datasources.artifacts import ArtifactLog
from crystallize.utils.exceptions import ContextMutationError


class FrozenMetrics:
    """Immutable mapping of metric lists with safe append."""

    def __init__(self) -> None:
        self._metrics: DefaultDict[str, List[Any]] = defaultdict(list)

    def __getitem__(self, key: str) -> Tuple[Any, ...]:
        return tuple(self._metrics[key])

    def add(self, key: str, value: Any) -> None:
        self._metrics[key].append(value)

    def as_dict(self) -> Mapping[str, Tuple[Any, ...]]:
        return MappingProxyType({k: tuple(v) for k, v in self._metrics.items()})


class FrozenContext:
    """Immutable execution context shared between pipeline steps.

    Once a key is set its value cannot be modified. Attempting to do so raises
    :class:`ContextMutationError`. This immutability guarantees deterministic
    provenance during pipeline execution.

        Attributes:
            metrics: :class:`FrozenMetrics` used to accumulate lists of metric
            values.
        artifacts: :class:`ArtifactLog` collecting binary artifacts to be saved
            by :class:`~crystallize.plugins.plugins.ArtifactPlugin`.
        logger: :class:`logging.Logger` used for debug and info messages.
    """

    def __init__(
        self, initial: Mapping[str, Any], logger: Optional[logging.Logger] = None
    ) -> None:
        self._data = copy.deepcopy(dict(initial))
        self.metrics = FrozenMetrics()
        self.artifacts = ArtifactLog()
        self.logger = logger or logging.getLogger("crystallize")

    def __getitem__(self, key: str) -> Any:
        return copy.deepcopy(self._data[key])

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._data:
            raise ContextMutationError(f"Cannot mutate existing key: '{key}'")
        self._data[key] = value

    def add(self, key: str, value: Any) -> None:
        """Alias for ``__setitem__`` providing a clearer API."""
        self.__setitem__(key, value)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Return the value for ``key`` if present else ``default``."""
        if key in self._data:
            return copy.deepcopy(self._data[key])
        return copy.deepcopy(default)

    def as_dict(self) -> Mapping[str, Any]:
        return MappingProxyType(copy.deepcopy(self._data))


class LoggingContext:
    """Proxy around :class:`FrozenContext` that records all key accesses."""

    def __init__(self, ctx: FrozenContext, logger: logging.Logger) -> None:
        self._ctx = ctx
        self._logger = logger
        self.reads: Dict[str, Any] = {}
        self.metrics = ctx.metrics

    # -------------------------------------------------------------- #
    def __getattr__(self, name: str) -> Any:  # pragma: no cover - passthrough
        return getattr(self._ctx, name)

    def __getitem__(self, key: str) -> Any:
        value = self._ctx[key]
        self.reads[key] = value
        self._logger.debug("Read %s -> %s", key, value)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self._ctx[key] = value

    def add(self, key: str, value: Any) -> None:
        self._ctx.add(key, value)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self._ctx.as_dict():
            value = self._ctx.get(key)
            self.reads[key] = value
            self._logger.debug("Read %s -> %s", key, value)
            return value
        return default

    def as_dict(self) -> Mapping[str, Any]:
        return self._ctx.as_dict()
