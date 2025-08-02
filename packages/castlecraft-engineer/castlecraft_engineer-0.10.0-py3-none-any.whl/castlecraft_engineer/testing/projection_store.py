import asyncio
import dataclasses  # Import dataclasses
import datetime
import uuid
from abc import abstractmethod  # Ensure AsyncGenerator is imported
from typing import AsyncGenerator, Dict, Generic, Optional, TypeVar

import pytest
import pytest_asyncio

from castlecraft_engineer.abstractions.projection import ProjectionId, ProjectionState
from castlecraft_engineer.abstractions.projection_store import ProjectionStore

# To avoid conflict with TEventId in ABC
TEventId_InMemory = TypeVar("TEventId_InMemory")


class InMemoryProjectionStore(ProjectionStore[TEventId_InMemory]):
    """
    An in-memory implementation of the ProjectionStore for testing purposes.
    """

    def __init__(self) -> None:
        self._projection_states: Dict[ProjectionId, ProjectionState] = {}
        # Global lock for simplicity
        self._lock: asyncio.Lock = asyncio.Lock()

    async def get_projection_state(
        self, projection_id: ProjectionId
    ) -> Optional[ProjectionState]:
        async with self._lock:
            state = self._projection_states.get(projection_id)
            if state:
                return dataclasses.replace(state)  # Return a copy
            return None

    async def save_projection_state(self, projection_state: ProjectionState) -> None:
        async with self._lock:
            self._projection_states[projection_state.projection_id] = projection_state

    async def clear_projection_state(self, projection_id: ProjectionId) -> None:
        async with self._lock:
            if projection_id in self._projection_states:
                del self._projection_states[projection_id]

    async def clear_all_for_testing(self) -> None:
        """Clears all projection states from the store for testing."""
        async with self._lock:
            self._projection_states.clear()


class BaseProjectionStoreTest(Generic[TEventId_InMemory]):
    @pytest_asyncio.fixture
    @abstractmethod
    async def projection_store(
        self,
    ) -> AsyncGenerator[ProjectionStore[TEventId_InMemory], None]:
        """Yields a clean instance of the ProjectionStore."""
        raise NotImplementedError

    @pytest.fixture
    def sample_projection_id(self) -> ProjectionId:
        return f"test_projection_{uuid.uuid4()}"

    @pytest.mark.asyncio
    async def test_save_and_get_projection_state(
        self,
        projection_store: ProjectionStore[TEventId_InMemory],
        sample_projection_id: ProjectionId,
    ):
        event_id = uuid.uuid4()
        event_ts = datetime.datetime.now(datetime.timezone.utc)
        state = ProjectionState(
            projection_id=sample_projection_id,
            last_processed_event_id=event_id,
            last_processed_event_timestamp=event_ts,
        )
        await projection_store.save_projection_state(state)

        retrieved_state = await projection_store.get_projection_state(
            sample_projection_id
        )
        assert retrieved_state is not None
        assert retrieved_state.projection_id == sample_projection_id
        assert retrieved_state.last_processed_event_id == event_id
        assert retrieved_state.last_processed_event_timestamp == event_ts

    @pytest.mark.asyncio
    async def test_get_non_existent_projection_state(
        self,
        projection_store: ProjectionStore[TEventId_InMemory],
        sample_projection_id: ProjectionId,
    ):
        retrieved_state = await projection_store.get_projection_state(
            sample_projection_id
        )
        assert retrieved_state is None

    @pytest.mark.asyncio
    async def test_update_projection_state(
        self,
        projection_store: ProjectionStore[TEventId_InMemory],
        sample_projection_id: ProjectionId,
    ):
        initial_event_id = uuid.uuid4()
        initial_state = ProjectionState(
            projection_id=sample_projection_id, last_processed_event_id=initial_event_id
        )
        await projection_store.save_projection_state(initial_state)

        updated_event_id = uuid.uuid4()
        updated_ts = datetime.datetime.now(datetime.timezone.utc)

        # Simulate retrieving and updating
        current_state = await projection_store.get_projection_state(
            sample_projection_id
        )
        assert current_state is not None
        current_state.update_progress(
            event_id=updated_event_id, event_timestamp=updated_ts
        )
        await projection_store.save_projection_state(current_state)

        final_state = await projection_store.get_projection_state(sample_projection_id)
        assert final_state is not None
        assert final_state.last_processed_event_id == updated_event_id
        assert final_state.last_processed_event_timestamp == updated_ts
        assert final_state.last_updated_at > initial_state.last_updated_at

    @pytest.mark.asyncio
    async def test_clear_projection_state(
        self,
        projection_store: ProjectionStore[TEventId_InMemory],
        sample_projection_id: ProjectionId,
    ):
        state = ProjectionState(
            projection_id=sample_projection_id, last_processed_event_id=uuid.uuid4()
        )
        await projection_store.save_projection_state(state)
        assert (
            await projection_store.get_projection_state(sample_projection_id)
            is not None
        )

        await projection_store.clear_projection_state(sample_projection_id)
        assert await projection_store.get_projection_state(sample_projection_id) is None
