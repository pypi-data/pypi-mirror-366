from typing import Any, Dict, Iterator, List, Optional, Type

import punq
import pytest

from castlecraft_engineer.abstractions.command import Command
from castlecraft_engineer.abstractions.command_bus import CommandBus
from castlecraft_engineer.abstractions.command_handler import CommandHandler
from castlecraft_engineer.authorization.permission import Permission


# --- Define Dummy Classes at Module Level ---
class _DummyCommand(Command):
    payload: str = "test"


class _DummyCommandHandler(CommandHandler[_DummyCommand]):
    def __init__(self) -> None:
        self.executed_command: Optional[_DummyCommand] = None
        self.execute_called: bool = False
        self.received_kwargs: Optional[Dict[str, Any]] = None
        self.received_args: Optional[tuple[Any, ...]] = None
        self.received_subject_id: Optional[str] = None
        self.received_permissions: Optional[List[Permission]] = None

    async def execute(
        self,
        command: _DummyCommand,
        *args: Any,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        **kwargs: Any,
    ) -> str:
        self.executed_command = command
        self.execute_called = True
        self.received_kwargs = kwargs
        self.received_args = args
        self.received_subject_id = subject_id
        self.received_permissions = permissions
        return f"Handled {command.payload}"


class _DummyCommandWithDependency(Command):
    pass


class _DummyDependency:
    def get_value(self) -> str:
        return "dependency_value"


@pytest.fixture(scope="class")
def DummyCommandOnly() -> Type[_DummyCommand]:
    """Provides a dummy Command class."""
    return _DummyCommand


@pytest.fixture(scope="class")
def DummyCommandHandlerOnly(
    DummyCommandOnly: Type[_DummyCommand],
) -> Type[_DummyCommandHandler]:
    """Provides a dummy CommandHandler class."""
    return _DummyCommandHandler


@pytest.fixture(scope="class")
def DummyCommandWithDependencyOnly() -> Type[_DummyCommandWithDependency]:
    """Provides a dummy Command class requiring a handler with dependency."""
    return _DummyCommandWithDependency


@pytest.fixture(scope="class")
def DummyDependencyOnly() -> Type[_DummyDependency]:
    """Provides a dummy dependency class."""
    return _DummyDependency


class _DummyCommandHandlerWithDependency(CommandHandler[_DummyCommandWithDependency]):
    def __init__(self, dependency: _DummyDependency):
        self.dependency = dependency
        self.executed_command: Optional[_DummyCommandWithDependency] = None
        self.execute_called: bool = False
        self.received_kwargs: Optional[Dict[str, Any]] = None
        self.received_args: Optional[tuple[Any, ...]] = None
        self.received_subject_id: Optional[str] = None
        self.received_permissions: Optional[List[Permission]] = None

    async def execute(
        self,
        command: _DummyCommandWithDependency,
        *args: Any,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        **kwargs: Any,
    ) -> str:
        self.executed_command = command
        self.execute_called = True
        self.received_kwargs = kwargs
        self.received_args = args
        self.received_subject_id = subject_id
        self.received_permissions = permissions
        return f"Handled with {self.dependency.get_value()}"


@pytest.fixture(scope="class")
def DummyCommandHandlerWithDependencyOnly(
    DummyCommandWithDependencyOnly: Type[_DummyCommandWithDependency],
    DummyDependencyOnly: Type[_DummyDependency],
) -> Type[_DummyCommandHandlerWithDependency]:
    """Provides a dummy CommandHandler class with a dependency."""
    return _DummyCommandHandlerWithDependency


@pytest.fixture(autouse=True)
def clean_container_for_bus_tests() -> Iterator[punq.Container]:
    """
    Provides a fresh, isolated punq container for each test
    by patching the global 'container' used by the CommandBus.
    Ensures test isolation for DI registrations.
    """
    isolated_container = punq.Container()

    yield isolated_container
    # Teardown (clearing the container) is implicitly handled by fixture scope


@pytest.fixture
def command_bus_instance(clean_container_for_bus_tests) -> CommandBus:
    """Provides a clean CommandBus instance for testing."""

    return CommandBus(
        container=clean_container_for_bus_tests,
    )
