import abc
from typing import Generic, Optional, TypeVar

from castlecraft_engineer.abstractions.projection import ProjectionId, ProjectionState

# Generic type for the event ID, can be int, UUID, etc.
TEventId = TypeVar("TEventId")


class ProjectionStore(abc.ABC, Generic[TEventId]):
    """
    Abstract base class for a store that manages the state of projections.
    This is crucial for projectors to know where they left off in an event stream.
    """

    @abc.abstractmethod
    async def get_projection_state(
        self, projection_id: ProjectionId
    ) -> Optional[ProjectionState]:
        """
        Retrieves the current state of a given projection.

        Args:
            projection_id: The unique identifier of the projection.

        Returns:
            The ProjectionState object, or None if no state exists for the projection.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def save_projection_state(self, projection_state: ProjectionState) -> None:
        """
        Saves or updates the state of a projection.

        Args:
            projection_state: The ProjectionState object to persist.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def clear_projection_state(self, projection_id: ProjectionId) -> None:
        """
        Optional: Clears the state for a given projection.
        Useful for replaying a projection from the beginning.

        Args:
            projection_id: The ID of the projection whose state is to be cleared.
        """
