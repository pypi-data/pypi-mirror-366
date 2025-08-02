import inspect
import typing
from typing import Any, Dict, List, Optional, Type, TypeVar

import punq
from punq import MissingDependencyError

from castlecraft_engineer.abstractions.command import Command
from castlecraft_engineer.abstractions.command_handler import CommandHandler
from castlecraft_engineer.authorization.permission import Permission

TCommand = TypeVar("TCommand", bound=Command)


class CommandHandlerNotFoundError(Exception):
    """Raised when no handler is found for a given command type."""

    def __init__(self, command_type: Type[Command]):
        super().__init__(
            f"No handler registered for command type {command_type.__name__}"
        )
        self.command_type = command_type


class CommandBus:
    """
    Coordinates the execution of commands by
    routing them to registered handlers,
    using a globally accessible
    dependency injection container.
    """

    def __init__(self, container: punq.Container) -> None:
        """
        Initializes the CommandBus with an
        empty handler registry.
        """

        self._container = container
        self._handler_classes: Dict[
            Type[Command],
            Type[CommandHandler[Any]],
        ] = {}

    def _get_command_type(
        self,
        handler_cls: Type[CommandHandler[TCommand]],
    ) -> Type[TCommand]:
        """
        Inspects a handler class to find the
        Command type it handles.

        Raises:
            TypeError: If the command type cannot be determined.
        """
        for base in getattr(handler_cls, "__orig_bases__", []):
            origin = typing.get_origin(base)
            if origin is CommandHandler:
                args = typing.get_args(base)
                if (
                    args
                    and isinstance(args[0], type)
                    and issubclass(args[0], Command)  # noqa: E501
                ):
                    return typing.cast(Type[TCommand], args[0])

        raise TypeError(
            "Could not determine Command type for "
            f"handler {handler_cls.__name__}. "
            "Ensure it inherits directly like: "
            "MyHandler(CommandHandler[MySpecificCommand])."
        )

    def register(
        self, handler_cls: Type[CommandHandler[TCommand]]
    ) -> Type[CommandHandler[TCommand]]:
        """
        Decorator to register a CommandHandler class with
        the bus and the global DI container.

        Args:
            handler_cls: The CommandHandler class to register.

        Returns:
            The original handler class, unchanged.

        Raises:
            TypeError: If the handler_cls is not a valid
                       CommandHandler subclass or its command
                       type cannot be determined.
        """
        is_class = inspect.isclass(handler_cls)
        if not is_class:
            raise TypeError(
                f"{repr(handler_cls)} is not a valid CommandHandler.",
            )

        if not issubclass(handler_cls, CommandHandler):
            raise TypeError(
                f"{handler_cls.__name__} is not a valid CommandHandler.",
            )

        command_type = self._get_command_type(handler_cls)

        if command_type in self._handler_classes:
            raise ValueError(
                f"Handler already registered for command {command_type.__name__}"  # noqa: E501
            )

        self._handler_classes[command_type] = handler_cls

        return handler_cls

    async def execute(
        self,
        command: Command,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        *args,
        **kwargs,
    ) -> Any:
        """
        Executes a command by finding its handler class,
        resolving it via the
        global DI container, authorizing, and handling.

        Args:
            command: The command instance to execute.
            subject_id: The ID of the subject attempting
                        to execute the command.
            permissions: The permissions associated
                        with the subject.

        Raises:
            CommandHandlerNotFoundError: If no handler class is
                                        registered for the command type.
            AuthorizationError: If the handler denies authorization.
            punq.MissingDependencyError: If the container cannot
                                        resolve the handler or
                                        its dependencies.
            Exception: Any other exception raised
                        during handler resolution
                        or execution.
        """
        command_type = type(command)
        handler_cls = self._handler_classes.get(command_type)

        if handler_cls is None:
            raise CommandHandlerNotFoundError(command_type)

        try:
            # Use the container directly
            handler = self._container.resolve(handler_cls)
        except MissingDependencyError as e:
            raise MissingDependencyError(
                "Failed to resolve handler "
                f"{handler_cls.__name__} for command "
                f"{command_type.__name__}: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error resolving handler for {handler_cls.__name__}: {e}"  # noqa: E501
            ) from e

        if not isinstance(handler, CommandHandler):
            raise TypeError(
                f"Resolved object for {handler_cls.__name__} is not a CommandHandler instance."  # noqa: E501
            )

        return await handler.execute(
            command,
            subject_id=subject_id,
            permissions=permissions,
            *args,
            **kwargs,
        )
