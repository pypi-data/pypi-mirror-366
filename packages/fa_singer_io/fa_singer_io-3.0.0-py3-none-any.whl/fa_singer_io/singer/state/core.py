from dataclasses import (
    dataclass,
)

from fa_purity.json import (
    JsonObj,
)


@dataclass(frozen=True)
class SingerState:
    value: JsonObj
