"""
Purpose: Provides services for the astrological daily planner.
This file is part of the astrology pillar and serves as a service component.
It provides functionality to calculate astrological events for specific dates,
including moon phases, planetary aspects, retrograde
periods, eclipses, and Venus cycles.
Key components:
- PlannerService: Service for astrological daily planner calculations
- PlannerEvent: Data model for astrological events
"""
import uuid
from datetime import datetime, time, timedelta
from typing import Dict, List

import swisseph as swe
from loguru import logger

from astrology.models.chart import Chart
from astrology.models.planner import EventType, PlannerEvent, PlannerSettings
from astrology.repositories.sqlite_planner_repository import SQLitePlannerRepository
from astrology.services.astrological_event_calculator import (
    AspectType,
    AstrologicalEventCalculator,
)
from astrology.services.astrology_calculation_service import AstrologyCalculationService
from astrology.services.chart_service import ChartService
from astrology.services.location_service import Location

# Import our astronomical calculators
from astrology.services.moon_phase_calculator import MoonPhaseCalculator
from shared.repositories.database import Database


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
        if PlannerService._instance is not None:
            raise Exception("PlannerService is a singleton!")

        self.repository = SQLitePlannerRepository(Database.get_instance())
        self.chart_service = ChartService.get_instance()
        self.astrology_calculation_service = AstrologyCalculationService.get_instance()
        self.moon_phase_calculator = MoonPhaseCalculator.get_instance()

        # Get the AstrologicalEventCalculator for planet phases
        self.astrological_event_calculator = AstrologicalEventCalculator.get_instance()

        self._settings = self._load_settings()

        PlannerService._instance = self
        logger.debug("PlannerService initialized")

    def _clear_cache(self):
        """Clear the calculation caches."""
        self._moon_phase_cache = {}

    def _load_settings(self) -> PlannerSettings:
        """Load planner settings from the database.
        Returns:
            PlannerSettings object with default values if not found
        """
        try:
            row = self.repository.database.query_one(
                "SELECT * FROM planner_settings LIMIT 1"
            )
            if row:
                # Create a location object if location data exists
                default_location = None
                if row.get("default_location_latitude") and row.get(
                    "default_location_longitude"
                ):
                    from astrology.services.location_service import Location

                    default_location = Location(
                        name=row.get("default_location_name", ""),
                        display_name=row.get("default_location_display", ""),
                        latitude=row.get("default_location_latitude", 0.0),
                        longitude=row.get("default_location_longitude", 0.0),
                        country=row.get("default_location_country", ""),
                        state=row.get("default_location_state", ""),
                        city=row.get("default_location_city", ""),
                        # Default values for fields not stored
                        country_code="",
                        type="",
                        importance=0.0,
                    )
                    logger.debug(
                        f"Loaded default location: {default_location.display_name}"
                    )
                else:
                    logger.debug("No default location found in database")

                return PlannerSettings(
                    default_event_duration=row["default_event_duration"],
                    show_lunar_phases=bool(row["show_lunar_phases"]),
                    show_planetary_hours=bool(row["show_planetary_hours"]),
                    default_view="month",  # Add more settings as needed
                    show_retrogrades=bool(row.get("show_retrogrades", 1)),
                    show_eclipses=bool(row.get("show_eclipses", 1)),
                    show_venus_cycles=bool(row.get("show_venus_cycles", 1)),
                    show_planetary_aspects=bool(row.get("show_planetary_aspects", 1)),
                    default_location=default_location,
                )
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        # Return default settings if none found
        return PlannerSettings()

    def get_settings(self) -> PlannerSettings:
        """Get the current planner settings.
        Returns:
            PlannerSettings object
        """
        return self._settings

    def save_settings(self, settings: PlannerSettings) -> bool:
        """Save planner settings.
        Args:
            settings: Settings to save
        Returns:
            True if successful
        """
        try:
            with self.repository.database.transaction() as conn:
                # Location parameters
                location_name = None
                location_display = None
                location_latitude = None
                location_longitude = None
                location_country = None
                location_state = None
                location_city = None

                # Extract location data if available
                if settings.default_location:
                    location_name = settings.default_location.name
                    location_display = settings.default_location.display_name
                    location_latitude = settings.default_location.latitude
                    location_longitude = settings.default_location.longitude
                    location_country = settings.default_location.country
                    location_state = settings.default_location.state
                    location_city = settings.default_location.city
                    logger.debug(
                        f"Saving default location: {settings.default_location.display_name}"
                    )
                else:
                    logger.debug("No default location to save")

                conn.execute(
                    """
                    INSERT OR REPLACE INTO planner_settings (
                        id, default_event_duration, show_lunar_phases,
                        show_planetary_hours, show_retrogrades, show_eclipses,
                        show_venus_cycles, show_planetary_aspects,
                        default_location_name, default_location_display,
                        default_location_latitude, default_location_longitude,
                        default_location_country, default_location_state,
                        default_location_city
                    ) VALUES (
                        1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """,
                    (
                        settings.default_event_duration,
                        int(settings.show_lunar_phases),
                        int(settings.show_planetary_hours),
                        int(settings.show_retrogrades),
                        int(settings.show_eclipses),
                        int(settings.show_venus_cycles),
                        int(settings.show_planetary_aspects),
                        location_name,
                        location_display,
                        location_latitude,
                        location_longitude,
                        location_country,
                        location_state,
                        location_city,
                    ),
                )
                self._settings = settings
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def save_event(self, event: PlannerEvent) -> bool:
        """Save a planner event.
        Args:
            event: Event to save
        Returns:
            True if successful
        """
        return self.repository.save_event(event)

    def get_events_for_date(self, date: datetime.date) -> List[PlannerEvent]:
        """Get all events for a specific date.
        Args:
            date: Date to get events for
        Returns:
            List of events
        """
        # Get user events from repository
        user_events = self.repository.get_events_for_date(date)
        # Get astrological events
        astro_events = self.get_all_astrological_events_for_date(date)
        # Combine and return all events
        return user_events + astro_events

    def get_all_astrological_events_for_date(
        self, date: datetime.date, include_minor_aspects: bool = False
    ) -> List[PlannerEvent]:
        """Get all astrological events for a specific date.
        Args:
            date: Date to get events for
            include_minor_aspects: Whether to include minor aspects
        Returns:
            List of PlannerEvent objects for the specified date
        """
        events = []

        try:
            # Get moon phase events if enabled
            if self._settings.show_lunar_phases:
                moon_phase_events = (
                    self.moon_phase_calculator.get_moon_phase_events_for_date(date)
                )
                events.extend(moon_phase_events)
                logger.debug(
                    f"Added {len(moon_phase_events)} moon phase events for {date}"
                )
        except Exception as e:
            logger.error(f"Error getting moon phase events: {e}")

        try:
            # Get planetary aspects from the database if enabled
            if self._settings.show_planetary_aspects:
                logger.debug(
                    f"Fetching planetary aspects for {date} with include_minor={include_minor_aspects}"
                )
                aspect_events = self.get_planetary_aspects_for_date(
                    date, include_minor=include_minor_aspects
                )
                logger.debug(f"Returned aspect events: {len(aspect_events)}")

                # Log the first few aspect events for debugging
                for i, event in enumerate(aspect_events[:3]):
                    logger.debug(
                        f"  Aspect event {i+1}: {event.title}, type={event.event_type}, time={event.start_time}"
                    )

                events.extend(aspect_events)
                logger.debug(
                    f"Added {len(aspect_events)} planetary aspect events for {date}, total events now: {len(events)}"
                )
        except Exception as e:
            logger.error(f"Error getting aspect events: {e}", exc_info=True)

        try:
            # Get retrograde events if enabled
            if self._settings.show_retrogrades:
                retrograde_events = self.get_retrograde_periods(date)
                events.extend(retrograde_events)
                logger.debug(
                    f"Added {len(retrograde_events)} retrograde events for {date}"
                )
        except Exception as e:
            logger.error(f"Error getting retrograde events: {e}")

        try:
            # Get eclipse events if enabled
            if self._settings.show_eclipses:
                eclipse_events = self.get_eclipse_events(date)
                events.extend(eclipse_events)
                logger.debug(f"Added {len(eclipse_events)} eclipse events for {date}")
        except Exception as e:
            logger.error(f"Error getting eclipse events: {e}")

        try:
            # Get planet phases (Mercury and Venus phases) from the database if enabled
            if self._settings.show_venus_cycles:
                date_as_datetime = datetime.combine(date, time())
                # Use the AstrologicalEventCalculator instance to get planet phases
                planet_phases = (
                    self.astrological_event_calculator.get_planet_phases_for_date(
                        date_as_datetime
                    )
                )

                for phase in planet_phases:
                    event = PlannerEvent(
                        id=phase.get("id", str(uuid.uuid4())),
                        title=phase.get("title", "Unknown phase"),
                        description=phase.get("description", ""),
                        event_type=EventType.PLANETARY_PHASE,
                        start_time=phase.get("timestamp", date_as_datetime),
                        end_time=phase.get("timestamp", date_as_datetime)
                        + timedelta(hours=1),  # Set a 1-hour duration for display
                        color="#9370DB",  # Medium purple color for planetary phases
                        metadata={
                            "precise_time": phase.get("timestamp", date_as_datetime),
                            "body_name": phase.get("body_name"),
                            "phase_type": phase.get("phase_type"),
                            "elongation_degree": phase.get("elongation_degree"),
                            "zodiac_sign": phase.get("zodiac_sign"),
                        },
                    )
                    events.append(event)
                logger.debug(
                    f"Added {len(planet_phases)} planetary phase events for {date}"
                )
        except Exception as e:
            logger.error(f"Error getting planet phase events: {e}")

        logger.info(f"Found {len(events)} total astrological events for {date}")
        return events

    def _convert_aspects_to_events(self, aspects: List) -> List[PlannerEvent]:
        """Convert aspect objects to PlannerEvent objects.
        Args:
            aspects: List of Aspect objects
        Returns:
            List of PlannerEvent objects
        """
        events = []

        # Define aspect colors
        aspect_colors = {
            "conjunction": "#E67E22",  # Orange
            "opposition": "#C0392B",  # Dark Red
            "trine": "#2ECC71",  # Green
            "square": "#E74C3C",  # Red
            "sextile": "#3498DB",  # Blue
            "semisextile": "#F1C40F",  # Yellow
            "quincunx": "#9B59B6",  # Purple
            "semisquare": "#FF7979",  # Light red
            "sesquiquadrate": "#FF5733",  # Red/orange
        }

        for aspect in aspects:
            try:
                # Try to convert using the built-in method if available
                if hasattr(aspect, "to_planner_event") and callable(
                    getattr(aspect, "to_planner_event")
                ):
                    event = aspect.to_planner_event()

                    # Set default color based on aspect type
                    if hasattr(aspect, "aspect_type"):
                        aspect_name = ""
                        aspect_key = ""

                        # Get the aspect type in the correct format
                        if hasattr(aspect.aspect_type, "name"):
                            aspect_name = aspect.aspect_type.name.lower()
                            aspect_key = aspect_name
                        elif hasattr(aspect.aspect_type, "value"):
                            aspect_name = str(aspect.aspect_type.value).lower()
                            aspect_key = aspect_name
                        elif isinstance(aspect.aspect_type, str):
                            aspect_name = aspect.aspect_type.lower()
                            aspect_key = aspect_name

                        # Set color if we have a specific one for this aspect type
                        if aspect_key in aspect_colors:
                            event.color = aspect_colors[aspect_key]
                        else:
                            # Try standard keys if the direct lookup failed
                            if "opposition" in aspect_key:
                                event.color = aspect_colors["opposition"]
                            elif "conjunction" in aspect_key:
                                event.color = aspect_colors["conjunction"]
                            elif "trine" in aspect_key:
                                event.color = aspect_colors["trine"]
                            elif "square" in aspect_key:
                                event.color = aspect_colors["square"]
                            elif "sextile" in aspect_key:
                                event.color = aspect_colors["sextile"]
                            else:
                                # Default blue if no match
                                event.color = "#3498db"

                    # IMPORTANT FIX: Make sure the event has the correct event_type
                    event.event_type = EventType.PLANETARY_ASPECT

                    events.append(event)
                    continue

                # Fallback if to_planner_event isn't available
                # Safely extract planet names
                planet1_name = "Unknown"
                planet2_name = "Unknown"
                aspect_name = "Unknown"
                aspect_key = "conjunction"  # Default for color selection

                # Try to get planet1 name
                if hasattr(aspect, "planet1"):
                    planet1 = aspect.planet1
                    if hasattr(planet1, "name"):
                        planet1_name = planet1.name
                    elif isinstance(planet1, dict) and "name" in planet1:
                        planet1_name = planet1["name"]

                # Try to get planet2 name
                if hasattr(aspect, "planet2"):
                    planet2 = aspect.planet2
                    if hasattr(planet2, "name"):
                        planet2_name = planet2.name
                    elif isinstance(planet2, dict) and "name" in planet2:
                        planet2_name = planet2["name"]

                # Try to get aspect type
                if hasattr(aspect, "aspect_type"):
                    aspect_type = aspect.aspect_type
                    if hasattr(aspect_type, "display_name"):
                        aspect_name = aspect_type.display_name
                        if hasattr(aspect_type, "name"):
                            aspect_key = aspect_type.name.lower()
                    elif hasattr(aspect_type, "name"):
                        aspect_name = aspect_type.name.replace("_", " ").title()
                        aspect_key = aspect_type.name.lower()
                    elif isinstance(aspect_type, str):
                        aspect_name = aspect_type.replace("_", " ").title()
                        aspect_key = aspect_type.lower()

                # Get the exact time if available
                exact_time = None
                if hasattr(aspect, "exact_time") and aspect.exact_time:
                    exact_time = aspect.exact_time
                else:
                    # Default to current date/time if not available
                    exact_time = datetime.now()

                # Create a unique ID
                unique_id = f"aspect_{planet1_name}_{planet2_name}_{aspect_name}_{uuid.uuid4().hex[:8]}"

                # Determine aspect color
                color = aspect_colors.get(
                    aspect_key, "#3498db"
                )  # Default blue if aspect not found

                # Create an event from the aspect
                event = PlannerEvent(
                    id=unique_id,
                    title=f"{planet1_name} {aspect_name} {planet2_name}",
                    description=f"Planetary Aspect: {planet1_name} is in {aspect_name} with {planet2_name}",
                    event_type=EventType.PLANETARY_ASPECT,
                    start_time=exact_time,
                    end_time=exact_time
                    + timedelta(hours=1),  # 1-hour duration for visibility
                    color=color,
                )
                events.append(event)

            except Exception as e:
                logger.error(f"Error converting aspect to event: {str(e)}")
                # Continue processing other aspects even if one fails
                continue
        return events

    def get_events_for_month(
        self, year: int, month: int, include_minor_aspects: bool = True
    ) -> Dict[int, List[PlannerEvent]]:
        """Get all events for a specific month.
        Args:
            year: Year
            month: Month (1-12)
            include_minor_aspects: Whether to include minor aspects
        Returns:
            Dictionary mapping days to events
        """
        # Get user events from repository
        user_events_by_day = self.repository.get_events_for_month(year, month)
        # Get astrological events day by day (aspects still need to be calculated daily)
        all_events = {}
        current_day = datetime(year, month, 1).date()

        while current_day.month == month:
            day_events = []

            # Add user events
            if current_day.day in user_events_by_day:
                day_events.extend(user_events_by_day[current_day.day])

            # Add moon phases for this day if enabled
            if self._settings.show_lunar_phases:
                moon_phases = self.moon_phase_calculator.get_moon_phase_events_for_date(
                    current_day
                )
                if moon_phases:
                    day_events.extend(moon_phases)

            # Get planetary aspects from database instead of calculating them if enabled
            if self._settings.show_planetary_aspects:
                # Use get_planetary_aspects_for_date which uses the database
                aspects = self.get_planetary_aspects_for_date(
                    current_day, include_minor=include_minor_aspects
                )
                if aspects:
                    logger.debug(
                        f"Adding {len(aspects)} aspects to events for {current_day}"
                    )
                    day_events.extend(aspects)

            # Get retrograde events if enabled
            if self._settings.show_retrogrades:
                retrogrades = self.get_retrograde_periods(current_day)
                if retrogrades:
                    day_events.extend(retrogrades)

            # Get eclipse events if enabled
            if self._settings.show_eclipses:
                eclipses = self.get_eclipse_events(current_day)
                if eclipses:
                    day_events.extend(eclipses)

            # Get Venus cycle and planetary phase events from database if enabled
            if self._settings.show_venus_cycles:
                # Convert date to datetime for the database query
                day_datetime = datetime.combine(current_day, time())

                # Get planet phases which includes Venus cycle events
                # Use the AstrologicalEventCalculator instance to get planet phases
                planet_phases = (
                    self.astrological_event_calculator.get_planet_phases_for_date(
                        day_datetime
                    )
                )

                for phase in planet_phases:
                    # Only include Venus events if they match what we're looking for
                    if "Venus" in phase.get("title", ""):
                        event = PlannerEvent(
                            id=phase.get("id", str(uuid.uuid4())),
                            title=phase.get("title", "Unknown phase"),
                            description=phase.get("description", ""),
                            event_type=EventType.VENUS_CYCLE,
                            start_time=phase.get("timestamp", day_datetime),
                            end_time=phase.get("timestamp", day_datetime)
                            + timedelta(hours=1),
                            color="#FF69B4",  # Hot pink for Venus events
                        )
                        day_events.append(event)

            # Store events for this day
            if day_events:
                all_events[current_day.day] = day_events

            # Move to next day
            current_day += timedelta(days=1)
        return all_events

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
        try:
            # Get the timezone string
            try:
                import tzlocal

                timezone_str = str(tzlocal.get_localzone())
                logger.debug(f"Using local timezone for chart: {timezone_str}")
            except Exception as e:
                logger.warning(f"Could not get local timezone, using UTC: {e}")
                timezone_str = "UTC"

            # Use precise time from metadata if available, otherwise use the display time
            birth_date = event.start_time
            if event.metadata and "precise_time" in event.metadata:
                precise_time = event.metadata["precise_time"]
                if isinstance(precise_time, datetime):
                    birth_date = precise_time
                    logger.debug(f"Using precise time from metadata: {birth_date}")
                else:
                    logger.warning(
                        f"Precise time in metadata is not a datetime: {precise_time}"
                    )
            else:
                logger.debug(
                    f"No precise time in metadata, using display time: {birth_date}"
                )

            # Create a chart for the event
            chart = self.chart_service.create_natal_chart(
                name=event.title,
                birth_date=birth_date,
                latitude=location.latitude,
                longitude=location.longitude,
                location_name=location.display_name,
                birth_time_known=True,  # Explicitly set birth_time_known
            )

            # Explicitly set the timezone
            chart.timezone = timezone_str

            return chart
        except Exception as e:
            logger.error(f"Error creating chart from planner event: {e}", exc_info=True)
            raise

    def get_moon_phases_for_month(self, year: int, month: int) -> List[PlannerEvent]:
        """Get moon phases for a specific month.
        Args:
            year: Year
            month: Month (1-12)
        Returns:
            List of moon phase events
        """
        return self.moon_phase_calculator.get_moon_phases_for_month(year, month)

    def get_planetary_aspects(
        self, date: datetime.date, include_minor: bool = True
    ) -> List[PlannerEvent]:
        """Get planetary aspects for a specific date using Swiss Ephemeris calculations.
        Args:
            date: Date to get planetary aspects for
            include_minor: Whether to include minor aspects (default: True)
        Returns:
            List of aspect events
        """
        logger.debug(
            f"Calculating planetary aspects for {date} using Swiss Ephemeris (include_minor={include_minor})"
        )
        # Get aspects from the calculation service
        aspects = self.astrology_calculation_service.get_aspects_for_date(
            date,
            orb=2.0,  # Use a reasonable orb for daily aspects
            include_major=True,
            include_minor=include_minor,
        )
        # Convert to PlannerEvent objects
        events = []
        for aspect in aspects:
            body1 = aspect["body1"]
            body2 = aspect["body2"]
            aspect_type = aspect["aspect_type"]
            body1_sign = aspect["body1_position"]["zodiac_sign"]
            body1_degree = aspect["body1_position"]["zodiac_degree"]
            # Handle the time field correctly - it's already a datetime
            aspect_time = aspect["time"]
            if isinstance(aspect_time, datetime):
                # Use the time from the datetime object directly
                precise_time = aspect_time
            else:
                # Fallback in case it's just a time object
                precise_time = datetime.combine(date, aspect_time)

            # Round to the nearest hour for display
            display_time = precise_time.replace(minute=0, second=0, microsecond=0)
            if precise_time.minute >= 30:
                display_time = display_time + timedelta(hours=1)

            events.append(
                PlannerEvent(
                    title=f"{body1} {aspect_type} {body2}",
                    description=f"{body1} {aspect_type} {body2} at {body1_degree:.1f}° {body1_sign}",
                    event_type=EventType.PLANETARY_ASPECT,
                    start_time=display_time,  # Display-friendly time
                    color=aspect["color"],
                    metadata={
                        "precise_time": precise_time,  # Store exact calculated time
                        "body1": body1,
                        "body2": body2,
                        "aspect_type": aspect_type,
                        "body1_sign": body1_sign,
                        "body1_degree": body1_degree,
                    },
                )
            )
            logger.debug(
                f"Added aspect: {body1} {aspect_type} {body2} at {precise_time} (display: {display_time})"
            )
        logger.debug(f"Found {len(events)} planetary aspects for {date}")
        return events

    def get_retrograde_periods(self, date: datetime.date) -> List[PlannerEvent]:
        """Get retrograde periods for specified date.

        Uses Swiss Ephemeris to check if planets are in retrograde motion
        and returns appropriate PlannerEvent objects.
        Args:
            date: Date to check for retrograde periods
        Returns:
            List of retrograde events for the specified date
        """
        events = []
        # Define planet colors for retrograde events
        planet_colors = {
            "Mercury": "#8C7853",  # Brown
            "Venus": "#E2A76F",  # Light orange
            "Mars": "#E27B58",  # Red-orange
            "Jupiter": "#9B59B6",  # Purple
            "Saturn": "#5D6D7E",  # Dark gray
            "Uranus": "#AED6F1",  # Light blue
            "Neptune": "#5DADE2",  # Medium blue
            "Pluto": "#6C3483",  # Dark purple
        }

        # List of planets to check for retrograde motion (SE planet constants)
        planets = [
            (swe.MERCURY, "Mercury"),
            (swe.VENUS, "Venus"),
            (swe.MARS, "Mars"),
            (swe.JUPITER, "Jupiter"),
            (swe.SATURN, "Saturn"),
            (swe.URANUS, "Uranus"),
            (swe.NEPTUNE, "Neptune"),
            (swe.PLUTO, "Pluto"),
        ]

        try:
            # Set ephemeris path if configured
            if hasattr(self.astrology_calculation_service, "ephemeris_path"):
                swe.set_ephe_path(self.astrology_calculation_service.ephemeris_path)

            # Convert date to Julian day at noon
            jd = swe.julday(date.year, date.month, date.day, 12.0)

            # Check retrograde status for each planet
            for planet_id, planet_name in planets:
                # Calculate planet position and retrieve speed
                flags = swe.FLG_SWIEPH | swe.FLG_SPEED
                ret, result = swe.calc_ut(jd, planet_id, flags)

                if ret == 0:  # Successful calculation
                    longitude = result[0]
                    speed = result[3]  # Daily speed in longitude

                    # If speed is negative, planet is retrograde
                    if speed < 0:
                        logger.debug(f"{planet_name} is retrograde on {date}")

                        # Create datetime objects for start/end of day
                        start_time = datetime.combine(date, datetime.min.time())
                        end_time = datetime.combine(date, datetime.max.time())

                        # Check if this is the beginning or end of retrograde period
                        retrograde_status = ""

                        # Check previous day
                        prev_jd = jd - 1.0
                        prev_ret, prev_result = swe.calc_ut(prev_jd, planet_id, flags)
                        if prev_ret == 0 and prev_result[3] >= 0:
                            retrograde_status = " begins"

                        # Check next day
                        next_jd = jd + 1.0
                        next_ret, next_result = swe.calc_ut(next_jd, planet_id, flags)
                        if next_ret == 0 and next_result[3] >= 0:
                            retrograde_status = " ends"

                        # Format position for description
                        degrees = int(longitude) % 30
                        minutes = int((longitude % 1) * 60)
                        sign = int(longitude / 30) + 1
                        sign_names = [
                            "Aries",
                            "Taurus",
                            "Gemini",
                            "Cancer",
                            "Leo",
                            "Virgo",
                            "Libra",
                            "Scorpio",
                            "Sagittarius",
                            "Capricorn",
                            "Aquarius",
                            "Pisces",
                        ]
                        position_str = f"{degrees}°{minutes}' {sign_names[sign-1]}"

                        # Create the event
                        event = PlannerEvent(
                            title=f"{planet_name} Retrograde{retrograde_status}",
                            description=f"{planet_name} retrograde at {position_str}. Speed: {speed:.4f}°/day",
                            start_time=start_time,
                            end_time=end_time,
                            all_day=True,
                            event_type=EventType.RETROGRADE,
                            color=planet_colors.get(
                                planet_name, "#7F8C8D"
                            ),  # Default color if not found
                            metadata={
                                "planet": planet_name,
                                "position": longitude,
                                "speed": speed,
                            },
                        )
                        events.append(event)
                        logger.debug(f"Added retrograde event: {event.title}")

        except Exception as e:
            logger.error(f"Error calculating retrograde periods: {e}")

            # Fallback to basic Mercury retrograde data if calculation failed
            if self.astrology_calculation_service is None:
                logger.warning(
                    "Using placeholder Mercury retrograde data as AstrologyCalculationService is unavailable"
                )
                # Mercury retrograde placeholder (would be removed in production with proper calculation)
                mercury_retro_periods_2023 = [
                    (datetime(2023, 4, 21), datetime(2023, 5, 14)),
                    (datetime(2023, 8, 23), datetime(2023, 9, 15)),
                    (datetime(2023, 12, 13), datetime(2024, 1, 1)),
                ]

                for start, end in mercury_retro_periods_2023:
                    if start.date() <= date <= end.date():
                        event = PlannerEvent(
                            title="Mercury Retrograde (Placeholder)",
                            description="Mercury appears to move backwards (Placeholder data)",
                            start_time=datetime.combine(date, datetime.min.time()),
                            end_time=datetime.combine(date, datetime.max.time()),
                            all_day=True,
                            event_type=EventType.RETROGRADE,
                            color="#8C7853",
                        )
                        events.append(event)
                        break
        return events

    def get_eclipse_events(self, date: datetime.date) -> List[PlannerEvent]:
        """Get eclipse events for a specific date.
        Args:
            date: Date to get eclipse events for
        Returns:
            List of eclipse events
        """
        events = []
        try:
            # Use the repository from the calculator
            repository = self.astrological_event_calculator.repository

            # Get start and end of the day
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())

            # Get eclipse events for this date
            eclipses = repository.get_eclipses(start_date=start_date, end_date=end_date)

            # Convert eclipse data to PlannerEvent objects
            for eclipse_data in eclipses:
                (
                    timestamp,
                    eclipse_type,
                    sun_position,
                    moon_position,
                    sun_zodiac,
                    moon_zodiac,
                ) = eclipse_data

                # Create appropriate title and description based on eclipse type
                if eclipse_type.lower().startswith("solar"):
                    title = f"{eclipse_type} Eclipse"
                    description = (
                        f"{eclipse_type} Eclipse at {sun_position:.1f}° {sun_zodiac}"
                    )
                    color = "#000080"  # Navy for solar eclipses
                else:  # Lunar eclipse
                    title = f"{eclipse_type} Eclipse"
                    description = (
                        f"{eclipse_type} Eclipse at {moon_position:.1f}° {moon_zodiac}"
                    )
                    color = "#4B0082"  # Indigo for lunar eclipses

                # Create the event with precise time in metadata
                # For planner display, we use a rounded time to the nearest hour
                display_time = timestamp.replace(minute=0, second=0, microsecond=0)
                if timestamp.minute >= 30:
                    display_time = display_time + timedelta(hours=1)

                eclipse_event = PlannerEvent(
                    title=title,
                    description=description,
                    event_type=EventType.ECLIPSE,
                    start_time=display_time,  # Display-friendly time
                    color=color,
                    metadata={
                        "precise_time": timestamp,  # Store exact calculated time
                        "eclipse_type": eclipse_type,
                        "sun_position": sun_position,
                        "moon_position": moon_position,
                        "sun_zodiac": sun_zodiac,
                        "moon_zodiac": moon_zodiac,
                    },
                )
                events.append(eclipse_event)

        except Exception as e:
            logger.error(f"Error retrieving eclipse events: {str(e)}")

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

    def get_planetary_aspects_for_date(
        self, date: datetime.date, include_minor: bool = False
    ) -> List[PlannerEvent]:
        """Get planetary aspects for a specific date from the database.
        Args:
            date: Date to get aspects for
            include_minor: Whether to include minor aspects
        Returns:
            List of PlannerEvent objects for the specified date
        """
        try:
            # Get aspect calculator
            calculator = AstrologicalEventCalculator.get_instance()

            # Get aspects from database
            aspects = calculator.get_aspects_for_date(date)

            # Log successful retrieval
            logger.debug(f"Retrieved {len(aspects)} aspects for {date}")

            # Log aspect details for debugging
            for i, aspect in enumerate(aspects):
                logger.debug(f"Aspect {i+1} details: {type(aspect)}")
                if hasattr(aspect, "get_description"):
                    logger.debug(f"  Description: {aspect.get_description()}")

            # Filter out minor aspects if not requested
            if not include_minor and aspects:
                try:
                    # Check how aspects are structured to filter properly
                    if hasattr(aspects[0], "aspect_type"):
                        # If aspects have aspect_type attribute, filter by the major types
                        aspects = [
                            a
                            for a in aspects
                            if getattr(a, "aspect_type", None)
                            in [
                                AspectType.CONJUNCTION,
                                AspectType.OPPOSITION,
                                AspectType.TRINE,
                                AspectType.SQUARE,
                                AspectType.SEXTILE,
                            ]
                        ]
                    else:
                        # Skip filtering if we can't determine the structure
                        logger.warning(
                            "Could not filter minor aspects: unexpected aspect structure"
                        )
                except (IndexError, AttributeError) as e:
                    logger.warning(f"Could not filter aspects: {str(e)}")

            # Convert aspects to events, handling potential errors
            events = self._convert_aspects_to_events(aspects)
            logger.debug(f"Final events count: {len(events)}")
            return events
        except Exception as e:
            logger.error(f"Error getting planetary aspects: {str(e)}", exc_info=True)
            return []

    def get_planet_phases_for_date(self, date: datetime) -> List[Dict]:
        """
        Get planet phases (Mercury and Venus) for a specific date.
        Args:
            date (datetime): The date to get planet phases for.
        Returns:
            List[Dict]: A list of planet phase events as dictionaries.
        """
        try:
            logger.debug(f"Getting planet phases for {date}")
            result = []

            # Convert to Julian day for calculations
            jd = self.astrology_calculation_service._datetime_to_jd(date)

            # Check Mercury phases
            mercury_result = swe.calc_ut(jd, swe.MERCURY)
            if not isinstance(mercury_result, tuple) or len(mercury_result) < 2:
                logger.error(f"Invalid Mercury calculation result: {mercury_result}")
            else:
                mercury_pos = mercury_result[0]
                sun_result = swe.calc_ut(jd, swe.SUN)
                if isinstance(sun_result, tuple) and len(sun_result) > 0:
                    sun_pos = sun_result[0]
                    # Calculate angular difference (elongation)
                    angular_diff = abs((mercury_pos - sun_pos) % 360)
                    if angular_diff > 180:
                        angular_diff = 360 - angular_diff

                    if (
                        angular_diff < 0.5
                    ):  # Within half a degree of inferior conjunction
                        result.append(
                            {
                                "id": f"mercury_inferior_{date.strftime('%Y%m%d')}",
                                "title": "Mercury Inferior Conjunction",
                                "description": "Mercury is at inferior conjunction with the Sun, marking the start of a new Mercury cycle.",
                                "date": date,
                            }
                        )
                    elif (
                        abs(angular_diff - 180) < 0.5
                    ):  # Within half a degree of superior conjunction
                        result.append(
                            {
                                "id": f"mercury_superior_{date.strftime('%Y%m%d')}",
                                "title": "Mercury Superior Conjunction",
                                "description": "Mercury is at superior conjunction with the Sun, midpoint of the Mercury cycle.",
                                "date": date,
                            }
                        )

            # Check Venus phases
            venus_result = swe.calc_ut(jd, swe.VENUS)
            if not isinstance(venus_result, tuple) or len(venus_result) < 2:
                logger.error(f"Invalid Venus calculation result: {venus_result}")
            else:
                venus_pos = venus_result[0]
                sun_result = swe.calc_ut(jd, swe.SUN)
                if isinstance(sun_result, tuple) and len(sun_result) > 0:
                    sun_pos = sun_result[0]
                    # Calculate angular difference (elongation)
                    angular_diff = abs((venus_pos - sun_pos) % 360)
                    if angular_diff > 180:
                        angular_diff = 360 - angular_diff

                    if (
                        angular_diff < 0.5
                    ):  # Within half a degree of inferior conjunction
                        result.append(
                            {
                                "id": f"venus_inferior_{date.strftime('%Y%m%d')}",
                                "title": "Venus Inferior Conjunction",
                                "description": "Venus is at inferior conjunction with the Sun, marking the start of a new Venus cycle.",
                                "date": date,
                            }
                        )
                    elif (
                        abs(angular_diff - 180) < 0.5
                    ):  # Within half a degree of superior conjunction
                        result.append(
                            {
                                "id": f"venus_superior_{date.strftime('%Y%m%d')}",
                                "title": "Venus Superior Conjunction",
                                "description": "Venus is at superior conjunction with the Sun, midpoint of the Venus cycle.",
                                "date": date,
                            }
                        )

                    # Check for greatest elongation (morning/evening star)
                    # Eastern elongation (evening star)
                    if 45 < angular_diff < 48:
                        result.append(
                            {
                                "id": f"venus_evening_{date.strftime('%Y%m%d')}",
                                "title": "Venus Greatest Eastern Elongation",
                                "description": "Venus is visible as the evening star, reaching its greatest angular distance from the Sun.",
                                "date": date,
                            }
                        )
                    # Western elongation (morning star)
                    elif 45 < angular_diff < 48 and venus_pos < sun_pos:
                        result.append(
                            {
                                "id": f"venus_morning_{date.strftime('%Y%m%d')}",
                                "title": "Venus Greatest Western Elongation",
                                "description": "Venus is visible as the morning star, reaching its greatest angular distance from the Sun.",
                                "date": date,
                            }
                        )

            logger.debug(f"Found {len(result)} planet phase events for {date}")
            return result

        except Exception as e:
            logger.error(f"Error calculating planet phases: {str(e)}", exc_info=True)
            return []
