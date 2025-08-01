from __future__ import (
    annotations,
)

from collections.abc import Callable
from dataclasses import (
    dataclass,
)
from typing import (
    Generic,
    TypeVar,
)

from fa_purity import (
    FrozenDict,
    PureIter,
)
from fa_purity.json import (
    JsonValueFactory,
    Primitive,
)

from fa_singer_io.singer.record import (
    SingerRecord,
)
from fa_singer_io.singer.schema.core import (
    Property,
    SingerSchema,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class _Patch(Generic[_T]):
    inner: _T


@dataclass(frozen=True)
class EncodeItem(Generic[_T]):
    _encode: _Patch[Callable[[_T], Primitive]]
    prop: Property

    def encode(self, item: _T) -> Primitive:
        return self._encode.inner(item)

    @staticmethod
    def new(
        encode: Callable[[_T], Primitive],
        prop: Property,
        _type: type[_T] | None = None,
    ) -> EncodeItem[_T]:
        """Use `_type` arg if typevar `_T` cannot be deduced and/or had to be set explicitly."""
        return EncodeItem(_Patch(encode), prop)


@dataclass(frozen=True)
class SingerEncoder(Generic[_T]):
    stream: str
    schema: SingerSchema
    _records: _Patch[Callable[[_T], SingerRecord]]

    def record(self, item: _T) -> SingerRecord:
        return self._records.inner(item)

    @staticmethod
    def new(stream: str, mapper: FrozenDict[str, EncodeItem[_T]]) -> SingerEncoder[_T]:
        props = FrozenDict({k: v.prop for k, v in mapper.items()})
        schema = SingerSchema.obj_schema(stream, props)

        def _records(item: _T) -> SingerRecord:
            encoded = FrozenDict(
                {k: JsonValueFactory.from_unfolded(v.encode(item)) for k, v in mapper.items()},
            )
            return SingerRecord(stream, encoded, None)

        return SingerEncoder(
            stream,
            schema,
            _Patch(_records),
        )


@dataclass(frozen=True)
class FullSingerEncoder(Generic[_T]):
    obj_encoders: PureIter[SingerEncoder[_T]]

    @property
    def schemas(self) -> PureIter[SingerSchema]:
        return self.obj_encoders.map(lambda e: e.schema)

    def records(self, item: _T) -> PureIter[SingerRecord]:
        return self.obj_encoders.map(lambda e: e.record(item))
