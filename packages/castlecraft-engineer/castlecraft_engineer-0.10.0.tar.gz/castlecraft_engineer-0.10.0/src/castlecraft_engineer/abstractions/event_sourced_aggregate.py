import abc
import logging
from typing import Any, Callable, Dict, Generic, List, Type, TypeVar

from castlecraft_engineer.abstractions.aggregate import Aggregate, TAggregateId
from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.snapshot import Snapshot

ESA = TypeVar("ESA", bound="EventSourcedAggregate")
logger = logging.getLogger(__name__)


class EventSourcedAggregate(Aggregate[TAggregateId], Generic[TAggregateId], abc.ABC):
    """
    Base class for Aggregates that are event-sourced.
    It extends the base Aggregate with event application logic.
    """

    def __init__(self, id: TAggregateId, version: int = -1) -> None:
        super().__init__(id, version)
        # _event_appliers maps event types to methods that apply them
        self._event_appliers: Dict[Type[Event], Callable[[Event], None]] = {}
        self._register_event_appliers()

    @abc.abstractmethod
    def _register_event_appliers(self) -> None:
        """
        Subclasses must implement this method to register their event appliers.
        Example: self._register_applier(MyEvent, self._apply_my_event)
        """

    def _register_applier(
        self, event_type: Type[Event], applier: Callable[[Event], None]
    ) -> None:
        """Registers a method to apply a specific event type."""
        if not issubclass(event_type, Event):
            raise TypeError(f"event_type must be a subclass of Event, got {event_type}")
        if not callable(applier):
            raise TypeError(f"applier must be callable, got {applier}")
        self._event_appliers[event_type] = applier

    def _handle_unapplied_event(self, event: Event) -> None:
        """
        Hook method called when no applier is found for an event.
        Default behavior is to log a warning. Subclasses can override
        to raise an error or implement other custom logic.
        """
        logger.warning(
            f"No event applier registered for event type {type(event).__name__} "
            f"in {self.__class__.__name__}. Event was not applied to state."
        )

    def _apply_event(self, event: Event) -> None:
        """
        Applies an event to the aggregate, changing its state.
        This method finds the registered applier for the event type and calls it.
        It also increments the aggregate's version.
        """
        applier = self._event_appliers.get(type(event))
        if not applier:
            self._handle_unapplied_event(event)
        else:
            applier(event)

        # Version is incremented for each applied event
        self._increment_version()

    def _record_and_apply_event(self, event: Event) -> None:
        """
        Records an event and then applies it to the aggregate.
        This is the primary way domain methods should effect state changes.
        """
        # From base Aggregate: adds to _uncommitted_events
        self._record_event(event)

        # Applies to current state and increments version
        self._apply_event(event)

    @classmethod
    def load_from_history(
        cls: Type[ESA], aggregate_id: TAggregateId, history: List[Event]
    ) -> ESA:
        """
        Reconstructs an aggregate instance from its event history.
        The initial version is -1, and each applied event increments it.
        """
        # Initial version is -1, as per Aggregate base class for a new/empty instance
        instance = cls(id=aggregate_id, version=-1)
        for event in history:
            instance._apply_event(event)
        # After applying all historical events, clear uncommitted events
        # as these are already persisted.
        instance._uncommitted_events.clear()
        return instance

    def create_snapshot(self) -> Snapshot[TAggregateId]:
        """
        Creates a snapshot of the aggregate's current state and version.
        Subclasses might need to override this if their state isn't easily
        serializable from public attributes or if they need custom serialization.
        """
        state_to_snapshot = self._get_snapshot_state()
        return Snapshot(
            aggregate_id=self.id,
            aggregate_state=state_to_snapshot,
            version=self.version,
        )

    @abc.abstractmethod
    def _get_snapshot_state(self) -> Any:
        """
        Returns the serializable state of the aggregate for snapshotting.
        Subclasses must implement this to define what data constitutes their snapshot.
        """

    @abc.abstractmethod
    def _apply_snapshot_state(self, state: Any) -> None:
        """
        Applies a deserialized state from a snapshot to the aggregate.
        Subclasses must implement this to restore their state from snapshot data.
        """
