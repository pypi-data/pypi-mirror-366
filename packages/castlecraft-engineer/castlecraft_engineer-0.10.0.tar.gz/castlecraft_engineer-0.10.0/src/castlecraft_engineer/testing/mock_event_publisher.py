import asyncio
import logging
import time
from typing import List, Optional, Type, TypeVar, overload

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_publisher import ExternalEventPublisher

TEvent = TypeVar("TEvent", bound=Event)
logger = logging.getLogger(__name__)


class MockExternalEventPublisher(ExternalEventPublisher):
    def __init__(self) -> None:
        self.published_events: List[Event] = []
        self.was_closed: bool = False
        self._publish_exception: Optional[Exception] = None
        self._close_exception: Optional[Exception] = None
        self._publish_delay: float = 0
        self._logger = logging.getLogger(self.__class__.__name__)

    async def publish(self, events: List[Event]) -> None:
        if self._publish_exception:
            exc_to_raise = self._publish_exception
            raise exc_to_raise

        if self._publish_delay > 0:
            await asyncio.sleep(self._publish_delay)

        self.published_events.extend(events)
        self._logger.debug(
            f"Recorded {len(events)} events. Total now: {len(self.published_events)}"  # noqa: E501
        )

    async def close(self) -> None:
        if self._close_exception:
            exc_to_raise = self._close_exception
            raise exc_to_raise

        await asyncio.sleep(0)
        self.was_closed = True
        self._logger.debug("close() called.")

    def set_publish_delay(self, delay_seconds: float) -> None:
        self._publish_delay = max(0, delay_seconds)

    def simulate_publish_failure(self, exception: Exception) -> None:
        self._publish_exception = exception

    def simulate_close_failure(self, exception: Exception) -> None:
        self._close_exception = exception

    def reset(self) -> None:
        self.published_events = []
        self.was_closed = False
        self._publish_exception = None
        self._close_exception = None
        self._publish_delay = 0
        self._logger.debug("Reset.")

    @overload
    def get_published_events(self, event_type: Type[TEvent]) -> List[TEvent]: ...

    @overload
    def get_published_events(self, event_type: None = None) -> List[Event]: ...

    def get_published_events(
        self, event_type: Optional[Type[TEvent]] = None
    ) -> List[Event] | List[TEvent]:
        if event_type:
            return [
                event
                for event in self.published_events
                if isinstance(event, event_type)
            ]
        return self.published_events[:]

    def assert_published(
        self, event_type: Type[TEvent], count: Optional[int] = None
    ) -> List[TEvent]:
        matching_events = self.get_published_events(event_type)
        found_count = len(matching_events)

        if count is None:
            if found_count == 0:
                raise AssertionError(
                    f"Expected at least one event of type {event_type.__name__} to be published, but none were found. "  # noqa: E501
                    f"Total published: {len(self.published_events)}."
                )
        elif found_count != count:
            raise AssertionError(
                f"Expected exactly {count} event(s) of type {event_type.__name__} to be published, but found {found_count}. "  # noqa: E501
                f"Matching: {matching_events!r}. All published: {self.published_events!r}"  # noqa: E501
            )
        return matching_events

    def assert_published_event(self, expected_event: Event) -> None:
        if expected_event not in self.published_events:
            published_types = [type(e).__name__ for e in self.published_events]
            raise AssertionError(
                f"Expected event {expected_event!r} to be published, but it was not found.\n"  # noqa: E501
                f"Published events ({len(self.published_events)} total): {self.published_events!r}\n"  # noqa: E501
                f"Published types: {published_types}"
            )

    def assert_not_published(
        self,
        event_type: Optional[Type[Event]] = None,
    ) -> None:
        if event_type:
            matching_events = self.get_published_events(event_type)
            if matching_events:
                raise AssertionError(
                    f"Expected no events of type {event_type.__name__} to be published, but found {len(matching_events)}: {matching_events!r}"  # noqa: E501
                )
        else:
            if self.published_events:
                raise AssertionError(
                    f"Expected no events to be published at all, but found {len(self.published_events)}: {self.published_events!r}"  # noqa: E501
                )

    def assert_closed(self) -> None:
        if not self.was_closed:
            raise AssertionError(
                "Expected close() to be called on the publisher, but it wasn't."  # noqa: E501
            )

    def assert_not_closed(self) -> None:
        if self.was_closed:
            raise AssertionError(
                "Expected close() *not* to be called on the publisher, but it was."  # noqa: E501
            )


