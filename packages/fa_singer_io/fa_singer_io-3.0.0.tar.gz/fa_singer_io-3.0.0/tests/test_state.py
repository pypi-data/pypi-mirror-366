from fa_purity import (
    FrozenTools,
    Unsafe,
)
from fa_purity.json import (
    JsonPrimitive,
    JsonValue,
)

from fa_singer_io.singer.state.core import (
    SingerState,
)
from fa_singer_io.singer.state.decoder import (
    build_state,
)
from fa_singer_io.singer.state.encode import (
    encode_state,
)


def test_inverse() -> None:
    state = SingerState(
        FrozenTools.freeze(
            {"state": JsonValue.from_primitive(JsonPrimitive.from_str("some state"))},
        ),
    )
    assert state == build_state(encode_state(state)).alt(Unsafe.raise_exception).to_union()
