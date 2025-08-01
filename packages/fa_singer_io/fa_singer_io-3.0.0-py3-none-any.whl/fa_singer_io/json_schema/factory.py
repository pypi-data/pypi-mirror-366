import warnings

from ._factory import (
    JSchemaFactory,
    SupportedType,
)

warnings.warn(
    "`json_schema.factory` module is deprecated. Use `json_schema.JSchemaFactory` class instead",
    DeprecationWarning,
    stacklevel=2,
)

from_json = JSchemaFactory.from_json
multi_type = JSchemaFactory.multi_type
from_prim_type = JSchemaFactory.from_prim_type
opt_prim_type = JSchemaFactory.opt_prim_type
datetime_schema = JSchemaFactory.datetime_schema
opt_datetime_schema = JSchemaFactory.opt_datetime_schema

__all__ = [
    "SupportedType",
]
