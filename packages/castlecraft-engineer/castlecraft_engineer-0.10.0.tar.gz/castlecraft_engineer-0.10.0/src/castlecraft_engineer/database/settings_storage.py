from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlmodel import Field, SQLModel, Text, delete, select


class Singles(SQLModel, table=True):
    __tablename__ = "singles"

    singles_name: Optional[str] = Field(default=None, primary_key=True)
    field: Optional[str] = Field(default=None, primary_key=True)
    value: Optional[str] = Field(
        default=None,
        sa_type=Text,
    )


class SinglesBase(BaseModel):
    @property
    def singles_name(self):
        return self.__class__.__name__

    def get_array_fields(self) -> dict[str, Type[SQLModel]]:
        """
        Returns a dictionary of field names that are arrays
        and their corresponding SQLModel types for querying.
        Example: {"my_array_field": MyArrayTableModel}
        Override in subclasses if array fields are present.
        """
        return {}


TSingles = TypeVar("TSingles", bound=SinglesBase)


def get_array_fields(meta: TSingles) -> dict[str, Type[SQLModel]]:
    try:
        return meta.get_array_fields()
    except AttributeError:
        return {}


def get_singles(meta: TSingles, session: Session) -> dict[str, Any]:
    statement = select(Singles).where(Singles.singles_name == meta.singles_name)
    array_fields = get_array_fields(meta)
    results = session.execute(statement)
    settings: dict[str, Any] = dict(singles_name=meta.singles_name)

    for field_name, model_type in array_fields.items():
        array_statement = select(
            model_type
        )  # Query the specific model type for the array
        settings[field_name] = session.execute(array_statement).scalars().all()

    for single in results.scalars().all():
        if single.field is not None:
            settings[single.field] = single.value
    return settings


def delete_singles(meta: SinglesBase, session: Session):
    statement = delete(Singles).where(Singles.singles_name == meta.singles_name)
    session.execute(statement)
    session.commit()


def save_singles(doc: SinglesBase, session: Session):
    fields = doc.model_dump()
    singles_name_val = doc.singles_name
    array_field_definitions = doc.get_array_fields()

    for key, value in fields.items():
        # Skip array fields as they are typically handled by separate tables/logic
        if key in array_field_definitions:
            continue

        statement = select(Singles).where(
            Singles.singles_name == singles_name_val,
            Singles.field == key,
        )
        results = session.execute(statement)
        single_record = results.scalar_one_or_none()

        current_value_str: Optional[str] = None
        if value is not None:
            current_value_str = str(value)

        if single_record:
            if single_record.value != current_value_str:  # Only update if value changed
                single_record.value = current_value_str
                session.add(single_record)
        elif (
            current_value_str is not None
        ):  # Only create if there's a non-None value to save
            single_record = Singles(
                singles_name=singles_name_val,
                field=key,
                value=current_value_str,
            )
            session.add(single_record)
        # If single_record is None and current_value_str is None, do nothing.

    session.commit()  # Commit once after processing all fields


def set_singles_value(
    session: Session,
    settings_cls: Type[TSingles],
    field: str,
    value: str,
):
    statement = select(Singles).where(
        Singles.singles_name == settings_cls.__name__, Singles.field == field
    )
    results = session.execute(statement)
    single_setting = results.scalar_one_or_none()
    if single_setting:
        single_setting.value = value
    else:
        single_setting = Singles(
            singles_name=settings_cls.__name__,
            field=field,
            value=value,
        )
    session.add(single_setting)
    session.commit()
    session.refresh(single_setting)
