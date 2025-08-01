from decimal import (
    Decimal,
)

from fa_purity import (
    FrozenTools,
    Unsafe,
)
from fa_purity.json import (
    JsonValue,
    JsonValueFactory,
)

from fa_singer_io.json_schema.factory import (
    datetime_schema,
    from_json,
    from_prim_type,
    opt_datetime_schema,
    opt_prim_type,
)

MOCK_SCHEMA = (
    from_json(
        FrozenTools.freeze(
            {
                "properties": JsonValue.from_json(
                    FrozenTools.freeze({"foo": JsonValue.from_json(from_prim_type(int).encode())}),
                ),
            },
        ),
    )
    .alt(Unsafe.raise_exception)
    .to_union()
)
PrimitiveTypesList = [
    bool,
    int,
    type(None),
    Decimal,
    float,
    str,
]


def test_mock_schema() -> None:
    valid = FrozenTools.freeze({"foo": JsonValueFactory.from_unfolded(123)})
    invalid = FrozenTools.freeze({"foo": JsonValueFactory.from_unfolded("text")})
    assert MOCK_SCHEMA.validate(valid).alt(Unsafe.raise_exception).to_union() is None
    assert (
        MOCK_SCHEMA.validate(invalid)
        .map(lambda _: Unsafe.raise_exception(ValueError("Should fail")))
        .to_union()
    )


def test_from_prim_type() -> None:
    for t in PrimitiveTypesList:
        assert from_prim_type(t)


def test_opt_prim_type() -> None:
    for t in PrimitiveTypesList:
        assert opt_prim_type(t)


def test_datetime_schema() -> None:
    assert datetime_schema()


def test_opt_datetime_schema() -> None:
    assert opt_datetime_schema()
