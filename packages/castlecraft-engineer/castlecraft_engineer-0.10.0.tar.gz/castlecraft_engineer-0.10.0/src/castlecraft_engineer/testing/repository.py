import uuid
from typing import Any, Generic, List, Optional, Type, TypeVar
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from castlecraft_engineer.database.repository import (
    AsyncModelRepository,
    ModelRepository,
)

TSQLModel = TypeVar("TSQLModel", bound=SQLModel)
SyncRepo = TypeVar("SyncRepo", bound=ModelRepository)  # type: ignore
AsyncRepo = TypeVar("AsyncRepo", bound=AsyncModelRepository)  # type: ignore


class BaseModelRepositoryTest(Generic[TSQLModel, SyncRepo]):
    """
    Base class for testing ModelRepository implementations.

    Provides pytest fixtures and helper methods for testing synchronous
    repository operations. Subclasses should define `repository_class`
    and `model_class`.
    """

    repository_class: Optional[Type[SyncRepo]] = None
    model_class: Optional[Type[TSQLModel]] = None

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Provides a MagicMock instance simulating a Session."""
        mock = MagicMock(spec=Session)
        # Mock the execute chain for get_all
        mock.execute.return_value.scalars.return_value.all.return_value = []
        return mock

    @pytest.fixture
    def sample_model_id(self) -> Any:
        """Provides a sample ID for the model.
        Can be overridden if the PK is not UUID."""
        return uuid.uuid4()

    @pytest.fixture
    def sample_model_instance(self, sample_model_id: Any) -> TSQLModel:
        if not self.model_class:
            pytest.skip("model_class not set")
        # Assumes model can be instantiated with its ID or relevant fields
        # Adjust if your model's __init__ is different
        try:
            return self.model_class(id=sample_model_id)  # type: ignore
        except TypeError:
            # Fallback for models without 'id' in __init__ or complex init
            return MagicMock(spec=self.model_class, id=sample_model_id)

    @pytest.fixture
    def repository_instance(self) -> SyncRepo:
        if not self.repository_class:
            pytest.skip("repository_class not set")
        if not self.model_class:
            pytest.skip("model_class not set for repository test")
        return self.repository_class(model=self.model_class)

    def setup_session_get_mock(
        self,
        mock_session: MagicMock,
        return_value: Optional[TSQLModel],
    ):
        """Configure mock session.get to return a specific value."""
        mock_session.get.return_value = return_value

    def setup_session_execute_mock(
        self,
        mock_session: MagicMock,
        return_value: List[TSQLModel],
    ):
        """Configure mock session.execute().scalars().all() chain."""
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            return_value
        )

    def assert_session_add_called(
        self, mock_session: MagicMock, expected_model: TSQLModel
    ):
        mock_session.add.assert_called_once_with(expected_model)

    def assert_session_commit_called(self, mock_session: MagicMock):
        mock_session.commit.assert_called_once()

    def assert_session_refresh_called(
        self, mock_session: MagicMock, expected_model: TSQLModel
    ):
        mock_session.refresh.assert_called_once_with(expected_model)

    def assert_session_delete_called(
        self, mock_session: MagicMock, expected_model: TSQLModel
    ):
        mock_session.delete.assert_called_once_with(expected_model)


class BaseAsyncModelRepositoryTest(Generic[TSQLModel, AsyncRepo]):
    """
    Base class for testing AsyncModelRepository implementations.

    Provides pytest fixtures and helper methods for testing asynchronous
    repository operations. Subclasses should define `repository_class`
    and `model_class`.
    """

    repository_class: Optional[Type[AsyncRepo]] = None
    model_class: Optional[Type[TSQLModel]] = None

    @pytest.fixture
    def mock_async_session(self) -> AsyncMock:
        """Provides an AsyncMock instance simulating an AsyncSession."""
        mock = AsyncMock(spec=AsyncSession)
        # Mock the execute chain for get_all
        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()
        mock_scalars_result.all.return_value = []  # Default to empty list

        mock_execute_result.scalars.return_value = mock_scalars_result
        mock.execute.return_value = mock_execute_result
        return mock

    @pytest.fixture
    def sample_model_id(self) -> Any:
        """Provides a sample ID for the model.
        Can be overridden if the PK is not UUID."""
        return uuid.uuid4()

    @pytest.fixture
    def sample_model_instance(self, sample_model_id: Any) -> TSQLModel:
        if not self.model_class:
            pytest.skip("model_class not set")
        try:
            return self.model_class(id=sample_model_id)  # type: ignore
        except TypeError:
            return MagicMock(spec=self.model_class, id=sample_model_id)

    @pytest.fixture
    def repository_instance(self) -> AsyncRepo:
        if not self.repository_class:
            pytest.skip("repository_class not set")
        if not self.model_class:
            pytest.skip("model_class not set for repository test")
        return self.repository_class(model=self.model_class)

    def setup_session_get_mock_async(
        self,
        mock_async_session: AsyncMock,
        return_value: Optional[TSQLModel],
    ):
        """Configure mock async_session.get to return a specific value."""
        mock_async_session.get.return_value = return_value

    def setup_session_execute_mock_async(
        self,
        mock_async_session: AsyncMock,
        return_value: List[TSQLModel],
    ):
        """Configure mock async_session.execute().scalars().all() chain."""
        mock_async_session.execute.return_value.scalars.return_value.all.return_value = (
            return_value
        )

    def assert_session_add_called(
        self, mock_async_session: AsyncMock, expected_model: TSQLModel
    ):
        # session.add is synchronous even in AsyncSession
        mock_async_session.add.assert_called_once_with(expected_model)

    def assert_session_commit_awaited(self, mock_async_session: AsyncMock):
        mock_async_session.commit.assert_awaited_once()

    def assert_session_refresh_awaited(
        self, mock_async_session: AsyncMock, expected_model: TSQLModel
    ):
        mock_async_session.refresh.assert_awaited_once_with(expected_model)

    def assert_session_delete_awaited(
        self, mock_async_session: AsyncMock, expected_model: TSQLModel
    ):
        # session.delete is synchronous, but the repo method is async
        # and might await other things or be part of an async flow.
        # The actual call to session.delete itself is not awaited.
        # However, the repository's delete_by_id method will await session.commit()
        mock_async_session.delete.assert_called_once_with(expected_model)
