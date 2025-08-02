import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from unittest.mock import MagicMock

import punq
import pytest
from punq import Container
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from castlecraft_engineer.abstractions.query import Query
from castlecraft_engineer.abstractions.query_bus import QueryBus
from castlecraft_engineer.abstractions.query_handler import QueryHandler

TQuery = TypeVar("TQuery", bound=Query)
THandler = TypeVar("THandler", bound=QueryHandler)


class QueryBusTestHelper:
    """
    A helper class for testing
    QueryBus interactions.

    Manages registration and cleanup of handlers
    and dependencies within a DI container for
    isolated testing.
    """

    def __init__(self, bus: QueryBus, container: Container):
        if not isinstance(bus, QueryBus):
            raise TypeError("bus must be an instance of QueryBus")
        if not isinstance(container, Container):
            raise TypeError("container must be an instance of punq.Container")

        self._bus = bus
        self._container = container
        self._logger = logging.getLogger(self.__class__.__name__)
        self._container = container
        # Keep track of what was registered to clean up later
        self._registered_handlers: List[Type[QueryHandler]] = []
        self._original_registrations: Dict[Type, Any] = {}
        self._original_handler_map = bus._handler_classes.copy()

    def register_handler(
        self,
        handler_cls: Type[THandler],
        dependencies: Optional[Dict[Type, Any]] = None,
    ) -> THandler:
        """
        Registers a handler and its dependencies
        in the container for the test.

        Args:
            handler_cls: The QueryHandler class to register.
            dependencies: A dictionary mapping dependency types
                          to specific instances or mocks to be
                          used by this handler.

        Returns:
            An instance of the registered handler
            resolved from the container.
        """
        # Store original registrations
        # if they exist, before overwriting
        if dependencies:
            for dep_type, instance in dependencies.items():
                if self._container.is_registered(dep_type):
                    if dep_type not in self._original_registrations:
                        # Store only the first time we encounter it
                        self._original_registrations[dep_type] = (
                            self._container.resolve(dep_type)
                        )
                self._container.register(dep_type, instance=instance)

        # Register the handler itself
        if self._container.is_registered(handler_cls):
            if handler_cls not in self._original_registrations:
                self._original_registrations[handler_cls] = (
                    self._container.resolve(  # noqa: E501
                        handler_cls,  # noqa: E501
                    )  # noqa: E501
                )  # noqa: E501
        # Register or overwrite
        self._container.register(handler_cls)

        # Register with the bus
        # We use the bus's internal
        # method to bypass DI registration again
        query_type = self._bus._get_query_type(handler_cls)
        if query_type in self._bus._handler_classes:
            # If the test explicitly registers, it overrides
            self._logger.warning(
                f"Warning: Overwriting handler for {query_type.__name__} in test setup.",  # noqa: 501
            )
        self._bus._handler_classes[query_type] = handler_cls

        self._registered_handlers.append(handler_cls)

        # Resolve and return an instance for convenience
        return self._container.resolve(handler_cls)

    def execute(self, query: Query, **kwargs) -> Any:
        """Executes a query using the configured bus."""
        return self._bus.execute(query, **kwargs)

    def cleanup(self):
        """Restores the container and bus to their original state."""
        # Remove handlers registered with the bus during the test
        self._bus._handler_classes = self._original_handler_map.copy()

        # Remove or restore registrations in the container
        for handler_cls in self._registered_handlers:
            if handler_cls in self._original_registrations:
                # Restore original if it existed
                self._container.register(
                    handler_cls,
                    instance=self._original_registrations[handler_cls],
                )

        # Restore original dependencies
        for (
            dep_type,
            original_instance,
        ) in self._original_registrations.items():  # noqa: E501
            # Check if it's not a handler we already potentially restored
            if dep_type not in self._registered_handlers:
                self._container.register(dep_type, instance=original_instance)

        # Clear tracking for the next test
        self._registered_handlers.clear()
        self._original_registrations.clear()
        self._original_handler_map.clear()


@pytest.fixture
def query_bus_helper(request):
    """
    Provides an isolated QueryBusTestHelper instance,
    container, and bus for each test, with automatic cleanup.
    """
    # Create isolated instances for the test
    test_container = punq.Container()
    test_bus = QueryBus(container=test_container)
    helper = QueryBusTestHelper(bus=test_bus, container=test_container)
    yield helper
    # Teardown: Cleanup registrations made via the helper
    helper.cleanup()


# Mock Session and Sessionmaker for database interactions
@pytest.fixture
def mock_session():
    """Provides a mock SQLModel Session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_session_factory(mock_session):
    """Provides a mock sessionmaker that returns the mock_session."""
    factory = MagicMock(spec=sessionmaker)
    # Configure the context manager (__enter__) to return the mock session
    factory.return_value.__enter__.return_value = mock_session
    return factory
