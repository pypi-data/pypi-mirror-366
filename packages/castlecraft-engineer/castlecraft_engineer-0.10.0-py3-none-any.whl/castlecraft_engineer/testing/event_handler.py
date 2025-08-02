import abc
from typing import Generic, Type, TypeVar

import pytest

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_handler import EventHandler

TEvent = TypeVar("TEvent", bound=Event)
TEventHandler = TypeVar("TEventHandler", bound=EventHandler)


class BaseEventHandlerTest(Generic[TEvent, TEventHandler], abc.ABC):
    """
    Base class for testing EventHandler implementations.

    Provides common fixtures and helper methods for event handler tests.
    Subclasses must define the `handler_class` attribute.
    """

    @property
    @abc.abstractmethod
    def handler_class(self) -> Type[TEventHandler]:
        """The specific EventHandler class being tested."""
        raise NotImplementedError

    @pytest.fixture
    def handler_instance(self) -> TEventHandler:
        """
        Provides an instance of the handler_class.
        Override this fixture if your handler requires specific dependencies
        during initialization.
        """
        try:
            # Assumes the handler has a parameterless __init__ or
            # dependencies are handled internally/statically.
            return self.handler_class()
        except TypeError as e:
            pytest.fail(
                f"Failed to instantiate {self.handler_class.__name__}. "
                "Does it have a parameterless __init__? "
                "If not, override the 'handler_instance' "
                f"fixture in your test class. Original error: {e}"
            )

    async def execute_handle(
        self,
        handler: TEventHandler,
        event: TEvent,
    ) -> None:
        """
        Helper method to execute the handler's handle method asynchronously.

        Args:
            handler: The event handler instance.
            event: The event instance to handle.
        """
        await handler.handle(event=event)
