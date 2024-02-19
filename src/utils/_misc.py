from typing import TypeVar

T = TypeVar("T")


def lists_union(list1: list[T], list2: list[T]) -> list[T]:
    """Return the union of two lists containing unique elements. There is no guarantee of
    the order of the elements in the resulting list.

    Params:
    - list1 - The first list
    - list2 - The second list"""
    return list(set(list1).union(set(list2)))
