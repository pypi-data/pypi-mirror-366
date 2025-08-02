import abc
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Type, Union

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.projection import ProjectionId
from castlecraft_engineer.abstractions.projection_store import ProjectionStore

logger = logging.getLogger(__name__)


class Projector(abc.ABC):
    """
    Abstract base class for projectors.
    Projectors are responsible for consuming events and updating read models
    or performing other side effects based on those events.
    """

    def __init__(self, projection_store: ProjectionStore):
        self._event_handlers: Dict[
            Type[Event],
            List[
                Union[
                    Callable[[Event], None],
                    Callable[[Event], Coroutine[Any, Any, None]],
                ]
            ],
        ] = {}
        # Store to manage projection's last processed event
        self._projection_store = projection_store
        self._register_event_handlers()

    @property
    @abc.abstractmethod
    def projection_id(self) -> ProjectionId:
        """
        A unique identifier for this projector or the projection it manages.
        Used to store and retrieve its processing state.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _register_event_handlers(self) -> None:
        """
        Subclasses must implement this method to register handlers for specific event types.
        Example: self._register_handler(MyEvent, self._handle_my_event)
        """
        raise NotImplementedError

    def _register_handler(
        self,
        event_type: Type[Event],
        handler: Union[
            Callable[[Event], None], Callable[[Event], Coroutine[Any, Any, None]]
        ],
    ) -> None:
        """Registers a method to handle a specific event type."""
        if not issubclass(event_type, Event):
            raise TypeError(f"event_type must be a subclass of Event, got {event_type}")
        if not callable(handler):
            raise TypeError(f"handler must be callable, got {handler}")

        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def handle_event(self, event: Event) -> None:
        """
        Handles an incoming event by dispatching it to registered handlers.
        This method should be called by the event stream consumer.
        It also updates the projection state after successful handling.
        """
        event_type = type(event)
        handlers = self._event_handlers.get(event_type)

        if not handlers:
            # Optionally log or ignore events the projector is not interested in
            logger.debug(
                f"Projector {self.projection_id} has no handler for event type {event_type.__name__}"
            )
            return

        try:
            for handler in handlers:
                # Depending on whether handlers are async or sync, you might need to adjust.
                # For simplicity, assuming sync handlers here. If async, use `await handler(event)`.
                # If handlers can be async, this method should be `async def handle_event`.
                # For now, let's assume handlers are synchronous for simplicity in the ABC.
                # Concrete projectors can decide if their handlers are async.
                # If a handler is async, the `handle_event` method itself should be async.
                # Let's make it async to be more flexible.
                await self._invoke_handler(handler, event)

            # After all handlers for this event type have successfully processed the event,
            # update the projection state.
            # This assumes the event has an `event_id` and `occurred_on` attribute.
            # You might need to adapt this based on your Event base class.
            projection_state = await self._projection_store.get_projection_state(
                self.projection_id
            )
            if projection_state is None:
                # This import is fine here as it's for a specific type
                from castlecraft_engineer.abstractions.projection import ProjectionState

                projection_state = ProjectionState(projection_id=self.projection_id)

            projection_state.update_progress(
                event_id=getattr(
                    event, "event_id", None
                ),  # Adapt if your Event has a different ID field
                event_timestamp=getattr(
                    event, "occurred_on", None
                ),  # Adapt for timestamp
            )
            await self._projection_store.save_projection_state(projection_state)

        except Exception as e:
            logger.error(
                f"Error handling event {event_type.__name__} in projector {self.projection_id}: {e}",
                exc_info=True,
            )
            # Decide on error handling strategy: re-raise, log and skip, move to dead-letter queue, etc.
            raise  # Re-raise by default to let the caller handle it

    async def _invoke_handler(
        self,
        handler: Union[
            Callable[[Event], None], Callable[[Event], Coroutine[Any, Any, None]]
        ],
        event: Event,
    ) -> None:
        """Helper to invoke a handler, allowing for async handlers in subclasses if needed."""
        # This basic implementation assumes synchronous handlers.
        # If your handlers can be async, this method (and `handle_event`) should be more sophisticated
        # or the projector itself should be designed for async handlers.
        # For now, let's assume the handler itself can be async.
        import inspect

        if inspect.iscoroutinefunction(handler):
            await handler(event)
        else:
            handler(event)  # type: ignore

    async def get_last_processed_event_details(
        self,
    ) -> tuple[Optional[Any], Optional[Any]]:
        """
        Retrieves the ID and timestamp of the last event processed by this projector.
        Useful for resuming event stream consumption.
        """
        state = await self._projection_store.get_projection_state(self.projection_id)
        if state:
            return state.last_processed_event_id, state.last_processed_event_timestamp
        return None, None
