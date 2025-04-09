"""
Purpose: Provides services for the astrological daily planner.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to calculate astrological events for specific dates,
including moon phases, void-of-course periods, planetary aspects, retrograde
periods, eclipses, and Venus cycles.

Key components:
- PlannerService: Service for astrological daily planner calculations
- PlannerEvent: Data model for astrological events
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from astrology.models.chart import Chart

# Import our models
from astrology.models.planner import EventType, PlannerEvent
from astrology.services.chart_service import ChartService
from astrology.services.location_service import Location, LocationService

# Import our astronomical moon phase calculator
from astrology.services.moon_phase_calculator import calculate_moon_phases_for_month

# EventType and PlannerEvent are now imported from astrology.models.planner


class PlannerSettings(BaseModel):
    """Model for planner settings."""

    default_location: Optional[Location] = None
    default_view: str = "month"  # "month" or "day"


class PlannerService:
    """Service for astrological daily planner calculations."""

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the planner service."""
        # Get other services
        self.chart_service = ChartService.get_instance()
        self.location_service = LocationService.get_instance()

        # Initialize events storage
        self.events_file = os.path.join(
            os.path.expanduser("~"), ".isopgem", "planner_events.json"
        )
        self.settings_file = os.path.join(
            os.path.expanduser("~"), ".isopgem", "planner_settings.json"
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.events_file), exist_ok=True)

        # Load events and settings
        self.events = self._load_events()
        self.settings = self._load_settings()

        logger.debug("PlannerService initialized")

    def _load_events(self) -> Dict[str, List[PlannerEvent]]:
        """Load events from file.

        Returns:
            Dictionary of events by date
        """
        if not os.path.exists(self.events_file):
            return {}

        try:
            with open(self.events_file, "r") as f:
                data = json.load(f)

            # Convert to PlannerEvent objects
            events = {}
            for date_str, event_list in data.items():
                # Process each event to handle potential string enum values
                processed_events = []
                for event_data in event_list:
                    # Check if event_type is a string and convert it to the proper enum value
                    if "event_type" in event_data and isinstance(
                        event_data["event_type"], str
                    ):
                        # Handle the case where event_type is stored as 'EventType.USER_EVENT'
                        if event_data["event_type"].startswith("EventType."):
                            enum_name = event_data["event_type"].split(".")[1]
                            try:
                                event_data["event_type"] = EventType[enum_name]
                            except KeyError:
                                # If the enum name doesn't exist, default to USER_EVENT
                                logger.warning(
                                    f"Unknown event type: {event_data['event_type']}, defaulting to USER_EVENT"
                                )
                                event_data["event_type"] = EventType.USER_EVENT

                    # Create the PlannerEvent object
                    try:
                        processed_events.append(PlannerEvent(**event_data))
                    except Exception as e:
                        logger.warning(
                            f"Error processing event: {e}. Event data: {event_data}"
                        )

                events[date_str] = processed_events

            logger.debug(
                f"Loaded {sum(len(events) for events in events.values())} events from {self.events_file}"
            )
            return events

        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return {}

    def _save_events(self) -> bool:
        """Save events to file.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to serializable format
            data = {}
            for date_str, event_list in self.events.items():
                # Process each event to ensure event_type is saved as an integer
                serialized_events = []
                for event in event_list:
                    # Get the event data
                    event_data = event.model_dump()

                    # Ensure event_type is saved as an integer
                    if "event_type" in event_data and hasattr(
                        event_data["event_type"], "value"
                    ):
                        event_data["event_type"] = event_data["event_type"].value

                    serialized_events.append(event_data)

                data[date_str] = serialized_events

            with open(self.events_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug(
                f"Saved {sum(len(events) for events in self.events.values())} events to {self.events_file}"
            )
            return True

        except Exception as e:
            logger.error(f"Error saving events: {e}")
            return False

    def _load_settings(self) -> PlannerSettings:
        """Load settings from file.

        Returns:
            PlannerSettings object
        """
        if not os.path.exists(self.settings_file):
            return PlannerSettings()

        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)

            # Convert to PlannerSettings object
            settings = PlannerSettings(**data)

            logger.debug(f"Loaded settings from {self.settings_file}")
            return settings

        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return PlannerSettings()

    def _save_settings(self) -> bool:
        """Save settings to file.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to serializable format
            data = self.settings.model_dump()

            with open(self.settings_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug(f"Saved settings to {self.settings_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def save_event(self, event: PlannerEvent) -> bool:
        """Save an event.

        Args:
            event: Event to save

        Returns:
            True if successful, False otherwise
        """
        # Get date string
        date_str = event.start_time.strftime("%Y-%m-%d")

        # Add to events
        if date_str not in self.events:
            self.events[date_str] = []

        # Check if event already exists
        for i, existing_event in enumerate(self.events[date_str]):
            if existing_event.id == event.id:
                # Update existing event
                self.events[date_str][i] = event
                return self._save_events()

        # Add new event
        self.events[date_str].append(event)

        # Save events
        return self._save_events()

    def delete_event(self, event_id: str) -> bool:
        """Delete an event.

        Args:
            event_id: ID of the event to delete

        Returns:
            True if successful, False otherwise
        """
        # Find and delete the event
        for date_str, event_list in self.events.items():
            for i, event in enumerate(event_list):
                if event.id == event_id:
                    # Remove the event
                    self.events[date_str].pop(i)

                    # Remove empty date entries
                    if not self.events[date_str]:
                        del self.events[date_str]

                    # Save events
                    return self._save_events()

        # Event not found
        logger.warning(f"Event {event_id} not found for deletion")
        return False

    def get_events_for_date(self, date: datetime.date) -> List[PlannerEvent]:
        """Get events for a specific date.

        Args:
            date: Date to get events for

        Returns:
            List of events for the date
        """
        # Get date string
        date_str = date.strftime("%Y-%m-%d")

        # Get events for the date
        events = self.events.get(date_str, [])

        # Add yearly repeating events
        for date_str, event_list in self.events.items():
            for event in event_list:
                if (
                    event.repeats_yearly
                    and event.start_time.month == date.month
                    and event.start_time.day == date.day
                ):
                    # Create a copy of the event with the current year
                    new_event = event.model_copy()
                    new_event.start_time = datetime.combine(
                        date, event.start_time.time()
                    )
                    if event.end_time:
                        new_event.end_time = datetime.combine(
                            date, event.end_time.time()
                        )

                    events.append(new_event)

        return events

    def get_events_for_month(
        self, year: int, month: int
    ) -> Dict[int, List[PlannerEvent]]:
        """Get events for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Dictionary of events by day of month
        """
        # Get all days in the month
        first_day = datetime(year, month, 1).date()
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

        # Get events for each day
        events_by_day = {}
        current_day = first_day
        while current_day <= last_day:
            events_by_day[current_day.day] = self.get_events_for_date(current_day)
            current_day += timedelta(days=1)

        return events_by_day

    def save_settings(self, settings: PlannerSettings) -> bool:
        """Save settings.

        Args:
            settings: Settings to save

        Returns:
            True if successful, False otherwise
        """
        self.settings = settings
        return self._save_settings()

    def get_settings(self) -> PlannerSettings:
        """Get settings.

        Returns:
            PlannerSettings object
        """
        return self.settings

    def _get_zodiac_sign(self, date: datetime) -> str:
        """Get the zodiac sign for a date.

        This is a simplified calculation that doesn't account for the exact
        transition dates between signs, which can vary slightly each year.

        Args:
            date: Date to get zodiac sign for

        Returns:
            Zodiac sign as a string
        """
        # Define the approximate dates for each zodiac sign
        zodiac_dates = [
            (1, 20, "Aquarius"),  # Jan 20 - Feb 18
            (2, 19, "Pisces"),  # Feb 19 - Mar 20
            (3, 21, "Aries"),  # Mar 21 - Apr 19
            (4, 20, "Taurus"),  # Apr 20 - May 20
            (5, 21, "Gemini"),  # May 21 - Jun 20
            (6, 21, "Cancer"),  # Jun 21 - Jul 22
            (7, 23, "Leo"),  # Jul 23 - Aug 22
            (8, 23, "Virgo"),  # Aug 23 - Sep 22
            (9, 23, "Libra"),  # Sep 23 - Oct 22
            (10, 23, "Scorpio"),  # Oct 23 - Nov 21
            (11, 22, "Sagittarius"),  # Nov 22 - Dec 21
            (12, 22, "Capricorn"),  # Dec 22 - Jan 19
        ]

        # Get the month and day
        month = date.month
        day = date.day

        # Find the zodiac sign
        if month == 12 and day >= 22 or month == 1 and day <= 19:
            return "Capricorn"

        for m, d, sign in zodiac_dates:
            if (
                month == m
                and day >= d
                or month == m + 1
                and day < zodiac_dates[m % 12][1]
            ):
                return sign

        # Default to Aries if something goes wrong
        return "Aries"

    def get_moon_phases_for_month(self, year: int, month: int) -> List[PlannerEvent]:
        """Get moon phases for a specific month using accurate astronomical calculations.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            List of moon phase events
        """
        # Get the default location from settings
        default_location = self.settings.default_location

        # Use astronomical calculations to determine accurate moon phases
        # Pass the default location to adjust for timezone
        return calculate_moon_phases_for_month(
            year, month, self._get_zodiac_sign, default_location
        )

    def get_void_of_course_periods(self, date: datetime.date) -> List[PlannerEvent]:
        """Get void-of-course periods for a specific date.

        Args:
            date: Date to get void-of-course periods for

        Returns:
            List of void-of-course events
        """
        # Calculate void-of-course periods for the date
        events = []

        # For now, we'll just add a placeholder event
        # In a real implementation, we would calculate actual void-of-course periods

        # Add Void-of-Course period
        voc_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=14)
        voc_end = voc_start + timedelta(hours=2)
        events.append(
            PlannerEvent(
                title="Moon Void-of-Course",
                description="Moon Void-of-Course",
                event_type=EventType.VOID_OF_COURSE,
                start_time=voc_start,
                end_time=voc_end,
                color="#800080",  # Purple
            )
        )

        return events

    def get_planetary_aspects(self, date: datetime.date) -> List[PlannerEvent]:
        """Get planetary aspects for a specific date.

        Args:
            date: Date to get planetary aspects for

        Returns:
            List of aspect events
        """
        # Calculate planetary aspects for the date
        events = []

        # For now, we'll just add placeholder events
        # In a real implementation, we would calculate actual planetary aspects

        # Add Sun-Jupiter conjunction
        aspect_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=10)
        events.append(
            PlannerEvent(
                title="Sun conjunct Jupiter",
                description="Sun conjunct Jupiter at 15° Aries",
                event_type=EventType.PLANETARY_ASPECT,
                start_time=aspect_time,
                color="#FFA500",  # Orange
            )
        )

        # Add Moon-Venus square
        aspect_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=16)
        events.append(
            PlannerEvent(
                title="Moon square Venus",
                description="Moon square Venus at 22° Cancer/Aries",
                event_type=EventType.PLANETARY_ASPECT,
                start_time=aspect_time,
                color="#FF0000",  # Red
            )
        )

        return events

    def get_retrograde_periods(self, date: datetime.date) -> List[PlannerEvent]:
        """Get retrograde periods for a specific date.

        Args:
            date: Date to get retrograde periods for

        Returns:
            List of retrograde events
        """
        # Calculate retrograde periods for the date
        events = []

        # For now, we'll just add placeholder events
        # In a real implementation, we would calculate actual retrograde periods

        # Add Mercury retrograde
        if date.month == 5 and 10 <= date.day <= 31:
            # Mercury goes retrograde
            if date.day == 10:
                retro_time = datetime.combine(date, datetime.min.time()) + timedelta(
                    hours=12
                )
                events.append(
                    PlannerEvent(
                        title="Mercury Retrograde Begins",
                        description="Mercury stations retrograde at 5° Gemini",
                        event_type=EventType.RETROGRADE,
                        start_time=retro_time,
                        color="#800000",  # Maroon
                    )
                )
            # Mercury is retrograde
            else:
                events.append(
                    PlannerEvent(
                        title="Mercury Retrograde",
                        description="Mercury retrograde in Gemini",
                        event_type=EventType.RETROGRADE,
                        start_time=datetime.combine(date, datetime.min.time()),
                        end_time=datetime.combine(date, datetime.max.time()),
                        color="#800000",  # Maroon
                    )
                )

        # Add Venus retrograde
        if date.month == 7 and 15 <= date.day <= 31:
            # Venus goes retrograde
            if date.day == 15:
                retro_time = datetime.combine(date, datetime.min.time()) + timedelta(
                    hours=18
                )
                events.append(
                    PlannerEvent(
                        title="Venus Retrograde Begins",
                        description="Venus stations retrograde at 28° Leo",
                        event_type=EventType.RETROGRADE,
                        start_time=retro_time,
                        color="#008000",  # Green
                    )
                )
            # Venus is retrograde
            else:
                events.append(
                    PlannerEvent(
                        title="Venus Retrograde",
                        description="Venus retrograde in Leo",
                        event_type=EventType.RETROGRADE,
                        start_time=datetime.combine(date, datetime.min.time()),
                        end_time=datetime.combine(date, datetime.max.time()),
                        color="#008000",  # Green
                    )
                )

        return events

    def get_eclipse_events(self, date: datetime.date) -> List[PlannerEvent]:
        """Get eclipse events for a specific date.

        Args:
            date: Date to get eclipse events for

        Returns:
            List of eclipse events
        """
        # Calculate eclipse events for the date
        events = []

        # For now, we'll just add placeholder events
        # In a real implementation, we would calculate actual eclipse events

        # Add Solar Eclipse
        if date.month == 4 and date.day == 20:
            eclipse_time = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=8
            )
            events.append(
                PlannerEvent(
                    title="Total Solar Eclipse",
                    description="Total Solar Eclipse at 0° Taurus",
                    event_type=EventType.ECLIPSE,
                    start_time=eclipse_time,
                    color="#000080",  # Navy
                )
            )

        # Add Lunar Eclipse
        if date.month == 10 and date.day == 14:
            eclipse_time = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=20
            )
            events.append(
                PlannerEvent(
                    title="Partial Lunar Eclipse",
                    description="Partial Lunar Eclipse at 21° Aries",
                    event_type=EventType.ECLIPSE,
                    start_time=eclipse_time,
                    color="#4B0082",  # Indigo
                )
            )

        return events

    def get_venus_cycle_events(self, date: datetime.date) -> List[PlannerEvent]:
        """Get Venus cycle events for a specific date.

        Args:
            date: Date to get Venus cycle events for

        Returns:
            List of Venus cycle events
        """
        # Calculate Venus cycle events for the date
        events = []

        # For now, we'll just add placeholder events
        # In a real implementation, we would calculate actual Venus cycle events

        # Add Venus Morning Star
        if date.month == 6 and date.day == 10:
            venus_time = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=5
            )
            events.append(
                PlannerEvent(
                    title="Venus Morning Star Begins",
                    description="Venus becomes visible as Morning Star",
                    event_type=EventType.VENUS_CYCLE,
                    start_time=venus_time,
                    color="#00FFFF",  # Cyan
                )
            )

        # Add Venus Evening Star
        if date.month == 1 and date.day == 15:
            venus_time = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=18
            )
            events.append(
                PlannerEvent(
                    title="Venus Evening Star Begins",
                    description="Venus becomes visible as Evening Star",
                    event_type=EventType.VENUS_CYCLE,
                    start_time=venus_time,
                    color="#00FFFF",  # Cyan
                )
            )

        return events

    def get_all_astrological_events_for_date(
        self, date: datetime.date
    ) -> List[PlannerEvent]:
        """Get all astrological events for a specific date.

        Args:
            date: Date to get events for

        Returns:
            List of astrological events
        """
        events = []

        # Get moon phases
        # Note: Moon phases are calculated for the month, so we need to filter for this date
        moon_phases = self.get_moon_phases_for_month(date.year, date.month)
        for event in moon_phases:
            if event.start_time.date() == date:
                events.append(event)

        # Get void-of-course periods
        events.extend(self.get_void_of_course_periods(date))

        # Get planetary aspects
        events.extend(self.get_planetary_aspects(date))

        # Get retrograde periods
        events.extend(self.get_retrograde_periods(date))

        # Get eclipse events
        events.extend(self.get_eclipse_events(date))

        # Get Venus cycle events
        events.extend(self.get_venus_cycle_events(date))

        return events

    def calculate_chart(self, date_time: datetime, location: Location) -> Chart:
        """Calculate a chart for a specific date, time, and location.

        Args:
            date_time: Date and time
            location: Location

        Returns:
            Chart object
        """
        # Create a name for the chart based on the date and time
        name = f"Chart for {date_time.strftime('%Y-%m-%d %H:%M')}"

        # Calculate the chart
        chart = self.chart_service.create_natal_chart(
            name=name,
            birth_date=date_time,
            latitude=location.latitude,
            longitude=location.longitude,
            location_name=location.display_name,
        )

        return chart

    def send_event_to_chart_maker(
        self, event: PlannerEvent, location: Location
    ) -> Chart:
        """Send an event to the chart maker.

        Args:
            event: Event to send
            location: Location for the chart

        Returns:
            Chart object
        """
        # Create a chart for the event
        chart = self.chart_service.create_natal_chart(
            name=event.title,
            birth_date=event.start_time,
            latitude=location.latitude,
            longitude=location.longitude,
            location_name=location.display_name,
        )

        return chart
