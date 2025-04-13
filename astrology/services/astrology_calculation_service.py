"""
Purpose: Provides astrological calculations using Swiss Ephemeris with caching.

This file is part of the astrology pillar and serves as a calculation service.
It handles planetary positions, aspects, and other astrological calculations.
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import os
import math
import pytz

import swisseph as swe
from loguru import logger

from astrology.models.aspect import Aspect, AspectType, AspectInfo


class AstrologyCalculationService:
    """Service for astrological calculations using Swiss Ephemeris directly with selective caching."""

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the service with optional cache directory.

        Args:
            cache_dir: Directory to store cache files (optional)
        """
        # Initialize Swiss Ephemeris
        swe.set_ephe_path(None)  # Use default ephemeris files

        # Set up caching
        self.cache_dir = cache_dir
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Initialize in-memory caches
        self.position_cache = {}
        self.aspect_cache = {}
        
        # Initialize repository for database storage (we'll set this later)
        self.repository = None

        # Define planets
        self.planets = [
            (swe.SUN, "Sun"),
            (swe.MOON, "Moon"),
            (swe.MERCURY, "Mercury"),
            (swe.VENUS, "Venus"),
            (swe.MARS, "Mars"),
            (swe.JUPITER, "Jupiter"),
            (swe.SATURN, "Saturn"),
            (swe.URANUS, "Uranus"),
            (swe.NEPTUNE, "Neptune"),
            (swe.PLUTO, "Pluto")
        ]

        # Define aspects with their default orbs and types
        # Format: (angle, AspectType, color, default_orb)

        # Major aspects (traditional)
        self.major_aspects = [
            (0, AspectType.CONJUNCTION, "#FF0000", 8.0),    # Red
            (60, AspectType.SEXTILE, "#00FF00", 4.0),       # Green
            (90, AspectType.SQUARE, "#FF0000", 8.0),        # Red
            (120, AspectType.TRINE, "#00FF00", 8.0),        # Green
            (180, AspectType.OPPOSITION, "#FF0000", 8.0)    # Red
        ]

        # Minor aspects
        self.minor_aspects = [
            (30, AspectType.SEMISEXTILE, "#AAFFAA", 2.0),    # Light Green
            (45, AspectType.SEMISQUARE, "#FFAAAA", 2.0),     # Light Red
            (135, AspectType.SESQUISQUARE, "#FFAAAA", 2.0),  # Light Red
            (150, AspectType.QUINCUNX, "#FFAAAA", 3.0)       # Light Red
        ]

        # Combine all aspects
        self.aspects = self.major_aspects + self.minor_aspects

        logger.debug("AstrologyCalculationService initialized")

    def get_planet_position(self, planet_id: int, date_time: datetime) -> Dict:
        """Get the position of a planet at a specific date and time.

        Args:
            planet_id: Swiss Ephemeris planet ID
            date_time: Date and time to calculate position for

        Returns:
            Dictionary with planetary position data
        """
        # Check cache first
        cache_key = f"{planet_id}_{date_time.isoformat()}"
        if cache_key in self.position_cache:
            return self.position_cache[cache_key]

        # Calculate position using Swiss Ephemeris
        jd = self._datetime_to_jd(date_time)
        result = swe.calc_ut(jd, planet_id)

        position = {
            'longitude': result[0][0],
            'latitude': result[0][1],
            'distance': result[0][2],
            'speed_longitude': result[0][3],
            'speed_latitude': result[0][4],
            'zodiac_sign': self._get_zodiac_sign(result[0][0]),
            'zodiac_degree': result[0][0] % 30,
            'is_retrograde': result[0][3] < 0
        }

        # Cache the result
        self.position_cache[cache_key] = position

        return position

    def get_all_planet_positions(self, date_time: datetime) -> Dict[str, Dict]:
        """Get positions of all major planets at a specific date and time.

        Args:
            date_time: Date and time to calculate positions for

        Returns:
            Dictionary mapping planet names to position data
        """
        positions = {}
        for planet_id, planet_name in self.planets:
            positions[planet_name] = self.get_planet_position(planet_id, date_time)

        return positions

    def get_aspects_for_date(self, date: datetime.date, orb: float = 1.0,
                          include_major: bool = True, include_minor: bool = True,
                          timezone: str = 'UTC') -> List[Dict]:
        """Get all planetary aspects that become exact on a specific date.

        Args:
            date: Date to calculate aspects for
            orb: Maximum orb to consider (in degrees)
            include_major: Whether to include major aspects
            include_minor: Whether to include minor aspects
            timezone: Timezone to use for calculations (default: 'UTC')

        Returns:
            List of aspect dictionaries
        """
        # Convert date to datetime at midnight in specified timezone
        tz = pytz.timezone(timezone)
        local_midnight = tz.localize(datetime.combine(date, time.min))
        utc_midnight = local_midnight.astimezone(pytz.UTC)

        # Check cache using timezone-aware key
        cache_key = f"{date.isoformat()}_{orb}_{timezone}"
        if cache_key in self.aspect_cache:
            return self.aspect_cache[cache_key]

        # Calculate aspects with improved time precision
        all_aspects = self._calculate_aspects_for_date(date, orb, timezone)

        # Cache the results
        self.aspect_cache[cache_key] = all_aspects

        # Filter aspects based on type
        if include_major and include_minor:
            return all_aspects
        elif include_major:
            return [a for a in all_aspects if a['is_major']]
        elif include_minor:
            return [a for a in all_aspects if not a['is_major']]
        else:
            return []

    def _calculate_aspects_for_date(self, date: datetime.date, orb: float = 1.0,
                                 timezone: str = 'UTC') -> List[Dict]:
        """Calculate all planetary aspects that become exact on a specific date.

        Args:
            date: Date to calculate aspects for
            orb: Maximum orb to consider (in degrees)
            timezone: Timezone to use for calculations

        Returns:
            List of aspect dictionaries
        """
        aspects = []
        tz = pytz.timezone(timezone)
        
        # Convert to timezone-aware datetime
        start_time = tz.localize(datetime.combine(date, time.min))
        end_time = tz.localize(datetime.combine(date, time.max))

        # Check every hour for potential aspects
        current_time = start_time
        while current_time <= end_time:
            # For each pair of planets
            for i, (planet1_id, planet1_name) in enumerate(self.planets):
                for planet2_id, planet2_name in self.planets[i+1:]:
                    # For each aspect type
                    for angle, aspect_type, color, default_orb in self.aspects:
                        # Use the smaller of the default orb or specified orb
                        aspect_orb = min(orb, default_orb)

                        # Get positions at current time
                        pos1 = self.get_planet_position(planet1_id, current_time)
                        pos2 = self.get_planet_position(planet2_id, current_time)

                        # Calculate angular separation
                        separation = abs(pos1['longitude'] - pos2['longitude']) % 360
                        if separation > 180:
                            separation = 360 - separation

                        # Check if within orb of aspect
                        aspect_diff = abs(separation - angle)
                        if aspect_diff <= aspect_orb:
                            # Refine exact time using binary search
                            exact_time = self._find_exact_aspect_time(
                                planet1_id, planet2_id, angle,
                                current_time - timedelta(hours=1),
                                current_time + timedelta(hours=1)
                            )

                            if exact_time and exact_time.date() == date:
                                # Create aspect object with precise timing
                                aspect = {
                                    'body1': planet1_name,
                                    'body2': planet2_name,
                                    'aspect_type': aspect_type,
                                    'angle': angle,
                                    'orb': aspect_diff,
                                    'exact_angle': separation,
                                    'time': exact_time,
                                    'body1_position': pos1,
                                    'body2_position': pos2,
                                    'is_major': angle in [0, 60, 90, 120, 180],
                                    'color': color
                                }
                                aspects.append(aspect)

            # Move to next hour
            current_time += timedelta(hours=1)

        return aspects

    def _find_exact_aspect_time(self, planet1_id: int, planet2_id: int,
                             target_angle: float, start_time: datetime,
                             end_time: datetime, precision: float = 1/60) -> Optional[datetime]:
        """Find the exact time an aspect becomes exact using binary search.

        Args:
            planet1_id: First planet's ID
            planet2_id: Second planet's ID
            target_angle: Target aspect angle
            start_time: Start of search window
            end_time: End of search window
            precision: Desired precision in hours (default: 1 minute)

        Returns:
            Datetime of exact aspect, or None if not found
        """
        while (end_time - start_time) > timedelta(hours=precision):
            mid_time = start_time + (end_time - start_time) / 2

            # Get positions at midpoint
            pos1 = self.get_planet_position(planet1_id, mid_time)
            pos2 = self.get_planet_position(planet2_id, mid_time)

            # Calculate separation
            separation = abs(pos1['longitude'] - pos2['longitude']) % 360
            if separation > 180:
                separation = 360 - separation

            # Check which half contains the exact aspect
            if abs(separation - target_angle) < 0.01:  # Found exact aspect
                return mid_time
            elif separation < target_angle:
                start_time = mid_time
            else:
                end_time = mid_time

        return start_time + (end_time - start_time) / 2

    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert Python datetime to Julian day.

        Args:
            dt: Datetime to convert

        Returns:
            Julian day number
        """
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

    def _get_zodiac_sign(self, longitude: float) -> str:
        """Get zodiac sign from ecliptic longitude.

        Args:
            longitude: Ecliptic longitude in degrees (0-360)

        Returns:
            Zodiac sign name
        """
        # Normalize longitude to 0-360 range
        longitude = longitude % 360

        # Define zodiac signs and their starting longitudes
        zodiac_signs = [
            (0, "Aries"),
            (30, "Taurus"),
            (60, "Gemini"),
            (90, "Cancer"),
            (120, "Leo"),
            (150, "Virgo"),
            (180, "Libra"),
            (210, "Scorpio"),
            (240, "Sagittarius"),
            (270, "Capricorn"),
            (300, "Aquarius"),
            (330, "Pisces")
        ]

        # Find the appropriate zodiac sign
        for i, (start_long, sign) in enumerate(zodiac_signs):
            next_idx = (i + 1) % 12
            next_start = zodiac_signs[next_idx][0]

            # Handle the case where we wrap around from Pisces to Aries
            if next_start < start_long:  # We're at Pisces
                if longitude >= start_long or longitude < next_start:
                    return sign
            else:
                if start_long <= longitude < next_start:
                    return sign

        # This should never happen, but just in case
        return "Unknown"

    def set_repository(self, repository):
        """Set the repository for database storage.
        
        Args:
            repository: AstrologicalEventsRepository instance
        """
        self.repository = repository
        logger.debug("Repository set for AstrologyCalculationService")

    def calculate_and_store_aspects(self, start_year: int, end_year: int, 
                                   include_major: bool = True, 
                                   include_minor: bool = False,
                                   orb: float = 1.0) -> Dict:
        """Calculate and store aspects in the database for a specified time range.
        
        This method calculates planetary aspects for each day in the specified range
        and stores them in the database for efficient retrieval later.
        
        Args:
            start_year: Starting year for the calculation
            end_year: Ending year for the calculation
            include_major: Whether to include major aspects (default: True)
            include_minor: Whether to include minor aspects (default: False)
            orb: Maximum orb to consider for aspects (in degrees)
            
        Returns:
            Dictionary with statistics about the calculations
        """
        if not self.repository:
            raise ValueError("Repository not set. Call set_repository first.")
        
        # Initialize statistics
        stats = {
            "years_processed": 0,
            "days_processed": 0,
            "aspects_found": 0,
            "aspects_stored": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "status": "in_progress"
        }
        
        try:
            logger.info(f"Starting aspect calculation for {start_year}-{end_year}")
            
            # Process each year
            for year in range(start_year, end_year + 1):
                year_start = datetime.now()
                logger.info(f"Processing aspects for year {year}...")
                
                year_aspects = 0
                days_in_year = 366 if self._is_leap_year(year) else 365
                
                # Insert all aspects for this year in a single transaction for better performance
                with self.repository.database.transaction() as conn:
                    # Calculate aspects for each day in the year
                    for day in range(1, days_in_year + 1):
                        # Create date object from year and day of year
                        try:
                            date = datetime.strptime(f"{year}-{day}", "%Y-%j").date()
                        except ValueError:
                            # Skip invalid dates (shouldn't happen if days_in_year is correct)
                            continue
                        
                        # Calculate aspects for this day
                        aspects = self.get_aspects_for_date(
                            date=date,
                            orb=orb,
                            include_major=include_major,
                            include_minor=include_minor
                        )
                        
                        if aspects:
                            logger.debug(f"Found {len(aspects)} aspects for {date}")
                        
                        # First check if we have celestial bodies and add any missing ones
                        planet_ids = {}
                        for aspect in aspects:
                            for planet_name in [aspect['body1'], aspect['body2']]:
                                if planet_name not in planet_ids:
                                    # Try to find in DB
                                    result = conn.execute(
                                        "SELECT id FROM celestial_bodies WHERE name = ?", 
                                        (planet_name,)
                                    ).fetchone()
                                    
                                    if result:
                                        planet_ids[planet_name] = result[0]
                                    else:
                                        # Add to DB
                                        cursor = conn.execute(
                                            "INSERT INTO celestial_bodies (name, type) VALUES (?, 'planet')",
                                            (planet_name,)
                                        )
                                        planet_ids[planet_name] = cursor.lastrowid
                        
                        # Store each aspect in the database
                        for aspect in aspects:
                            try:
                                # Get celestial body IDs
                                body1_id = planet_ids[aspect['body1']]
                                body2_id = planet_ids[aspect['body2']]
                                
                                # Always store aspects with the lower ID planet first
                                if body1_id > body2_id:
                                    body1_id, body2_id = body2_id, body1_id
                                
                                # Get aspect type and determine if major
                                aspect_type = aspect['aspect_type']
                                is_major = True
                                for _, aspect_enum, _, _ in self.minor_aspects:
                                    if aspect_type == aspect_enum.value:
                                        is_major = False
                                        break
                                
                                # Format the exact timestamp
                                exact_time = aspect['time']
                                if isinstance(exact_time, datetime):
                                    exact_timestamp = exact_time.isoformat()
                                else:
                                    # If it's a string already, use as is
                                    exact_timestamp = exact_time
                                
                                # Get positions
                                body1_position = aspect['body1_position']['longitude'] if 'body1_position' in aspect else 0.0
                                body2_position = aspect['body2_position']['longitude'] if 'body2_position' in aspect else 0.0
                                
                                # Insert the aspect into the database - use REPLACE to handle duplicates
                                conn.execute("""
                                INSERT OR REPLACE INTO aspects (
                                    body1_id, body2_id, aspect_type, is_major, year,
                                    exact_timestamp, exact_position1, exact_position2
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    body1_id, 
                                    body2_id, 
                                    aspect_type,
                                    1 if is_major else 0,
                                    year,
                                    exact_timestamp,
                                    body1_position,
                                    body2_position
                                ))
                                
                                year_aspects += 1
                                stats["aspects_stored"] += 1
                                stats["aspects_found"] += 1
                            except Exception as e:
                                logger.error(f"Error storing aspect: {e}", exc_info=True)
                        
                        stats["days_processed"] += 1
                        
                        # Log progress periodically
                        if day % 30 == 0:
                            logger.debug(f"Processed {day}/{days_in_year} days in {year}")
                    
                    # Update calculation metadata in database while still in transaction
                    conn.execute("""
                    INSERT OR REPLACE INTO calculation_metadata (
                        start_year, end_year, calculation_timestamp, status, events_count
                    ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        year, 
                        year, 
                        datetime.now().isoformat(), 
                        "completed", 
                        year_aspects
                    ))
                
                stats["years_processed"] += 1
                
                year_end = datetime.now()
                year_duration = (year_end - year_start).total_seconds()
                logger.info(f"Completed {year}: {year_aspects} aspects in {year_duration:.1f} seconds")
            
            stats["status"] = "completed"
        except Exception as e:
            logger.error(f"Error calculating aspects: {e}", exc_info=True)
            stats["status"] = "error"
        finally:
            stats["end_time"] = datetime.now()
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["duration"] = duration
            
            logger.info(f"Aspect calculation completed in {duration:.1f} seconds")
            logger.info(f"Processed {stats['years_processed']} years, {stats['days_processed']} days")
            logger.info(f"Found {stats['aspects_found']} aspects, stored {stats['aspects_stored']} in database")
            
            return stats
        
    def _is_leap_year(self, year: int) -> bool:
        """Check if a year is a leap year.
        
        Args:
            year: Year to check
            
        Returns:
            True if the year is a leap year, False otherwise
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def _get_or_create_celestial_body(self, body_name: str) -> int:
        """Get the ID of a celestial body from the database, creating it if it doesn't exist.
        
        Args:
            body_name: Name of the celestial body
            
        Returns:
            Database ID of the celestial body
        """
        if not self.repository:
            raise ValueError("Repository not set")
        
        # Try to get existing ID
        result = self.repository.database.query_one(
            "SELECT id FROM celestial_bodies WHERE name = ?",
            (body_name,)
        )
        
        if result:
            return result['id']
        
        # Create new record if not found
        with self.repository.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO celestial_bodies (name, type) VALUES (?, 'planet')",
                (body_name,)
            )
            return cursor.lastrowid

    def _update_calculation_metadata(self, start_year: int, end_year: int, events_count: int) -> None:
        """Update calculation metadata in the database.
        
        Args:
            start_year: Start year of the calculation range
            end_year: End year of the calculation range
            events_count: Number of events calculated
        """
        if not self.repository:
            return
        
        try:
            self.repository.database.execute("""
            INSERT OR REPLACE INTO calculation_metadata (
                start_year, end_year, calculation_timestamp, status, events_count
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                start_year, 
                end_year, 
                datetime.now().isoformat(), 
                "completed", 
                events_count
            ))
        except Exception as e:
            logger.error(f"Error updating calculation metadata: {e}")
