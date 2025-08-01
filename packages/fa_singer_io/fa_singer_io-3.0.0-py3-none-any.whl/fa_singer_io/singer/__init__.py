from __future__ import (
    annotations,
)

from collections.abc import Callable
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TypeVar,
)

from fa_purity import (
    Coproduct,
)

from fa_singer_io.singer.record import (
    SingerRecord,
)
from fa_singer_io.singer.schema import (
    SingerSchema,
)
from fa_singer_io.singer.state import (
    SingerState,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class SingerMessage:
    _private: _Private = field(repr=False, hash=False, compare=False)
    _inner: Coproduct[SingerRecord, Coproduct[SingerSchema, SingerState]]

    @staticmethod
    def from_record(record: SingerRecord) -> SingerMessage:
        return SingerMessage(_Private(), Coproduct.inl(record))

    @staticmethod
    def from_schema(schema: SingerSchema) -> SingerMessage:
        return SingerMessage(_Private(), Coproduct.inr(Coproduct.inl(schema)))

    @staticmethod
    def from_state(state: SingerState) -> SingerMessage:
        return SingerMessage(_Private(), Coproduct.inr(Coproduct.inr(state)))

    def map(
        self,
        record_case: Callable[[SingerRecord], _T],
        schema_case: Callable[[SingerSchema], _T],
        state_case: Callable[[SingerState], _T],
    ) -> _T:
        return self._inner.map(record_case, lambda c: c.map(schema_case, state_case))


__all__ = [
    "SingerRecord",
    "SingerSchema",
    "SingerState",
]
