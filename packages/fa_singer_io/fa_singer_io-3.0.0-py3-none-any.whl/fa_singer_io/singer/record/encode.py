from fa_purity import (
    FrozenTools,
    Maybe,
    Unsafe,
)
from fa_purity.json import (
    JsonObj,
    JsonValue,
    JsonValueFactory,
)

from .core import (
    SingerRecord,
)


def encode_record(record: SingerRecord) -> JsonObj:
    time_str = Maybe.from_optional(record.time_extracted).map(lambda date: date.to_utc_str())
    raw_json: dict[str, JsonValue] = {
        "type": JsonValueFactory.from_unfolded("RECORD"),
        "stream": JsonValueFactory.from_unfolded(record.stream),
        "record": JsonValueFactory.from_unfolded(record.record),
    }
    if time_str.map(bool).value_or(False):
        raw_json["time_extracted"] = JsonValueFactory.from_unfolded(
            time_str.or_else_call(lambda: Unsafe.raise_exception(Exception("impossible"))),
        )

    return FrozenTools.freeze(raw_json)
