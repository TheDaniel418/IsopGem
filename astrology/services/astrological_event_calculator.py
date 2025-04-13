"""
Purpose: Calculates astrological events for storage in the database.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to calculate long-term astronomical events like
planetary aspects, moon phases, eclipses, and planetary cycles. These events
are calculated once and stored in the database for efficient retrieval.

Key components:
- AstrologicalEventCalculator: Service for calculating astronomical events

Dependencies:
- swisseph: For astronomical calculations
- astrology.repositories.astrological_events_repository: For event storage
"""

import math
import calendar
import time
from datetime import datetime, timedelta, date
from enum import Enum
from typing import Callable, Dict, List, Optional, Any
from pathlib import Path

from loguru import logger
import swisseph as swe

from astrology.repositories.astrological_events_repository import AstrologicalEventsRepository
from shared.services.singleton_service import SingletonService
from shared.repositories.database import Database

class AspectType(Enum):
    """Types of planetary aspects."""
    CONJUNCTION = "conjunction"
    OPPOSITION = "opposition"
    TRINE = "trine"
    SQUARE = "square"
    SEXTILE = "sextile"
    SEMISEXTILE = "semisextile"
    QUINCUNX = "quincunx"
    SESQUIQUADRATE = "sesquiquadrate"
    SEMISQUARE = "semisquare"
    QUINTILE = "quintile"
    BIQUINTILE = "biquintile"

class LunarPhaseType(Enum):
    """Types of lunar phases."""
    NEW_MOON = "new_moon"
    WAXING_CRESCENT = "waxing_crescent"
    FIRST_QUARTER = "first_quarter"
    WAXING_GIBBOUS = "waxing_gibbous"
    FULL_MOON = "full_moon"
    WANING_GIBBOUS = "waning_gibbous"
    LAST_QUARTER = "last_quarter"
    WANING_CRESCENT = "waning_crescent"

class SolarEventType(Enum):
    """Types of solar events."""
    SPRING_EQUINOX = "spring_equinox"
    SUMMER_SOLSTICE = "summer_solstice"
    FALL_EQUINOX = "fall_equinox"
    WINTER_SOLSTICE = "winter_solstice"

class PlanetPhaseType(Enum):
    """Types of planetary phases for Mercury and Venus."""
    SUPERIOR_CONJUNCTION = "superior_conjunction"
    INFERIOR_CONJUNCTION = "inferior_conjunction"
    GREATEST_EASTERN_ELONGATION = "greatest_eastern_elongation"
    GREATEST_WESTERN_ELONGATION = "greatest_western_elongation"
    STATIONARY_DIRECT = "stationary_direct"
    STATIONARY_RETROGRADE = "stationary_retrograde"

class EclipseType(Enum):
    """Types of eclipses."""
    SOLAR_TOTAL = "solar_total"
    SOLAR_ANNULAR = "solar_annular"
    SOLAR_PARTIAL = "solar_partial"
    LUNAR_TOTAL = "lunar_total"
    LUNAR_PARTIAL = "lunar_partial"
    LUNAR_PENUMBRAL = "lunar_penumbral"

# Define aspect angles and orbs
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
    AspectType.BIQUINTILE: 144.0
}

# Define which aspects are major/minor
MAJOR_ASPECTS = {
    AspectType.CONJUNCTION,
    AspectType.OPPOSITION,
    AspectType.TRINE,
    AspectType.SQUARE,
    AspectType.SEXTILE
}

# Define orbs for aspects
MAJOR_ASPECT_ORB = 6.0  # 6 degrees for major aspects
MINOR_ASPECT_ORB = 2.0  # 2 degrees for minor aspects

