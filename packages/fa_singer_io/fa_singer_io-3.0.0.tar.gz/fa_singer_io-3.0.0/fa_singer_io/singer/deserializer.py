from __future__ import (
    annotations,
)

from collections.abc import Iterable
from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)
from typing import (
    IO,
)

from fa_purity import (
    Cmd,
    PureIter,
    PureIterTransform,
    Result,
    ResultE,
    Unsafe,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValueFactory,
    Unfolder,
)

from fa_singer_io.singer import (
    SingerMessage,
)
from fa_singer_io.singer.record.decoder import (
    build_record,
)
from fa_singer_io.singer.schema.decoder import (
    build_schema,
)
from fa_singer_io.singer.state.decoder import (
    build_state,
)


@dataclass(frozen=True)
class _TmpWrapper:
    value: SingerMessage


class SingerType(Enum):
    RECORD = "RECORD"
    SCHEMA = "SCHEMA"
    STATE = "STATE"

    @staticmethod
    def decode(raw: str) -> ResultE[SingerType]:
        try:
            return Result.success(SingerType(raw.upper()))
        except ValueError as error:
            return Result.failure(error).alt(cast_exception)


def _deserialize(obj_type: SingerType, raw: JsonObj) -> ResultE[SingerMessage]:
    if obj_type is SingerType.RECORD:
        return build_record(raw).map(SingerMessage.from_record)
    if obj_type is SingerType.SCHEMA:
        return build_schema(raw).map(SingerMessage.from_schema)
    if obj_type is SingerType.STATE:
        return build_state(raw).map(SingerMessage.from_state)


def deserialize(raw: JsonObj) -> ResultE[SingerMessage]:
    obj_type = JsonUnfolder.require(
        raw,
        "type",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    ).bind(SingerType.decode)
    return obj_type.bind(lambda o: _deserialize(o, raw))


def _read_file(file: IO[str]) -> PureIter[str]:
    # IO file is supposed to be read-only
    def _iter_lines() -> Iterable[str]:
        line = file.readline()
        while line:
            yield line
            line = file.readline()

    return Unsafe.pure_iter_from_cmd(Cmd.wrap_impure(lambda: iter(_iter_lines())))


def try_from_file(file: IO[str]) -> PureIter[ResultE[SingerMessage]]:
    return (
        _read_file(file)
        .map(JsonValueFactory.loads)
        .map(lambda r: r.bind(Unfolder.to_json).bind(deserialize))
    )


def from_file_ignore_failed(file: IO[str]) -> PureIter[SingerMessage]:
    return (
        try_from_file(file)
        .map(lambda r: r.map(_TmpWrapper).value_or(None))
        .transform(lambda i: PureIterTransform.filter_opt(i))
        .map(lambda w: w.value)
    )
