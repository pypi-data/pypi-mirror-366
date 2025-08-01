from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
)

from fa_purity import (
    Cmd,
    Unsafe,
)
from fa_purity.date_time import (
    DatetimeFactory,
    DatetimeTZ,
    DatetimeUTC,
)
from pyrfc3339 import (
    generate,
)
from pyrfc3339 import (
    parse as parse_rfc3339,
)


@dataclass(frozen=True)
class _Private:
    pass


def _no_micro(date: datetime) -> datetime:
    return datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
        0,
        date.tzinfo,
    )


@dataclass(frozen=True)
class DateTime:
    _private: _Private = field(repr=False, hash=False, compare=False)
    _date: DatetimeUTC

    @staticmethod
    def from_utc(date: DatetimeUTC) -> DateTime:
        return DateTime(
            _Private(),
            DatetimeUTC.assert_utc(_no_micro(date.date_time))
            .alt(Unsafe.raise_exception)
            .to_union(),
        )

    @classmethod
    def now(cls) -> Cmd[DateTime]:
        return DatetimeFactory.date_now().map(cls.from_utc)

    @classmethod
    def parse(cls, raw: str) -> DateTime:
        return cls.from_utc(
            DatetimeFactory.to_utc(
                DatetimeTZ.assert_tz(parse_rfc3339(raw)).alt(Unsafe.raise_exception).to_union(),
            ),
        )

    def to_utc_str(self) -> str:
        return generate(self._date.date_time)

    def to_str(self) -> str:
        return generate(self._date.date_time, utc=False)
