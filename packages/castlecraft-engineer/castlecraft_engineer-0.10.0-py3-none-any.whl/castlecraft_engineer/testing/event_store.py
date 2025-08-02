import asyncio
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Sequence, cast

import pytest

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_store import (
    EventStore,
    EventStoreConflictError,
    TAggregateId,
)


class InMemoryEventStore(EventStore[TAggregateId]):
    """
    An in-memory implementation of the EventStore for testing purposes.

    This store is not thread-safe for concurrent writes from multiple async tasks
    if those tasks might interleave operations on the same aggregate ID without
    proper external synchronization. However, for typical single-threaded test
    execution or sequential operations within a test, it's perfectly suitable.
    """

    def __init__(self) -> None:
        self._streams: Dict[TAggregateId, List[Event]] = defaultdict(list)
        self._versions: Dict[TAggregateId, int] = {}
        # For async operations, a lock per aggregate_id might be needed
        # if true concurrent access to the same stream is simulated in tests.
        # For most unit test scenarios, this is not strictly necessary.
        self._locks: Dict[TAggregateId, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def _get_stream_lock(self, aggregate_id: TAggregateId) -> asyncio.Lock:
        return self._locks[aggregate_id]

    async def append_events(
        self,
        aggregate_id: TAggregateId,
        expected_version: int,
        events: Sequence[Event],
    ) -> None:
        if not events:
            return

        async with await self._get_stream_lock(aggregate_id):
            current_version = self._versions.get(aggregate_id, -1)

            if current_version != expected_version:
                raise EventStoreConflictError(
                    aggregate_id, expected_version, current_version
                )

            stream = self._streams[aggregate_id]
            stream.extend(events)
            # The new version is the index of the last event in the stream
            self._versions[aggregate_id] = current_version + len(events)

    async def load_events(
        self,
        aggregate_id: TAggregateId,
        from_version: Optional[int] = None,
    ) -> List[Event]:
        # Lock for read consistency if needed
        async with await self._get_stream_lock(aggregate_id):
            stream = self._streams.get(aggregate_id, [])
            if from_version is None:
                return list(stream)  # Return a copy

            # Versions are 0-indexed (sequence number of the event)
            # from_version means "after this version"
            # So, if from_version is 0, we want events from index 1 onwards.
            # The events themselves are indexed 0, 1, 2...
            # If from_version is X, we need events whose sequence is > X.
            # Event at index `i` has sequence `i`.
            # So we need events from index `from_version + 1`.
            start_index = from_version + 1
            if start_index < 0:  # Should not happen with valid from_version
                start_index = 0
            # Return a copy
            return list(stream[start_index:])

    async def get_current_version(self, aggregate_id: TAggregateId) -> Optional[int]:
        # Lock for read consistency
        async with await self._get_stream_lock(aggregate_id):
            # Version is the sequence number of the last event.
            # If no events, version is -1, but the method should return None.
            if aggregate_id not in self._versions:
                return None
            return self._versions[aggregate_id]

    async def clear(self) -> None:
        """Clears all streams and versions from the store."""
        # Need to acquire all locks or a global lock if we had one.
        # For simplicity in a test store, direct clear is often acceptable,
        # assuming tests run sequentially or manage their own isolation.
        # If locks are per-stream, clearing _locks needs care if streams are active.
        # A more robust clear might involve iterating and acquiring each lock.
        # However, for typical test teardown, this should be fine.
        self._streams.clear()
        self._versions.clear()
        # Re-create defaultdict for locks
        self._locks.clear()

    async def get_stream(self, aggregate_id: TAggregateId) -> List[Event]:
        """Returns a copy of the event stream for a given aggregate ID."""
        async with await self._get_stream_lock(aggregate_id):
            return list(self._streams.get(aggregate_id, []))


@dataclass(frozen=True, kw_only=True)
class MyTestEvent(Event):
    payload: str
    # event_id and occurred_on are inherited and will get default values


def create_test_events(
    count: int, payload_prefix: str = "event_data_"
) -> List[MyTestEvent]:
    """Helper function to create a list of MyTestEvent instances."""
    return [MyTestEvent(payload=f"{payload_prefix}{i+1}") for i in range(count)]


class BaseEventStoreTest(Generic[TAggregateId]):
    """
    A base class for testing EventStore implementations.

    Subclasses must provide two asynchronous fixtures:
    1. `event_store(self) -> EventStore[TAggregateId]`:
       Yields a clean instance of the EventStore implementation.
    2. `generate_aggregate_id(self) -> TAggregateId`:
       Yields a unique aggregate ID of the correct type for each call.
    """

    # Version expected when appending to a new stream
    NEW_STREAM_EXPECTED_VERSION: int = -1

    @pytest.fixture
    @abstractmethod
    async def event_store(self) -> EventStore[TAggregateId]:
        """
        Pytest fixture to provide a clean instance of the EventStore.
        This MUST be implemented by concrete test subclasses.
        The store should be reset/cleared for each test.
        Implementations should `yield` the store.
        """
        raise NotImplementedError(
            "Subclasses must implement the 'event_store' fixture."
        )

    @pytest.fixture
    @abstractmethod
    def generate_aggregate_id(self) -> TAggregateId:
        """
        Pytest fixture to generate a unique aggregate ID of the type TAggregateId.
        This MUST be implemented by concrete test subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement the 'generate_aggregate_id' fixture."
        )

    async def test_append_to_new_stream(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        events_to_append = create_test_events(2)

        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, events_to_append
        )

        retrieved_events = await event_store.load_events(stream_id)
        assert retrieved_events == events_to_append

        # Version is 0-indexed. After 2 events (event 0, event 1), version is 1.
        current_version = await event_store.get_current_version(stream_id)
        assert current_version == len(events_to_append) - 1

    async def test_append_to_new_stream_no_events(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        await event_store.append_events(stream_id, self.NEW_STREAM_EXPECTED_VERSION, [])

        retrieved_events = await event_store.load_events(stream_id)
        assert retrieved_events == []
        current_version = await event_store.get_current_version(stream_id)
        # No events, so no version / stream doesn't exist in terms of versioning
        assert current_version is None

    async def test_append_to_existing_stream(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        initial_events = create_test_events(2, "initial_")
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, initial_events
        )

        expected_version_for_next_append = len(initial_events) - 1
        assert (
            await event_store.get_current_version(stream_id)
            == expected_version_for_next_append
        )

        additional_events = create_test_events(3, "additional_")
        await event_store.append_events(
            stream_id, expected_version_for_next_append, additional_events
        )

        retrieved_events = await event_store.load_events(stream_id)
        all_expected_events = initial_events + additional_events
        assert retrieved_events == all_expected_events
        assert (
            await event_store.get_current_version(stream_id)
            == len(all_expected_events) - 1
        )

    async def test_append_to_existing_stream_no_events(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        initial_events = create_test_events(1, "initial_")
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, initial_events
        )

        expected_version_for_next_append = len(initial_events) - 1

        await event_store.append_events(stream_id, expected_version_for_next_append, [])

        retrieved_events = await event_store.load_events(stream_id)
        assert retrieved_events == initial_events
        assert (
            await event_store.get_current_version(stream_id)
            == expected_version_for_next_append
        )

    async def test_append_conflict_new_stream_wrong_expected_version(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        events_to_append = create_test_events(1)

        wrong_expected_version = 0  # Should be NEW_STREAM_EXPECTED_VERSION (-1)
        with pytest.raises(EventStoreConflictError) as exc_info:
            await event_store.append_events(
                stream_id, wrong_expected_version, events_to_append
            )

        assert exc_info.value.aggregate_id == stream_id
        assert exc_info.value.expected_version == wrong_expected_version
        # Actual version of a non-existent stream is effectively NEW_STREAM_EXPECTED_VERSION
        assert exc_info.value.actual_version == self.NEW_STREAM_EXPECTED_VERSION

        assert await event_store.load_events(stream_id) == []
        assert await event_store.get_current_version(stream_id) is None

    async def test_append_conflict_existing_stream_wrong_expected_version(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        initial_events = create_test_events(2, "initial_")
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, initial_events
        )

        actual_current_version = len(initial_events) - 1
        # Intentionally wrong
        wrong_expected_version = actual_current_version - 1

        additional_events = create_test_events(1, "additional_")
        with pytest.raises(EventStoreConflictError) as exc_info:
            await event_store.append_events(
                stream_id, wrong_expected_version, additional_events
            )

        assert exc_info.value.aggregate_id == stream_id
        assert exc_info.value.expected_version == wrong_expected_version
        assert exc_info.value.actual_version == actual_current_version

        # Ensure stream is unchanged
        assert await event_store.load_events(stream_id) == initial_events
        assert (
            await event_store.get_current_version(stream_id) == actual_current_version
        )

    async def test_load_events_non_existent_stream(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        retrieved_events = await event_store.load_events(stream_id)
        assert retrieved_events == []

    async def test_load_all_events_with_from_version_none(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        appended_events = create_test_events(3)
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, appended_events
        )

        retrieved_events = await event_store.load_events(stream_id, from_version=None)
        assert retrieved_events == appended_events

    async def test_load_events_from_specific_version(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        # Events E0, E1, E2, E3, E4 (versions 0, 1, 2, 3, 4 respectively)
        all_events = create_test_events(5)
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, all_events
        )

        # from_version = -1 (load events with sequence > -1, i.e., all events)
        assert await event_store.load_events(stream_id, from_version=-1) == all_events

        # from_version = 0 (load events with sequence > 0, i.e., E1, E2, E3, E4)
        assert (
            await event_store.load_events(stream_id, from_version=0) == all_events[1:]
        )

        # from_version = 2 (load events with sequence > 2, i.e., E3, E4)
        assert (
            await event_store.load_events(stream_id, from_version=2) == all_events[3:]
        )

        # from_version = 4 (load events with sequence > 4, i.e., empty list)
        assert await event_store.load_events(stream_id, from_version=4) == []

        # from_version = 5 (beyond last event version, still empty list)
        assert await event_store.load_events(stream_id, from_version=5) == []

        # from_version = -10 (should behave like -1)
        assert await event_store.load_events(stream_id, from_version=-10) == all_events

    async def test_load_events_returns_copy(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        appended_events = create_test_events(2)
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, appended_events
        )

        retrieved_1 = await event_store.load_events(stream_id)
        assert retrieved_1 == appended_events

        # Try to modify the retrieved list (if it's mutable)
        try:
            # This cast is to attempt modification; MyTestEvent is frozen, but List[MyTestEvent] is not.
            # The point is to check if the store returns a *copy* of its internal list.
            mutated_retrieved_1 = cast(List[MyTestEvent], retrieved_1)
            mutated_retrieved_1.append(create_test_events(1, "rogue_")[0])
        except AttributeError:  # If list is immutable tuple, this is fine too
            pass

        retrieved_2 = await event_store.load_events(stream_id)
        assert retrieved_2 == appended_events  # Should be original, unmodified
        assert len(retrieved_2) == 2

    async def test_get_current_version_non_existent_stream(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        assert await event_store.get_current_version(stream_id) is None

    async def test_get_current_version_after_first_append(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        event_e0 = create_test_events(1)[0]
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, [event_e0]
        )
        # E0 is version 0
        assert await event_store.get_current_version(stream_id) == 0

    async def test_get_current_version_after_multiple_appends(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id

        # Append E0
        events_batch1 = create_test_events(1, "batch1_")
        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, events_batch1
        )
        # Should be 0
        version_after_batch1 = len(events_batch1) - 1
        assert await event_store.get_current_version(stream_id) == version_after_batch1

        # Append E1, E2
        events_batch2 = create_test_events(2, "batch2_")
        await event_store.append_events(stream_id, version_after_batch1, events_batch2)
        # New version = old_version + len(new_events)
        # Here, old_version was 0. len(new_events) is 2. So new version is 0 + 2 = 2.
        # (E0 is ver 0, E1 is ver 1, E2 is ver 2)
        version_after_batch2 = version_after_batch1 + len(events_batch2)
        assert await event_store.get_current_version(stream_id) == version_after_batch2
        assert version_after_batch2 == 2  # (0-indexed version of last event)

    async def test_stream_isolation(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id_a = generate_aggregate_id
        stream_id_b = generate_aggregate_id

        events_a1 = create_test_events(2, "streamA_batch1_")
        await event_store.append_events(
            stream_id_a, self.NEW_STREAM_EXPECTED_VERSION, events_a1
        )
        version_a1 = len(events_a1) - 1

        events_b1 = create_test_events(3, "streamB_batch1_")
        await event_store.append_events(
            stream_id_b, self.NEW_STREAM_EXPECTED_VERSION, events_b1
        )
        version_b1 = len(events_b1) - 1

        # Check stream A
        assert await event_store.load_events(stream_id_a) == events_a1
        assert await event_store.get_current_version(stream_id_a) == version_a1

        # Check stream B
        assert await event_store.load_events(stream_id_b) == events_b1
        assert await event_store.get_current_version(stream_id_b) == version_b1

        # Append more to stream A
        events_a2 = create_test_events(1, "streamA_batch2_")
        await event_store.append_events(stream_id_a, version_a1, events_a2)
        version_a2 = version_a1 + len(events_a2)

        # Verify stream A updated, stream B unaffected
        assert await event_store.load_events(stream_id_a) == events_a1 + events_a2
        assert await event_store.get_current_version(stream_id_a) == version_a2

        # Still original
        assert await event_store.load_events(stream_id_b) == events_b1
        # Still original
        assert await event_store.get_current_version(stream_id_b) == version_b1

    async def test_append_many_events_in_one_batch(
        self, event_store: EventStore[TAggregateId], generate_aggregate_id: TAggregateId
    ):
        stream_id = generate_aggregate_id
        num_events = 50
        many_events = create_test_events(num_events)

        await event_store.append_events(
            stream_id, self.NEW_STREAM_EXPECTED_VERSION, many_events
        )

        retrieved_events = await event_store.load_events(stream_id)
        assert retrieved_events == many_events
        assert len(retrieved_events) == num_events
        assert await event_store.get_current_version(stream_id) == num_events - 1
