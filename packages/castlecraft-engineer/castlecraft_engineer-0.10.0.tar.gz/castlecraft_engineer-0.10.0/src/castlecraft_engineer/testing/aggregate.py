import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from castlecraft_engineer.abstractions.aggregate import Aggregate
from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.repository import (
    AggregateRepository,
    AsyncAggregateRepository,
)

T = TypeVar("T", bound=Aggregate)
E = TypeVar("E", bound=Event)
M = TypeVar("M")
Repo = TypeVar("Repo", bound=AggregateRepository)  # type: ignore


class BaseAggregateTest(Generic[T]):
    aggregate_class: Optional[Type[T]] = None

    @pytest.fixture
    def aggregate_id(self) -> uuid.UUID:
        return uuid.uuid4()

    def _create_aggregate(
        self, aggregate_id: uuid.UUID, *args: Any, **kwargs: Any
    ) -> T:
        if not self.aggregate_class:
            raise NotImplementedError(
                "Subclasses must define 'aggregate_class'",
            )
        # Ensure 'id' from kwargs doesn't conflict with the explicit aggregate_id
        # If 'id' is in kwargs, it will be ignored in favor of aggregate_id.
        # Alternatively, you could raise an error if 'id' is in kwargs.
        kwargs.pop("id", None)
        return self.aggregate_class(id=aggregate_id, *args, **kwargs)  # type: ignore[no-any-return, misc]

    def _load_aggregate_from_history(
        self, aggregate_id: uuid.UUID, history: List[Event]
    ) -> T:  # type: ignore
        if not self.aggregate_class:
            raise NotImplementedError(
                "Subclasses must define 'aggregate_class'"
            )  # noqa: E501
        if not hasattr(self.aggregate_class, "load_from_history"):
            raise NotImplementedError(
                f"{self.aggregate_class.__name__} must implement 'load_from_history'"  # noqa: E501
            )
        return self.aggregate_class.load_from_history(aggregate_id, history)  # type: ignore

    def _get_uncommitted_events(self, aggregate: T) -> List[Event]:
        return getattr(aggregate, "_uncommitted_events", [])[:]

    def _clear_uncommitted_events(self, aggregate: T):
        if hasattr(aggregate, "_uncommitted_events"):
            setattr(aggregate, "_uncommitted_events", [])

    def assert_event_recorded(
        self,
        aggregate: T,
        event_type: Type[E],
        count: int = 1,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        recorded_events = self._get_uncommitted_events(aggregate)
        matching_events = [  # noqa: E501
            e for e in recorded_events if isinstance(e, event_type)  # noqa: E501
        ]  # noqa: E501

        assert len(matching_events) == count, (
            f"Expected {count} event(s) of type {event_type.__name__}, "
            f"but found {len(matching_events)} in {recorded_events}"
        )

        if count == 1 and attributes:
            event = matching_events[0]
            for attr, expected_value in attributes.items():
                assert hasattr(
                    event, attr
                ), f"Event {event_type.__name__} does not have attribute '{attr}'"  # noqa: E501
                actual_value = getattr(event, attr)
                assert actual_value == expected_value, (
                    f"Attribute '{attr}' mismatch on {event_type.__name__}. "
                    f"Expected: {expected_value}, Actual: {actual_value}"
                )

    def assert_no_events_recorded(self, aggregate: T):
        recorded_events = self._get_uncommitted_events(aggregate)
        assert (
            len(recorded_events) == 0
        ), f"Expected no events recorded, but found: {recorded_events}"


class BaseAggregateRepositoryTest(Generic[T, M, Repo]):
    repository_class: Optional[Type[Repo]] = None
    aggregate_class: Optional[Type[T]] = None
    orm_model_class: Optional[Type[M]] = None

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        return MagicMock(spec=Session)

    @pytest.fixture
    def aggregate_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def sample_aggregate(self, aggregate_id: uuid.UUID) -> T:
        if not self.aggregate_class:
            pytest.skip("aggregate_class not set")
        # Assumes Aggregate takes id in __init__
        return self.aggregate_class(id=aggregate_id)  # type: ignore[misc]

    @pytest.fixture
    def sample_orm_model(self) -> M:
        if not self.orm_model_class:
            pytest.skip("orm_model_class not set")
        # Create a mock or real instance as needed
        return MagicMock(spec=self.orm_model_class)

    @pytest.fixture
    def repository_instance(
        self,
        mock_session: MagicMock,
    ) -> Repo:
        if not self.repository_class:
            pytest.skip("repository_class not set")
        if not self.aggregate_class:
            pytest.skip("aggregate_class not set for repository test")
        if not self.orm_model_class:
            pytest.skip("orm_model_class not set for repository test")

        # Pass both required arguments to the constructor
        return self.repository_class(
            aggregate_cls=self.aggregate_class,
            model_cls=self.orm_model_class,
        )

    def setup_get_by_id_mock(
        self,
        mock_session: MagicMock,
        orm_model_instance: Optional[M],
    ):
        """Configure mock session for get_by_id."""
        mock_session.get.return_value = orm_model_instance

    def assert_session_add_called(
        self,
        mock_session: MagicMock,
        expected_model: Any,
    ):
        """Verify session.add was called correctly."""
        mock_session.add.assert_called_once_with(expected_model)

    def assert_session_commit_called(self, mock_session: MagicMock):
        """Verify session.commit was called."""
        # Note: Commit is often called outside the repo
        mock_session.commit.assert_called_once()

    def assert_session_refresh_called(
        self, mock_session: MagicMock, expected_model: Any
    ):
        """Verify session.refresh was called."""
        mock_session.refresh.assert_called_once_with(expected_model)

    def assert_session_delete_called(
        self, mock_session: MagicMock, expected_model: Any
    ):
        """Verify session.delete was called correctly."""
        mock_session.delete.assert_called_once_with(expected_model)


AsyncRepo = TypeVar("AsyncRepo", bound=AsyncAggregateRepository)  # type: ignore


class BaseAsyncAggregateRepositoryTest(Generic[T, M, AsyncRepo]):
    """
    Base class for testing AsyncAggregateRepository implementations.

    Provides pytest fixtures and helper methods for testing asynchronous
    repository operations. Subclasses should define `repository_class`,
    `aggregate_class`, and `orm_model_class`.
    """

    repository_class: Optional[Type[AsyncRepo]] = None
    aggregate_class: Optional[Type[T]] = None
    orm_model_class: Optional[Type[M]] = None

    @pytest.fixture
    def mock_async_session(self) -> AsyncMock:
        """Provides an AsyncMock instance simulating an AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def aggregate_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def sample_aggregate(self, aggregate_id: uuid.UUID) -> T:
        if not self.aggregate_class:
            pytest.skip("aggregate_class not set")
        # Assumes Aggregate takes id in __init__
        return self.aggregate_class(id=aggregate_id)  # type: ignore[misc]

    @pytest.fixture
    def sample_orm_model(self) -> M:
        if not self.orm_model_class:
            pytest.skip("orm_model_class not set")
        # Create a mock or real instance as needed
        return AsyncMock(spec=self.orm_model_class)

    @pytest.fixture
    def repository_instance(
        self,
        mock_async_session: AsyncMock,  # Injected but not directly used by constructor
    ) -> AsyncRepo:
        if not self.repository_class:
            pytest.skip("repository_class not set")
        if not self.aggregate_class:
            pytest.skip("aggregate_class not set for repository test")
        if not self.orm_model_class:
            pytest.skip("orm_model_class not set for repository test")

        # Pass both required arguments to the constructor
        return self.repository_class(
            aggregate_cls=self.aggregate_class,
            model_cls=self.orm_model_class,
        )

    def setup_get_by_id_mock_async(
        self,
        mock_async_session: AsyncMock,
        orm_model_instance: Optional[M],
    ):
        """Configure mock async session for get_by_id."""
        mock_async_session.get.return_value = orm_model_instance

    def assert_session_add_called(
        self,
        mock_async_session: AsyncMock,
        expected_model: Any,
    ):
        """Verify session.add was called correctly (session.add is synchronous)."""
        mock_async_session.add.assert_called_once_with(expected_model)

    def assert_session_commit_awaited(self, mock_async_session: AsyncMock):
        """Verify session.commit was awaited."""
        mock_async_session.commit.assert_awaited_once()

    def assert_session_refresh_awaited(
        self, mock_async_session: AsyncMock, expected_model: Any
    ):
        """Verify session.refresh was awaited."""
        mock_async_session.refresh.assert_awaited_once_with(expected_model)

    def assert_session_delete_awaited(
        self, mock_async_session: AsyncMock, expected_model: Any
    ):
        """Verify session.delete was awaited."""
        mock_async_session.delete.assert_awaited_once_with(expected_model)
