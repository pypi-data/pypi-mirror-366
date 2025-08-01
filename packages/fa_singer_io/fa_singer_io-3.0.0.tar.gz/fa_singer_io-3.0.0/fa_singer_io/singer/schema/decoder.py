from fa_purity import (
    ResultE,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)

from fa_singer_io.json_schema.factory import (
    from_json,
)

from .core import (
    SingerSchema,
)


class DecodeError(Exception):
    pass


def build_schema(raw: JsonObj) -> ResultE[SingerSchema]:
    _bookmark_properties = JsonUnfolder.optional(
        raw,
        "bookmark_properties",
        lambda v: Unfolder.to_list_of(
            v,
            lambda j: Unfolder.to_primitive(j).bind(JsonPrimitiveUnfolder.to_str),
        ),
    ).map(lambda m: m.map(lambda item: frozenset(item)))
    _stream = JsonUnfolder.require(
        raw,
        "stream",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    )
    _schema = JsonUnfolder.require(raw, "schema", Unfolder.to_json).bind(from_json)
    _key_properties = JsonUnfolder.require(
        raw,
        "key_properties",
        lambda v: Unfolder.to_list_of(
            v,
            lambda j: Unfolder.to_primitive(j).bind(JsonPrimitiveUnfolder.to_str),
        ),
    ).map(lambda item: frozenset(item))
    return _bookmark_properties.bind(
        lambda bookmarks: _stream.bind(
            lambda stream: _schema.bind(
                lambda schema: _key_properties.bind(
                    lambda key_props: SingerSchema.new(
                        stream,
                        schema,
                        key_props,
                        bookmarks.value_or(None),
                    ),
                ),
            ),
        ),
    )
