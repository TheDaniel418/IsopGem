"""
Accurate moon phase calculator using astronomical algorithms.

This file is part of the astrology pillar and serves as a service component.
It provides accurate calculations for moon phases and planetary aspects
using Swiss Ephemeris.

Key components:
- MoonPhaseCalculator: Main calculator class using singleton pattern
- Aspect: Class representing planetary aspects with strength calculations
- calculate_moon_phases_for_month: Function for calculating lunar phases
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, NamedTuple, Optional, Tuple, Union

import ephem  # PyEphem for accurate astronomical calculations
import swisseph as swe
from loguru import logger

from astrology.models.planner import EventType, PlannerEvent
from astrology.services.astrological_event_calculator import AspectType
from astrology.services.location_service import Location

# Define constants for the planets
PLANET_SUN = swe.SUN
PLANET_MOON = swe.MOON
PLANET_MERCURY = swe.MERCURY
PLANET_VENUS = swe.VENUS
PLANET_MARS = swe.MARS
PLANET_JUPITER = swe.JUPITER
PLANET_SATURN = swe.SATURN
PLANET_URANUS = swe.URANUS
PLANET_NEPTUNE = swe.NEPTUNE
PLANET_PLUTO = swe.PLUTO

# Define the major planets used for aspect calculations
MAJOR_PLANETS = [
    PLANET_SUN,
    PLANET_MOON,
    PLANET_MERCURY,
    PLANET_VENUS,
    PLANET_MARS,
    PLANET_JUPITER,
    PLANET_SATURN,
    PLANET_URANUS,
    PLANET_NEPTUNE,
    PLANET_PLUTO,
]

# Define aspect angles - this maps our imported AspectType to the angle values
ASPECT_ANGLES = {
    AspectType.CONJUNCTION: 0.0,
    AspectType.OPPOSITION: 180.0,
    AspectType.TRINE: 120.0,
    AspectType.SQUARE: 90.0,
    AspectType.SEXTILE: 60.0,
    AspectType.SEMISEXTILE: 30.0,
    AspectType.QUINCUNX: 150.0,
    AspectType.SESQUIQUADRATE: 135.0,
    AspectType.SEMISQUARE: 45.0,
    AspectType.QUINTILE: 72.0,
    AspectType.BIQUINTILE: 144.0,
}

# Define display names for aspects
ASPECT_DISPLAY_NAMES = {
    AspectType.CONJUNCTION: "Conjunction",
    AspectType.OPPOSITION: "Opposition",
    AspectType.TRINE: "Trine",
    AspectType.SQUARE: "Square",
    AspectType.SEXTILE: "Sextile",
    AspectType.SEMISEXTILE: "Semisextile",
    AspectType.QUINCUNX: "Quincunx",
    AspectType.SESQUIQUADRATE: "Sesquiquadrate",
    AspectType.SEMISQUARE: "Semisquare",
    AspectType.QUINTILE: "Quintile",
    AspectType.BIQUINTILE: "Biquintile",
}

# Define orbs for aspects
ASPECT_ORBS = {
    AspectType.CONJUNCTION: 8.0,
    AspectType.OPPOSITION: 8.0,
    AspectType.TRINE: 7.0,
    AspectType.SQUARE: 7.0,
    AspectType.SEXTILE: 6.0,
    AspectType.SEMISEXTILE: 2.0,
    AspectType.QUINCUNX: 2.0,
    AspectType.SESQUIQUADRATE: 2.0,
    AspectType.SEMISQUARE: 2.0,
    AspectType.QUINTILE: 2.0,
    AspectType.BIQUINTILE: 2.0,
}


class PlanetInfo(NamedTuple):
    id: int
    name: str
    weight: float = 1.0  # Importance weight for aspect calculations
    position: float = None  # Position in degrees, used for aspect calculations


PLANETS = {
    swe.SUN: PlanetInfo(swe.SUN, "Sun", 1.0),  # Luminary
    swe.MOON: PlanetInfo(swe.MOON, "Moon", 1.0),  # Luminary
    swe.MERCURY: PlanetInfo(swe.MERCURY, "Mercury", 0.7),
    swe.VENUS: PlanetInfo(swe.VENUS, "Venus", 0.7),
    swe.MARS: PlanetInfo(swe.MARS, "Mars", 0.7),
    swe.JUPITER: PlanetInfo(swe.JUPITER, "Jupiter", 0.8),
    swe.SATURN: PlanetInfo(swe.SATURN, "Saturn", 0.8),
    swe.URANUS: PlanetInfo(swe.URANUS, "Uranus", 0.6),
    swe.NEPTUNE: PlanetInfo(swe.NEPTUNE, "Neptune", 0.6),
    swe.PLUTO: PlanetInfo(swe.PLUTO, "Pluto", 0.6),
}


class Aspect:
    def __init__(
        self,
        planet1,
        planet2,
        aspect_type: Union[AspectType, str],
        orb: float = 0.0,
        exact_time: datetime = None,
        strength: float = 100.0,
    ):
        """Initialize an aspect between two planets.

        Args:
            planet1: First planet (PlanetInfo or ID)
            planet2: Second planet (PlanetInfo or ID)
            aspect_type: Type of aspect (AspectType, string name, or angle value)
            orb: Actual orb of the aspect in degrees (default: 0.0)
            exact_time: Time when aspect is exact (default: None)
            strength: Strength of the aspect 0-100 (default: 100.0)
        """
        try:
            # Handle different types of planet input
            if isinstance(planet1, PlanetInfo):
                self.planet1 = planet1
            elif isinstance(planet1, int) and planet1 in PLANETS:
                self.planet1 = PLANETS[planet1]
            elif isinstance(planet1, str):
                # Map planet name to PlanetInfo
                planet_id = None
                for pid, pinfo in PLANETS.items():
                    if pinfo.name.lower() == planet1.lower():
                        planet_id = pid
                        break
                if planet_id:
                    self.planet1 = PLANETS[planet_id]
                else:
                    raise ValueError(f"Unknown planet name: {planet1}")
            else:
                raise ValueError(f"Invalid planet1 type: {type(planet1)}")

            # Same for planet2
            if isinstance(planet2, PlanetInfo):
                self.planet2 = planet2
            elif isinstance(planet2, int) and planet2 in PLANETS:
                self.planet2 = PLANETS[planet2]
            elif isinstance(planet2, str):
                # Map planet name to PlanetInfo
                planet_id = None
                for pid, pinfo in PLANETS.items():
                    if pinfo.name.lower() == planet2.lower():
                        planet_id = pid
                        break
                if planet_id:
                    self.planet2 = PLANETS[planet_id]
                else:
                    raise ValueError(f"Unknown planet name: {planet2}")
            else:
                raise ValueError(f"Invalid planet2 type: {type(planet2)}")

            # Handle different aspect_type formats
            if isinstance(aspect_type, AspectType):
                self.aspect_type = aspect_type
            elif isinstance(aspect_type, str):
                # Try to match the string to an AspectType value
                aspect_found = False
                # Try to match the string to an enum value
                for at in AspectType:
                    if (
                        at.value == aspect_type
                        or at.name.lower() == aspect_type.lower()
                    ):
                        self.aspect_type = at
                        aspect_found = True
                        break

                # If not found by name, check if it's a string representation of an angle
                if not aspect_found:
                    try:
                        # Try to interpret as an angle
                        angle = float(aspect_type)
                        # Find the closest aspect by angle
                        closest_aspect = None
                        min_diff = 360
                        for at, ang in ASPECT_ANGLES.items():
                            diff = abs(angle - ang)
                            if diff < min_diff:
                                min_diff = diff
                                closest_aspect = at

                        if min_diff <= 5:  # Within 5 degrees
                            self.aspect_type = closest_aspect
                            aspect_found = True
                    except (ValueError, TypeError):
                        pass

                # If still not found, use the string as is
                if not aspect_found:
                    # Try to find a matching known aspect type
                    for at in AspectType:
                        if (
                            at.value.lower() in aspect_type.lower()
                            or at.name.lower() in aspect_type.lower()
                        ):
                            self.aspect_type = at
                            aspect_found = True
                            logger.debug(
                                f"Matched aspect type {at} from string '{aspect_type}'"
                            )
                            break

                # If absolutely nothing matches, default to conjunction
                if not aspect_found:
                    logger.warning(
                        f"Could not determine aspect type from '{aspect_type}', defaulting to conjunction"
                    )
                    self.aspect_type = AspectType.CONJUNCTION
            else:
                # Default to conjunction if we can't interpret the aspect type
                logger.warning(
                    f"Unrecognized aspect type: {aspect_type}, defaulting to conjunction"
                )
                self.aspect_type = AspectType.CONJUNCTION

            self.orb = orb
            self.exact_time = exact_time or datetime.now()
            # Ensure strength is within valid range (0-100)
            self.strength = max(0.0, min(100.0, float(strength)))
        except Exception as e:
            logger.error(f"Error creating Aspect: {e}")
            # Set fallback values to prevent attribute errors
            self.planet1 = PLANETS[swe.SUN]  # Default to Sun
            self.planet2 = PLANETS[swe.MOON]  # Default to Moon
            self.aspect_type = AspectType.CONJUNCTION
            self.orb = 0.0
            self.exact_time = datetime.now()
            self.strength = 0.0

    def get_description(self) -> str:
        """Get a human-readable description of the aspect."""
        try:
            display_name = ASPECT_DISPLAY_NAMES.get(
                self.aspect_type, self.aspect_type.value.capitalize()
            )
            return f"{self.planet1.name} {display_name} {self.planet2.name}"
        except Exception:
            return "Unknown aspect"

    def to_planner_event(self) -> PlannerEvent:
        """Convert the aspect to a planner event."""
        try:
            from astrology.models.planner import EventType, PlannerEvent

            # Set event duration based on orb and planet speeds
            duration = timedelta(hours=2)  # Default 2-hour window

            # Determine aspect color based on aspect type
            aspect_colors = {
                AspectType.CONJUNCTION: "#E67E22",  # Orange
                AspectType.OPPOSITION: "#C0392B",  # Dark Red
                AspectType.TRINE: "#2ECC71",  # Green
                AspectType.SQUARE: "#E74C3C",  # Red
                AspectType.SEXTILE: "#3498DB",  # Blue
                AspectType.SEMISEXTILE: "#F1C40F",  # Yellow
                AspectType.QUINCUNX: "#9B59B6",  # Purple
                AspectType.SEMISQUARE: "#FF7979",  # Light red
                AspectType.SESQUIQUADRATE: "#FF5733",  # Red/orange
                AspectType.QUINTILE: "#9370DB",  # Medium purple
                AspectType.BIQUINTILE: "#9370DB",  # Medium purple
            }

            # Get color for this aspect type
            color = aspect_colors.get(
                self.aspect_type, "#3498db"
            )  # Default blue if aspect not found

            # Get a human readable display name
            display_name = ASPECT_DISPLAY_NAMES.get(
                self.aspect_type, self.aspect_type.value.capitalize()
            )

            # Store the precise time
            precise_time = self.exact_time

            # Create a display-friendly rounded time for the planner
            display_time = precise_time.replace(minute=0, second=0, microsecond=0)
            if precise_time.minute >= 30:
                display_time = display_time + timedelta(hours=1)

            # Create the event
            return PlannerEvent(
                id=f"aspect_{self.planet1.name}_{self.planet2.name}_{uuid.uuid4().hex[:8]}",
                title=f"{self.planet1.name} {display_name} {self.planet2.name}",
                description=f"{self.planet1.name} {display_name} {self.planet2.name} (Strength: {self.strength:.0f}%)",
                event_type=EventType.PLANETARY_ASPECT,
                start_time=display_time,
                end_time=display_time + duration,
                color=color,
                metadata={
                    "precise_time": precise_time,
                    "planet1_name": self.planet1.name,
                    "planet2_name": self.planet2.name,
                    "aspect_type": self.aspect_type.value
                    if hasattr(self.aspect_type, "value")
                    else str(self.aspect_type),
                    "strength": self.strength,
                    "orb": self.orb,
                },
            )
        except Exception as e:
            logger.error(f"Error creating planner event from aspect: {e}")
            # Return a minimal valid event to prevent errors
            from astrology.models.planner import EventType, PlannerEvent

            return PlannerEvent(
                title="Planetary Aspect",
                description="Aspect calculation error",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                event_type=EventType.PLANETARY_ASPECT,
            )


def calculate_moon_phases_for_month(
    year: int,
    month: int,
    get_zodiac_sign_func,
    default_location: Optional[Location] = None,
) -> List[PlannerEvent]:
    """Calculate moon phases for a specific month using accurate astronomical calculations.

    Args:
        year: Year
        month: Month (1-12)
        get_zodiac_sign_func: Function to get zodiac sign from a datetime
        default_location: Optional default location to adjust timezone (default: None, uses UTC)

    Returns:
        List of moon phase events
    """
    logger.debug(
        f"Calculating moon phases for {year}-{month} using astronomical calculations"
    )

    # Calculate moon phases for the month
    events = []

    # Get the first and last day of the month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)

    # Use PyEphem for accurate astronomical calculations
    # We'll calculate all moon phases in the month

    # Define the moon phases we want to find
    phases = [
        (ephem.next_new_moon, "New Moon", "#000000"),  # Black
        (ephem.next_first_quarter_moon, "First Quarter Moon", "#808080"),  # Gray
        (ephem.next_full_moon, "Full Moon", "#FFFF00"),  # Yellow
        (ephem.next_last_quarter_moon, "Last Quarter Moon", "#808080"),  # Gray
    ]

    # Start looking from a few days before the month begins to catch phases at the start of the month
    # Convert to PyEphem date format (Dublin Julian Day)
    start_date = ephem.Date(first_day - timedelta(days=5))
    end_date = ephem.Date(last_day + timedelta(days=5))

    # For each phase type, find all occurrences in the month
    for phase_func, phase_name, color in phases:
        # Start from our search start date
        current_date = start_date

        # Find all occurrences of this phase until we're past the end of the month
        while current_date < end_date:
            # Calculate the next occurrence of this phase
            next_phase_date = phase_func(current_date)

            # Convert PyEphem date to Python datetime
            # PyEphem dates are in UTC
            phase_datetime_utc = datetime.strptime(
                str(next_phase_date), "%Y/%m/%d %H:%M:%S"
            )
            phase_datetime_utc = phase_datetime_utc.replace(tzinfo=timezone.utc)

            # Adjust for timezone if a default location is provided
            if default_location:
                # Estimate timezone offset based on longitude
                # Each 15 degrees of longitude corresponds to 1 hour of time difference
                estimated_offset = default_location.longitude / 15.0
                # Round to the nearest hour for simplicity
                offset_hours = round(estimated_offset)
                phase_datetime = phase_datetime_utc + timedelta(hours=offset_hours)
                logger.debug(
                    f"Adjusted time from UTC to {offset_hours:+d} hours (estimated from longitude {default_location.longitude:.2f}) for {default_location.name}"
                )
            else:
                # Use UTC time if no location is provided
                phase_datetime = phase_datetime_utc

            # Check if this phase occurs in our target month
            if phase_datetime.year == year and phase_datetime.month == month:
                # Get zodiac sign using the provided function
                zodiac_sign = get_zodiac_sign_func(phase_datetime)

                # Convert back to naive datetime to maintain compatibility with the rest of the code
                # We've already adjusted for timezone, so we just need to remove the timezone info
                naive_datetime = datetime(
                    phase_datetime.year,
                    phase_datetime.month,
                    phase_datetime.day,
                    phase_datetime.hour,
                    phase_datetime.minute,
                    phase_datetime.second,
                )

                # Create a display-friendly rounded time for the planner
                display_time = naive_datetime.replace(minute=0, second=0, microsecond=0)
                if naive_datetime.minute >= 30:
                    display_time = display_time + timedelta(hours=1)

                # Create event for this moon phase
                events.append(
                    PlannerEvent(
                        title=phase_name,
                        description=f"{phase_name} in {zodiac_sign}",
                        event_type=EventType.MOON_PHASE,
                        start_time=display_time,
                        color=color,
                        metadata={
                            "precise_time": naive_datetime,
                            "zodiac_sign": zodiac_sign,
                            "phase_type": phase_name,
                        },
                    )
                )

                logger.debug(
                    f"Added {phase_name} on {phase_datetime.date()} in {zodiac_sign}"
                )

            # Move past this phase to avoid finding it again
            # Add a small increment to ensure we don't get the same phase again
            current_date = ephem.Date(next_phase_date + 1)

    # Sort events by date
    events.sort(key=lambda x: x.start_time)

    # Log the events found
    logger.debug(f"Found {len(events)} moon phase events for {year}-{month}")

    return events


class MoonPhaseCalculator:
    """Singleton class for calculating moon phases and other lunar events."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MoonPhaseCalculator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of MoonPhaseCalculator.

        Returns:
            The singleton instance of MoonPhaseCalculator
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Initialize cache for moon phases
        self._phase_cache = {}
        self._initialized = True
        logger.debug("MoonPhaseCalculator initialized")

    def _clear_cache(self):
        """Clear the calculator's cache."""
        self._phase_cache = {}
        logger.debug("MoonPhaseCalculator cache cleared")

    def get_moon_phases_for_month(self, year: int, month: int) -> List[PlannerEvent]:
        """Get moon phases for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            List of moon phase events
        """
        cache_key = (year, month)
        if cache_key not in self._phase_cache:
            # Calculate moon phases using the existing function
            self._phase_cache[cache_key] = calculate_moon_phases_for_month(
                year=year,
                month=month,
                get_zodiac_sign_func=self._get_zodiac_sign,
                default_location=None,  # We'll handle timezone adjustments elsewhere
            )
            logger.debug(f"Calculated and cached moon phases for {year}-{month}")

        return self._phase_cache[cache_key]

    def _get_zodiac_sign(self, date: datetime) -> str:
        """Get the zodiac sign for a date using Swiss Ephemeris.

        Args:
            date: Date to get zodiac sign for

        Returns:
            Zodiac sign as a string
        """
        # Convert to Julian day
        jd = swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute / 60.0 + date.second / 3600.0,
        )

        # Get sun position
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]

        # Get zodiac sign (0-11)
        sign_num = int(sun_pos[0] / 30)

        # Map to sign names
        signs = [
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

        return signs[sign_num % 12]

    def _normalize_angle(self, angle) -> float:
        """Normalize an angle to the 0-360 degree range.

        This function is type-safe and handles both numeric angles and tuples.

        Args:
            angle: The angle to normalize, can be float, int, or tuple

        Returns:
            Normalized angle in the range 0-360 degrees as a float
        """
        try:
            # Handle tuple case (common when getting direct result from Swiss Ephemeris)
            if isinstance(angle, tuple) and len(angle) > 0:
                # Extract the first element (longitude) from the position tuple
                angle_value = float(angle[0])
            else:
                # Try to convert to float directly
                angle_value = float(angle)

            # Normalize to 0-360 range
            normalized = angle_value % 360.0

            # Handle negative values
            if normalized < 0:
                normalized += 360.0

            return normalized
        except (TypeError, ValueError, IndexError) as e:
            # Log the error and return a safe default value
            logger.error(f"Error normalizing angle {angle}: {e}, type={type(angle)}")
            # Return 0.0 as a safe fallback
            return 0.0

    def _calculate_aspect_orb(
        self, pos1, pos2
    ) -> Union[Tuple[AspectType, float], None]:
        """Calculate the orb of any major aspect between two positions given in degrees.

        Args:
            pos1: Position of first planet in degrees
            pos2: Position of second planet in degrees

        Returns:
            Tuple of (AspectType, orb) if a major aspect is found within max orb of 1 degree,
            None if no major aspect is found
        """
        try:
            # Normalize input positions using our type-safe function
            norm_pos1 = self._normalize_angle(pos1)
            norm_pos2 = self._normalize_angle(pos2)

            # Calculate the angle between the two positions
            angle_diff = abs(norm_pos1 - norm_pos2)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # Define major aspects and their orbs
            aspects = {
                AspectType.CONJUNCTION: 0,
                AspectType.SEXTILE: 60,
                AspectType.SQUARE: 90,
                AspectType.TRINE: 120,
                AspectType.OPPOSITION: 180,
            }

            # Maximum orb for precision (1 degree)
            max_orb = 1.0

            # Check each aspect
            for aspect_type, aspect_angle in aspects.items():
                orb = abs(angle_diff - aspect_angle)
                if orb <= max_orb:
                    return (aspect_type, orb)

            return None
        except Exception as e:
            logger.error(
                f"Error calculating aspect orb: {e}, pos1={type(pos1)}, pos2={type(pos2)}"
            )
            return None

    def calculate_aspects(
        self, date: datetime.date, include_planets: List[int] = None
    ) -> List[Aspect]:
        """Calculate significant planetary aspects for the given date.

        Args:
            date: The date to calculate aspects for
            include_planets: Optional list of planet IDs to include (defaults to all planets)

        Returns:
            List of significant planetary aspects ordered by strength (descending)
        """
        try:
            # Convert date to Julian day
            jd = swe.julday(date.year, date.month, date.day, 0)

            # Planet IDs to calculate aspects for
            all_planet_ids = [
                swe.SUN,
                swe.MOON,
                swe.MERCURY,
                swe.VENUS,
                swe.MARS,
                swe.JUPITER,
                swe.SATURN,
                swe.URANUS,
                swe.NEPTUNE,
                swe.PLUTO,
            ]

            # Filter planets if specified
            planet_ids = include_planets if include_planets else all_planet_ids

            # Get positions for all planets
            planet_positions = {}
            for planet_id in planet_ids:
                try:
                    result = swe.calc_ut(jd, planet_id)
                    # The first element is the longitude (for swe.calc_ut, it's a tuple where first item is longitude)
                    position = result[0] if isinstance(result, tuple) else 0.0
                    planet_positions[planet_id] = self._normalize_angle(position)
                except Exception as e:
                    logger.error(
                        f"Error calculating position for planet {planet_id}: {e}"
                    )

            # Calculate aspects between all planet pairs
            aspects = []
            for i, planet1 in enumerate(planet_ids):
                if planet1 not in planet_positions:
                    continue

                for planet2 in planet_ids[i + 1 :]:
                    if planet2 not in planet_positions:
                        continue

                    aspect_result = self._calculate_aspect_orb(
                        planet_positions[planet1], planet_positions[planet2]
                    )

                    if aspect_result:
                        aspect_type, orb = aspect_result
                        # Calculate strength (inverse of orb - closer = stronger)
                        # 0 orb = 100% strength, 1 orb = 0% strength
                        base_strength = (1.0 - orb) * 100

                        # Get planet info from PLANETS dictionary with position added
                        planet1_info = PLANETS.get(planet1)
                        planet2_info = PLANETS.get(planet2)

                        # Only proceed if both planets are valid
                        if planet1_info and planet2_info:
                            # Apply planet weights to strength calculation
                            # Combined weight factor: average of both planet weights
                            weight_factor = (
                                planet1_info.weight + planet2_info.weight
                            ) / 2
                            adjusted_strength = base_strength * weight_factor

                            # Create new PlanetInfo objects with position
                            p1_with_pos = PlanetInfo(
                                id=planet1_info.id,
                                name=planet1_info.name,
                                weight=planet1_info.weight,
                                position=planet_positions[planet1],
                            )

                            p2_with_pos = PlanetInfo(
                                id=planet2_info.id,
                                name=planet2_info.name,
                                weight=planet2_info.weight,
                                position=planet_positions[planet2],
                            )

                            # Add to aspects list if strength is significant
                            if adjusted_strength >= 50:
                                aspects.append(
                                    Aspect(
                                        planet1=p1_with_pos,
                                        planet2=p2_with_pos,
                                        aspect_type=aspect_type,
                                        orb=orb,
                                        exact_time=date,
                                        strength=adjusted_strength,
                                    )
                                )

            # Sort aspects by strength (descending)
            aspects.sort(key=lambda a: a.strength, reverse=True)

            logger.info(f"Found {len(aspects)} significant aspects for {date}")
            return aspects

        except Exception as e:
            logger.error(f"Error calculating aspects for {date}: {e}")
            return []

    def _get_planet_position(self, dt: datetime, planet_id: int) -> float:
        """Get the position of a planet at a specific time.

        Args:
            dt: Date and time to get the position for
            planet_id: Swiss Ephemeris planet ID

        Returns:
            Position of the planet in degrees (0-360)
        """
        try:
            # Convert the datetime to Julian day
            jd = swe.julday(
                dt.year,
                dt.month,
                dt.day,
                dt.hour + dt.minute / 60.0 + dt.second / 3600.0,
            )

            # Calculate the planet's position
            result = swe.calc_ut(jd, planet_id)

            # Get the longitude (position in the zodiac)
            lon = self._normalize_angle(result[0])

            return lon
        except Exception as e:
            logger.error(f"Error calculating position for planet {planet_id}: {e}")
            return 0.0

    def _get_julian_day(self, date: datetime) -> float:
        """Convert datetime to Julian day.

        Args:
            date: Datetime to convert

        Returns:
            Julian day as float
        """
        return swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute / 60.0 + date.second / 3600.0,
        )

    def get_moon_phase_events_for_date(self, date: datetime.date) -> List[PlannerEvent]:
        """Get moon phase events for a specific date.

        Args:
            date: The date to get events for

        Returns:
            List of PlannerEvent objects for moon phases occurring on the given date
        """
        events = []

        # Get moon phases for the month
        moon_phases = self.get_moon_phases_for_month(date.year, date.month)

        # Filter for events on this date and ensure naive datetimes
        for event in moon_phases:
            if event.start_time.date() == date:
                # Ensure datetime is naive
                if event.start_time.tzinfo is not None:
                    event.start_time = event.start_time.replace(tzinfo=None)
                if event.end_time and event.end_time.tzinfo is not None:
                    event.end_time = event.end_time.replace(tzinfo=None)
                events.append(event)

        return events
