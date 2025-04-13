"""
Purpose: Defines models for planner functionality.

This file is part of the astrology pillar and serves as a model component.
It provides data structures for planner events and settings.
"""

from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import uuid

from astrology.services.location_service import Location


class EventType(Enum):
    """Types of planner events."""

    MOON_PHASE = "moon_phase"
    PLANETARY_ASPECT = "planetary_aspect"
    RETROGRADE = "retrograde"
    ECLIPSE = "eclipse"
    VENUS_CYCLE = "venus_cycle"
    PLANETARY_PHASE = "planetary_phase"
    USER_EVENT = "user_event"


class PlannerEvent:
    """Planner event model.

    Attributes:
        id: Unique identifier
        title: Event title
        description: Event description
        event_type: Type of event
        start_time: Start time of the event
        end_time: End time of the event (optional)
        all_day: Whether the event is an all-day event
        repeats_yearly: Whether the event repeats yearly
        color: Event color in hex format
        metadata: Additional metadata for the event, which may include:
            - precise_time: The exact astronomical time of the event
            - planet: Planet name for planetary events
            - position: Celestial position in degrees
            - speed: Speed in degrees per day (for retrograde events)
            - other event-specific data
    """

    def __init__(
        self,
        id=None,
        title=None,
        description=None,
        event_type=EventType.USER_EVENT,
        start_time=None,
        end_time=None,
        all_day=False,
        repeats_yearly=False,
        color="#3498db",
        metadata=None,
    ):
        """Initialize a planner event.

        Args:
            id: Unique identifier (default: None, auto-generated)
            title: Event title (default: None)
            description: Event description (default: None)
            event_type: Type of event (default: USER_EVENT)
            start_time: Start time of the event (default: None)
            end_time: End time of the event (default: None)
            all_day: Whether the event is an all-day event (default: False)
            repeats_yearly: Whether the event repeats yearly (default: False)
            color: Event color in hex format (default: "#3498db")
            metadata: Additional metadata for the event (default: None)
        """
        self.id = id if id else str(uuid.uuid4())
        self.title = title
        self.description = description
        self.event_type = event_type
        self.start_time = start_time
        self.end_time = end_time
        self.all_day = all_day
        self.repeats_yearly = repeats_yearly
        self.color = color
        self.metadata = metadata or {}


class PlannerSettings:
    """Settings for the planner.

    Attributes:
        default_event_duration: Default duration for events in minutes
        show_lunar_phases: Whether to show lunar phases
        show_planetary_hours: Whether to show planetary hours
        show_retrogrades: Whether to show retrograde periods
        show_eclipses: Whether to show eclipses
        show_venus_cycles: Whether to show Venus cycles
        default_view: Default view (day or month)
        default_location: Default location for charts
        show_planetary_aspects: Whether to show planetary aspects
    """

    def __init__(
        self,
        default_event_duration=60,
        show_lunar_phases=True,
        show_planetary_hours=True,
        show_retrogrades=True,
        show_eclipses=True,
        show_venus_cycles=True,
        default_view="month",
        default_location=None,
        show_planetary_aspects=True,
    ):
        """Initialize planner settings.

        Args:
            default_event_duration: Default duration for events in minutes (default: 60)
            show_lunar_phases: Whether to show lunar phases (default: True)
            show_planetary_hours: Whether to show planetary hours (default: True)
            show_retrogrades: Whether to show retrograde periods (default: True)
            show_eclipses: Whether to show eclipses (default: True)
            show_venus_cycles: Whether to show Venus cycles (default: True)
            default_view: Default view (default: "month")
            default_location: Default location for charts (default: None)
            show_planetary_aspects: Whether to show planetary aspects (default: True)
        """
        self.default_event_duration = default_event_duration
        self.show_lunar_phases = show_lunar_phases
        self.show_planetary_hours = show_planetary_hours
        self.show_retrogrades = show_retrogrades
        self.show_eclipses = show_eclipses
        self.show_venus_cycles = show_venus_cycles
        self.default_view = default_view
        self.default_location = default_location
        self.show_planetary_aspects = show_planetary_aspects
