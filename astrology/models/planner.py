"""
Models for the astrological planner.
"""

from datetime import datetime
from enum import Enum, auto
from typing import Optional
from pydantic import BaseModel, Field

class EventType(Enum):
    """Type of astrological event."""
    MOON_PHASE = auto()
    VOID_OF_COURSE = auto()
    PLANETARY_ASPECT = auto()
    RETROGRADE = auto()
    ECLIPSE = auto()
    SPIRITUAL_PRACTICE = auto()
    REPEATING_EVENT = auto()
    VENUS_CYCLE = auto()
    CUSTOM = auto()

class PlannerEvent(BaseModel):
    """Astrological planner event."""
    id: str = Field(default_factory=lambda: str(hash(datetime.now())))
    title: str
    description: str = ""
    event_type: EventType
    start_time: datetime
    end_time: Optional[datetime] = None
    color: str = "#000000"  # Default to black
    
    class Config:
        arbitrary_types_allowed = True
