import abc
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Specification(abc.ABC, Generic[T]):
    """
    Abstract base class for the Specification pattern.
    A specification determines if a candidate object matches some criteria.
    """

    @abc.abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Checks if the given candidate object satisfies the specification.

        Args:
            candidate: The object to check.

        Returns:
            True if the candidate satisfies the specification, False otherwise.
        """
        raise NotImplementedError

    def __and__(self, other: Any) -> "Specification[T]":
        """Combines this specification with another using a logical AND."""
        if not isinstance(other, Specification):
            return NotImplemented  # Allows Python to try reflected __rand__ or raise TypeError
        return AndSpecification(self, other)

    def __or__(self, other: Any) -> "Specification[T]":
        """Combines this specification with another using a logical OR."""
        if not isinstance(other, Specification):
            return NotImplemented  # Allows Python to try reflected __ror__ or raise TypeError
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        """Negates this specification using a logical NOT."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """
    A composite specification that is satisfied if both of its
    component specifications are satisfied.
    """

    def __init__(self, spec1: Specification[T], spec2: Specification[T]):
        self._spec1 = spec1
        self._spec2 = spec2

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._spec1.is_satisfied_by(candidate) and self._spec2.is_satisfied_by(
            candidate
        )


class OrSpecification(Specification[T]):
    """
    A composite specification that is satisfied if at least one of its
    component specifications is satisfied.
    """

    def __init__(self, spec1: Specification[T], spec2: Specification[T]):
        self._spec1 = spec1
        self._spec2 = spec2

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._spec1.is_satisfied_by(candidate) or self._spec2.is_satisfied_by(
            candidate
        )


class NotSpecification(Specification[T]):
    """
    A specification that is satisfied if its component specification
    is not satisfied (logical negation).
    """

    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
