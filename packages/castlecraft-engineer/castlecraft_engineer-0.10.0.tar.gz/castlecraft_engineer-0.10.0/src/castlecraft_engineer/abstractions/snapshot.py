from dataclasses import dataclass
from typing import Any, Generic

from castlecraft_engineer.abstractions.aggregate import TAggregateId


@dataclass(frozen=True)
class Snapshot(Generic[TAggregateId]):
    aggregate_id: TAggregateId
    aggregate_state: Any  # The serialized state of the aggregate
    version: (
        int  # The version of the aggregate after the last event included in this state
    )
