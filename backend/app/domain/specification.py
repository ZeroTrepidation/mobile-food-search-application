from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Iterable, List

T = TypeVar("T")


def _has_custom_order(spec: "Specification[T]") -> bool:
    # Detect if a specification overrides the default order implementation
    return type(spec).order is not Specification.order


class Specification(ABC, Generic[T]):
    """
    Specification pattern generic so that we can use it to define and combine simple and complex filters.
    Also allows us to add additional methods later on if needed that can be used by repository adapters to
    define how they should carry out the specifications (e.g., ordering of results).
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        raise NotImplementedError

    def filter(self, items: Iterable[T]) -> List[T]:
        return [i for i in items if self.is_satisfied_by(i)]

    def order(self, items: List[T]) -> List[T]:
        """
        Optional ordering hook. By default, returns items unchanged.
        Repository adapters should call this to allow specifications to influence ordering.
        """
        return items

    def __and__(self, other: "Specification[T]") -> "Specification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "Specification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "Specification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def order(self, items: List[T]) -> List[T]:
        # Prefer a child that provides a custom ordering. Deterministically favor left when both do.
        if _has_custom_order(self.left):
            return self.left.order(items)
        if _has_custom_order(self.right):
            return self.right.order(items)
        return items


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

    def order(self, items: List[T]) -> List[T]:
        if _has_custom_order(self.left):
            return self.left.order(items)
        if _has_custom_order(self.right):
            return self.right.order(items)
        return items


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def order(self, items: List[T]) -> List[T]:
        # Negation does not define its own order; delegate if inner has custom ordering.
        if _has_custom_order(self.spec):
            return self.spec.order(items)
        return items
