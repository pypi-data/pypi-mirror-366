from fa_purity import (
    Cmd,
)
from fa_purity.json import (
    JsonObj,
)

from fa_singer_io.time import (
    DateTime,
)

from .core import (
    SingerRecord,
)


def new_record_auto_time(stream: str, record: JsonObj) -> Cmd[SingerRecord]:
    return DateTime.now().map(lambda d: SingerRecord(stream, record, d))
