import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class Command(abc.ABC):
    """
    Abstract base class for all commands in the CQRS pattern.
    Commands represent an intention to change the system state.
    They should be immutable data structures.
    """
