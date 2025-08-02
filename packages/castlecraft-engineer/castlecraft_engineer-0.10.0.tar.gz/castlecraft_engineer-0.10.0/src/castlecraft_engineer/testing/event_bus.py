import asyncio
import types
from typing import Any, Dict, Type, TypeVar
from unittest.mock import AsyncMock

import punq

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_bus import EventBus
from castlecraft_engineer.abstractions.event_handler import EventHandler

TEvent = TypeVar("TEvent", bound=Event)


class EventBusTestHelper:
    def __init__(self, bus: EventBus, container: punq.Container):
        if not isinstance(bus, EventBus):
            raise TypeError(
                "event_bus must be an instance of EventBus",
            )
        if not isinstance(container, punq.Container):
            raise TypeError("container must be an instance of punq.Container")

        self.event_bus = bus
        self._container = container
        self._mock_handler_instances: Dict[
            Type[EventHandler],
            EventHandler,
        ] = {}

    def register_mock_handler(
        self,
        event_type: Type[TEvent],
    ) -> Any:
        """
        Creates a unique mock EventHandler
        class dynamically with the correct
        handle signature, registers it,
        and prepares a mock instance for DI.
        """
        async_mock_handle = AsyncMock(
            spec=True, name=f"MockHandle_{event_type.__name__}"
        )

        mock_handler_class_name = (
            f"MockEventHandler_{event_type.__name__}_{id(async_mock_handle)}"
        )

        def exec_body(ns):
            def __init__(self, mock_func: AsyncMock):
                self._mock_handle = mock_func

            ns["__init__"] = __init__

            async def handle(self, event: TEvent) -> None:
                await self._mock_handle(event)

            ns["handle"] = handle

            ns["mock"] = property(lambda self: self._mock_handle)

            if "handle" in ns:
                ns["handle"].__annotations__ = {
                    "event": event_type,
                    "return": None,
                }

            return ns

        MockHandlerForEvent = types.new_class(
            name=mock_handler_class_name,
            bases=(EventHandler[event_type],),  # type: ignore[valid-type]
            kwds={},
            exec_body=exec_body,
        )

        self.event_bus.register(MockHandlerForEvent)

        mock_handler_instance = MockHandlerForEvent(async_mock_handle)

        self._mock_handler_instances[MockHandlerForEvent] = (
            mock_handler_instance  # noqa: E501
        )

        self._container.register(
            MockHandlerForEvent,
            instance=mock_handler_instance,
        )

        return mock_handler_instance

    async def publish_and_wait(self, event: Event, delay_after: float = 0.01):
        if not isinstance(event, Event):
            raise TypeError("event must be an instance of Event")

        await self.event_bus.publish(event)
        await asyncio.sleep(delay_after)

    def assert_handler_called_with(
        self,
        mock_handler_instance: Any,
        event: Event,
    ):
        mock_handler_instance.mock.assert_awaited_once_with(event)

    def assert_handler_called(
        self,
        mock_handler_instance: Any,
        times: int = 1,
    ):
        assert mock_handler_instance.mock.await_count == times, (
            f"Expected handler mock {mock_handler_instance.mock.name} to be awaited {times} times, "  # noqa: E501
            f"but was awaited {mock_handler_instance.mock.await_count} times."
        )

    def assert_handler_not_called(self, mock_handler_instance: Any):
        mock_handler_instance.mock.assert_not_awaited()

    def reset_mocks(self):
        for handler_instance in self._mock_handler_instances.values():
            handler_instance.mock.reset_mock()

    def cleanup_registrations(self):
        for handler_class in list(
            self._mock_handler_instances.keys(),
        ):
            event_type = self.event_bus._get_event_type(handler_class)
            if event_type in self.event_bus._handler_map:
                try:
                    self.event_bus._handler_map[event_type,].remove(
                        handler_class,
                    )
                    if not self.event_bus._handler_map[event_type]:
                        del self.event_bus._handler_map[event_type]
                except ValueError:
                    pass
                except TypeError:
                    pass
            del self._mock_handler_instances[handler_class]
