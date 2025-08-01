from typing import (
    TypeVar,
)

from fa_purity import (
    Result,
)

_T = TypeVar("_T")


def all_keys_in(
    items: frozenset[_T],
    requires: frozenset[_T] | None,
) -> Result[None, frozenset[_T]]:
    _requires: frozenset[_T] = requires if requires is not None else frozenset([])
    if all(r in items for r in _requires):
        return Result.success(None)
    return Result.failure(_requires - items)
