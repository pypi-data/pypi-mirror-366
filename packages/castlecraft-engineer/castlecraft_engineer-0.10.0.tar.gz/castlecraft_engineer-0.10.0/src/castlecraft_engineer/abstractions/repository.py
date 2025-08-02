import logging
from typing import (
    Any,
    Generic,
    Optional,
    Type,
    TypeVar,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from sqlmodel import SQLModel

from .aggregate import Aggregate, TAggregateId

# Type variables for repository generics
TSQLModel = TypeVar("TSQLModel", bound=SQLModel)
TAggregate = TypeVar("TAggregate", bound=Aggregate)


# Custom Exceptions
class RepositoryError(Exception):
    """Base repository error."""


class AggregateNotFoundError(RepositoryError):
    """Aggregate not found."""

    def __init__(self, aggregate_id: Any):
        super().__init__(f"Aggregate ID '{aggregate_id}' not found.")
        self.aggregate_id = aggregate_id


class OptimisticConcurrencyError(RepositoryError, StaleDataError):
    """Optimistic concurrency conflict."""

    def __init__(
        self,
        aggregate_id: Any,
        expected_version: int,
        actual_version: Optional[int] = None,
    ):
        msg = (
            f"Concurrency error for ID '{aggregate_id}'. "
            f"Expected version {expected_version}, "
            f"but found version {actual_version} in database."
        )
        super().__init__(msg)
        self.aggregate_id = aggregate_id
        self.expected_version = expected_version
        self.actual_version = actual_version


class _RepositoryBase(Generic[TAggregateId, TAggregate, TSQLModel]):
    def __init__(
        self,
        aggregate_cls: Type[TAggregate],
        model_cls: Type[TSQLModel],
    ):
        if not issubclass(aggregate_cls, Aggregate):
            raise ValueError("aggregate_cls must be an Aggregate subclass.")
        if not issubclass(model_cls, SQLModel):
            raise ValueError("model_cls must be an SQLModel subclass.")
        if "id" not in model_cls.model_fields:
            raise TypeError(
                f"{model_cls.__name__} needs an 'id' attribute defined as a model field."  # noqa: E501
            )
        if "version" not in model_cls.model_fields:
            raise TypeError(
                f"{model_cls.__name__} needs a 'version' attribute defined as a model field for optimistic concurrency."  # noqa: E501
            )

        self.aggregate_cls = aggregate_cls
        self.model_cls = model_cls
        self._logger = logging.getLogger(
            f"{self.__class__.__name__}[{self.aggregate_cls.__name__}]"
        )
        self._logger.debug(
            f"Initialized for Aggregate: {self.aggregate_cls.__name__}, Root Model: {self.model_cls.__name__}"  # noqa: E501
        )

    def _map_model_to_aggregate(self, model_instance: TSQLModel) -> TAggregate:
        """
        Maps the root SQLModel (and potentially its loaded relationships)
        to the Aggregate instance.

        **Override this method** in a subclass for complex Aggregates
        that involve specific logic to map data from multiple related models
        into the Aggregate's structure.

        The default implementation assumes a direct mapping of fields
        from the root model to the aggregate.
        """
        self._logger.debug(
            f"Mapping {self.model_cls.__name__} -> {self.aggregate_cls.__name__} (ID: {getattr(model_instance, 'id', 'N/A')})"  # noqa: E501
        )
        try:
            agg_id = getattr(model_instance, "id", None)
            agg_version = getattr(model_instance, "version", None)

            if agg_id is None:
                raise ValueError(
                    f"Model instance of {self.model_cls.__name__} is missing 'id'."  # noqa: E501
                )
            if agg_version is None:
                raise ValueError(
                    f"Model instance of {self.model_cls.__name__} is missing 'version'."  # noqa: E501
                )

            agg = self.aggregate_cls(id=agg_id, version=agg_version)

            model_fields = self.model_cls.model_fields.keys()
            for field in model_fields:
                if field not in ("id", "version") and hasattr(agg, field):
                    try:
                        value = getattr(model_instance, field)
                        setattr(agg, field, value)
                        self._logger.debug(f"  Mapped field '{field}'")
                    except Exception as field_e:
                        self._logger.warning(
                            f"  Failed to map field '{field}': {field_e!s}"
                        )
            self._logger.debug(
                f"Finished mapping model to Aggregate (Version: {agg.version})"
            )
            return agg
        except Exception as e:
            self._logger.error(
                f"Default Model->Aggregate mapping failed: {e!s}",
                exc_info=True,
            )
            raise RepositoryError(
                f"Failed to map model {self.model_cls.__name__} to aggregate {self.aggregate_cls.__name__}: {e!s}"  # noqa: E501
            ) from e

    def _map_aggregate_to_model(
        self, aggregate: TAggregate, model_instance: TSQLModel
    ) -> None:
        """
        Updates the state of the root SQLModel instance (and potentially its
        related models managed by the ORM) based on the Aggregate's state.

        **Override this method** in a subclass for complex Aggregates
        to handle mapping the Aggregate's state (including child entities
        or value objects) back to the corresponding SQLModel instances.

        The default implementation maps fields from the aggregate directly
        onto the provided root model instance. It assumes that changes to
        related objects within the aggregate will be detected and handled
        by the SQLAlchemy Unit of Work upon session flush,
        provided relationships
        and cascades are correctly configured on the SQLModels.

        Args:
            aggregate: The source Aggregate instance.
            model_instance: The target SQLModel instance to update.
        """
        self._logger.debug(
            f"Mapping {self.aggregate_cls.__name__} -> {self.model_cls.__name__} (ID: {aggregate.id})"  # noqa: E501
        )
        try:
            aggregate_state = aggregate.__dict__
            model_fields = self.model_cls.model_fields.keys()

            for field_name, agg_value in aggregate_state.items():
                # Skip private/internal aggregate attributes and id/version
                if field_name.startswith("_") or field_name in (
                    "id",
                    "version",
                ):
                    continue

                if field_name in model_fields:
                    try:
                        # Directly set the attribute on the model instance
                        setattr(model_instance, field_name, agg_value)
                        self._logger.debug(
                            f"  Updated model field '{field_name}'",
                        )
                    except Exception as field_e:
                        self._logger.warning(  # noqa: E501
                            f"  Failed to update model field '{field_name}': {field_e!s}"  # noqa: E501
                        )

            self._logger.debug("Finished mapping Aggregate to model")

        except Exception as e:
            self._logger.error(
                f"Default Aggregate->Model mapping failed: {e!s}",
                exc_info=True,
            )
            raise RepositoryError(
                f"Failed to map aggregate {self.aggregate_cls.__name__} to model {self.model_cls.__name__}: {e!s}"  # noqa: E501
            ) from e


class AggregateRepository(
    _RepositoryBase[
        TAggregateId,
        TAggregate,
        TSQLModel,
    ],
):
    """
    Generic repository mapping Aggregates to SQLModels.

    Handles persistence for Aggregates, potentially spanning multiple
    related SQLModels if relationships and cascades are configured
    correctly on the SQLModel classes themselves.

    Relies on the SQLAlchemy Unit of Work pattern managed outside
    the repository (e.g., in a Command Handler or Application Service).
    """

    def __init__(
        self,
        aggregate_cls: Type[TAggregate],
        model_cls: Type[TSQLModel],
    ):
        super().__init__(aggregate_cls, model_cls)

    def get_by_id(
        self,
        session: Session,
        id: TAggregateId,
    ) -> Optional[TAggregate]:
        """
        Retrieves an Aggregate by its ID.
        Loads the root model and relies on ORM relationship loading
        (eager or lazy) for related data.
        """
        self._logger.debug(f"Getting aggregate by ID: {id}")
        model = session.get(self.model_cls, id)
        if not model:
            self._logger.warning(
                f"Aggregate ID {id} not found in database for root model {self.model_cls.__name__}."  # noqa: E501
            )
            return None

        self._logger.debug(
            f"Found root model for ID {id}. Mapping to aggregate.",
        )
        return self._map_model_to_aggregate(model)

    def save(self, session: Session, aggregate: TAggregate) -> TAggregate:
        """
        Persists Aggregate state (handles create or update).

        Relies on the provided session being managed externally (Unit of Work).
        Adds new aggregates to the session or updates existing ones.
        Handles optimistic concurrency checking based on the 'version' field
        of the root model.

        For updates involving related models (multiple tables), ensure
        SQLModel relationships and cascade options are correctly configured.
        The mapping logic (`_map_aggregate_to_model`) should update the
        state of the model instances, and the SQLAlchemy session flush
        will handle persisting those changes.
        """
        if not isinstance(aggregate, self.aggregate_cls):
            raise TypeError(
                f"Input must be an instance of {self.aggregate_cls.__name__}, got {type(aggregate).__name__}"  # noqa: E501
            )

        agg_id = aggregate.id
        current_agg_version = aggregate.version
        is_new = current_agg_version == -1

        self._logger.debug(
            f"Attempting to save aggregate ID: {agg_id}, Current Aggregate Version: {current_agg_version}, Is New: {is_new}"  # noqa: E501
        )

        model: Optional[TSQLModel] = None  # Declare model once with its optional type
        try:
            if is_new:
                self._logger.debug(
                    f"Aggregate ID {agg_id} is new. Preparing data for new root model."
                )
                # Prepare data for model creation from the aggregate
                model_init_data = {"id": agg_id, "version": -1}

                aggregate_state = aggregate.__dict__
                for field_name, agg_value in aggregate_state.items():
                    # Skip private/internal aggregate attributes and id/version
                    if field_name.startswith("_") or field_name in (
                        "id",
                        "version",
                    ):
                        continue
                    # Only include fields that are actual model fields
                    if field_name in self.model_cls.model_fields:
                        model_init_data[field_name] = agg_value

                self._logger.debug(
                    f"Final model_init_data for new aggregate: {model_init_data}"
                )
                model = self.model_cls(**model_init_data)

                session.add(model)
                aggregate._increment_version()
                model.version = aggregate.version
                self._logger.info(
                    f"Added new aggregate ID: {agg_id} to session with version {aggregate.version}. Commit required externally."  # noqa: E501
                )
            else:
                self._logger.debug(
                    f"Aggregate ID {agg_id} exists. Loading root model for update."  # noqa: E501
                )
                model = session.get(self.model_cls, agg_id)

                if not model:
                    self._logger.error(
                        f"Aggregate ID {agg_id} not found in database during update attempt."  # noqa: E501
                    )
                    raise AggregateNotFoundError(agg_id)

                db_version = getattr(model, "version", None)
                if db_version is None:
                    raise RepositoryError(
                        f"Database model {self.model_cls.__name__} for ID {agg_id} is missing 'version'. Cannot perform optimistic lock."  # noqa: E501
                    )

                if db_version != current_agg_version:
                    self._logger.warning(
                        f"Optimistic lock failed for ID: {agg_id}. Expected DB version {current_agg_version}, found {db_version}."  # noqa: E501
                    )
                    raise OptimisticConcurrencyError(
                        agg_id, current_agg_version, db_version
                    )
                self._logger.debug(
                    f"Optimistic lock check passed for ID {agg_id} (Version: {current_agg_version})."  # noqa: E501
                )

                self._map_aggregate_to_model(aggregate, model)
                aggregate._increment_version()
                model.version = aggregate.version
                self._logger.info(
                    f"Updated aggregate ID: {agg_id} in session to version {aggregate.version}. Commit required externally."  # noqa: E501
                )
            return aggregate

        except (OptimisticConcurrencyError, AggregateNotFoundError) as e:
            self._logger.error(f"Save failed for aggregate ID {agg_id}: {e!s}")
            raise e
        except Exception as e:
            self._logger.exception(
                f"Unexpected error during save for aggregate ID {agg_id}: {e!s}"  # noqa: E501
            )
            raise RepositoryError(
                f"Save failed for aggregate ID {agg_id}: {e!s}"
            ) from e

    def delete_by_id(self, session: Session, id: TAggregateId) -> bool:
        """
        Deletes an Aggregate by its ID.
        Relies on the ORM's cascade delete configuration for related models.
        """
        self._logger.debug(f"Attempting to delete aggregate ID: {id}")
        model = session.get(self.model_cls, id)
        if not model:
            self._logger.warning(f"Aggregate ID: {id} not found for deletion.")
            return False

        try:
            session.delete(model)
            self._logger.info(
                f"Marked aggregate ID: {id} for deletion in session. Commit required externally."  # noqa: E501
            )
            return True
        except Exception as e:
            self._logger.exception(
                f"Delete failed for aggregate ID {id}: {e!s}",
            )
            raise RepositoryError(f"Delete failed for {id}: {e!s}") from e


class AsyncAggregateRepository(
    _RepositoryBase[
        TAggregateId,
        TAggregate,
        TSQLModel,
    ],
):
    """
    Generic asynchronous repository mapping
    Aggregates to SQLModels using AsyncSession.
    """

    def __init__(
        self,
        aggregate_cls: Type[TAggregate],
        model_cls: Type[TSQLModel],
    ):
        super().__init__(aggregate_cls, model_cls)

    # _map_model_to_aggregate and _map_aggregate_to_model are inherited

    async def get_by_id(
        self,
        session: AsyncSession,
        id: TAggregateId,
    ) -> Optional[TAggregate]:
        """
        Asynchronously retrieves an Aggregate by its ID using AsyncSession.
        """
        self._logger.debug(f"Getting aggregate by ID: {id}")
        model: Optional[TSQLModel] = await session.get(self.model_cls, id)
        if not model:
            self._logger.warning(
                f"Aggregate ID {id} not found in database for root model {self.model_cls.__name__}."  # noqa: 501
            )
            return None

        self._logger.debug(
            f"Found root model for ID {id}. Mapping to aggregate.",
        )
        return self._map_model_to_aggregate(model)

    async def save(
        self,
        session: AsyncSession,
        aggregate: TAggregate,
    ) -> TAggregate:
        """
        Asynchronously persists Aggregate state using AsyncSession.
        """
        if not isinstance(aggregate, self.aggregate_cls):
            raise TypeError(
                f"Input must be an instance of {self.aggregate_cls.__name__}, got {type(aggregate).__name__}"  # noqa: 501
            )

        agg_id = aggregate.id
        current_agg_version = aggregate.version
        is_new = current_agg_version == -1

        self._logger.debug(
            f"Attempting to save aggregate ID: {agg_id}, Current Aggregate Version: {current_agg_version}, Is New: {is_new}"  # noqa: 501
        )

        model: Optional[TSQLModel] = None  # Declare model once with its optional type
        try:
            if is_new:
                self._logger.debug(
                    f"Aggregate ID {agg_id} is new. Preparing data for new root model."
                )
                # Prepare data for model creation from the aggregate
                model_init_data = {"id": agg_id, "version": -1}

                aggregate_state = aggregate.__dict__
                for field_name, agg_value in aggregate_state.items():
                    # Skip private/internal aggregate attributes and id/version
                    if field_name.startswith("_") or field_name in (
                        "id",
                        "version",
                    ):
                        continue
                    # Only include fields that are actual model fields
                    if field_name in self.model_cls.model_fields:
                        model_init_data[field_name] = agg_value

                self._logger.debug(
                    f"Final model_init_data for new aggregate: {model_init_data}"
                )
                model = self.model_cls(**model_init_data)

                session.add(model)
                aggregate._increment_version()
                model.version = aggregate.version
                self._logger.info(
                    f"Added new aggregate ID: {agg_id} to session with version {aggregate.version}. Commit required externally."  # noqa: 501
                )
            else:
                self._logger.debug(
                    f"Aggregate ID {agg_id} exists. Loading root model for update."  # noqa: E501
                )
                model = await session.get(self.model_cls, agg_id)

                if not model:
                    self._logger.error(
                        f"Aggregate ID {agg_id} not found in database during update attempt."  # noqa: 501
                    )
                    raise AggregateNotFoundError(agg_id)

                db_version = getattr(model, "version", None)
                if db_version is None:
                    raise RepositoryError(
                        f"Database model {self.model_cls.__name__} for ID {agg_id} is missing 'version'. Cannot perform optimistic lock."  # noqa: 501
                    )

                if db_version != current_agg_version:
                    self._logger.warning(
                        f"Optimistic lock failed for ID: {agg_id}. Expected DB version {current_agg_version}, found {db_version}."  # noqa: 501
                    )
                    raise OptimisticConcurrencyError(
                        agg_id, current_agg_version, db_version
                    )
                self._logger.debug(
                    f"Optimistic lock check passed for ID {agg_id} (Version: {current_agg_version})."  # noqa: 501
                )

                self._map_aggregate_to_model(aggregate, model)
                aggregate._increment_version()
                model.version = aggregate.version

                self._logger.info(
                    f"Updated aggregate ID: {agg_id} in session to version {aggregate.version}. Commit required externally."  # noqa: 501
                )
            return aggregate

        except (OptimisticConcurrencyError, AggregateNotFoundError) as e:
            self._logger.error(f"Save failed for aggregate ID {agg_id}: {e!s}")
            raise e
        except Exception as e:
            self._logger.exception(
                f"Unexpected error during save for aggregate ID {agg_id}: {e!s}"  # noqa: 501
            )
            raise RepositoryError(
                f"Save failed for aggregate ID {agg_id}: {e!s}"
            ) from e

    async def delete_by_id(
        self,
        session: AsyncSession,
        id: TAggregateId,
    ) -> bool:
        """
        Asynchronously deletes an Aggregate by its ID using AsyncSession.
        """
        self._logger.debug(f"Attempting to delete aggregate ID: {id}")
        model: Optional[TSQLModel] = await session.get(self.model_cls, id)
        if not model:
            self._logger.warning(f"Aggregate ID: {id} not found for deletion.")
            return False

        try:
            # For async, session.delete is synchronous, flush/commit is async
            # However, SQLModel/SQLAlchemy handles this correctly.
            # The actual delete operation is usually part of the flush.
            await session.delete(model)  # This marks the object for deletion.
            self._logger.info(
                f"Marked aggregate ID: {id} for deletion in session. Commit/flush required externally."  # noqa: 501
            )
            return True
        except Exception as e:
            self._logger.exception(
                f"Delete failed for aggregate ID {id}: {e!s}",
            )
            raise RepositoryError(f"Delete failed for {id}: {e!s}") from e