class AstrologicalEventCalculator(SingletonService):
    """Service for calculating and storing astrological events."""

    DEFAULT_RANGE = (1900, 2100)
    
    # Swiss Ephemeris planet IDs
    PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
        "North Node": swe.MEAN_NODE  # Using mean node
    }
    
    # Planet pairs for aspects
    ASPECT_PAIRS = [
        ("Sun", "Moon"),
        ("Sun", "Mercury"),
        ("Sun", "Venus"),
        ("Sun", "Mars"),
        ("Sun", "Jupiter"),
        ("Sun", "Saturn"),
        ("Sun", "Uranus"),
        ("Sun", "Neptune"),
        ("Sun", "Pluto"),
        ("Sun", "North Node"),
        ("Moon", "Mercury"),
        ("Moon", "Venus"),
        ("Moon", "Mars"),
        ("Moon", "Jupiter"),
        ("Moon", "Saturn"),
        ("Moon", "Uranus"),
        ("Moon", "Neptune"),
        ("Moon", "Pluto"),
        ("Moon", "North Node"),
        ("Mercury", "Venus"),
        ("Mercury", "Mars"),
        ("Mercury", "Jupiter"),
        ("Mercury", "Saturn"),
        ("Mercury", "Uranus"),
        ("Mercury", "Neptune"),
        ("Mercury", "Pluto"),
        ("Mercury", "North Node"),
        ("Venus", "Mars"),
        ("Venus", "Jupiter"),
        ("Venus", "Saturn"),
        ("Venus", "Uranus"),
        ("Venus", "Neptune"),
        ("Venus", "Pluto"),
        ("Venus", "North Node"),
        ("Mars", "Jupiter"),
        ("Mars", "Saturn"),
        ("Mars", "Uranus"),
        ("Mars", "Neptune"),
        ("Mars", "Pluto"),
        ("Mars", "North Node"),
        ("Jupiter", "Saturn"),
        ("Jupiter", "Uranus"),
        ("Jupiter", "Neptune"),
        ("Jupiter", "Pluto"),
        ("Jupiter", "North Node"),
        ("Saturn", "Uranus"),
        ("Saturn", "Neptune"),
        ("Saturn", "Pluto"),
        ("Saturn", "North Node"),
        ("Uranus", "Neptune"),
        ("Uranus", "Pluto"),
        ("Uranus", "North Node"),
        ("Neptune", "Pluto"),
        ("Neptune", "North Node"),
        ("Pluto", "North Node")
    ]
    
    # Zodiac signs
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    def __init__(self, repository=None, ephemeris_path=None):
        """Initialize the calculator.
        
        Args:
            repository: Repository for storing calculated events (optional, will create default if None)
            ephemeris_path: Path to the Swiss Ephemeris files (optional)
        """
        super().__init__()
        
        # Create default repository if none provided
        if repository is None:
            repository = AstrologicalEventsRepository(Database.get_instance())
            
        self.repository = repository
        
        # Initialize Swiss Ephemeris
        try:
            if ephemeris_path:
                logger.info(f"Setting Swiss Ephemeris path to: {ephemeris_path}")
                swe.set_ephe_path(ephemeris_path)
            else:
                # Try to find ephemeris files
                app_dir = Path.home() / ".isopgem"
                ephe_dir = app_dir / "ephemeris"
                
                if ephe_dir.exists():
                    logger.info(f"Using ephemeris files from: {ephe_dir}")
                    swe.set_ephe_path(str(ephe_dir))
                else:
                    # Fall back to JPL ephemeris data
                    logger.info("No ephemeris path specified, using built-in data")
                    swe.set_ephe_path()
                    
            # Test if Swiss Ephemeris works by calculating Sun position
            test_jd = swe.julday(2000, 1, 1, 12)
            result = swe.calc_ut(test_jd, swe.SUN, swe.FLG_SWIEPH)
            logger.info(f"Swiss Ephemeris initialized successfully. Test Sun position: {result[0]}")
        except Exception as e:
            logger.error(f"Error initializing Swiss Ephemeris: {e}", exc_info=True)
            logger.warning("Some astrological calculations may be inaccurate")
        
        # Set calculation flags
        self.geo_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        self.helio_flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_HELCTR
        
        # Set progress tracking
        self.progress_callback = None
        self.total_progress = 0
        self.current_progress = 0
        
        logger.debug("AstrologicalEventCalculator initialized")
    
    def set_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        """Set callback for progress updates.
        
        Args:
            callback: Function to call with progress percentage and message
        """
        self.progress_callback = callback
    
    def _update_progress(self, percentage: float, message: str) -> None:
        """Update progress and call callback if set.
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        if self.progress_callback:
            self.progress_callback(percentage, message)
    
    def calculate_range(self, start_year: int, end_year: int) -> bool:
        """Calculate all events for a range of years.
        
        Args:
            start_year: First year to calculate
            end_year: Last year to calculate (inclusive)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Start calculation and record in metadata
            calculation_start = datetime.now()
            self.repository.database.execute("""
            INSERT OR REPLACE INTO calculation_metadata 
            (start_year, end_year, calculation_timestamp, status, events_count) 
            VALUES (?, ?, ?, ?, ?)
            """, (start_year, end_year, calculation_start.isoformat(), "in_progress", 0))
            
            # Ensure all celestial bodies are in the database
            self._ensure_celestial_bodies_exist()
            
            # Initialize progress tracking
            total_years = end_year - start_year + 1
            self.total_progress = total_years * 5  # 5 calculation types per year
            self.current_progress = 0
            
            # Calculate year by year
            event_count = 0
            for year in range(start_year, end_year + 1):
                # Calculate all event types for this year
                self._update_progress(self.current_progress / self.total_progress * 100, 
                                     f"Calculating aspects for {year}")
                try:
                    count = self._calculate_aspects_for_year(year)
                    event_count += count
                    logger.info(f"Successfully calculated {count} aspects for {year}")
                except Exception as e:
                    logger.error(f"Error calculating aspects for {year}: {e}", exc_info=True)
                self.current_progress += 1
                
                self._update_progress(self.current_progress / self.total_progress * 100, 
                                     f"Calculating lunar phases for {year}")
                count = self._calculate_lunar_phases_for_year(year)
                event_count += count
                self.current_progress += 1
                
                self._update_progress(self.current_progress / self.total_progress * 100, 
                                     f"Calculating planet phases for {year}")
                count = self._calculate_planet_phases_for_year(year)
                event_count += count
                self.current_progress += 1
                
                self._update_progress(self.current_progress / self.total_progress * 100, 
                                     f"Calculating eclipses for {year}")
                count = self._calculate_eclipses_for_year(year)
                event_count += count
                self.current_progress += 1
                
                self._update_progress(self.current_progress / self.total_progress * 100, 
                                     f"Calculating solar events for {year}")
                count = self._calculate_solar_events_for_year(year)
                event_count += count
                self.current_progress += 1
            
            # Update calculation metadata
            calculation_end = datetime.now()
            self.repository.database.execute("""
            UPDATE calculation_metadata 
            SET status = ?, events_count = ?, calculation_timestamp = ?
            WHERE start_year = ? AND end_year = ?
            """, ("complete", event_count, calculation_end.isoformat(), start_year, end_year))
            
            self._update_progress(100, "Calculation complete")
            logger.info(f"Calculated {event_count} events for years {start_year}-{end_year}")
            return True
            
        except Exception as e:
            logger.error(f"Error calculating range {start_year}-{end_year}: {e}", exc_info=True)
            # Mark calculation as failed
            self.repository.database.execute("""
            UPDATE calculation_metadata 
            SET status = ?
            WHERE start_year = ? AND end_year = ?
            """, ("failed", start_year, end_year))
            return False
    
    def _ensure_celestial_bodies_exist(self) -> None:
        """Ensure all celestial bodies used in calculations exist in the database."""
        with self.repository.database.transaction() as conn:
            for planet_name, planet_id in self.PLANETS.items():
                # Check if planet exists
                result = conn.execute("""
                    SELECT id FROM celestial_bodies WHERE name = ?
                """, (planet_name,)).fetchone()
                
                # If not, add it
                if not result:
                    conn.execute("""
                        INSERT INTO celestial_bodies (name, type)
                        VALUES (?, ?)
                    """, (planet_name, "planet"))
                    logger.info(f"Added celestial body {planet_name} to database")
        
        logger.debug("Ensured all celestial bodies exist in database")
    
    def _calculate_aspects_for_year(self, year: int) -> int:
        """Calculate all planetary aspects for a year.
        
        Args:
            year: Year to calculate
            
        Returns:
            Number of aspects calculated
        """
        logger.info(f"Starting aspect calculation for {year}")
        aspect_count = 0
        
        try:
            # Define the aspect configurations we want to track
            aspect_configs = [
                (AspectType.CONJUNCTION, 0.0, MAJOR_ASPECT_ORB),
                (AspectType.OPPOSITION, 180.0, MAJOR_ASPECT_ORB),
                (AspectType.TRINE, 120.0, MAJOR_ASPECT_ORB),
                (AspectType.SQUARE, 90.0, MAJOR_ASPECT_ORB),
                (AspectType.SEXTILE, 60.0, MAJOR_ASPECT_ORB),
                (AspectType.SEMISEXTILE, 30.0, MINOR_ASPECT_ORB),
                (AspectType.QUINCUNX, 150.0, MINOR_ASPECT_ORB),
                (AspectType.SESQUIQUADRATE, 135.0, MINOR_ASPECT_ORB),
                (AspectType.SEMISQUARE, 45.0, MINOR_ASPECT_ORB),
                (AspectType.QUINTILE, 72.0, MINOR_ASPECT_ORB),
                (AspectType.BIQUINTILE, 144.0, MINOR_ASPECT_ORB)
            ]
            
            # Define dates for the year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            
            # Step through the year (every 6 hours should be sufficient for most aspects)
            # For very fast-moving bodies like the Moon, we might miss some exact aspects,
            # but we'll still detect the general period
            step = timedelta(hours=6)
            current_date = start_date
            
            # Track aspects that we've found to avoid duplicates
            processed_aspects = {}  # key: (body1, body2, aspect_type, year, month)
            
            # Keep track of daily aspect pairs to avoid duplicate calculations
            # This will track which aspects we've already checked on a specific day
            checked_daily_aspects = set()  # set of (year, month, day, body1, body2, aspect_type)
            
            # Progress update frequency
            update_frequency = 100  # Update every 100 steps
            step_count = 0
            total_steps = (end_date - start_date) / step
            
            logger.debug(f"Starting aspect calculation loop for {year}")
            
            while current_date <= end_date:
                # Progress tracking
                step_count += 1
                if step_count % update_frequency == 0:
                    progress = (current_date - start_date) / (end_date - start_date) * 100
                    self._update_progress(
                        progress,
                        f"Calculating aspects for {year}: {current_date.strftime('%Y-%m-%d')}"
                    )
                
                # Get Julian day for current date
                jd = self._datetime_to_jd(current_date)
                
                # Current day identifier for skipping duplicates
                current_day = (year, current_date.month, current_date.day)
                
                # Get positions for all planets at this time
                planet_positions = {}
                for planet_name, planet_id in self.PLANETS.items():
                    try:
                        result = swe.calc_ut(jd, planet_id, self.geo_flags)
                        # Extract the longitude (first element) from the result tuple
                        # and then normalize it to 0-360 degrees
                        if isinstance(result, tuple) and len(result) > 0:
                            longitude = result[0]
                        else:
                            longitude = result
                        planet_positions[planet_name] = self._normalize_angle(longitude)
                    except swe.Error as e:
                        logger.error(f"SwissEph Error calculating position for {planet_name}: {e}")
                    except TypeError as e:
                        logger.error(f"Type Error calculating position for {planet_name}: {e}")
                    except Exception as e:
                        logger.error(f"Error calculating position for {planet_name}: {e}", exc_info=True)
                
                # Check for aspects between planet pairs
                for planet1, planet2 in self.ASPECT_PAIRS:
                    # Skip if we don't have positions for both planets
                    if planet1 not in planet_positions or planet2 not in planet_positions:
                        continue
                    
                    pos1 = planet_positions[planet1]
                    pos2 = planet_positions[planet2]
                    
                    # Calculate separation angle
                    separation = self._normalize_angle(abs(self._normalize_angle(pos1) - self._normalize_angle(pos2)))

                    # Check for aspects
                    for aspect_type, aspect_angle in ASPECT_ANGLES.items():
                        # Skip if we've already checked this combination today
                        daily_aspect_key = (*current_day, planet1, planet2, aspect_type.value)
                        if daily_aspect_key in checked_daily_aspects:
                            continue
                        
                        # Mark this combination as checked
                        checked_daily_aspects.add(daily_aspect_key)
                            
                        # Initialize include_minor and min_strength if not defined
                        include_minor = getattr(self, 'include_minor', True)
                        min_strength = getattr(self, 'min_strength', 50)
                        
                        # Skip minor aspects if not requested
                        if not include_minor and aspect_type not in MAJOR_ASPECTS:
                            continue
                            
                        # Calculate orb
                        orb = self._calculate_aspect_orb(self._normalize_angle(pos1), self._normalize_angle(pos2), aspect_type)
                        
                        # If within orb, add to results
                        if orb is not None:
                            # Calculate strength (100% = exact aspect, 0% = at maximum allowed orb)
                            max_orb = MAJOR_ASPECT_ORB if aspect_type in MAJOR_ASPECTS else MINOR_ASPECT_ORB
                            strength = 100 * (1 - orb / max_orb)
                            
                            # Only include aspects above minimum strength
                            if strength >= min_strength:
                                # Use the current date for the aspect event
                                aspect_date = current_date
                                # Use planet names from the planet_positions dictionary
                                p1, p2 = planet1, planet2
                                
                                # Generate key for processed_aspects to avoid duplicates
                                month = current_date.month
                                aspect_key = (p1, p2, aspect_type.value, year, month)
                                
                                # Create aspect event if not already processed or if this one is more exact
                                if aspect_key not in processed_aspects:
                                    processed_aspects[aspect_key] = {
                                        'first_seen': aspect_date,
                                        'exact_time': aspect_date,
                                        'last_seen': aspect_date,
                                        'exact_orb': orb,
                                        'exact_pos1': pos1,
                                        'exact_pos2': pos2
                                    }
                                    logger.debug(f"New aspect found: {p1} {aspect_type.name} {p2} ({orb:.2f}°)")
                                else:
                                    # Update if this is more exact than previously recorded
                                    if orb < processed_aspects[aspect_key]['exact_orb']:
                                        processed_aspects[aspect_key]['exact_time'] = aspect_date
                                        processed_aspects[aspect_key]['exact_orb'] = orb
                                        processed_aspects[aspect_key]['exact_pos1'] = pos1
                                        processed_aspects[aspect_key]['exact_pos2'] = pos2
                                    
                                    # Update last seen time
                                    processed_aspects[aspect_key]['last_seen'] = aspect_date
                
                # Move to next time step
                current_date += step
                
                # Periodically clear the daily aspect check cache to prevent memory buildup
                # Reset at the beginning of each month
                if current_date.day == 1 and current_date.hour < 6:
                    checked_daily_aspects.clear()
            
            logger.info(f"Found {len(processed_aspects)} potential aspects for {year}")
            
            # Process all the aspects we've found and store them in the database
            try:
                logger.debug(f"Starting database transaction for storing aspects for {year}")
                aspect_count = 0
                
                # First, ensure we have a mapping of planet names to database IDs
                planet_db_ids = {}
                
                # Get all celestial body IDs in a single query
                try:
                    rows = self.repository.database.query_all("SELECT id, name FROM celestial_bodies")
                    for row in rows:
                        planet_db_ids[row['name']] = row['id']
                        logger.debug(f"Found DB ID for {row['name']}: {row['id']}")
                    
                    # Log if any planets are missing
                    for planet_name in self.PLANETS.keys():
                        if planet_name not in planet_db_ids:
                            logger.error(f"No database ID found for planet {planet_name}")
                except Exception as e:
                    logger.error(f"Error retrieving celestial body IDs: {e}", exc_info=True)
                
                if not planet_db_ids:
                    logger.error("No celestial body IDs found in database. Cannot store aspects.")
                    return 0
                
                # Now insert each aspect in batches of 100 to avoid large transactions
                batch_size = 100
                aspect_batch = []
                
                for aspect_key, aspect_data in processed_aspects.items():
                    planet1, planet2, aspect_type_value, year, month = aspect_key
                    
                    # Skip if we don't have database IDs for both planets
                    if planet1 not in planet_db_ids or planet2 not in planet_db_ids:
                        logger.warning(f"Skipping aspect between {planet1} and {planet2} - missing DB IDs")
                        continue
                    
                    # Get the database IDs
                    planet1_id = planet_db_ids[planet1]
                    planet2_id = planet_db_ids[planet2]
                    
                    # Determine if this is a major aspect
                    aspect_type_enum = AspectType(aspect_type_value)
                    is_major = aspect_type_enum in MAJOR_ASPECTS
                    
                    # Add to batch
                    aspect_batch.append((
                        planet1_id, planet2_id, aspect_type_value, is_major, year,
                        aspect_data['first_seen'].isoformat(),
                        aspect_data['exact_time'].isoformat(),
                        aspect_data['last_seen'].isoformat(),
                        aspect_data['exact_pos1'],
                        aspect_data['exact_pos2']
                    ))
                    
                    # Insert batch if it reaches batch_size
                    if len(aspect_batch) >= batch_size:
                        self._insert_aspect_batch(aspect_batch, year)
                        aspect_count += len(aspect_batch)
                        aspect_batch = []
                
                # Insert any remaining aspects
                if aspect_batch:
                    self._insert_aspect_batch(aspect_batch, year)
                    aspect_count += len(aspect_batch)
                
                logger.info(f"Successfully stored {aspect_count} aspects for {year} in database")
                return aspect_count
                
            except Exception as e:
                logger.error(f"Database transaction failed: {e}", exc_info=True)
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating aspects for {year}: {e}", exc_info=True)
            return 0
    
    def _insert_aspect_batch(self, aspect_batch, year):
        """Insert a batch of aspects into the database.
        
        Args:
            aspect_batch: List of aspect tuples to insert
            year: Year for logging purposes
        """
        if not aspect_batch:
            return
            
        try:
            with self.repository.database.transaction() as conn:
                # Use executemany for efficient batch insert
                conn.executemany("""
                INSERT OR REPLACE INTO aspects (
                    body1_id, body2_id, aspect_type, is_major, year,
                    applying_timestamp, exact_timestamp, separation_timestamp,
                    exact_position1, exact_position2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, aspect_batch)
                
            logger.debug(f"Inserted batch of {len(aspect_batch)} aspects for {year}")
        except Exception as e:
            logger.error(f"Error inserting aspect batch for {year}: {e}", exc_info=True)
    
    def _calculate_lunar_phases_for_year(self, year: int) -> int:
        """Calculate lunar phases for a given year.
        
        Args:
            year: The year to calculate lunar phases for
            
        Returns:
            Number of lunar phases calculated
        """
        phases_count = 0
        
        try:
            # Set start and end dates for the year plus some margin
            # Include December of previous year and January of next year for completeness
            start_dt = datetime(year-1, 12, 1, 0, 0, 0) 
            end_dt = datetime(year+1, 1, 31, 23, 59, 59)
            
            # Convert to Julian days
            start_jd = self._datetime_to_jd(start_dt)
            end_jd = self._datetime_to_jd(end_dt)
            
            # Phase types to calculate
            phase_types = {
                0: LunarPhaseType.NEW_MOON,          # New Moon (0°)
                90: LunarPhaseType.FIRST_QUARTER,    # First Quarter (90°)
                180: LunarPhaseType.FULL_MOON,       # Full Moon (180°)
                270: LunarPhaseType.LAST_QUARTER     # Last Quarter (270°)
            }
            
            # Instead of using swe.next_phase_ut (which doesn't exist),
            # we'll search for the phases using a different approach
            
            # Approximate lunar cycle is 29.53 days
            lunar_cycle = 29.53
            
            # Calculate phases for the period
            current_jd = start_jd
            
            while current_jd < end_jd:
                for target_angle, phase_type in phase_types.items():
                    try:
                        # Find the exact Julian day when this phase occurs
                        phase_jd = self._find_exact_lunar_phase(current_jd, target_angle)
                        
                        if phase_jd and phase_jd < end_jd:
                            # Convert to datetime
                            phase_dt = self._jd_to_datetime(phase_jd)
                            
                            # Only store if within target year
                            if phase_dt.year == year:
                                self._store_lunar_phase(phase_dt, phase_type)
                                phases_count += 1
                                logger.debug(f"Found {phase_type.value} at {phase_dt}")
                    except Exception as e:
                        logger.warning(f"Error finding {phase_type.name} at JD {current_jd}: {e}")
                
                # Move forward by a quarter of the lunar cycle
                # This ensures we don't miss any phases
                current_jd += lunar_cycle / 4
            
            logger.info(f"Calculated {phases_count} lunar phases for {year}")
            return phases_count
            
        except Exception as e:
            logger.error(f"Error calculating lunar phases for {year}: {e}")
            # Fall back to simplified calculation
            return self._calculate_lunar_phases_fallback(year)
    
    def _find_exact_lunar_phase(self, start_jd: float, target_angle: float) -> Optional[float]:
        """Find exact time of a lunar phase.
        
        Args:
            start_jd: Julian day to start the search from
            target_angle: Target angle between sun and moon (0 for new moon, 180 for full moon)
            
        Returns:
            Julian day of lunar phase
        """
        try:
            # Find when moon-sun angle equals target_angle
            # Use a binary search approach
            
            # Set search range (about 29.5 days)
            jd_low = start_jd
            jd_high = start_jd + 29.5
            
            # Get initial moon and sun positions
            moon_pos = self._get_moon_position(jd_low)
            sun_pos = self._get_sun_position(jd_low)
            
            # Calculate initial angle
            angle = (moon_pos - sun_pos) % 360
            
            # If we're already very close to the target angle, return current jd
            if abs(angle - target_angle) < 1.0 or abs(angle - target_angle - 360) < 1.0:
                return jd_low
            
            # Binary search to find exact time
            for i in range(12):  # 12 iterations should give good precision
                try:
                    jd_mid = (jd_low + jd_high) / 2
                    
                    # Get sun and moon positions at midpoint
                    sun_pos = self._get_sun_position(jd_mid)
                    moon_pos = self._get_moon_position(jd_mid)
                    
                    # Calculate angle
                    angle = (moon_pos - sun_pos) % 360
                    
                    diff = angle - target_angle
                    if diff > 180:
                        diff -= 360
                    elif diff < -180:
                        diff += 360
                    
                    # Adjust search range based on whether we're before or after target
                    if diff < 0:
                        jd_low = jd_mid
                    else:
                        jd_high = jd_mid
                    
                    # If we're within 0.01 degrees, consider it found
                    if abs(diff) < 0.01:
                        return jd_mid
                except Exception as e:
                    logger.warning(f"Error in fine lunar phase search: {e}")
                    # Continue to next iteration
            
            # Return the midpoint of our final search range as best estimate
            return (jd_low + jd_high) / 2
            
        except Exception as e:
            logger.warning(f"Error finding exact lunar phase (target angle {target_angle}): {e}")
            return None
    
    def _find_quarter_moon(self, start_jd: float, target_angle: float) -> Optional[float]:
        """Find when the Sun-Moon angle reaches a certain value.
        
        Args:
            start_jd: Starting Julian day
            target_angle: Target angle in degrees
            
        Returns:
            Julian day of quarter moon
        """
        # This method is kept for backward compatibility, now it uses _find_exact_lunar_phase
        return self._find_exact_lunar_phase(start_jd, target_angle)
    
    def _get_moon_position(self, jd: float) -> float:
        """Get Moon's position at Julian day.
        
        Args:
            jd: Julian day
            
        Returns:
            Moon's longitude in degrees
        """
        try:
            # Get Moon's position using Swiss Ephemeris
            result = swe.calc_ut(jd, swe.MOON, self.geo_flags)
            
            # Extract longitude from result
            # Swiss Ephemeris returns a tuple: ((lon, lat, dist, ...), return_flags)
            if isinstance(result, tuple):
                if len(result) >= 2:
                    # First element contains the coordinates
                    pos_data = result[0]
                    
                    # Check if pos_data is list/tuple and get longitude
                    if isinstance(pos_data, (list, tuple)) and len(pos_data) > 0:
                        longitude = pos_data[0]
                    else:
                        longitude = pos_data
                    
                    logger.debug(f"Moon position at JD {jd}: {longitude}°")
                    return longitude
                else:
                    logger.warning(f"Unexpected Swiss Ephemeris result format: {result}")
            
            # If we got here, something unusual happened with the format
            logger.error(f"Invalid Swiss Ephemeris result for Moon: {result}")
            
            # Use fallback method only if Swiss Ephemeris fails
            fallback_position = self._get_moon_position_fallback(jd)
            logger.warning(f"Using FALLBACK method for Moon position. Result: {fallback_position:.2f}°")
            return fallback_position
            
        except Exception as e:
            logger.error(f"Error calculating Moon position: {e}", exc_info=True)
            
            # Use fallback method
            fallback_position = self._get_moon_position_fallback(jd)
            logger.warning(f"Using FALLBACK method for Moon position. Result: {fallback_position:.2f}°")
            return fallback_position
    
    def _get_sun_position(self, jd: float) -> float:
        """Get the Sun's ecliptic longitude (position in zodiac) for a Julian day.
        
        Args:
            jd: Julian day
            
        Returns:
            Sun's position in degrees (0-360)
        """
        try:
            # Get Sun's position using Swiss Ephemeris
            result = swe.calc_ut(jd, swe.SUN, self.geo_flags)
            
            # Extract longitude from result
            # Swiss Ephemeris returns a tuple: ((lon, lat, dist, ...), return_flags)
            if isinstance(result, tuple):
                if len(result) >= 2:
                    # First element contains the coordinates
                    pos_data = result[0]
                    
                    # Check if pos_data is list/tuple and get longitude
                    if isinstance(pos_data, (list, tuple)) and len(pos_data) > 0:
                        longitude = pos_data[0]
                    else:
                        longitude = pos_data
                    
                    logger.debug(f"Sun position at JD {jd}: {longitude}°")
                    return longitude
                else:
                    logger.warning(f"Unexpected Swiss Ephemeris result format: {result}")
            
            # If we got here, something unusual happened with the format
            logger.error(f"Invalid Swiss Ephemeris result for Sun: {result}")
            
            # Use fallback method only if Swiss Ephemeris fails
            fallback_position = self._get_sun_position_fallback(jd)
            logger.warning(f"Using FALLBACK method for Sun position. Result: {fallback_position:.2f}°")
            return fallback_position
            
        except Exception as e:
            logger.error(f"Error calculating Sun position: {e}", exc_info=True)
            
            # Use fallback method
            fallback_position = self._get_sun_position_fallback(jd)
            logger.warning(f"Using FALLBACK method for Sun position. Result: {fallback_position:.2f}°")
            return fallback_position
    
    def _store_lunar_phase(self, timestamp: datetime, phase_type: LunarPhaseType, 
                      moon_position: Optional[float] = None, sun_position: Optional[float] = None) -> None:
        """Store a lunar phase in the database.
        
        Args:
            timestamp: Date and time of the lunar phase
            phase_type: Type of lunar phase (new moon, full moon, etc.)
            moon_position: Moon's position in degrees (0-360), or None to calculate
            sun_position: Sun's position in degrees (0-360), or None to calculate
        """
        try:
            # Calculate positions if not provided
            if moon_position is None or sun_position is None:
                try:
                    # First try using Swiss Ephemeris for accurate positions
                    jd = self._datetime_to_jd(timestamp)
                    
                    if moon_position is None:
                        moon_position = self._get_moon_position(jd)
                    
                    if sun_position is None:
                        sun_position = self._get_sun_position(jd)
                
                except Exception as e:
                    # Fall back to approximate positions if Swiss Ephemeris fails
                    logger.warning(f"Swiss Ephemeris calculation failed for lunar phase {phase_type} "
                                  f"at {timestamp}. Using approximation. Error: {e}")
                    
                    if moon_position is None:
                        moon_position = self._approximate_moon_position(timestamp)
                    
                    if sun_position is None:
                        sun_position = self._approximate_sun_position(timestamp)
                        
                    # For specific phase types, use approximate values based on phase angle
                    if phase_type == LunarPhaseType.NEW_MOON:
                        # At new moon, the moon and sun are at approximately the same position
                        if moon_position is None:
                            moon_position = sun_position
                        elif sun_position is None:
                            sun_position = moon_position
                    
                    elif phase_type == LunarPhaseType.FULL_MOON:
                        # At full moon, the moon and sun are approximately 180 degrees apart
                        if moon_position is not None and sun_position is None:
                            sun_position = (moon_position + 180) % 360
                        elif sun_position is not None and moon_position is None:
                            moon_position = (sun_position + 180) % 360
            
            # Ensure we have valid positions before proceeding
            if moon_position is None or sun_position is None:
                logger.error(f"Could not determine positions for lunar phase {phase_type} at {timestamp}")
                return
            
            # Normalize positions to 0-360 range
            moon_position = float(moon_position) % 360
            sun_position = float(sun_position) % 360
            
            # Determine the zodiac sign of the moon
            zodiac_sign = self._get_zodiac_sign_for_position(moon_position)
            
            # Store in database
            year = timestamp.year
            with self.repository.database.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO lunar_phases (
                        timestamp, year, phase_type, moon_position, sun_position, zodiac_sign
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timestamp.isoformat(),
                    year,
                    phase_type.value,
                    moon_position,
                    sun_position,
                    zodiac_sign
                ))
            
        except Exception as e:
            logger.error(f"Error storing lunar phase {phase_type} at {timestamp}: {e}")
            # Only rollback if the repository object has the rollback method
            if hasattr(self.repository.database, 'rollback'):
                self.repository.database.rollback()
    
    def _calculate_planet_phases_for_year(self, year: int) -> int:
        """Calculate Mercury and Venus phases for a year.
        
        Calculates:
        - Conjunctions with the Sun (superior & inferior)
        - Maximum elongations (eastern & western)
        - Retrograde/direct stations

        Args:
            year: Year to calculate phases for
            
        Returns:
            Number of phases calculated
        """
        logger.info(f"Calculating planet phases for {year}")
        
        # Track events found
        phases_count = 0
        
        # Only Mercury and Venus have the phases we're interested in
        planets = {
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS
        }
        
        # Sun ID for conjunction calculations
        sun_id = swe.SUN
        
        # Set up the start and end dates for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        # Convert to Julian days
        start_jd = self._datetime_to_jd(start_date)
        end_jd = self._datetime_to_jd(end_date)
        
        for planet_name, planet_id in planets.items():
            logger.info(f"Calculating phases for {planet_name}")
            
            # Track the planet's position and speed day by day
            prev_position = None
            prev_speed = None
            prev_elongation = None
            
            # Track if the planet is retrograde
            is_retrograde = False
            
            # Track days since last event to avoid duplicates
            last_event_day = None
            
            # Process each day of the year
            current_jd = start_jd
            day_step = 1.0  # 1 day step for normal scanning
            
            while current_jd <= end_jd:
                try:
                    # Calculate planet position
                    planet_result = swe.calc_ut(current_jd, planet_id)
                    sun_result = swe.calc_ut(current_jd, sun_id)
                    
                    # Safely extract planet position and speed
                    if not isinstance(planet_result, tuple):
                        logger.error(f"Invalid planet calculation result for {planet_name}: {planet_result}")
                        current_jd += day_step
                        continue
                        
                    # SwissEph sometimes returns a tuple where the first element is the coordinates
                    # And other times returns a tuple of coordinates directly
                    if len(planet_result) >= 2 and isinstance(planet_result[0], (int, float)):
                        # Direct tuple of coordinates
                        current_position = planet_result[0]  # longitude
                        current_speed = planet_result[3] if len(planet_result) > 3 else 0.0  # speed
                    elif len(planet_result) >= 1 and isinstance(planet_result[0], (list, tuple)):
                        # Tuple where first element is coordinates
                        coords = planet_result[0]
                        current_position = coords[0] if len(coords) > 0 else 0.0
                        current_speed = coords[3] if len(coords) > 3 else 0.0
                    else:
                        logger.error(f"Unexpected format for {planet_name} result: {planet_result}")
                        current_jd += day_step
                        continue
                        
                    # Safely extract sun position
                    if not isinstance(sun_result, tuple):
                        logger.error(f"Invalid sun calculation result: {sun_result}")
                        current_jd += day_step
                        continue
                        
                    # SwissEph sometimes returns a tuple where the first element is the coordinates
                    # And other times returns a tuple of coordinates directly
                    if len(sun_result) >= 1 and isinstance(sun_result[0], (int, float)):
                        # Direct tuple of coordinates
                        sun_position = sun_result[0]  # longitude
                    elif len(sun_result) >= 1 and isinstance(sun_result[0], (list, tuple)):
                        # Tuple where first element is coordinates
                        coords = sun_result[0]
                        sun_position = coords[0] if len(coords) > 0 else 0.0
                    else:
                        logger.error(f"Unexpected format for Sun result: {sun_result}")
                        current_jd += day_step
                        continue
                    
                    # Calculate elongation (angular distance from Sun)
                    elongation = (current_position - sun_position) % 360
                    if elongation > 180:
                        elongation = 360 - elongation
                    
                    # Convert JD to datetime for storage
                    current_date = self._jd_to_datetime(current_jd)
                    
                    # Skip processing if we're too close to the last event
                    if last_event_day is not None and (current_jd - last_event_day) < 10:
                        prev_position = current_position
                        prev_speed = current_speed
                        prev_elongation = elongation
                        current_jd += day_step
                        continue
                    
                    # Check for retrograde or direct station (speed sign change)
                    if prev_speed is not None:
                        if prev_speed >= 0 and current_speed < 0:
                            # Changed from direct to retrograde
                            logger.info(f"{planet_name} station retrograde at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.STATIONARY_RETROGRADE,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                            is_retrograde = True
                            
                        elif prev_speed < 0 and current_speed >= 0:
                            # Changed from retrograde to direct
                            logger.info(f"{planet_name} station direct at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.STATIONARY_DIRECT,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                            is_retrograde = False
                    
                    # Check for conjunctions with the Sun
                    # Conjunction is when the angular difference is close to 0 or 180 degrees
                    angular_diff = abs((current_position - sun_position) % 360)
                    if prev_position is not None:
                        prev_angular_diff = abs((prev_position - sun_position) % 360)
                        
                        # Superior conjunction (planet behind the Sun)
                        if (angular_diff < 1 or angular_diff > 359) and (prev_angular_diff > 1 and prev_angular_diff < 359):
                            logger.info(f"{planet_name} superior conjunction at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.SUPERIOR_CONJUNCTION,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                            
                        # Inferior conjunction (planet between Earth and Sun)
                        elif abs(angular_diff - 180) < 1 and abs(prev_angular_diff - 180) > 1:
                            logger.info(f"{planet_name} inferior conjunction at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.INFERIOR_CONJUNCTION,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                    
                    # Check for maximum elongations
                    if prev_elongation is not None and elongation != prev_elongation:
                        # Increasing to decreasing = Eastern (evening) maximum elongation
                        if elongation < prev_elongation and prev_speed > 0:
                            logger.info(f"{planet_name} greatest eastern elongation {prev_elongation:.2f}° at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.GREATEST_EASTERN_ELONGATION,
                                elongation_degree=prev_elongation,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                            
                        # Decreasing to increasing = Western (morning) maximum elongation
                        elif elongation > prev_elongation and prev_speed < 0:
                            logger.info(f"{planet_name} greatest western elongation {prev_elongation:.2f}° at {current_date.isoformat()}")
                            self._store_planet_phase(
                                current_date, 
                                planet_id, 
                                PlanetPhaseType.GREATEST_WESTERN_ELONGATION,
                                elongation_degree=prev_elongation,
                                planet_position=current_position
                            )
                            phases_count += 1
                            last_event_day = current_jd
                    
                    # Update previous values
                    prev_position = current_position
                    prev_speed = current_speed
                    prev_elongation = elongation
                    
                except Exception as e:
                    logger.error(f"Error calculating phase for {planet_name} at JD {current_jd}: {e}")
                
                # Move to next day
                current_jd += day_step
        
        logger.info(f"Calculated {phases_count} planet phases for {year}")
        return phases_count
    
    def _calculate_elongation(self, planet_pos: float, sun_pos: float) -> float:
        """Calculate the elongation (angular distance) of a planet from the Sun.
        
        Args:
            planet_pos: Planet's longitude in degrees
            sun_pos: Sun's longitude in degrees
            
        Returns:
            Elongation in degrees (0-180)
        """
        # Calculate the absolute angular difference
        angle_diff = abs(planet_pos - sun_pos)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        return angle_diff
    
    def _is_eastern_elongation(self, planet_pos: float, sun_pos: float) -> bool:
        """Determine if a planet is in eastern or western elongation.
        
        Args:
            planet_pos: Planet's longitude in degrees
            sun_pos: Sun's longitude in degrees
            
        Returns:
            True if eastern elongation (evening sky), False if western (morning sky)
        """
        # Calculate the signed difference
        diff = (planet_pos - sun_pos) % 360
        
        # If diff is between 0 and 180, it's eastern (evening sky)
        # If diff is between 180 and 360, it's western (morning sky)
        return 0 <= diff <= 180
    
    def _is_inferior_conjunction(self, jd: float, planet_id: int) -> bool:
        """Determine if a conjunction is inferior (planet between Earth and Sun) or superior.
        
        Args:
            jd: Julian day of the conjunction
            planet_id: Planet ID (Mercury or Venus)
            
        Returns:
            True if inferior conjunction, False if superior
        """
        try:
            # We need to check the latitude of the planet relative to the ecliptic
            # In an inferior conjunction, the planet typically has non-zero latitude
            # In a superior conjunction, the planet is typically behind the Sun
            
            # Get all coordinates including latitude
            flags = swe.FLG_SWIEPH
            result = swe.calc_ut(jd, planet_id, flags)
            
            if not isinstance(result, tuple) or len(result) < 2:
                return False
                
            # Get the latitude (index 1 in the result tuple)
            lat = result[1]
            
            # Get the heliocentric longitude - if close to geocentric, it's inferior
            helio_flags = swe.FLG_SWIEPH | swe.FLG_HELIOCENTRIC
            helio_result = swe.calc_ut(jd, planet_id, helio_flags)
            
            if not isinstance(helio_result, tuple) or len(helio_result) < 1:
                return False
                
            helio_lon = helio_result[0]
            geo_lon = result[0]
            
            # Calculate the absolute difference between heliocentric and geocentric longitudes
            lon_diff = abs(helio_lon - geo_lon)
            if lon_diff > 180:
                lon_diff = 360 - lon_diff
                
            # If the longitudes are nearly opposite, it's an inferior conjunction
            # (Earth-Planet-Sun are approximately in line)
            return lon_diff > 90  # More than 90° difference indicates inferior conjunction
            
        except Exception as e:
            logger.error(f"Error determining conjunction type: {e}")
            # Default to superior conjunction (more common)
            return False
    
    def _find_exact_station(self, start_jd: float, end_jd: float, planet_id: int) -> float:
        """Find the exact moment when a planet's speed changes sign (station).
        
        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            planet_id: Planet ID
            
        Returns:
            Julian day of the exact station
        """
        # Binary search to find when speed crosses zero
        low = start_jd
        high = end_jd
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # Maximum iterations to prevent infinite loops
        max_iter = 20
        iter_count = 0
        
        while iter_count < max_iter:
            iter_count += 1
            
            mid = (low + high) / 2
            
            try:
                result = swe.calc_ut(mid, planet_id, flags)
                if not isinstance(result, tuple) or len(result) < 4:
                    # If we can't get a valid result, return the midpoint
                    return mid
                    
                speed = result[3]  # Daily speed in longitude
                
                # If speed is close enough to zero, we're done
                if abs(speed) < 0.0001:
                    return mid
                    
                # Adjust search bounds
                if speed < 0:
                    # If retrograde at midpoint, exact station is earlier
                    high = mid
                else:
                    # If direct at midpoint, exact station is later
                    low = mid
                    
            except Exception as e:
                logger.error(f"Error in station search: {e}")
                return mid  # Return best guess
        
        # Return midpoint as best estimate after max iterations
        return (start_jd + end_jd) / 2
    
    def _find_exact_max_elongation(self, start_jd: float, end_jd: float, planet_id: int, sun_id: int) -> float:
        """Find the exact moment of maximum elongation.
        
        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            planet_id: Planet ID
            sun_id: Sun ID
            
        Returns:
            Julian day of the exact maximum elongation
        """
        # Use golden section search to find maximum
        # https://en.wikipedia.org/wiki/Golden-section_search
        golden_ratio = (5**0.5 - 1) / 2  # ≈ 0.618
        
        a = start_jd
        b = end_jd
        
        c = b - golden_ratio * (b - a)
        d = a + golden_ratio * (b - a)
        
        # Maximum iterations to prevent infinite loops
        max_iter = 10
        iter_count = 0
        
        while abs(b - a) > 0.01 and iter_count < max_iter:  # Stop when interval is small enough
            iter_count += 1
            
            # Evaluate function at c and d
            fc = self._calculate_elongation_at_jd(c, planet_id, sun_id)
            fd = self._calculate_elongation_at_jd(d, planet_id, sun_id)
            
            if fc > fd:
                # Maximum is in [a, d]
                b = d
                d = c
                c = b - golden_ratio * (b - a)
            else:
                # Maximum is in [c, b]
                a = c
                c = d
                d = a + golden_ratio * (b - a)
        
        # Return midpoint of final interval
        return (a + b) / 2
    
    def _calculate_elongation_at_jd(self, jd: float, planet_id: int, sun_id: int) -> float:
        """Calculate elongation at a specific Julian day.
        
        Args:
            jd: Julian day
            planet_id: Planet ID
            sun_id: Sun ID
            
        Returns:
            Elongation in degrees
        """
        try:
            planet_result = swe.calc_ut(jd, planet_id)
            sun_result = swe.calc_ut(jd, sun_id)
            
            planet_pos = planet_result[0] if isinstance(planet_result, tuple) and len(planet_result) > 0 else 0
            sun_pos = sun_result[0] if isinstance(sun_result, tuple) and len(sun_result) > 0 else 0
            
            return self._calculate_elongation(planet_pos, sun_pos)
            
        except Exception as e:
            logger.error(f"Error calculating elongation at JD {jd}: {e}")
            return 0.0
    
    def _find_exact_conjunction(self, start_jd: float, end_jd: float, planet_id: int, sun_id: int) -> float:
        """Find the exact moment of conjunction.
        
        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            planet_id: Planet ID
            sun_id: Sun ID
            
        Returns:
            Julian day of the exact conjunction
        """
        # Binary search to find when elongation is minimized
        low = start_jd
        high = end_jd
        
        # Maximum iterations to prevent infinite loops
        max_iter = 10
        iter_count = 0
        
        while iter_count < max_iter:
            iter_count += 1
            
            mid = (low + high) / 2
            
            try:
                # Calculate elongation at three points
                e_low = self._calculate_elongation_at_jd(low, planet_id, sun_id)
                e_mid = self._calculate_elongation_at_jd(mid, planet_id, sun_id)
                e_high = self._calculate_elongation_at_jd(high, planet_id, sun_id)
                
                # If mid is less than both low and high, we've found a minimum
                if e_mid < e_low and e_mid < e_high:
                    # Refine further if needed
                    if abs(high - low) > 0.01:
                        # Narrow the search interval
                        if e_low < e_high:
                            high = mid
                        else:
                            low = mid
                    else:
                        return mid  # Precise enough
                elif e_low < e_mid:
                    # Minimum is between low and mid
                    high = mid
                else:
                    # Minimum is between mid and high
                    low = mid
                    
            except Exception as e:
                logger.error(f"Error in conjunction search: {e}")
                return mid  # Return best guess
        
        # Return midpoint as best estimate after max iterations
        return (start_jd + end_jd) / 2
    
    def _store_planet_phase(self, timestamp: datetime, body_id: int, phase_type: PlanetPhaseType, 
                        elongation_degree: Optional[float] = None, planet_position: Optional[float] = None) -> None:
        """Store a planetary phase in the database.
        
        Args:
            timestamp: Date and time of the phase
            body_id: ID of the celestial body (Mercury or Venus)
            phase_type: Type of planetary phase
            elongation_degree: Elongation in degrees for greatest elongation events (East/West)
            planet_position: Planet's position in degrees (0-360), or None to calculate
        """
        try:
            # Get the body name from the planet ID
            body_name = None
            for name, planet_id in self.PLANETS.items():
                if planet_id == body_id:
                    body_name = name
                    break
                    
            if body_name is None:
                raise ValueError(f"Unknown planet ID: {body_id}")
                
            # Get the body ID from the database
            body_db_id = None
            rows = self.repository.database.query_all(
                "SELECT id FROM celestial_bodies WHERE name = ?", 
                (body_name,)
            )
            
            if rows:
                body_db_id = rows[0]['id']
            else:
                logger.warning(f"Celestial body {body_name} not found in database, skipping")
                return
            
            # Calculate planet position if not provided
            if planet_position is None:
                try:
                    jd = self._datetime_to_jd(timestamp)
                    result = swe.calc_ut(jd, body_id)
                    planet_position = result[0] if isinstance(result, tuple) and len(result) > 0 else 0.0
                except Exception as e:
                    logger.error(f"Error calculating position for {body_name}: {e}")
                    # Fallback to approximate position
                    planet_position = 0.0
            
            # Normalize position to 0-360°
            planet_position = planet_position % 360
            
            # Determine the zodiac sign
            zodiac_sign = self._get_zodiac_sign_for_position(planet_position)
            
            # Store in database
            year = timestamp.year
            with self.repository.database.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO planet_phases (
                        body_id, phase_type, timestamp, year, elongation_degree, zodiac_sign
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    body_db_id,
                    phase_type.value,
                    timestamp.isoformat(),
                    year,
                    elongation_degree,
                    zodiac_sign
                ))
                
            logger.debug(f"Stored {phase_type.value} for {body_name} at {timestamp.isoformat()}")
            
        except Exception as e:
            logger.error(f"Error storing planet phase {phase_type} for {body_id} at {timestamp}: {e}")
            # Roll back transaction on error
            self.repository.database.rollback()
    
    def _calculate_eclipses_for_year(self, year: int) -> int:
        """Calculate solar and lunar eclipses for a year.
        
        Args:
            year: Year to calculate
            
        Returns:
            Number of eclipses calculated
        """
        eclipse_count = 0
        
        try:
            # Set up date limits for the year with some margin
            start_date = datetime(year-1, 12, 15)  # Start slightly before the year to catch eclipses at the very beginning
            end_date = datetime(year+1, 1, 15)     # Continue slightly into next year to catch eclipses at the very end
            
            # Convert to Julian days
            start_jd = self._datetime_to_jd(start_date)
            end_jd = self._datetime_to_jd(end_date)
            
            # Calculate solar eclipses
            try:
                solar_eclipses = self._calculate_solar_eclipses(start_jd, end_jd, year)
                eclipse_count += solar_eclipses
                logger.info(f"Calculated {solar_eclipses} solar eclipses for {year}")
            except Exception as e:
                logger.error(f"Error calculating solar eclipses for {year}: {e}", exc_info=True)
            
            # Calculate lunar eclipses
            try:
                lunar_eclipses = self._calculate_lunar_eclipses(start_jd, end_jd, year)
                eclipse_count += lunar_eclipses
                logger.info(f"Calculated {lunar_eclipses} lunar eclipses for {year}")
            except Exception as e:
                logger.error(f"Error calculating lunar eclipses for {year}: {e}", exc_info=True)
                
            return eclipse_count
            
        except Exception as e:
            logger.error(f"Error in eclipse calculations for {year}: {e}", exc_info=True)
            return 0
    
    def _calculate_solar_eclipses(self, start_jd: float, end_jd: float, year: int) -> int:
        """Calculate solar eclipses within a Julian day range.
        
        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            year: Year for filtering results
            
        Returns:
            Number of solar eclipses calculated
        """
        eclipse_count = 0
        current_jd = start_jd
        
        while current_jd < end_jd:
            try:
                # Use sol_eclipse_when_glob instead of sol_eclipse_when_loc
                # This doesn't require geo coordinates and is more reliable
                # retflag: 
                #   1 = total eclipse
                #   2 = annular eclipse
                #   4 = partial eclipse
                #   8 = annular-total eclipse (hybrid)
                result = swe.sol_eclipse_when_glob(current_jd, self.geo_flags)
                
                # Extract results - format is tuple with (retflag, tret)
                if isinstance(result, tuple) and len(result) >= 2:
                    retflag = result[0]
                    tret = result[1]
                else:
                    logger.error(f"Unexpected result format from sol_eclipse_when_glob: {result}")
                    current_jd += 30  # Move forward and try again
                    continue

                if tret is None:
                    logger.warning("No solar eclipse times returned")
                    current_jd += 30  # Move forward a month
                    continue
                
                # Get the maximum eclipse time
                eclipse_time = tret[0]  # tret[0] is maximum eclipse time
                
                # Determine eclipse type
                eclipse_type = None
                if retflag & 1:  # Total eclipse
                    eclipse_type = EclipseType.SOLAR_TOTAL
                elif retflag & 2:  # Annular eclipse
                    # In an annular eclipse, the Moon is too far from Earth to cover the Sun completely
                    eclipse_type = EclipseType.SOLAR_ANNULAR
                elif retflag & 4:  # Partial eclipse
                    eclipse_type = EclipseType.SOLAR_PARTIAL
                else:
                    # Unrecognized eclipse type, use partial as default
                    eclipse_type = EclipseType.SOLAR_PARTIAL
                
                # Convert to datetime
                eclipse_dt = self._jd_to_datetime(eclipse_time)
                
                # Only store eclipses in the target year
                if eclipse_dt.year == year:
                    # Store in database
                    self._store_eclipse(eclipse_dt, eclipse_type)
                    eclipse_count += 1
                    logger.debug(f"Stored solar eclipse: {eclipse_type.value} on {eclipse_dt.isoformat()}")
                
                # Move past this eclipse
                current_jd = eclipse_time + 10  # Skip 10 days forward
                
            except Exception as e:
                logger.error(f"Error calculating solar eclipse at JD {current_jd}: {e}", exc_info=True)
                current_jd += 30  # Skip forward to avoid getting stuck
        
        return eclipse_count
    
    def _calculate_lunar_eclipses(self, start_jd: float, end_jd: float, year: int) -> int:
        """Calculate lunar eclipses within a Julian day range.
        
        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            year: Year for filtering results
            
        Returns:
            Number of lunar eclipses calculated
        """
        eclipse_count = 0
        current_jd = start_jd
        
        while current_jd < end_jd:
            try:
                # Call the Swiss Ephemeris function to get the next lunar eclipse
                # retflag: 
                #   1 = total eclipse
                #   2 = partial eclipse
                #   4 = penumbral eclipse
                result = swe.lun_eclipse_when(current_jd, self.geo_flags)
                
                # Extract results - format depends on SwissEph version, handle both tuple formats
                if isinstance(result, tuple):
                    if len(result) >= 2 and isinstance(result[0], int):
                        # Format: (retflag, tret, attr)
                        retflag = result[0]
                        tret = result[1] if len(result) > 1 else None
                    else:
                        # Older format
                        retflag = result[0] if len(result) > 0 else 0
                        tret = result[1] if len(result) > 1 else None
                else:
                    logger.error(f"Unexpected result format from lun_eclipse_when: {result}")
                    current_jd += 10  # Move forward and try again
                    continue

                if tret is None:
                    logger.warning("No lunar eclipse times returned")
                    current_jd += 30  # Move forward a month
                    continue
                
                # Get the maximum eclipse time
                eclipse_time = tret[0]  # tret[0] is maximum eclipse time
                
                # Determine eclipse type
                eclipse_type = None
                if retflag & 1:  # Total eclipse
                    eclipse_type = EclipseType.LUNAR_TOTAL
                elif retflag & 2:  # Partial eclipse
                    eclipse_type = EclipseType.LUNAR_PARTIAL
                elif retflag & 4:  # Penumbral eclipse
                    eclipse_type = EclipseType.LUNAR_PENUMBRAL
                else:
                    # Unrecognized eclipse type, use partial as default
                    eclipse_type = EclipseType.LUNAR_PARTIAL
                
                # Convert to datetime
                eclipse_dt = self._jd_to_datetime(eclipse_time)
                
                # Only store eclipses in the target year
                if eclipse_dt.year == year:
                    # Store in database
                    self._store_eclipse(eclipse_dt, eclipse_type)
                    eclipse_count += 1
                    logger.debug(f"Stored lunar eclipse: {eclipse_type.value} on {eclipse_dt.isoformat()}")
                
                # Move past this eclipse
                current_jd = eclipse_time + 10  # Skip 10 days forward
                
            except Exception as e:
                logger.error(f"Error calculating lunar eclipse at JD {current_jd}: {e}", exc_info=True)
                current_jd += 30  # Skip forward to avoid getting stuck
        
        return eclipse_count
    
    def _store_eclipse(self, timestamp: datetime, eclipse_type: EclipseType) -> None:
        """Store an eclipse in the database.
        
        Args:
            timestamp: Time of the eclipse
            eclipse_type: Type of eclipse
        """
        try:
            # Get positions of Sun, Moon and any other relevant data at the time of eclipse
            jd = self._datetime_to_jd(timestamp)
            sun_pos = None
            moon_pos = None
            node_pos = None
            
            try:
                # Get Sun position
                sun_result = swe.calc_ut(jd, swe.SUN, self.geo_flags)
                if isinstance(sun_result, tuple) and len(sun_result) > 0:
                    sun_pos = sun_result[0][0] if isinstance(sun_result[0], (list, tuple)) else sun_result[0]
                
                # Get Moon position
                moon_result = swe.calc_ut(jd, swe.MOON, self.geo_flags)
                if isinstance(moon_result, tuple) and len(moon_result) > 0:
                    moon_pos = moon_result[0][0] if isinstance(moon_result[0], (list, tuple)) else moon_result[0]
                
                # Get North Node position
                node_result = swe.calc_ut(jd, swe.MEAN_NODE, self.geo_flags)
                if isinstance(node_result, tuple) and len(node_result) > 0:
                    node_pos = node_result[0][0] if isinstance(node_result[0], (list, tuple)) else node_result[0]
                
            except Exception as e:
                logger.warning(f"Error calculating planet positions for eclipse: {e}")
                # Provide default positions if calculation fails
                if sun_pos is None:
                    sun_pos = 0.0
                if moon_pos is None:
                    moon_pos = 0.0
                if node_pos is None:
                    node_pos = 0.0
            
            # Normalize positions
            sun_pos = sun_pos % 360 if sun_pos is not None else 0.0
            moon_pos = moon_pos % 360 if moon_pos is not None else 0.0
            node_pos = node_pos % 360 if node_pos is not None else 0.0
            
            # Determine zodiac sign - use Sun's sign for solar eclipses, Moon's sign for lunar eclipses
            is_solar = "solar" in eclipse_type.value
            zodiac_sign = self._get_zodiac_sign(sun_pos if is_solar else moon_pos)
            
            # Determine eclipse classification (partial, total, annular, etc.)
            # This is included in the eclipse_type enum value after the first underscore
            eclipse_classification = eclipse_type.value.split('_', 1)[1] if '_' in eclipse_type.value else "unknown"
            
            # Store in database
            year = timestamp.year
            
            try:
                # Check table structure with PRAGMA table_info
                table_info = self.repository.database.query_all("PRAGMA table_info(eclipses)")
                columns = [row['name'] for row in table_info]
                
                # Create the appropriate SQL based on the available columns
                with self.repository.database.transaction() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO eclipses (
                            timestamp, year, eclipse_type, eclipse_classification,
                            sun_position, moon_position, node_position, zodiac_sign
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp.isoformat(),
                        year,
                        eclipse_type.value,
                        eclipse_classification,
                        sun_pos,
                        moon_pos,
                        node_pos,
                        zodiac_sign
                    ))
                
                logger.debug(f"Successfully stored {eclipse_type.value} eclipse at {timestamp.isoformat()}")
                
            except Exception as e:
                logger.error(f"Database error storing eclipse: {e}", exc_info=True)
                # The repository handles transaction management
        
        except Exception as e:
            logger.error(f"Error storing eclipse {eclipse_type} at {timestamp}: {e}", exc_info=True)
    
    def _calculate_solar_events_for_year(self, year: int) -> int:
        """Calculate solar events (equinoxes and solstices) for a given year.
        
        Args:
            year: The year to calculate solar events for
        """
        # Try to use Swiss Ephemeris for accurate calculations
        try:
            if not hasattr(swe, 'next_solpoint_ut'):
                raise AttributeError("Swiss Ephemeris module does not have next_solpoint_ut function")
                
            # Set start date to previous winter solstice if possible, or first day of year
            start_jd = self._datetime_to_jd(datetime(year-1, 12, 20, 0, 0, 0))
            
            # Calculate spring equinox
            spring_jd, spring_solar_lon = swe.next_solpoint_ut(start_jd, 0)
            spring_dt = self._jd_to_datetime(spring_jd)
            self._store_solar_event(spring_dt, SolarEventType.SPRING_EQUINOX, 0)
            
            # Calculate summer solstice
            summer_jd, summer_solar_lon = swe.next_solpoint_ut(spring_jd, 90)
            summer_dt = self._jd_to_datetime(summer_jd)
            self._store_solar_event(summer_dt, SolarEventType.SUMMER_SOLSTICE, 90)
            
            # Calculate fall equinox
            fall_jd, fall_solar_lon = swe.next_solpoint_ut(summer_jd, 180)
            fall_dt = self._jd_to_datetime(fall_jd)
            self._store_solar_event(fall_dt, SolarEventType.FALL_EQUINOX, 180)
            
            # Calculate winter solstice
            winter_jd, winter_solar_lon = swe.next_solpoint_ut(fall_jd, 270)
            winter_dt = self._jd_to_datetime(winter_jd)
            self._store_solar_event(winter_dt, SolarEventType.WINTER_SOLSTICE, 270)
            
            logger.info(f"Calculated solar events for {year} using Swiss Ephemeris")
            
        except (AttributeError, swe.Error) as e:
            # Use fallback method if Swiss Ephemeris fails
            logger.warning(f"Swiss Ephemeris error: {e}. Using approximate solar events for {year}.")
            self._calculate_solar_events_fallback(year)
            
        return 4  # Assuming 4 solar events are calculated
    
    def _is_leap_year(self, year: int) -> bool:
        """Determine if a year is a leap year.
        
        Args:
            year: The year to check
            
        Returns:
            True if the year is a leap year, False otherwise
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def _calculate_solar_events_fallback(self, year: int) -> None:
        """Calculate approximate solar events for a year using simple formulas.
        
        This is a fallback method when Swiss Ephemeris is not available.
        
        Args:
            year: The year to calculate solar events for
        """
        # Approximate dates for Northern Hemisphere solar events
        # These vary slightly from year to year but are close enough for a fallback
        
        # Spring Equinox (around March 20-21)
        march = 20
        if self._is_leap_year(year) and year % 100 != 0:
            march = 20  # Leap years can make it earlier
        elif not self._is_leap_year(year):
            march = 20  # Non-leap years make it later
            
        spring_dt = datetime(year, 3, march, 12, 0, 0)  # Noon as approximation
        self._store_solar_event(spring_dt, SolarEventType.SPRING_EQUINOX, 0)
        
        # Summer Solstice (around June 20-22)
        summer_dt = datetime(year, 6, 21, 12, 0, 0)  # Noon as approximation
        self._store_solar_event(summer_dt, SolarEventType.SUMMER_SOLSTICE, 90)
        
        # Fall Equinox (around September 22-23)
        fall_dt = datetime(year, 9, 22, 12, 0, 0)  # Noon as approximation
        self._store_solar_event(fall_dt, SolarEventType.FALL_EQUINOX, 180)
        
        # Winter Solstice (around December 21-22)
        winter_dt = datetime(year, 12, 21, 12, 0, 0)  # Noon as approximation
        self._store_solar_event(winter_dt, SolarEventType.WINTER_SOLSTICE, 270)
        
        logger.info(f"Calculated approximate solar events for {year} using fallback method")
    
    def _calculate_lunar_phases_fallback(self, year: int) -> int:
        """Calculate lunar phases using a simplified method when Swiss Ephemeris fails.
        
        This method uses the Metonic cycle (19 year pattern of lunar phases) and 
        a reference date to approximate lunar phases. Less accurate than Swiss 
        Ephemeris calculations but sufficient as a fallback.
        
        Args:
            year: Year to calculate lunar phases for
            
        Returns:
            Number of lunar phases calculated and stored
        """
        logger.info(f"Using fallback method for lunar phases calculation for year {year}")
        
        # Reference new moon (January 6, 2000 at 18:14 UTC)
        reference_new_moon = datetime(2000, 1, 6, 18, 14)
        
        # Average synodic month length (new moon to new moon) in days
        synodic_month = 29.53058867
        
        # Start from December of previous year to catch phases at the very start of the year
        start_date = datetime(year - 1, 12, 15)
        end_date = datetime(year + 1, 1, 15)  # Go slightly into next year
        
        # Calculate days since reference new moon
        days_since_reference = (start_date - reference_new_moon).total_seconds() / 86400
        
        # Calculate how many complete synodic months have passed
        complete_months = int(days_since_reference / synodic_month)
        
        # Calculate the date of the new moon just before our start date
        last_new_moon = reference_new_moon + timedelta(days=complete_months * synodic_month)
        
        # Initialize counter
        phase_count = 0
        
        # Generate lunar phases until we pass the end date
        current_date = last_new_moon
        while current_date <= end_date:
            # Only process if date is in our target year
            if current_date.year == year:
                try:
                    # New Moon (0% illumination)
                    self._store_lunar_phase(current_date, LunarPhaseType.NEW_MOON)
                    phase_count += 1
                    
                    # First Quarter (+7.38 days, 50% illumination)
                    first_quarter = current_date + timedelta(days=synodic_month / 4)
                    if first_quarter.year == year:
                        self._store_lunar_phase(first_quarter, LunarPhaseType.FIRST_QUARTER)
                        phase_count += 1
                    
                    # Full Moon (+14.77 days, 100% illumination)
                    full_moon = current_date + timedelta(days=synodic_month / 2)
                    if full_moon.year == year:
                        self._store_lunar_phase(full_moon, LunarPhaseType.FULL_MOON)
                        phase_count += 1
                    
                    # Last Quarter (+22.15 days, 50% illumination)
                    last_quarter = current_date + timedelta(days=3 * synodic_month / 4)
                    if last_quarter.year == year:
                        self._store_lunar_phase(last_quarter, LunarPhaseType.LAST_QUARTER)
                        phase_count += 1
                except Exception as e:
                    logger.error(f"Error storing fallback lunar phase at {current_date}: {e}")
            
            # Move to next new moon
            current_date += timedelta(days=synodic_month)
        
        logger.info(f"Fallback method calculated {phase_count} lunar phases for year {year}")
        return phase_count
    
    def _approximate_moon_position(self, dt: datetime) -> float:
        """Very rough approximation of moon position based on date.
        
        Args:
            dt: Date and time to calculate moon position for
            
        Returns:
            Moon longitude in degrees (0-360)
        """
        # Simple approximation: moon orbits roughly every 27.3 days
        # Calculate days since J2000 epoch
        jd = self._datetime_to_jd(dt)
        days_since_epoch = jd - 2451545.0  # J2000 epoch
        
        # Approximate mean longitude (very crude approximation)
        approx_pos = (days_since_epoch % 27.3) * (360 / 27.3)
        
        # Make sure it's in 0-360 range
        if approx_pos < 0:
            approx_pos += 360
            
        return approx_pos
        
    def _approximate_sun_position(self, timestamp: datetime) -> float:
        """Calculate an approximate position for the sun based on timestamp.
        
        This is a simplified calculation used as a fallback when Swiss Ephemeris fails.
        
        Args:
            timestamp: The date and time to calculate the position for
            
        Returns:
            Approximate position of the sun in degrees (0-360)
        """
        # Calculate day of year (1-366)
        day_of_year = timestamp.timetuple().tm_yday
        
        # Calculate the year fraction (0-1) including time of day
        day_fraction = (timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second) / 86400
        year_fraction = (day_of_year - 1 + day_fraction) / (366 if calendar.isleap(timestamp.year) else 365)
        
        # The sun traverses 360 degrees in a year
        raw_position = year_fraction * 360
        
        # Apply a correction for Earth's elliptical orbit using a simplified equation of time
        # This approximates the Equation of Center
        # The orbit is at perihelion around January 3rd (day 3)
        days_since_perihelion = (day_of_year - 3) % 365
        perihelion_fraction = days_since_perihelion / 365
        mean_anomaly = perihelion_fraction * 2 * math.pi
        
        # Simplified equation of center (normally up to 2 degrees)
        correction = 2 * math.sin(mean_anomaly)
        
        # Apply a fixed offset to align with the vernal equinox
        # Vernal equinox is around March 20 (day 79), which should be at 0°
        vernal_equinox_offset = 79 / 365 * 360
        position = (raw_position - vernal_equinox_offset + correction) % 360
        
        return position
    
    def _get_zodiac_sign_for_position(self, position: float) -> str:
        """Determine the zodiac sign for a given celestial position.
        
        Args:
            position: Position in ecliptic longitude (0-360 degrees)
            
        Returns:
            Name of the zodiac sign as a string
        """
        # Zodiac signs are 30 degrees each, starting with Aries at 0 degrees
        zodiac_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", 
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        # Calculate the index (0-11) of the zodiac sign
        sign_index = int(position / 30) % 12
        
        return zodiac_signs[sign_index]
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian day to datetime.
        
        Args:
            jd: Julian day
            
        Returns:
            Datetime object
        """
        # Get year, month, day, hour, minute, second
        y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
        
        # Calculate hours, minutes, seconds
        hour = int(h)
        minute = int((h - hour) * 60)
        second = int(((h - hour) * 60 - minute) * 60)
        
        # Create datetime
        return datetime(y, m, d, hour, minute, second)
    
    def _get_sun_position_fallback(self, jd: float) -> float:
        """Fallback approximation for Sun's position when Swiss Ephemeris is unavailable.
        
        This provides a simple approximation of the Sun's position based on
        the mean Sun longitude formula. It's much less accurate than Swiss Ephemeris
        but can be used when precise calculations aren't possible.
        
        Args:
            jd: Julian day
            
        Returns:
            Approximate Sun's position in degrees (0-360)
        """
        # Convert Julian day to date
        dt = self._jd_to_datetime(jd)
        
        # Calculate days since J2000.0 (Jan 1, 2000 12:00 UTC)
        jd2000 = jd - 2451545.0
        
        # Mean longitude of the Sun
        L = 280.460 + 0.9856474 * jd2000
        
        # Mean anomaly of the Sun
        g = 357.528 + 0.9856003 * jd2000
        
        # Convert to radians for the calculation
        g_rad = math.radians(g)
        
        # Calculate ecliptic longitude of the Sun
        lambda_sun = L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
        
        # Normalize to 0-360
        lambda_sun = lambda_sun % 360
        if lambda_sun < 0:
            lambda_sun += 360
            
        return lambda_sun
    
    def _get_moon_position_fallback(self, jd: float) -> float:
        """Fallback approximation for Moon's position when Swiss Ephemeris is unavailable.
        
        This is a very rough approximation of the Moon's position.
        It's much less accurate than Swiss Ephemeris but can be used
        when precise calculations aren't possible.
        
        Args:
            jd: Julian day
            
        Returns:
            Approximate Moon's position in degrees (0-360)
        """
        # Very basic approximation based on lunar orbit period
        days_since_epoch = jd - 2451545.0  # J2000 epoch
        
        # Moon orbits roughly every 27.3 days (sidereal period)
        # but this is a very crude approximation
        moon_lon = (days_since_epoch % 27.3) * (360 / 27.3)
        
        # Get Sun position to add solar longitude component
        # (very rough approximation of how Moon follows Sun)
        sun_lon = self._get_sun_position_fallback(jd)
        
        # Combine with an offset based on days in lunar cycle
        # This is very approximate but gives some variation in phase
        lunar_phase_component = (days_since_epoch % 29.53) * (360 / 29.53)
        
        # Combine components - this is a very rough approximation
        moon_lon = (sun_lon + lunar_phase_component) % 360
        
        return moon_lon
    
    def _store_solar_event(self, event_dt: datetime, event_type: SolarEventType, sun_position: float):
        """Store a solar event in the database.
        
        Args:
            event_dt: Event datetime
            event_type: Type of solar event
            sun_position: Sun's position in degrees
        """
        # Get zodiac sign
        zodiac_sign = self._get_zodiac_sign(sun_position)
        
        # Store in database
        with self.repository.database.transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO solar_events (
                    timestamp, year, event_type, sun_position, zodiac_sign
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                event_dt.isoformat(),
                event_dt.year,
                event_type.value,
                sun_position,
                zodiac_sign
            ))
        
    def _get_zodiac_sign(self, position: float) -> int:
        """Get the zodiac sign index (0-11) for a position.
        
        Args:
            position: Position in degrees (0-360)
            
        Returns:
            Zodiac sign index (0-11)
        """
        return int(position / 30) % 12
        
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

    def _calculate_aspect_orb(self, pos1: float, pos2: float, aspect_type: AspectType) -> Optional[float]:
        """Calculate the orb for an aspect between two positions.
        
        Args:
            pos1: Position of first planet (degrees)
            pos2: Position of second planet (degrees)
            aspect_type: Type of aspect to check
            
        Returns:
            Orb in degrees if within allowed range, None otherwise
        """
        # Get ideal angle for this aspect
        ideal_angle = ASPECT_ANGLES[aspect_type]
        
        # Calculate actual angle between planets
        angle_diff = abs(self._normalize_angle(pos1 - pos2))
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        # Calculate orb
        orb = abs(angle_diff - ideal_angle)
        
        # Check if within allowed orb
        max_orb = MAJOR_ASPECT_ORB if aspect_type in MAJOR_ASPECTS else MINOR_ASPECT_ORB
        if orb <= max_orb:
            return orb
        
        return None

    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian day.
        
        Args:
            dt: Datetime object
            
        Returns:
            Julian day
        """
        return swe.julday(dt.year, dt.month, dt.day, dt.hour / 24 + dt.minute / 1440 + dt.second / 86400) 

    def get_planet_phases_for_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get planet phases for a specific date.
        
        Retrieves Mercury and Venus phase events that occur on the specified date.
        
        Args:
            date: The date to get planet phases for
            
        Returns:
            List of planet phase events
        """
        try:
            # Ensure we have a naive datetime without timezone
            if date.tzinfo is not None:
                date = date.replace(tzinfo=None)
                
            # Get the start and end of the day
            start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            # Query database for planet phases on this date
            with self.repository.database.connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    p.id, 
                    p.timestamp, 
                    p.body_id, 
                    b.name as body_name, 
                    p.phase_type, 
                    p.elongation_degree, 
                    p.zodiac_sign
                FROM planet_phases p
                JOIN celestial_bodies b ON p.body_id = b.id
                WHERE p.timestamp BETWEEN ? AND ?
                ORDER BY p.timestamp
                """
                
                cursor.execute(query, (start_of_day, end_of_day))
                phases = []
                
                for row in cursor.fetchall():
                    # Format the phase event
                    phase = {
                        'id': row[0],
                        'timestamp': row[1],
                        'body_id': row[2],
                        'body_name': row[3],
                        'phase_type': row[4],
                        'elongation_degree': row[5],
                        'zodiac_sign': row[6]
                    }
                    
                    # Add additional info for frontend display
                    phase['title'] = self._format_phase_title(phase)
                    phase['description'] = self._format_phase_description(phase)
                    
                    phases.append(phase)
                
                logger.debug(f"Found {len(phases)} planet phases for {date.strftime('%Y-%m-%d')}")
                return phases
                
        except Exception as e:
            logger.error(f"Error retrieving planet phases for {date.strftime('%Y-%m-%d')}: {e}")
            return []
            
    def _format_phase_title(self, phase: Dict[str, Any]) -> str:
        """Format a title for a planet phase event.
        
        Args:
            phase: The phase event data
            
        Returns:
            Formatted title string
        """
        body_name = phase.get('body_name', 'Unknown')
        phase_type = phase.get('phase_type', 'Unknown')
        
        # Convert DB phase_type to readable format
        if isinstance(phase_type, str):
            phase_type_readable = phase_type.replace('_', ' ').title()
        else:
            # Handle Enum values if they're passed directly
            phase_type_readable = str(phase_type).replace('_', ' ').title()
        
        return f"{body_name} {phase_type_readable}"
        
    def _format_phase_description(self, phase: Dict[str, Any]) -> str:
        """Format a description for a planet phase event.
        
        Args:
            phase: The phase event data
            
        Returns:
            Formatted description string
        """
        body_name = phase.get('body_name', 'Unknown')
        phase_type = phase.get('phase_type', 'Unknown')
        zodiac_sign = phase.get('zodiac_sign', 'Unknown')
        elongation = phase.get('elongation_degree')
        
        # Ensure elongation has a valid value
        if elongation is None:
            elongation = 0.0
        
        # Base description
        description = f"{body_name} "
        
        # Add phase-specific details
        if phase_type == PlanetPhaseType.STATIONARY_RETROGRADE.value:
            description += f"stations retrograde at {elongation:.1f}° {zodiac_sign}"
        elif phase_type == PlanetPhaseType.STATIONARY_DIRECT.value:
            description += f"stations direct at {elongation:.1f}° {zodiac_sign}"
        elif phase_type == PlanetPhaseType.SUPERIOR_CONJUNCTION.value:
            description += f"reaches superior conjunction with the Sun at {elongation:.1f}° {zodiac_sign}"
        elif phase_type == PlanetPhaseType.INFERIOR_CONJUNCTION.value:
            description += f"reaches inferior conjunction with the Sun at {elongation:.1f}° {zodiac_sign}"
        elif phase_type == PlanetPhaseType.GREATEST_EASTERN_ELONGATION.value:
            description += f"reaches greatest eastern elongation ({elongation:.1f}° from the Sun) at {elongation:.1f}° {zodiac_sign}"
        elif phase_type == PlanetPhaseType.GREATEST_WESTERN_ELONGATION.value:
            description += f"reaches greatest western elongation ({elongation:.1f}° from the Sun) at {elongation:.1f}° {zodiac_sign}"
        else:
            description += f"at {elongation:.1f}° {zodiac_sign}"
            
        # Add astronomical significance hints
        if phase_type == PlanetPhaseType.GREATEST_EASTERN_ELONGATION.value:
            description += " (visible in the evening sky)"
        elif phase_type == PlanetPhaseType.GREATEST_WESTERN_ELONGATION.value:
            description += " (visible in the morning sky)"
        elif phase_type == PlanetPhaseType.STATIONARY_RETROGRADE.value:
            description += " (appears to move backward through the zodiac)"
        elif phase_type == PlanetPhaseType.STATIONARY_DIRECT.value:
            description += " (resumes forward motion through the zodiac)"
            
        return description

    def populate_planet_phases(self, start_year: int, end_year: int) -> int:
        """
        Populate the database with planet phases for Mercury and Venus.
        
        Args:
            start_year (int): Start year to calculate phases for
            end_year (int): End year to calculate phases for (inclusive)
            
        Returns:
            Number of planet phase events calculated and stored
        """
        if start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")
            
        logger.info(f"Populating planet phases for years {start_year}-{end_year}")
        
        # Track total phases added
        total_phases = 0
        
        # Setup Swiss Ephemeris
        self._setup_ephemeris()
        
        # Calculate phases for each year
        for year in range(start_year, end_year + 1):
            try:
                phases_count = self._calculate_planet_phases_for_year(year)
                total_phases += phases_count
                logger.info(f"Added {phases_count} planet phases for {year}")
            except Exception as e:
                logger.error(f"Error calculating planet phases for {year}: {e}")
                
        logger.info(f"Calculated {total_phases} total planet phases for {start_year}-{end_year}")
        return total_phases

    def _setup_ephemeris(self) -> None:
        """Setup Swiss Ephemeris with the proper path.
        
        This method ensures the Swiss Ephemeris files are properly loaded
        before calculations are performed.
        """
        try:
            # Check if ephemeris files location is specified
            app_dir = Path.home() / ".isopgem"
            ephe_dir = app_dir / "ephemeris"
            
            if ephe_dir.exists():
                logger.info(f"Using ephemeris files from: {ephe_dir}")
                swe.set_ephe_path(str(ephe_dir))
            else:
                # Fall back to built-in data
                logger.info("No ephemeris files found in ~/.isopgem/ephemeris, using built-in data")
                swe.set_ephe_path()
                
            # Test if Swiss Ephemeris works by calculating Sun and Moon positions
            logger.debug("Testing Swiss Ephemeris with sample calculations...")
            
            # Test date (J2000.0)
            test_jd = swe.julday(2000, 1, 1, 12)
            
            # Test Sun calculation
            sun_result = swe.calc_ut(test_jd, swe.SUN, self.geo_flags)
            if isinstance(sun_result, tuple) and len(sun_result) >= 2:
                sun_lon = sun_result[0][0] if isinstance(sun_result[0], (tuple, list)) else sun_result[0]
                logger.info(f"Swiss Ephemeris initialized successfully. Test Sun longitude: {sun_lon:.4f}°")
            else:
                logger.warning(f"Unexpected Sun calculation result format: {sun_result}")
            
            # Test Moon calculation
            moon_result = swe.calc_ut(test_jd, swe.MOON, self.geo_flags)
            if isinstance(moon_result, tuple) and len(moon_result) >= 2:
                moon_lon = moon_result[0][0] if isinstance(moon_result[0], (tuple, list)) else moon_result[0]
                logger.info(f"Test Moon longitude: {moon_lon:.4f}°")
            else:
                logger.warning(f"Unexpected Moon calculation result format: {moon_result}")
                
            # Log Swiss Ephemeris version
            version = getattr(swe, 'version', 'unknown')
            logger.info(f"Using Swiss Ephemeris version: {version}")
            
        except Exception as e:
            logger.error(f"Error setting up Swiss Ephemeris: {e}", exc_info=True)
            logger.warning("Some calculations will use mathematical approximations instead of precise ephemeris data")

    def get_aspects_for_date(self, date: date) -> List:
        """Get planetary aspects for a specific date from the database.
        
        Args:
            date: Date to get aspects for
            
        Returns:
            List of Aspect objects for the specified date
        """
        try:
            logger.debug(f"Getting aspects for {date.isoformat()}")
            
            # Convert date to datetime for database comparison
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            # Query aspects from the database
            with self.repository.database.connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    a.id, 
                    a.body1_id, 
                    b1.name as body1_name, 
                    a.body2_id, 
                    b2.name as body2_name, 
                    a.aspect_type, 
                    a.is_major,
                    a.exact_timestamp,
                    a.exact_position1,
                    a.exact_position2
                FROM aspects a
                JOIN celestial_bodies b1 ON a.body1_id = b1.id
                JOIN celestial_bodies b2 ON a.body2_id = b2.id
                WHERE a.exact_timestamp BETWEEN ? AND ?
                ORDER BY a.exact_timestamp
                """
                
                cursor.execute(query, (start_of_day.isoformat(), end_of_day.isoformat()))
                aspects = []
                
                for row in cursor.fetchall():
                    # Create PlanetInfo objects for the planets
                    from astrology.services.moon_phase_calculator import PlanetInfo, Aspect as MoonAspect
                    
                    # Make sure we have valid planet names
                    body1_name = row[2] if row[2] else "Unknown Planet"
                    body2_name = row[4] if row[4] else "Unknown Planet"
                    
                    planet1 = PlanetInfo(id=row[1], name=body1_name, weight=1.0, position=row[8])
                    planet2 = PlanetInfo(id=row[3], name=body2_name, weight=1.0, position=row[9])
                    
                    # Get the aspect type as a string and convert to AspectType if possible
                    aspect_type_str = row[5]
                    aspect_type = None
                    
                    # Try to convert string to AspectType enum
                    for at in AspectType:
                        if at.value == aspect_type_str:
                            aspect_type = at
                            break
                    
                    # If we couldn't find a matching enum, use the string
                    if aspect_type is None:
                        aspect_type = aspect_type_str
                    
                    # Get exact time
                    exact_time = None
                    if row[7]:
                        try:
                            exact_time = datetime.fromisoformat(row[7])
                        except (ValueError, TypeError):
                            # Fallback if we can't parse the timestamp
                            exact_time = start_of_day
                    
                    # Create the Aspect object
                    aspect = MoonAspect(
                        planet1=planet1,
                        planet2=planet2,
                        aspect_type=aspect_type,
                        orb=0.0,  # We don't store orb in the database, so use 0
                        exact_time=exact_time
                    )
                    
                    logger.debug(f"Found aspect: {body1_name} {aspect_type_str} {body2_name}")
                    aspects.append(aspect)
                
                logger.debug(f"Found {len(aspects)} aspects for {date.isoformat()}")
                return aspects
                
        except Exception as e:
            logger.error(f"Error getting aspects for {date.isoformat()}: {e}")
            return []

    @classmethod
    def get_instance(cls) -> 'AstrologicalEventCalculator':
        """Get the singleton instance of the calculator.
        
        Returns:
            The singleton instance
        """
        return super().get_instance()