import enum


class BaseStringEnum(str, enum.Enum):
    """Base class for string-based enums to ensure string representation."""

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class Action(BaseStringEnum):
    """Common actions. Extendable by creating new enums."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"


class Resource(BaseStringEnum):
    """Common resource types. Extendable by creating new enums."""

    # Add common resources if any, or leave empty for extension
    GENERIC = "generic"


class Scope(BaseStringEnum):
    """
    Common scopes. Extendable by creating new enums.
    """

    ANY = "any"
    OWN = "own"
