from typing import (
    TypeVar,
)

from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)
from fa_purity import (
    FrozenList,
)

_dag: dict[str, FrozenList[FrozenList[str] | str]] = {
    "fa_singer_io": (
        "singer",
        "json_schema",
        "time",
    ),
    "fa_singer_io.singer": (
        ("deserializer", "emitter", "validate", "encoder"),
        ("record", "schema", "state"),
        "errors",
        "_utils",
    ),
    "fa_singer_io.json_schema": (
        "factory",
        "_factory",
        "core",
        "_inner",
    ),
    "fa_singer_io.singer.state": (
        ("encode", "decoder"),
        "core",
    ),
    "fa_singer_io.singer.schema": (
        ("encode", "decoder", "factory"),
        "core",
    ),
    "fa_singer_io.singer.record": (
        ("encode", "decoder", "factory"),
        "core",
    ),
}
_T = TypeVar("_T")


def raise_or_return(item: Exception | _T) -> _T:
    if isinstance(item, Exception):
        raise item
    return item


def project_dag() -> DagMap:
    return raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> dict[FullPathModule, frozenset[FullPathModule]]:
    _raw: dict[str, frozenset[str]] = {}
    return {
        raise_or_return(FullPathModule.from_raw(k)): frozenset(
            raise_or_return(FullPathModule.from_raw(i)) for i in v
        )
        for k, v in _raw.items()
    }
