from typing import TypeVar

T = TypeVar("T")


def lists_union(list1: list[T], list2: list[T]) -> list[T]:
    """Return the union of two lists"""
    return list(set(list1).union(set(list2)))
