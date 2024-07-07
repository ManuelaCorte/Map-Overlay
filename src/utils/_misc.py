from typing import TypeVar

T = TypeVar("T")


def lists_union(list1: list[T], list2: list[T]) -> list[T]:
    """Return the union of two lists containing unique elements. There is no guarantee of
    the order of the elements in the resulting list.

    Params:
    - list1 - The first list
    - list2 - The second list"""
    return list(set(list1).union(set(list2)))


def trunc_float(number: float, decimals: int) -> float:
    """Truncate a float number to a given number of decimal places.

    Params:
    - number - The number to truncate
    - decimals - The number of decimal places to keep"""
    x = round(number, decimals + 1)
    return int(x * 10**decimals) / 10**decimals
