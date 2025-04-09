"""
Accurate moon phase calculator using astronomical algorithms.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
import ephem  # PyEphem for accurate astronomical calculations
from loguru import logger

from astrology.models.planner import PlannerEvent, EventType
from astrology.services.location_service import Location

def calculate_moon_phases_for_month(year: int, month: int, get_zodiac_sign_func, default_location: Optional[Location] = None) -> List[PlannerEvent]:
    """Calculate moon phases for a specific month using accurate astronomical calculations.

    Args:
        year: Year
        month: Month (1-12)
        get_zodiac_sign_func: Function to get zodiac sign from a datetime
        default_location: Optional default location to adjust timezone (default: None, uses UTC)

    Returns:
        List of moon phase events
    """
    logger.debug(f"Calculating moon phases for {year}-{month} using astronomical calculations")

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
        (ephem.next_last_quarter_moon, "Last Quarter Moon", "#808080")  # Gray
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
            phase_datetime_utc = datetime.strptime(str(next_phase_date), '%Y/%m/%d %H:%M:%S')
            phase_datetime_utc = phase_datetime_utc.replace(tzinfo=timezone.utc)

            # Adjust for timezone if a default location is provided
            if default_location:
                # Estimate timezone offset based on longitude
                # Each 15 degrees of longitude corresponds to 1 hour of time difference
                estimated_offset = default_location.longitude / 15.0
                # Round to the nearest hour for simplicity
                offset_hours = round(estimated_offset)
                phase_datetime = phase_datetime_utc + timedelta(hours=offset_hours)
                logger.debug(f"Adjusted time from UTC to {offset_hours:+d} hours (estimated from longitude {default_location.longitude:.2f}) for {default_location.name}")
            else:
                # Use UTC time if no location is provided
                phase_datetime = phase_datetime_utc

            # Check if this phase occurs in our target month
            if phase_datetime.year == year and phase_datetime.month == month:
                # Get zodiac sign using the provided function
                zodiac_sign = get_zodiac_sign_func(phase_datetime)

                # Convert back to naive datetime to maintain compatibility with the rest of the code
                # We've already adjusted for timezone, so we just need to remove the timezone info
                naive_datetime = datetime(phase_datetime.year, phase_datetime.month, phase_datetime.day,
                                         phase_datetime.hour, phase_datetime.minute, phase_datetime.second)

                # Create event for this moon phase
                events.append(PlannerEvent(
                    title=phase_name,
                    description=f"{phase_name} in {zodiac_sign}",
                    event_type=EventType.MOON_PHASE,
                    start_time=naive_datetime,
                    color=color
                ))

                logger.debug(f"Added {phase_name} on {phase_datetime.date()} in {zodiac_sign}")

            # Move past this phase to avoid finding it again
            # Add a small increment to ensure we don't get the same phase again
            current_date = ephem.Date(next_phase_date + 1)

    # Sort events by date
    events.sort(key=lambda x: x.start_time)

    # Log the events found
    logger.debug(f"Found {len(events)} moon phase events for {year}-{month}")

    return events
