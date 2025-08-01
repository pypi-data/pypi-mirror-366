from fa_purity import (
    Unsafe,
)

from fa_singer_io.json_schema.core import (
    JsonSchema,
)

from .core import (
    SingerSchema,
)


def from_jschema(
    stream: str,
    schema: JsonSchema,
) -> SingerSchema:
    return (
        SingerSchema.new(stream, schema, frozenset([]), None).alt(Unsafe.raise_exception).to_union()
    )
