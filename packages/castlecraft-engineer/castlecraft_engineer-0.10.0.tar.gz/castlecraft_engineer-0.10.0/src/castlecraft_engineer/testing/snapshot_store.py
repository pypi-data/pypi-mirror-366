import asyncio
from abc import abstractmethod
from collections import defaultdict
from typing import AsyncGenerator, Dict, Generic, Optional

import pytest
import pytest_asyncio  # Import pytest_asyncio

from castlecraft_engineer.abstractions.aggregate import TAggregateId
from castlecraft_engineer.abstractions.snapshot import Snapshot
from castlecraft_engineer.abstractions.snapshot_store import SnapshotStore


class InMemorySnapshotStore(SnapshotStore[TAggregateId]):
    """
    An in-memory implementation of the SnapshotStore for testing purposes.
    Stores only the latest snapshot per aggregate.
    """

    def __init__(self) -> None:
        self._snapshots: Dict[TAggregateId, Snapshot[TAggregateId]] = {}
        self._locks: Dict[TAggregateId, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def _get_lock(self, aggregate_id: TAggregateId) -> asyncio.Lock:
        return self._locks[aggregate_id]

    async def save_snapshot(self, snapshot: Snapshot[TAggregateId]) -> None:
        async with await self._get_lock(snapshot.aggregate_id):
            existing_snapshot = self._snapshots.get(snapshot.aggregate_id)
            if (
                existing_snapshot is None
                or snapshot.version >= existing_snapshot.version
            ):
                self._snapshots[snapshot.aggregate_id] = snapshot

    async def get_latest_snapshot(
        self, aggregate_id: TAggregateId
    ) -> Optional[Snapshot[TAggregateId]]:
        async with await self._get_lock(aggregate_id):
            return self._snapshots.get(aggregate_id)

    async def clear_snapshots(self, aggregate_id: TAggregateId) -> None:
        async with await self._get_lock(aggregate_id):
            if aggregate_id in self._snapshots:
                del self._snapshots[aggregate_id]
            # Optionally remove lock if no longer needed and no other operations expected
            # if aggregate_id in self._locks and not self._snapshots.get(aggregate_id):
            # del self._locks[aggregate_id]

    async def clear_all_for_testing(self) -> None:
        """Clears all snapshots from the store for testing."""
        self._snapshots.clear()
        self._locks.clear()


# Example concrete snapshot data for testing
class MyTestSnapshotData:
    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MyTestSnapshotData) and self.value == other.value


class BaseSnapshotStoreTest(Generic[TAggregateId]):
    @pytest_asyncio.fixture  # Use pytest_asyncio.fixture for consistency
    @abstractmethod
    async def snapshot_store(
        self,
    ) -> AsyncGenerator[SnapshotStore[TAggregateId], None]:
        """Yields a clean instance of the SnapshotStore."""
        raise NotImplementedError

    @pytest.fixture
    @abstractmethod
    def generate_aggregate_id(self) -> TAggregateId:
        """Generates a unique aggregate ID."""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_save_and_get_snapshot(
        self,
        snapshot_store: SnapshotStore[TAggregateId],
        generate_aggregate_id: TAggregateId,
    ):
        agg_id = generate_aggregate_id
        snapshot_data = MyTestSnapshotData("state_v1")
        snapshot1 = Snapshot(
            aggregate_id=agg_id, aggregate_state=snapshot_data, version=0
        )
        await snapshot_store.save_snapshot(snapshot1)
        retrieved = await snapshot_store.get_latest_snapshot(agg_id)
        assert retrieved is not None
        assert retrieved.aggregate_id == agg_id
        assert retrieved.aggregate_state == snapshot_data
        assert retrieved.version == 0

    @pytest.mark.asyncio
    async def test_get_non_existent_snapshot(
        self,
        snapshot_store: SnapshotStore[TAggregateId],
        generate_aggregate_id: TAggregateId,
    ):
        agg_id = generate_aggregate_id
        retrieved = await snapshot_store.get_latest_snapshot(agg_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_save_newer_snapshot_overwrites_older(
        self,
        snapshot_store: SnapshotStore[TAggregateId],
        generate_aggregate_id: TAggregateId,
    ):
        agg_id = generate_aggregate_id
        snapshot1 = Snapshot(
            aggregate_id=agg_id,
            aggregate_state=MyTestSnapshotData("state_v1"),
            version=0,
        )
        await snapshot_store.save_snapshot(snapshot1)
        snapshot2 = Snapshot(
            aggregate_id=agg_id,
            aggregate_state=MyTestSnapshotData("state_v2"),
            version=5,
        )
        await snapshot_store.save_snapshot(snapshot2)
        retrieved = await snapshot_store.get_latest_snapshot(agg_id)
        assert (
            retrieved is not None
            and retrieved.aggregate_state.value == "state_v2"
            and retrieved.version == 5
        )

    @pytest.mark.asyncio
    async def test_save_older_snapshot_is_ignored(
        self,
        snapshot_store: SnapshotStore[TAggregateId],
        generate_aggregate_id: TAggregateId,
    ):
        agg_id = generate_aggregate_id
        snapshot2 = Snapshot(
            aggregate_id=agg_id,
            aggregate_state=MyTestSnapshotData("state_v2"),
            version=5,
        )
        await snapshot_store.save_snapshot(snapshot2)
        snapshot1 = Snapshot(
            aggregate_id=agg_id,
            aggregate_state=MyTestSnapshotData("state_v1"),
            version=0,
        )
        await snapshot_store.save_snapshot(snapshot1)
        retrieved = await snapshot_store.get_latest_snapshot(agg_id)
        assert (
            retrieved is not None
            and retrieved.aggregate_state.value == "state_v2"
            and retrieved.version == 5
        )

    @pytest.mark.asyncio
    async def test_snapshot_isolation_between_aggregates(
        self,
        snapshot_store: SnapshotStore[TAggregateId],
        generate_aggregate_id: TAggregateId,  # This is agg_id1
    ):
        agg_id1 = (
            generate_aggregate_id  # Use the injected fixture result for the first ID
        )

        # For the second ID, call the method that the fixture would call.
        # This relies on knowing the implementation detail of the concrete fixture.
        agg_id2 = __import__("uuid").uuid4()
        snap1 = Snapshot(
            aggregate_id=agg_id1,
            aggregate_state=MyTestSnapshotData("state_agg1"),
            version=0,
        )
        await snapshot_store.save_snapshot(snap1)
        snap2 = Snapshot(
            aggregate_id=agg_id2,
            aggregate_state=MyTestSnapshotData("state_agg2"),
            version=0,
        )
        await snapshot_store.save_snapshot(snap2)
        retrieved1 = await snapshot_store.get_latest_snapshot(agg_id1)
        retrieved2 = await snapshot_store.get_latest_snapshot(agg_id2)
        assert (
            retrieved1 is not None and retrieved1.aggregate_state.value == "state_agg1"
        )
        assert (
            retrieved2 is not None and retrieved2.aggregate_state.value == "state_agg2"
        )
