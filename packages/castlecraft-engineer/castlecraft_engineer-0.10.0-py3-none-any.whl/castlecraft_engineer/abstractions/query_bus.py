import inspect
import typing
from typing import Any, Dict, List, Optional, Type, TypeVar

import punq
from punq import MissingDependencyError

from castlecraft_engineer.abstractions.query import Query
from castlecraft_engineer.abstractions.query_handler import QueryHandler
from castlecraft_engineer.authorization.permission import Permission

TQuery = TypeVar("TQuery", bound=Query)


class QueryHandlerNotFoundError(Exception):
    """Raised when no handler is found for a given query type."""

    def __init__(self, query_type: Type[Query]):
        super().__init__(
            f"No handler registered for query type {query_type.__name__}",
        )
        self.query_type = query_type


class QueryBus:
    """
    Coordinates the execution of query by
    routing them to registered handlers,
    using a globally accessible
    dependency injection container.
    """

    def __init__(self, container: punq.Container) -> None:
        """
        Initializes the QueryBus with an
        empty handler registry.
        It relies on a globally accessible
        DI container ('container').
        """

        self._container = container
        self._handler_classes: Dict[
            Type[Query],
            Type[QueryHandler[Any]],
        ] = {}

    def _get_query_type(
        self,
        handler_cls: Type[QueryHandler[TQuery]],
    ) -> Type[TQuery]:
        """
        Inspects a handler class to find the
        Query type it handles.

        Raises:
            TypeError: If the query type cannot be determined.
        """

        for base in getattr(handler_cls, "__orig_bases__", []):
            origin = typing.get_origin(base)
            if origin is QueryHandler:
                args = typing.get_args(base)
                if (
                    args
                    and isinstance(args[0], type)
                    and issubclass(args[0], Query)  # noqa: E501
                ):
                    return typing.cast(Type[TQuery], args[0])

        raise TypeError(
            "Could not determine Query type for "
            f"handler {handler_cls.__name__}. "
            "Ensure it inherits directly like: "
            "MyHandler(QueryHandler[MySpecificQuery])."
        )

    def register(
        self, handler_cls: Type[QueryHandler[TQuery]]
    ) -> Type[QueryHandler[TQuery]]:
        """
        Decorator to register a QueryHandler class with
        the bus and the global DI container.

        Args:
            handler_cls: The QueryHandler class to register.

        Returns:
            The original handler class, unchanged.

        Raises:
            TypeError: If the handler_cls is not a valid
                       QueryHandler subclass or its query
                       type cannot be determined.
            ValueError: If a handler is already registered
                        for the query type.
        """

        is_class = inspect.isclass(handler_cls)
        if not is_class:
            raise TypeError(
                f"{repr(handler_cls)} is not a valid QueryHandler.",
            )

        if not issubclass(handler_cls, QueryHandler):
            raise TypeError(
                f"{handler_cls.__name__} is not a valid QueryHandler.",
            )

        query_type = self._get_query_type(handler_cls)

        if query_type in self._handler_classes:
            raise ValueError(
                f"Handler already registered for query {query_type.__name__}"  # noqa: E501
            )

        self._handler_classes[query_type] = handler_cls

        return handler_cls

    async def execute(
        self,
        query: Query,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        *args,
        **kwargs,
    ) -> Any:
        """
        Executes a query by finding its handler class,
        resolving it via the
        global DI container, authorizing, and handling.

        Args:
            query: The query instance to execute.

        Raises:
            QueryHandlerNotFoundError: If no handler class is
                                        registered for the query type.
            punq.MissingDependencyError: If the container cannot
                                        resolve the handler or
                                        its dependencies.
            Exception: Any other exception raised
                        during handler resolution
                        or execution.
        """  # noqa: E501
        query_type: Type[Query] = type(query)
        handler_cls = self._handler_classes.get(query_type)

        if handler_cls is None:
            raise QueryHandlerNotFoundError(query_type)

        try:
            handler = self._container.resolve(handler_cls)
        except MissingDependencyError as e:
            raise MissingDependencyError(
                "Failed to resolve handler "
                f"{handler_cls.__name__} for query "
                f"{query_type.__name__}: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error resolving handler for {handler_cls.__name__}: {e}"  # noqa: E501
            ) from e

        if not isinstance(handler, QueryHandler):
            raise TypeError(
                f"Resolved object for {handler_cls.__name__} is not a QueryHandler instance."  # noqa: E501
            )

        return await handler.execute(
            query,
            subject_id=subject_id,
            permissions=permissions,
            *args,
            **kwargs,
        )
