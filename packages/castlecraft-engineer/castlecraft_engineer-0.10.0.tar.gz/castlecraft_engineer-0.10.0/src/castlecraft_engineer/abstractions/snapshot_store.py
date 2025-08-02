import abc
from typing import Generic, Optional

from castlecraft_engineer.abstractions.aggregate import TAggregateId
from castlecraft_engineer.abstractions.snapshot import Snapshot


class SnapshotStore(Generic[TAggregateId], abc.ABC):
    """
    Abstract base class for a snapshot store, responsible for persisting
    and retrieving aggregate snapshots.
    """

    @abc.abstractmethod
    async def save_snapshot(self, snapshot: Snapshot[TAggregateId]) -> None:
        """
        Saves an aggregate snapshot. If a snapshot for the given aggregate_id
        and version (or newer) already exists, it might be overwritten or ignored,
        depending on the store's strategy. Typically, you'd overwrite if the new
        snapshot is for a more recent version.

        Args:
            snapshot: The Snapshot object to persist.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_latest_snapshot(
        self, aggregate_id: TAggregateId
    ) -> Optional[Snapshot[TAggregateId]]:
        """
        Retrieves the latest snapshot for a given aggregate.

        Args:
            aggregate_id: The ID of the aggregate whose snapshot is to be loaded.

        Returns:
            The latest Snapshot object, or None if no snapshot exists for the aggregate.
        """
        raise NotImplementedError

    async def clear_snapshots(self, aggregate_id: TAggregateId) -> None:
        """Optional: Clears all snapshots for a given aggregate."""
        pass  # Default implementation does nothing or can raise NotImplementedError
