from typing import Any, Generic, List, Optional, Type, TypeVar
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from castlecraft_engineer.abstractions.command import Command
from castlecraft_engineer.abstractions.command_handler import CommandHandler
from castlecraft_engineer.abstractions.event_publisher import ExternalEventPublisher
from castlecraft_engineer.abstractions.repository import AggregateRepository
from castlecraft_engineer.authorization.permission import Permission

T = TypeVar("T", bound=Command)
H = TypeVar("H", bound=CommandHandler)


class BaseCommandHandlerTest(Generic[T, H]):
    """
    Base class for testing CommandHandler implementations.

    Provides pytest fixtures for common dependencies like sessionmaker,
    repository, and event publisher, allowing subclasses to focus on
    testing the handler's execution logic.
    """

    handler_class: Optional[Type[H]] = None

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Provides a MagicMock instance simulating a Session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def mock_sessionmaker(self, mock_session: MagicMock) -> MagicMock:
        """Provides a MagicMock simulating a sessionmaker callable."""
        # Configure the mock sessionmaker to return the mock_session
        # when called as a context manager (`with sessionmaker() as session:`)
        mock_factory = MagicMock(spec=sessionmaker)
        mock_factory.return_value.__enter__.return_value = mock_session
        return mock_factory

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Provides a MagicMock simulating an AggregateRepository."""
        # Use spec=AggregateRepository for better type checking if needed
        return MagicMock(spec=AggregateRepository)

    @pytest.fixture
    def mock_publisher(self) -> MagicMock:
        """Provides a MagicMock simulating an ExternalEventPublisher."""
        return MagicMock(spec=ExternalEventPublisher)

    @pytest.fixture
    def handler_instance(
        self,
        mock_sessionmaker: MagicMock,
        mock_repository: MagicMock,
        mock_publisher: MagicMock,
    ) -> H:
        """
        Instantiates the handler_class with mocked dependencies.

        Assumes a standard constructor signature like:
        Handler(sessionmaker, repository, publisher, ...)

        Subclasses might need to override this fixture if their handler
        has a different constructor signature or requires additional mocks.
        """
        if not self.handler_class:
            pytest.skip(
                "handler_class not set in test subclass",
            )

        # Instantiate the handler with the mocked dependencies
        # Adjust arguments based on the actual handler's __init__
        try:
            instance = self.handler_class(
                session_factory=mock_sessionmaker,
                repository=mock_repository,
                publisher=mock_publisher,  # type: ignore[call-arg]
            )
            return instance
        except TypeError as e:
            pytest.fail(
                f"Failed to instantiate {self.handler_class.__name__}. "
                f"Check constructor signature and fixture arguments. Error: {e}"  # noqa: E501
            )

    async def execute_command(
        self,
        handler_instance: H,
        command: T,
        subject_id: Optional[str] = None,
        permissions: Optional[List[Permission]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Helper method to execute the command handler's execute method.
        """
        permissions = permissions if permissions is not None else []
        return await handler_instance.execute(
            command,
            subject_id=subject_id,
            permissions=permissions,
            *args,
            **kwargs,
        )
