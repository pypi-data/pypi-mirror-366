import abc
from typing import List

from castlecraft_engineer.abstractions.event import Event


class ExternalEventPublisher(abc.ABC):
    """
    Abstract base class for publishing domain events to external
    messaging systems (e.g., Kafka, RabbitMQ, Redis Streams).
    """

    @abc.abstractmethod
    async def publish(self, events: List[Event]) -> None:
        """
        Publishes a list of domain events to the external broker.

        Implementations should handle serialization,connection management,
        and the specifics of the chosen message broker protocol.

        Args:
            events: A list of domain event instances to publish.

        Raises:
            NotImplementedError: This method must be implemented by
                                 concrete subclasses.
            Exception: Implementation-specific exceptions related to
                       publishing failures (e.g., connection errors,
                       serialization issues).
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> None:
        """Clean up resources, like network connections."""
        raise NotImplementedError
