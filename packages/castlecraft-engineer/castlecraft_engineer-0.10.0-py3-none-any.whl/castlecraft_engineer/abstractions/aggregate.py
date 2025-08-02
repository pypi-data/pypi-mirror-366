import abc
from typing import (
    Generic,
    List,
    TypeVar,
)

from .event import Event

TAggregateId = TypeVar("TAggregateId")


class Aggregate(Generic[TAggregateId], abc.ABC):
    """Base class for Aggregate Roots."""

    def __init__(self, id: TAggregateId, version: int = -1) -> None:
        if id is None:
            raise ValueError("Aggregate ID required.")
        self._id: TAggregateId = id
        # version for optimistic concurrency
        self._version: int = version
        self._uncommitted_events: List[Event] = []

    @property
    def id(self) -> TAggregateId:
        return self._id

    @property
    def version(self) -> int:
        """Current version for optimistic concurrency."""
        return self._version

    @property
    def uncommitted_events(self) -> List[Event]:
        """Events recorded since last save."""
        return self._uncommitted_events

    def _record_event(self, event: Event) -> None:
        """Records a domain event."""
        if not isinstance(event, Event):
            raise TypeError("Can only record Event instances.")
        self._uncommitted_events.append(event)

    def pull_uncommitted_events(self) -> List[Event]:
        """Retrieves and clears uncommitted events."""
        events = self._uncommitted_events[:]
        self._uncommitted_events.clear()
        return events

    def _increment_version(self) -> None:
        self._version += 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id!r}, version={self.version})>"  # noqa: E501
