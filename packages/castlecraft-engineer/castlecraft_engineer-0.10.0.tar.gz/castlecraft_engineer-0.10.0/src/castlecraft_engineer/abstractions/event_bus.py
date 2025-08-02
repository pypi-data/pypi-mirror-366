import asyncio
import inspect
import logging
import typing
from collections import defaultdict
from typing import Any, Dict, List, Type, TypedDict, TypeVar

import punq
from punq import MissingDependencyError

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_handler import EventHandler

TEvent = TypeVar("TEvent", bound=Event)


class EventHandlerRegistrationError(Exception):
    pass


class _TaskInfo(TypedDict):
    task: asyncio.Task[None]
    handler_cls_name: str


class EventBus:
    def __init__(self, container: punq.Container) -> None:
        self._container = container
        self._handler_map: Dict[Type[Event], List[Type[EventHandler[Any]]]] = (
            defaultdict(list)
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    def _get_event_type(
        self,
        handler_cls: Type[EventHandler[TEvent]],
    ) -> Type[TEvent]:
        try:
            for base in getattr(handler_cls, "__orig_bases__", []):
                origin = typing.get_origin(base)
                if origin is EventHandler:
                    args = typing.get_args(base)
                    if (
                        args
                        and isinstance(args[0], type)
                        and issubclass(args[0], Event)
                    ):
                        return typing.cast(Type[TEvent], args[0])
        except Exception:
            pass

        try:
            handle_method = getattr(handler_cls, "handle", None)
            if handle_method:
                unwrapped_handle = inspect.unwrap(handle_method)
                sig = inspect.signature(unwrapped_handle)
                if "event" in sig.parameters:
                    event_param = sig.parameters["event"]
                    event_type_hint = event_param.annotation
                    if (
                        isinstance(event_type_hint, type)
                        and issubclass(event_type_hint, Event)
                        and event_type_hint is not Event
                    ):
                        return typing.cast(Type[TEvent], event_type_hint)

        except (ValueError, TypeError):
            pass

        raise TypeError(
            "Could not determine Event type for "
            f"handler {handler_cls.__name__}. "
            "Ensure it inherits directly like: "
            "MyEventHandler(EventHandler[MySpecificEvent]) "
            "or has a handle method with a specific Event type hint."
        )

    def register(
        self, handler_cls: Type[EventHandler[TEvent]]
    ) -> Type[EventHandler[TEvent]]:
        is_class = inspect.isclass(handler_cls)
        if not is_class:
            raise EventHandlerRegistrationError(
                f"{handler_cls!r} is not a valid EventHandler.",
            )

        if not issubclass(handler_cls, EventHandler):
            raise EventHandlerRegistrationError(
                f"{handler_cls.__name__} is not a valid EventHandler.",
            )

        try:
            event_type = self._get_event_type(handler_cls)
        except TypeError as e:
            raise TypeError(
                f"Registration failed for {handler_cls.__name__}: {e}",
            ) from e

        self._handler_map[event_type].append(handler_cls)

        return handler_cls

    async def publish(self, event: Event) -> None:
        event_type = type(event)
        handler_classes_for_event = self._handler_map.get(event_type, [])
        if not handler_classes_for_event:
            return

        tasks_with_context: List[_TaskInfo] = []
        for handler_cls in handler_classes_for_event:
            handler_instance = None
            try:
                handler_instance = self._container.resolve(handler_cls)
            except MissingDependencyError as e:
                self._logger.error(
                    f"Failed to resolve handler {handler_cls.__name__} "
                    f"for event {event_type.__name__}: {e}. Skipping."
                )
                continue  # Skip this handler, proceed to the next
            except Exception as e:
                self._logger.error(
                    f"Unexpected error resolving handler {handler_cls.__name__} "
                    f"for event {event_type.__name__}: {e}. Skipping."
                )
                continue  # Skip this handler

            if not isinstance(handler_instance, EventHandler):
                self._logger.warning(
                    f"Resolved object for {handler_cls.__name__} (for event {event_type.__name__}) "
                    f"is not an EventHandler instance (got {type(handler_instance).__name__}). Skipping."
                )
                continue

            task: asyncio.Task[None] = asyncio.create_task(
                self._execute_handler(handler_instance, event),
                name=f"EventHandler-{handler_cls.__name__}-{event.event_id}",
            )
            tasks_with_context.append(
                {"task": task, "handler_cls_name": handler_cls.__name__}
            )

        tasks_to_gather = [item["task"] for item in tasks_with_context]
        results = await asyncio.gather(*tasks_to_gather, return_exceptions=True)

        for i, result in enumerate(results):  # This loop won't run if results is empty.
            if isinstance(result, Exception):
                failed_task_context = tasks_with_context[i]
                handler_name = failed_task_context["handler_cls_name"]
                self._logger.error(
                    f"Error in event handler {handler_name} for event "
                    f"{event_type.__name__} (ID: {event.event_id}): {result!r}"
                )
                self._logger.debug(
                    f"Exception details for {handler_name}:",
                    exc_info=result,
                )

    async def _execute_handler(
        self,
        handler: EventHandler,
        event: Event,
    ) -> None:
        try:
            await handler.handle(event)
        except Exception:
            raise

    async def publish_batch(self, events: List[Event]) -> None:
        for event in events:
            await self.publish(event)
