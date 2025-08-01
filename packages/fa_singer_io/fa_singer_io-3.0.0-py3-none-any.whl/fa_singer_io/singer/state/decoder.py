from fa_purity import (
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)

from fa_singer_io.singer._utils import (
    all_keys_in,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)

from .core import (
    SingerState,
)


def _decode_state(parsed_type: str, raw_json: JsonObj) -> ResultE[SingerState]:
    if parsed_type == "STATE":
        value = JsonUnfolder.require(raw_json, "value", Unfolder.to_json)
        return value.map(SingerState)
    return Result.failure(Exception(f'Expected "RECORD" not "{parsed_type}"'))


def build_state(raw_json: JsonObj) -> ResultE[SingerState]:
    required_keys = frozenset({"type", "value"})
    check = (
        all_keys_in(frozenset(raw_json), required_keys)
        .alt(lambda m: MissingKeys(m, "raw singer state"))
        .to_union()
    )
    if check is not None:
        return Result.failure(cast_exception(ValueError(check)), SingerState)
    return JsonUnfolder.require(
        raw_json,
        "type",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    ).bind(lambda p: _decode_state(p, raw_json))
