from fa_purity import (
    FrozenTools,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitive,
    JsonValue,
)

from .core import (
    SingerState,
)


def encode_state(state: SingerState) -> JsonObj:
    return FrozenTools.freeze(
        {
            "type": JsonValue.from_primitive(JsonPrimitive.from_str("STATE")),
            "value": JsonValue.from_json(state.value),
        },
    )
