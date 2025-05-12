"""
@file kamea_astronomical_service.py
@description Service for Kamea-specific astronomical calculations supporting the Metonic cycle visualization.
@author Assistant
@created 2023-07-25
@lastModified 2023-07-25
@dependencies swisseph, datetime, astrology.services.astrology_calculation_service
"""

import math
from datetime import date, datetime, timedelta
from typing import Dict, List

import swisseph as swe
from loguru import logger

from astrology.services.astrology_calculation_service import AstrologyCalculationService


class KameaAstronomicalService:
    """Service for Kamea-specific astronomical calculations related to the Metonic cycle."""

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the Kamea Astronomical Service."""
        # Get instance of the base astrology calculation service
        self.astro_service = AstrologyCalculationService.get_instance()

        # Initialize Swiss Ephemeris if not already initialized
        swe.set_ephe_path(None)  # Use default ephemeris files

        # Metonic cycle constants
        self.YEARS_PER_METONIC_CYCLE = 19
        self.SYNODIC_MONTH_DAYS = 29.53059  # Average length of a synodic month

        # Constants for solar events
        self.SPRING_EQUINOX = 0
        self.SUMMER_SOLSTICE = 1
        self.FALL_EQUINOX = 2
        self.WINTER_SOLSTICE = 3

        logger.debug("KameaAstronomicalService initialized")

    def get_lunar_phase(self, target_date: date) -> Dict:
        """Get the lunar phase for a specific date.

        Args:
            target_date: The date to calculate the lunar phase for

        Returns:
            Dictionary with lunar phase data including phase angle and name
        """
        # Convert date to datetime at noon (to avoid time zone issues)
        dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))

        # Get positions of Sun and Moon
        sun_pos = self.astro_service.get_planet_position(swe.SUN, dt)
        moon_pos = self.astro_service.get_planet_position(swe.MOON, dt)

        # Calculate phase angle (difference in longitude)
        phase_angle = (moon_pos["longitude"] - sun_pos["longitude"]) % 360

        # Calculate illumination percentage (0-100)
        illumination = 50 * (1 - math.cos(math.radians(phase_angle)))

        # Determine phase name
        phase_name = self._get_phase_name(phase_angle)

        return {
            "date": target_date,
            "phase_angle": phase_angle,
            "illumination": illumination,
            "phase_name": phase_name,
            "is_new_moon": 0 <= phase_angle < 5 or 355 <= phase_angle < 360,
            "is_full_moon": 175 <= phase_angle < 185,
            "is_first_quarter": 85 <= phase_angle < 95,
            "is_last_quarter": 265 <= phase_angle < 275,
        }

    def _get_phase_name(self, phase_angle: float) -> str:
        """Get the name of the lunar phase based on the phase angle.

        Args:
            phase_angle: The lunar phase angle in degrees

        Returns:
            String name of the lunar phase
        """
        if 0 <= phase_angle < 5 or 355 <= phase_angle < 360:
            return "New Moon"
        elif 5 <= phase_angle < 85:
            return "Waxing Crescent"
        elif 85 <= phase_angle < 95:
            return "First Quarter"
        elif 95 <= phase_angle < 175:
            return "Waxing Gibbous"
        elif 175 <= phase_angle < 185:
            return "Full Moon"
        elif 185 <= phase_angle < 265:
            return "Waning Gibbous"
        elif 265 <= phase_angle < 275:
            return "Last Quarter"
        else:  # 275 <= phase_angle < 355
            return "Waning Crescent"

    def find_lunar_phase_events(
        self, start_date: date, end_date: date
    ) -> Dict[str, List[date]]:
        """Find all key lunar events between two dates.

        Args:
            start_date: Start date for the search
            end_date: End date for the search

        Returns:
            Dictionary mapping event types to lists of dates
        """
        events = {
            "new_moon": [],
            "full_moon": [],
            "first_quarter": [],
            "last_quarter": [],
        }

        # Start with getting lunar phases for each day
        current = start_date
        while current <= end_date:
            phase = self.get_lunar_phase(current)

            # Check for lunar events
            if phase["is_new_moon"]:
                events["new_moon"].append(current)
            elif phase["is_full_moon"]:
                events["full_moon"].append(current)
            elif phase["is_first_quarter"]:
                events["first_quarter"].append(current)
            elif phase["is_last_quarter"]:
                events["last_quarter"].append(current)

            current += timedelta(days=1)

        return events

    def get_solar_events(self, year: int) -> Dict[str, date]:
        """Get major solar events (solstices, equinoxes) for a specific year.

        Args:
            year: Year to calculate events for

        Returns:
            Dictionary with dates of solar events
        """
        events = {}

        # Spring equinox
        events["spring_equinox"] = self._find_solar_event(year, self.SPRING_EQUINOX)

        # Summer solstice
        events["summer_solstice"] = self._find_solar_event(year, self.SUMMER_SOLSTICE)

        # Fall equinox
        events["fall_equinox"] = self._find_solar_event(year, self.FALL_EQUINOX)

        # Winter solstice
        events["winter_solstice"] = self._find_solar_event(year, self.WINTER_SOLSTICE)

        return events

    def _find_solar_event(self, year: int, event_type: int) -> date:
        """Find the date of a specific solar event in a year.

        Args:
            year: Year to calculate the event for
            event_type: Type of solar event (0=spring, 1=summer, 2=fall, 3=winter)

        Returns:
            Date of the solar event
        """
        # Use Swiss Ephemeris to find the Julian day for the event
        jd_start = swe.julday(year, 1, 1, 0)

        # For calculating equinoxes and solstices
        # Convert our event_type to the appropriate longitude to search for
        if event_type == self.SPRING_EQUINOX:  # Spring equinox - Sun at 0° Aries
            target_longitude = 0
        elif (
            event_type == self.SUMMER_SOLSTICE
        ):  # Summer solstice - Sun at 0° Cancer (90°)
            target_longitude = 90
        elif event_type == self.FALL_EQUINOX:  # Fall equinox - Sun at 0° Libra (180°)
            target_longitude = 180
        elif (
            event_type == self.WINTER_SOLSTICE
        ):  # Winter solstice - Sun at 0° Capricorn (270°)
            target_longitude = 270
        else:
            raise ValueError(f"Invalid solar event type: {event_type}")

        # Find when the Sun crosses this longitude
        jd_event = swe.solcross_ut(target_longitude, jd_start, swe.FLG_SWIEPH)

        # Convert Julian day to calendar date
        y, m, d, h = swe.revjul(jd_event)

        return date(y, m, d)

    def get_metonic_cycle_data(self, target_date: date) -> Dict:
        """Get Metonic cycle information for a specific date.

        Args:
            target_date: Date to get cycle data for

        Returns:
            Dictionary with Metonic cycle data
        """
        # Determine current Metonic cycle
        cycle_start_year = target_date.year - (
            target_date.year % self.YEARS_PER_METONIC_CYCLE
        )
        cycle_end_year = cycle_start_year + self.YEARS_PER_METONIC_CYCLE - 1

        # Calculate position in cycle
        years_into_cycle = target_date.year - cycle_start_year
        days_into_year = (target_date - date(target_date.year, 1, 1)).days + 1

        # Calculate lunar data
        lunar_phase = self.get_lunar_phase(target_date)

        # Calculate lunar month number
        # Approximate calculation - more precise calculations would use full ephemeris data
        days_since_cycle_start = (target_date - date(cycle_start_year, 1, 1)).days
        lunar_month = int(days_since_cycle_start / self.SYNODIC_MONTH_DAYS) % 235

        return {
            "date": target_date,
            "cycle_start_year": cycle_start_year,
            "cycle_end_year": cycle_end_year,
            "years_into_cycle": years_into_cycle,
            "days_into_year": days_into_year,
            "lunar_phase": lunar_phase,
            "lunar_month": lunar_month,
            "lunar_day": int(
                lunar_phase["phase_angle"] / (360 / 30)
            ),  # Approximation of lunar day (1-30)
        }

    def find_special_days_in_range(
        self, start_date: date, end_date: date
    ) -> Dict[date, List[str]]:
        """Find special astronomical days in a date range.

        Args:
            start_date: Start date for the search
            end_date: End date for the search

        Returns:
            Dictionary mapping dates to lists of special events
        """
        special_days = {}

        # Find lunar events
        lunar_events = self.find_lunar_phase_events(start_date, end_date)

        # Add lunar events to special days
        for event_type, dates in lunar_events.items():
            for event_date in dates:
                if event_date not in special_days:
                    special_days[event_date] = []
                special_days[event_date].append(event_type)

        # Find solar events for each year in range
        for year in range(start_date.year, end_date.year + 1):
            solar_events = self.get_solar_events(year)

            # Add solar events to special days
            for event_type, event_date in solar_events.items():
                if start_date <= event_date <= end_date:
                    if event_date not in special_days:
                        special_days[event_date] = []
                    special_days[event_date].append(event_type)

        return special_days
