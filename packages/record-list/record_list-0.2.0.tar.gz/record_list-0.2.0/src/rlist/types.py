from typing import Protocol, Any, Callable, TypeVar


R = TypeVar("R")


class SupportsLt(Protocol):
    def __lt__(self, other: R) -> bool: ...


type FilterFunc = Callable[[R], bool]
type MapFunc = Callable[[R], Any]
type SortFunc = Callable[[R], SupportsLt]

type ListMultiplier = int
type ListAddend = list[R]
type ListComparand = list[R]
