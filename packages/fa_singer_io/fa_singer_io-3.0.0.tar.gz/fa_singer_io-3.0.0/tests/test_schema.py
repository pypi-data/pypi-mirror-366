from fa_purity import (
    Unsafe,
)

from fa_singer_io.json_schema.factory import (
    datetime_schema,
)
from fa_singer_io.singer.schema.core import (
    SingerSchema,
)
from fa_singer_io.singer.schema.decoder import (
    build_schema,
)
from fa_singer_io.singer.schema.encode import (
    encode_schema,
)
from fa_singer_io.singer.schema.factory import (
    from_jschema,
)
from tests.test_json_schema import (
    MOCK_SCHEMA,
)


def test_new_schema() -> None:
    assert from_jschema("foo", datetime_schema())


def test_inverse() -> None:
    schema = (
        SingerSchema.new(
            "test_stream",
            MOCK_SCHEMA,
            frozenset(["foo"]),
            frozenset(),
        )
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    assert schema == build_schema(encode_schema(schema)).alt(Unsafe.raise_exception).to_union()
