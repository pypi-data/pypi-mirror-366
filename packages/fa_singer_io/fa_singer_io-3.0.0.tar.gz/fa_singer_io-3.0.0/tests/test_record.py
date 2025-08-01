from fa_purity import (
    FrozenTools,
    Unsafe,
)
from fa_purity.json import (
    JsonValueFactory,
)

from fa_singer_io.singer.record.decoder import (
    build_record,
)
from fa_singer_io.singer.record.encode import (
    encode_record,
)
from fa_singer_io.singer.record.factory import (
    new_record_auto_time,
)


def test_inverse() -> None:
    record = Unsafe.compute(
        new_record_auto_time(
            "test_stream",
            FrozenTools.freeze({"data": JsonValueFactory.from_unfolded(123)}),
        ),
    )
    assert record == build_record(encode_record(record)).alt(Unsafe.raise_exception).to_union()
