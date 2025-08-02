import datetime
from dataclasses import dataclass, field
from typing import Any, Optional

# A unique identifier for a specific projection instance or type
ProjectionId = str


@dataclass
class ProjectionState:
    """
    Represents the state of a projection, typically used to track
    its progress in processing an event stream.
    """

    projection_id: ProjectionId
    # Could be UUID, int, str
    last_processed_event_id: Optional[Any] = None
    last_processed_event_timestamp: Optional[datetime.datetime] = None
    last_updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def update_progress(
        self, event_id: Any, event_timestamp: Optional[datetime.datetime]
    ):
        self.last_processed_event_id = event_id
        if event_timestamp:
            self.last_processed_event_timestamp = event_timestamp
        self.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
