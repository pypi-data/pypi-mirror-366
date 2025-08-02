import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar
from unittest.mock import AsyncMock, MagicMock

import pytest
from faker import Faker

from castlecraft_engineer.abstractions.event import Event
from castlecraft_engineer.abstractions.event_bus import EventBus
from castlecraft_engineer.abstractions.event_consumer import EventStreamConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio

TConsumer = TypeVar("TConsumer", bound=EventStreamConsumer)


@dataclass(frozen=True)
class SampleTestEvent(Event):
    payload: str
    correlation_id: uuid.UUID


class BaseEventStreamConsumerTest(ABC, Generic[TConsumer]):
    """
    Abstract base class for testing
    EventStreamConsumer implementations.

    Provides common fixtures and encourages a
    standard testing pattern.

    Subclasses MUST:
    1. Implement the `consumer_under_test` fixture. This fixture should:
       a. Instantiate the specific EventStreamConsumer implementation.
       b. Inject the `mock_event_bus` fixture provided by this base class.
       c. Inject any other necessary mocked dependencies, especially the
          mocked client for the *external event source* (e.g., Kafka, SQS).
    2. Write tests that simulate receiving data/messages from the mocked
       external source.
    3. Use the `mock_event_bus` to verify that events are correctly
       deserialized (if applicable) and published by the consumer.
    """

    @pytest.fixture
    def faker(self) -> Faker:
        """Provides a Faker instance for generating test data."""
        return Faker()

    @pytest.fixture
    def mock_event_bus(self) -> AsyncMock:
        """Provides a mock internal EventBus."""
        mock = AsyncMock(spec=EventBus)
        mock.publish.return_value = None
        return mock

    @pytest.fixture
    def sample_test_event(self, faker: Faker) -> Event:
        """Creates a generic sample Event for testing purposes."""
        generated_uuid_str = faker.uuid4()
        return SampleTestEvent(
            payload=faker.sentence(),
            correlation_id=uuid.UUID(generated_uuid_str),
        )

    @pytest.fixture
    @abstractmethod
    def consumer_under_test(self, mock_event_bus: AsyncMock) -> TConsumer:
        """
        Abstract Fixture: Subclasses MUST implement this.

        This fixture is responsible for creating an
        instance of the specific EventStreamConsumer implementation
        that is being tested. It must inject the `mock_event_bus`
        and any other mocked dependencies required by the consumer's
        constructor
        (e.g., a mocked client for the external message queue/stream).

        Example Implementation in Subclass:
        ```python
        @pytest.fixture
        def consumer_under_test(
            self, mock_event_bus: AsyncMock, mock_external_client: MagicMock
        ) -> MySpecificConsumer:
            # Assume MySpecificConsumer takes the bus and a client
            consumer = MySpecificConsumer(
                event_bus=mock_event_bus,
                external_client=mock_external_client,
                # ... other config ...
            )
            # Optional: Mock the internal logger for easier assertions
            consumer._logger = MagicMock(spec=logging.Logger)
            return consumer
        ```
        """
        raise NotImplementedError(
            "Subclasses must implement consumer_under_test fixture"
        )

    async def run_consumer_until_condition_or_timeout(
        self,
        consumer: TConsumer,
        condition_check: Callable[[], bool],
        timeout: float = 2.0,
        fail_message: str = "Condition not met within timeout",
    ):
        """
        Runs the consumer in a background task
        until a condition is met or timeout occurs.

        Handles basic task management and exception
        propagation from the consumer.

        Args:
            consumer: The consumer instance to run.
            condition_check: A callable that returns True when
                             the desired state is reached
                             (e.g., `lambda: mock_event_bus.publish.called`).
            timeout:
                    Maximum time in seconds to wait for the condition.
            fail_message:
                    Message for assertion error if timeout occurs.

        Raises:
            TimeoutError:
                    If the condition is not met within the timeout.
            Exception:
                    If the consumer task raises an
                    unexpected exception during execution.
        """
        consumer_task = asyncio.create_task(
            consumer.run(), name=f"ConsumerTask_{type(consumer).__name__}"
        )
        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                if consumer_task.done():
                    exc = consumer_task.exception()
                    if exc:
                        logger.error(
                            f"Consumer task {consumer_task.get_name()} failed: {exc!r}",  # noqa: E501
                            exc_info=exc,
                        )
                        raise exc

                if condition_check():
                    logger.debug(
                        f"Condition met for {consumer_task.get_name()}.",
                    )
                    return

                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.error(
                        f"Timeout waiting for condition in {consumer_task.get_name()}."  # noqa: E501
                    )
                    raise TimeoutError(fail_message)

                await asyncio.sleep(0.01)
        finally:
            if not consumer_task.done():
                logger.debug(
                    f"Cleaning up consumer task {consumer_task.get_name()}...",
                )
                shutdown_task = asyncio.create_task(consumer.shutdown())
                try:
                    await asyncio.wait_for(shutdown_task, timeout=0.5)
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Consumer shutdown() call timed out for {consumer_task.get_name()}."  # noqa: E501
                    )
                except Exception as sd_exc:
                    logger.error(
                        f"Error during consumer shutdown() call: {sd_exc!r}",
                        exc_info=sd_exc,
                    )

                try:
                    await asyncio.wait_for(consumer_task, timeout=0.5)
                    logger.debug(
                        f"Consumer task {consumer_task.get_name()} finished gracefully."  # noqa: E501
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Consumer task {consumer_task.get_name()} did not exit after shutdown, cancelling."  # noqa: E501
                    )
                    consumer_task.cancel()
                    await asyncio.gather(consumer_task, return_exceptions=True)
                except Exception as task_exc:
                    logger.error(
                        f"Error waiting for consumer task {consumer_task.get_name()} post-shutdown: {task_exc!r}",  # noqa: E501
                        exc_info=task_exc,
                    )

    async def assert_event_published(
        self,
        mock_event_bus: AsyncMock,
        expected_event_type: type[Event],
        expected_attributes: Optional[dict[str, Any]] = None,
        check_call_count: Optional[int] = 1,
    ):
        """
        Helper assertion to check if a specific
        event type was published to the bus.

        Args:
            mock_event_bus: The mocked EventBus instance.
            expected_event_type: The class of the event expected.
            expected_attributes: Optional dict of attributes and
                                 their expected values on the
                                 published event.
            check_call_count:
                            Expected number of times publish was
                            called. Use None to skip count check.
        """
        if check_call_count is not None:
            assert (
                mock_event_bus.publish.call_count == check_call_count
            ), f"Expected EventBus.publish to be called {check_call_count} times, but was called {mock_event_bus.publish.call_count} times."  # noqa: E501

        if check_call_count == 0:
            mock_event_bus.publish.assert_not_awaited()
            return

        mock_event_bus.publish.assert_awaited()

        last_call_args = mock_event_bus.publish.await_args
        assert (
            last_call_args is not None
        ), "EventBus.publish was awaited, but await_args is None."

        published_event = last_call_args[0][0]

        assert isinstance(
            published_event, expected_event_type
        ), f"Expected event of type {expected_event_type.__name__}, but got {type(published_event).__name__}"  # noqa: E501

        if expected_attributes:
            for attr, expected_value in expected_attributes.items():
                assert hasattr(
                    published_event, attr
                ), f"Published event missing attribute '{attr}'"
                actual_value = getattr(published_event, attr)
                assert (
                    actual_value == expected_value
                ), f"Attribute '{attr}' mismatch: Expected '{(expected_value)!r}', Got '{actual_value!r}'"  # noqa: E501

    @pytest.mark.asyncio
    async def test_shutdown_signals_loop_to_exit(
        self,
        consumer_under_test: TConsumer,
    ):
        """
        Verify that calling shutdown() signals
        the consumer's run() loop to exit gracefully.

        NOTE: This test assumes the consumer's run()
        loop checks an internal flag
        (like `self._shutdown_requested.is_set()`)
        and exits cleanly. It also assumes the external
        source mock allows the loop to proceed to check this flag
        (e.g., by returning None or timing out quickly).
        Subclasses may need to adjust their external
        source mock's behavior for this test.
        """

        if hasattr(consumer_under_test, "_logger"):
            consumer_under_test._logger = MagicMock(spec=logging.Logger)

        run_task = asyncio.create_task(consumer_under_test.run())

        await asyncio.sleep(0.05)
        assert (
            not run_task.done()
        ), "Consumer task finished unexpectedly early."  # noqa: E501

        await consumer_under_test.shutdown()

        try:
            await asyncio.wait_for(run_task, timeout=1.0)
        except asyncio.TimeoutError:
            run_task.cancel()
            await asyncio.gather(
                run_task,
                return_exceptions=True,
            )
            pytest.fail(
                "Consumer run() task did not terminate within timeout after shutdown() was called."  # noqa: E501
            )
        except Exception as e:
            pytest.fail(
                f"Consumer task raised an unexpected exception during shutdown test: {e!r}"  # noqa: E501
            )

        assert run_task.done()

        exc: Optional[BaseException] = run_task.exception()
        if exc:
            raise exc

        if hasattr(consumer_under_test, "_logger") and isinstance(
            consumer_under_test._logger, MagicMock
        ):
            consumer_under_test._logger.info.assert_any_call(
                "Requesting shutdown...",
            )
            consumer_under_test._logger.info.assert_any_call(
                "Shutdown requested. Exiting consumer loop."
            )
