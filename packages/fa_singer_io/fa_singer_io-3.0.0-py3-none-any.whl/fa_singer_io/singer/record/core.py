from dataclasses import (
    dataclass,
)

from fa_purity.json import (
    JsonObj,
)

from fa_singer_io.time import (
    DateTime,
)


@dataclass(frozen=True)
class SingerRecord:
    stream: str
    record: JsonObj
    time_extracted: DateTime | None
