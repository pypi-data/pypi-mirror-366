import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class Query(abc.ABC):
    """
    Abstract base class for all Queries in the CQRS pattern.
    Query represent an intention to request the system state.
    They should be immutable data structures.
    """
