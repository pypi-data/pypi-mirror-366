import abc
from typing import Any, Generic, List, Optional, Type, TypeVar
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from castlecraft_engineer.abstractions.query import Query
from castlecraft_engineer.abstractions.query_handler import QueryHandler
from castlecraft_engineer.authorization.permission import Permission

TQuery = TypeVar("TQuery", bound=Query)
TQueryHandler = TypeVar("TQueryHandler", bound=QueryHandler)


class BaseQueryHandlerTest(Generic[TQuery, TQueryHandler], abc.ABC):
    """
    Base class for testing QueryHandler implementations.

    Provides common fixtures and helper methods for query handler tests.
    Subclasses must define the `handler_class` attribute.
    """

    @property
    @abc.abstractmethod
    def handler_class(self) -> Type[TQueryHandler]:
        """The specific QueryHandler class being tested."""
        raise NotImplementedError

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Provides a mock SQLModel Session."""
        # Configure common methods used within a 'with' block
        mock = MagicMock(spec=Session)
        mock.__enter__.return_value = mock
        mock.__exit__.return_value = None
        # Mock the 'exec' chain often used with SQLModel select
        mock.exec.return_value = MagicMock()
        return mock

    @pytest.fixture
    def mock_session_factory(self, mock_session: MagicMock) -> MagicMock:
        """Provides a mock sessionmaker that returns the mock_session."""
        factory = MagicMock(spec=sessionmaker)
        # When the factory is called
        # (like in 'with self._sessionmaker() as session:')
        # it should return the mock_session
        factory.return_value = mock_session
        return factory

    @pytest.fixture
    def handler_instance(
        self,
        mock_session_factory: MagicMock,  # Keep for potential override by subclasses
    ) -> TQueryHandler:
        """
        Provides an instance of the handler_class with mocked dependencies.
        Override this fixture if your handler has different dependencies.
        """
        # If QueryHandler subclasses do not take session_factory in __init__,
        # then it should not be passed here.
        # Assuming a parameterless constructor or DI handles dependencies.
        try:
            return self.handler_class()
        except TypeError as e:
            pytest.fail(
                f"Failed to instantiate {self.handler_class.__name__}. "
                "Does it have a parameterless __init__ or require specific arguments? "
                "If not, override the 'handler_instance' "
                f"fixture in your test class. Original error: {e}"
            )

    async def execute_query(
        self,
        handler: TQueryHandler,
        query: TQuery,
        subject_id: Optional[str] = None,
        permissions: Optional[List[Permission]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Helper method to execute the query using the handler instance.

        Args:
            handler: The query handler instance.
            query: The query instance to execute.
            subject_id: Optional ID of the user or system initiating the query.
            permissions: Optional list of permissions held by the subject.
            *args: Additional positional arguments to pass to the handler's execute method.
            **kwargs: Additional keyword arguments to pass to the handler's execute method.

        Returns:
            Any: The result of the handler's execute method.
        """
        # Ensure default for permissions if None is passed,
        # matching the QueryHandler.execute signature.
        effective_permissions = permissions if permissions is not None else []

        return await handler.execute(
            query,
            subject_id=subject_id,
            permissions=effective_permissions,
            *args,
            **kwargs,
        )
