from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, select

TSQLModel = TypeVar("TSQLModel", bound=SQLModel)


class _BaseRepository(Generic[TSQLModel]):
    """
    A non-instantiable base for repositories, holding common initialization.

    This class can be instantiated directly for a specific model:
        `user_repo = ModelRepository(User)`
    or extended to add model-specific query methods:
        `class UserRepository(ModelRepository[User]): ...`
    """

    def __init__(self, model: Type[TSQLModel]):
        """
        Initializes the repository for a specific SQLModel.

        Args:
            model: The SQLModel to manage in repository.
        """
        if not model or not issubclass(model, SQLModel):
            raise ValueError(
                "The 'model' parameter must be a SQLModel subclass.",
            )
        self.model = model


class ModelRepository(_BaseRepository[TSQLModel]):
    """
    A generic base repository class providing CRUD operations for a SQLModel model.
    """

    def get_all(
        self,
        session: Session,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[TSQLModel]:
        """
        Retrieves a list of model instances
        with optional filtering, offset, and limit.

        Args:
            session: The SQLAlchemy Session.
            offset: The number of records to skip. Defaults to 0.
            limit: The maximum number of records to return.
                    Defaults to 100.
            filters: A dictionary of attribute names and values
                    to filter by. Filters are applied using
                    simple equality (==).
                    Example: `{'is_active': True, 'role': 'admin'}`

        Returns:
            A list of model instances matching the criteria.
        """
        statement = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    statement = statement.where(
                        getattr(self.model, key) == value,
                    )

        statement = statement.offset(offset).limit(limit)
        results = session.execute(statement).scalars().all()
        return list(results)

    def get_by_id(self, session: Session, docid: Any) -> Optional[TSQLModel]:
        """
        Retrieves a single model instance by its primary key.

        Uses `session.get` for efficiency when fetching by primary key.

        Args:
            session: The SQLAlchemy Session.
            docid: The primary key value of the instance to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        doc = session.get(self.model, docid)
        return doc

    def create(self, session: Session, doc_data: TSQLModel) -> TSQLModel:
        """
        Creates a new model instance in the database.

        Args:
            session: The SQLAlchemy Session.
            doc_data: The SQLModel instance containing
                      the data for the new record.
                      Must be an instance of the
                      model type this repository manages.

        Returns:
            The newly created and refreshed model instance.
        """
        # Ensure the input is of the correct model type if needed,
        # though type hints should guide this.
        # if not isinstance(doc_data, self.model):
        #     raise TypeError(f"Input must be of type {self.model.__name__}")

        session.add(doc_data)
        session.commit()
        # Refresh to get any database-generated defaults or state
        session.refresh(doc_data)
        # The instance 'doc_data' is now the persisted and refreshed object
        return doc_data

    def delete_by_id(
        self,
        session: Session,
        docid: Any,
    ) -> Optional[TSQLModel]:
        """
        Deletes a model instance by its primary key.

        Args:
            session: The SQLAlchemy Session.
            docid: The primary key value of the instance to delete.

        Returns:
            The deleted model instance if found and deleted, otherwise None.
        """
        doc = session.get(self.model, docid)
        if not doc:
            return None

        session.delete(doc)
        session.commit()
        return doc

    def update(
        self, session: Session, docid: Any, update_data: Dict[str, Any]
    ) -> Optional[TSQLModel]:
        """
        Updates an existing model instance by its primary key.
        It first fetches the instance, then updates its fields
        with the provided data.

        Args:
            session: The SQLAlchemy Session.
            docid: The primary key of the instance to update.
            update_data: A dictionary containing the fields to update
                         and their new values.

        Returns:
            The updated and refreshed model instance.
            Returns None if the instance with the given ID is not found.
        """
        db_doc = session.get(self.model, docid)
        if not db_doc:
            return None

        for key, value in update_data.items():
            if hasattr(db_doc, key):
                setattr(db_doc, key, value)
            else:
                # Optionally, log a warning or raise an error for unknown fields
                # logger.warning(f"Field '{key}' not found in model '{self.model.__name__}' during update.")
                pass

        session.commit()
        session.refresh(db_doc)
        return db_doc


class AsyncModelRepository(_BaseRepository[TSQLModel]):
    """
    A generic asynchronous base repository
    class providing CRUD operations
    for a SQLModel model using AsyncSession.

    This class can be instantiated directly for a specific model:
        `user_repo = AsyncModelRepository(User)`
    or extended to add model-specific query methods:
        `class UserAsyncRepository(AsyncModelRepository[User]): ...`
    """

    async def get_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[TSQLModel]:
        """
        Asynchronously retrieves a list of model instances
        with optional filtering, offset, and limit.

        Args:
            session: The SQLAlchemy AsyncSession.
            offset: The number of records to skip. Defaults to 0.
            limit: The maximum number of records to return.
                    Defaults to 100.
            filters: A dictionary of attribute names and
                     values to filter by.
                     Filters are applied using
                     simple equality (==).
                     Example: `{'is_active': True, 'role': 'admin'}`

        Returns:
            A list of model instances matching the criteria.
        """
        statement = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    statement = statement.where(
                        getattr(self.model, key) == value,
                    )

        statement = statement.offset(offset).limit(limit)
        result = await session.execute(statement)
        instances = result.scalars().all()
        return list(instances)

    async def get_by_id(
        self,
        session: AsyncSession,
        docid: Any,
    ) -> Optional[TSQLModel]:
        """
        Asynchronously retrieves a single model instance by its primary key.

        Uses `session.get` for efficiency when fetching by primary key.

        Args:
            session: The SQLAlchemy AsyncSession.
            docid: The primary key value of the instance to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        doc = await session.get(self.model, docid)
        return doc

    async def create(
        self,
        session: AsyncSession,
        doc_data: TSQLModel,
    ) -> TSQLModel:
        """
        Asynchronously creates a new model instance in the database.

        Args:
            session: The SQLAlchemy AsyncSession.
            doc_data: The SQLModel instance containing
                      the data for the new record.
                      Must be an instance of the model
                      type this repository manages.

        Returns:
            The newly created and refreshed model instance.
        """
        session.add(doc_data)
        await session.commit()
        await session.refresh(doc_data)
        return doc_data

    async def delete_by_id(
        self, session: AsyncSession, docid: Any
    ) -> Optional[TSQLModel]:
        """
        Asynchronously deletes a model instance by its primary key.

        Args:
            session: The SQLAlchemy AsyncSession.
            docid: The primary key value of the instance to delete.

        Returns:
            The deleted model instance if found and deleted, otherwise None.
        """
        doc = await session.get(self.model, docid)
        if not doc:
            return None

        await session.delete(doc)
        await session.commit()
        # The 'doc' object is expired after deletion, but we return it
        # as it was just before deletion.
        return doc

    async def update(
        self, session: AsyncSession, docid: Any, update_data: Dict[str, Any]
    ) -> Optional[TSQLModel]:
        """
        Asynchronously updates an existing model instance by its primary key.
        It first fetches the instance, then updates its fields
        with the provided data.

        Args:
            session: The SQLAlchemy AsyncSession.
            docid: The primary key of the instance to update.
            update_data: A dictionary containing the fields to update
                         and their new values.

        Returns:
            The updated and refreshed model instance.
            Returns None if the instance with the given ID is not found.
        """
        db_doc = await session.get(self.model, docid)
        if not db_doc:
            return None

        for key, value in update_data.items():
            if hasattr(db_doc, key):
                setattr(db_doc, key, value)
            else:
                pass  # Optionally log warning for unknown fields

        await session.commit()
        await session.refresh(db_doc)
        return db_doc
