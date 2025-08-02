import abc
from typing import Generic, List, Optional, Sequence, TypeVar

from castlecraft_engineer.abstractions.event import Event

TAggregateId = TypeVar("TAggregateId")


class EventStoreConflictError(RuntimeError):
    """Raised when there's a conflict appending events, e.g., due to version mismatch."""

    def __init__(
        self,
        aggregate_id: TAggregateId,
        expected_version: int,
        actual_version: Optional[int] = None,
    ):
        self.aggregate_id = aggregate_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Conflict appending events for aggregate {aggregate_id}. "
            f"Expected version {expected_version}, but current version is {actual_version}."
        )


class EventStore(Generic[TAggregateId], abc.ABC):
    """
    Abstract base class for an event store, responsible for persisting
    and retrieving streams of domain events.
    """

    @abc.abstractmethod
    async def append_events(
        self,
        aggregate_id: TAggregateId,
        expected_version: int,
        events: Sequence[Event],
    ) -> None:
        """
        Appends a list of events to the stream for a given aggregate.

        Args:
            aggregate_id: The ID of the aggregate to which the events belong.
            expected_version: The version of the aggregate that these events are based on.
                              Used for optimistic concurrency control. If the current
                              version in the store does not match this, an
                              EventStoreConflictError should be raised.
            events: A list of domain event instances to append.

        Raises:
            EventStoreConflictError: If the expected_version does not match the
                                     current version of the event stream for the aggregate.
            Exception: Implementation-specific exceptions related to storage failures.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def load_events(
        self,
        aggregate_id: TAggregateId,
        from_version: Optional[int] = None,
    ) -> List[Event]:
        """
        Loads the stream of events for a given aggregate.

        Args:
            aggregate_id: The ID of the aggregate whose events are to be loaded.
            from_version: Optionally, the version from which to start loading events.
                          If None, loads all events for the aggregate.

        Returns:
            A list of domain event instances, ordered by their sequence.
            Returns an empty list if the aggregate has no events or doesn't exist.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_current_version(self, aggregate_id: TAggregateId) -> Optional[int]:
        """
        Retrieves the current version of the event stream for a given aggregate.

        Args:
            aggregate_id: The ID of the aggregate.

        Returns:
            The current version (number of events - 1, or sequence of last event)
            or None if the aggregate stream doesn't exist.
        """
        raise NotImplementedError
