import abc
from typing import Any, Generic, List, Optional, TypeVar

from castlecraft_engineer.abstractions.query import Query
from castlecraft_engineer.authorization.permission import Permission

TQuery = TypeVar("TQuery", bound=Query)


class QueryHandler(Generic[TQuery], abc.ABC):
    """
    Abstract base class for query handlers.
    Each handler is responsible for processing
    a specific type of query.
    """

    async def authorize(
        self,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        *args: Any,
        **kwargs: Any,
    ) -> Optional[bool]:
        """
        Optional pre-execution authorization check for the query.

        NOTE: This method is NOT automatically called by the default QueryBus.
        It serves as a convention or hook for developers to implement custom
        pre-authorization logic if they choose to call it explicitly from within
        their `execute` method, or if they are using a custom bus implementation
        that invokes it.

        The recommended pattern for authorization with the default bus is to use
        an injected `AuthorizationService` within the `execute` method.

        Args:
            subject_id: The ID of the subject.
            permissions: A list of Permission objects representing the
                         permissions granted to the subject.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments for context.
        Returns:
            True if the subject has permission, False otherwise.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    async def execute(
        self,
        query: TQuery,
        *args,
        subject_id: Optional[str] = None,
        permissions: List[Permission] = [],
        **kwargs,
    ) -> Any:
        """
        Handles the execution logic for the given query.

        Args:
            query: The query instance to be processed.
            subject_id: The ID of the subject attempting
                        to execute the query. Optional.
            permissions: The permissions associated with the subject.

        Raises:
            NotImplementedError: This method must be implemented by concrete subclasses.
        """
        raise NotImplementedError