class MockExternalEventPublisherSync:
    def __init__(self) -> None:
        self.published_events: List[Event] = []
        self.was_closed: bool = False
        self._publish_exception: Optional[Exception] = None
        self._close_exception: Optional[Exception] = None
        self._publish_delay: float = 0
        self.last_publish_count: int = 0
        # Explicitly type the logger attribute
        self._logger = logging.getLogger(self.__class__.__name__)

    def publish(self, events: List[Event]) -> int:
        self.last_publish_count = 0
        if self._publish_exception:
            exc_to_raise = self._publish_exception
            raise exc_to_raise

        if self._publish_delay > 0:
            time.sleep(self._publish_delay)

        if not events:
            self._logger.debug("No events to publish.")
            return 0

        self.published_events.extend(events)
        self.last_publish_count = len(events)
        self._logger.debug(
            f"Recorded {len(events)} events. Total now: {len(self.published_events)}"  # noqa: E501
        )
        return self.last_publish_count

    def close(self) -> None:
        if self._close_exception:
            exc_to_raise = self._close_exception
            raise exc_to_raise

        if self._publish_delay > 0:
            time.sleep(self._publish_delay)

        self.was_closed = True
        self._logger.debug("close() called.")

    def set_publish_delay(self, delay_seconds: float) -> None:
        self._publish_delay = max(0, delay_seconds)

    def simulate_publish_failure(self, exception: Exception) -> None:
        self._publish_exception = exception

    def simulate_close_failure(self, exception: Exception) -> None:
        self._close_exception = exception

    def reset(self) -> None:
        self.published_events = []
        self.was_closed = False
        self._publish_exception = None
        self._close_exception = None
        self._publish_delay = 0
        self.last_publish_count = 0
        self._logger.debug("Reset.")

    @overload
    def get_published_events(self, event_type: Type[TEvent]) -> List[TEvent]: ...

    @overload
    def get_published_events(self, event_type: None = None) -> List[Event]: ...

    def get_published_events(
        self, event_type: Optional[Type[TEvent]] = None
    ) -> List[Event] | List[TEvent]:
        if event_type:
            # Ensure mypy knows this list comprehension results in List[TEvent]
            # by virtue of the isinstance check.
            return [
                event
                for event in self.published_events
                if isinstance(event, event_type)
            ]
        return self.published_events[:]

    def assert_published(
        self, event_type: Type[TEvent], count: Optional[int] = None
    ) -> List[TEvent]:
        matching_events = self.get_published_events(event_type)
        found_count = len(matching_events)

        if count is None:
            if found_count == 0:
                raise AssertionError(
                    f"Expected at least one event of type {event_type.__name__} to be published, but none were found. "  # noqa: E501
                    f"Total published: {len(self.published_events)}."
                )
        elif found_count != count:
            raise AssertionError(
                f"Expected exactly {count} event(s) of type {event_type.__name__} to be published, but found {found_count}. "  # noqa: E501
                f"Matching: {matching_events!r}. All published: {self.published_events!r}"  # noqa: E501
            )
        return matching_events

    def assert_published_event(self, expected_event: Event) -> None:
        if expected_event not in self.published_events:
            published_types = [type(e).__name__ for e in self.published_events]
            raise AssertionError(
                f"Expected event {expected_event!r} to be published, but it was not found.\n"  # noqa: E501
                f"Published events ({len(self.published_events)} total): {self.published_events!r}\n"  # noqa: E501
                f"Published types: {published_types}"
            )

    def assert_not_published(
        self,
        event_type: Optional[Type[Event]] = None,
    ) -> None:
        if event_type:
            matching_events = self.get_published_events(event_type)
            if matching_events:
                raise AssertionError(
                    f"Expected no events of type {event_type.__name__} to be published, but found {len(matching_events)}: {matching_events!r}"  # noqa: E501
                )
        else:
            if self.published_events:
                raise AssertionError(
                    f"Expected no events to be published at all, but found {len(self.published_events)}: {self.published_events!r}"  # noqa: E501
                )

    def assert_closed(self) -> None:
        if not self.was_closed:
            raise AssertionError(
                "Expected close() to be called on the publisher, but it wasn't."  # noqa: E501
            )

    def assert_not_closed(self) -> None:
        if self.was_closed:
            raise AssertionError(
                "Expected close() *not* to be called on the publisher, but it was."  # noqa: E501
            )
