import abc
from typing import Generic, TypeVar

from castlecraft_engineer.abstractions.event import Event

TEvent = TypeVar("TEvent", bound=Event)


class EventHandler(Generic[TEvent], abc.ABC):
    """
    Abstract base class for event handlers.
    Each handler is responsible for reacting to
    a specific type of domain event.
    """

    @abc.abstractmethod
    async def handle(self, event: TEvent) -> None:
        """
        Handles the logic to execute when the specific event occurs.
        Marked as async to easily accommodate I/O operations
        (like sending emails, updating databases, calling APIs).

        Args:
            event: The event instance to be processed.

        Raises:
            NotImplementedError: This method must be implemented by
                                concrete subclasses.
        """
        raise NotImplementedError
