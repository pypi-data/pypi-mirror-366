from dataclasses import (
    dataclass,
)

from fa_purity import (
    Result,
)
from fa_purity.json import (
    JsonObj,
    JsonValue,
    Unfolder,
)
from jsonschema.exceptions import (
    ValidationError,
)

from ._inner import (
    InnerJsonSchema,
)


@dataclass(frozen=True)
class JsonSchema:
    _inner: InnerJsonSchema

    def validate(self, record: JsonObj) -> Result[None, ValidationError]:
        try:
            self._inner.validator.validate(Unfolder.to_raw(JsonValue.from_json(record)))  # type: ignore[misc]
            return Result.success(None)
        except ValidationError as error:  # type: ignore[misc]
            return Result.failure(error)

    def encode(self) -> JsonObj:
        return self._inner.raw
