from abc import ABC, abstractmethod


class EventStreamConsumer(ABC):
    """
    Abstract base class for consuming events from an external stream
    and publishing them to an internal EventBus.
    """

    @abstractmethod
    async def run(self):
        """
        Starts the consumer loop to listen for and process events.
        This method should typically run indefinitely
        until shutdown is requested.
        """
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self):
        """
        Initiates a graceful shutdown of the consumer.
        Implementations should ensure pending work is
        handled and resources are released.
        """
        raise NotImplementedError
