"""
Purpose: Provides SQLite repository for astronomical and astrological events.

This file is part of the astrology pillar and serves as a repository component.
It provides functionality to store, retrieve and calculate long-term astronomical events
like planetary aspects, phases, and eclipses. The goal is to pre-calculate these events
for extended time periods (1900-2100 by default) to eliminate redundant calculations
and improve application performance.

Key components:
- AstrologicalEventsRepository: Repository for astronomical events
- Database schema for various event types (aspects, phases, eclipses, etc.)

Dependencies:
- sqlite3: For database operations
- shared.repositories.database: For database access
- swisseph: For astronomical calculations
"""

from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Callable
import sqlite3

from loguru import logger

from shared.repositories.database import Database

class AstrologicalDatabaseError(Exception):
    """Base class for critical database operations errors."""
    pass

class CalculationError(AstrologicalDatabaseError):
    """Raised when critical calculation errors occur."""
    pass

def handle_database_error(func):
    """Decorator for handling critical database errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise AstrologicalDatabaseError(f"Critical database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise AstrologicalDatabaseError(f"Unexpected error: {e}")
    return wrapper

class AstrologicalEventsRepository:
    """Repository for astronomical and astrological events."""

    def __init__(self, database: Database):
        """Initialize the astrological events repository.

        Args:
            database: Database instance
        """
        self.database = database
        self._initialize_tables()
        logger.debug("AstrologicalEventsRepository initialized")

    @handle_database_error
    def _initialize_tables(self) -> None:
        """Initialize the database tables."""
        # Create calculation metadata table
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS calculation_metadata (
            id INTEGER PRIMARY KEY,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            calculation_timestamp DATETIME NOT NULL,
            status TEXT NOT NULL,
            events_count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(start_year, end_year)
        )
        """)
        
        # Create celestial bodies table
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS celestial_bodies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            zodiac_sign INTEGER,
            UNIQUE(name)
        )
        """)

        # Create positions table (both helio/geocentric)
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY,
            body_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            year INTEGER NOT NULL,
            is_heliocentric BOOLEAN NOT NULL,
            absolute_position REAL NOT NULL,
            zodiac_sign INTEGER NOT NULL,
            degree_in_sign INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            second INTEGER NOT NULL,
            FOREIGN KEY (body_id) REFERENCES celestial_bodies(id),
            UNIQUE(body_id, timestamp, is_heliocentric)
        )
        """)

        # Create aspects table
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS aspects (
            id INTEGER PRIMARY KEY,
            body1_id INTEGER NOT NULL,
            body2_id INTEGER NOT NULL,
            aspect_type TEXT NOT NULL,
            is_major BOOLEAN NOT NULL,
            year INTEGER NOT NULL,
            applying_timestamp DATETIME,
            exact_timestamp DATETIME NOT NULL,
            separation_timestamp DATETIME,
            applying_position1 REAL,
            applying_position2 REAL,
            exact_position1 REAL NOT NULL,
            exact_position2 REAL NOT NULL,
            separation_position1 REAL,
            separation_position2 REAL,
            FOREIGN KEY (body1_id) REFERENCES celestial_bodies(id),
            FOREIGN KEY (body2_id) REFERENCES celestial_bodies(id),
            UNIQUE(body1_id, body2_id, exact_timestamp, aspect_type)
        )
        """)

        # Create lunar phases table
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS lunar_phases (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            year INTEGER NOT NULL,
            phase_type TEXT NOT NULL,
            moon_position REAL NOT NULL,
            sun_position REAL NOT NULL,
            zodiac_sign INTEGER NOT NULL,
            UNIQUE(timestamp, phase_type)
        )
        """)

        # Create planet phases table (Mercury/Venus)
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS planet_phases (
            id INTEGER PRIMARY KEY,
            body_id INTEGER NOT NULL,
            phase_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            year INTEGER NOT NULL,
            elongation_degree REAL,
            zodiac_sign INTEGER NOT NULL,
            FOREIGN KEY (body_id) REFERENCES celestial_bodies(id),
            UNIQUE(body_id, timestamp, phase_type)
        )
        """)

        # Create eclipses table
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS eclipses (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            year INTEGER NOT NULL,
            eclipse_type TEXT NOT NULL,
            sun_position REAL NOT NULL,
            moon_position REAL NOT NULL,
            sun_zodiac TEXT NOT NULL,
            moon_zodiac TEXT NOT NULL,
            UNIQUE(timestamp, eclipse_type)
        )
        """)

        # Create solar events table (equinoxes/solstices)
        self.database.execute("""
        CREATE TABLE IF NOT EXISTS solar_events (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            year INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            sun_position REAL NOT NULL,
            zodiac_sign INTEGER NOT NULL,
            UNIQUE(timestamp, event_type)
        )
        """)
        
        # Create indexes for efficient queries
        self._create_indexes()
        
        # Initialize celestial bodies if empty
        self._initialize_celestial_bodies()
    
    def _create_indexes(self) -> None:
        """Create indexes for efficient querying."""
        # Indexes for positions
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_positions_body_timestamp 
        ON positions(body_id, timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_positions_year 
        ON positions(year)
        """)
        
        # Indexes for aspects
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_aspects_bodies 
        ON aspects(body1_id, body2_id)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_aspects_exact_timestamp 
        ON aspects(exact_timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_aspects_year 
        ON aspects(year)
        """)
        
        # Indexes for lunar phases
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_lunar_phases_timestamp 
        ON lunar_phases(timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_lunar_phases_year 
        ON lunar_phases(year)
        """)
        
        # Indexes for planet phases
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_planet_phases_timestamp 
        ON planet_phases(timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_planet_phases_year 
        ON planet_phases(year)
        """)
        
        # Indexes for eclipses
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_eclipses_timestamp 
        ON eclipses(timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_eclipses_year 
        ON eclipses(year)
        """)
        
        # Indexes for solar events
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_solar_events_timestamp 
        ON solar_events(timestamp)
        """)
        self.database.execute("""
        CREATE INDEX IF NOT EXISTS idx_solar_events_year 
        ON solar_events(year)
        """)
    
    def _initialize_celestial_bodies(self) -> None:
        """Initialize the celestial bodies table with default planets."""
        try:
            # Get current celestial bodies
            rows = self.database.query_all("SELECT name FROM celestial_bodies")
            existing_bodies = set(row['name'] for row in rows)
            
            # Define standard planets and celestial bodies with their types
            celestial_bodies = [
                ("Sun", "star"),
                ("Moon", "satellite"),
                ("Mercury", "planet"),
                ("Venus", "planet"),
                ("Mars", "planet"),
                ("Jupiter", "planet"),
                ("Saturn", "planet"),
                ("Uranus", "planet"),
                ("Neptune", "planet"),
                ("Pluto", "dwarf_planet"),
                ("North Node", "lunar_node"),
                ("South Node", "lunar_node"),
                ("Chiron", "asteroid"),
                ("Ceres", "dwarf_planet"),
                ("Pallas", "asteroid"),
                ("Juno", "asteroid"),
                ("Vesta", "asteroid")
            ]
            
            # Add missing celestial bodies
            with self.database.transaction() as conn:
                for name, body_type in celestial_bodies:
                    if name not in existing_bodies:
                        logger.debug(f"Adding celestial body: {name} ({body_type})")
                        
                        try:
                            conn.execute("""
                            INSERT INTO celestial_bodies (name, type)
                            VALUES (?, ?)
                            """, (name, body_type))
                        except sqlite3.Error as e:
                            logger.error(f"SQLite error inserting celestial body {name}: {e}")
                        except Exception as e:
                            logger.error(f"Error inserting celestial body {name}: {e}")
            
            # Verify celestial bodies were added
            count = self.database.query_one("SELECT COUNT(*) as count FROM celestial_bodies")
            logger.info(f"Celestial bodies initialized: {count['count']} bodies in database")
            
        except sqlite3.Error as e:
            logger.error(f"Database error in celestial bodies initialization: {e}")
        except Exception as e:
            logger.error(f"Error initializing celestial bodies: {e}", exc_info=True)

    @handle_database_error
    def get_calculation_status(self) -> Dict:
        """Get the status of calculations.

        Returns:
            Dictionary with calculation status information
        """
        result = {
            'calculated_ranges': [],
            'total_events': 0,
            'has_default_range': False
        }
        
        # Get calculation metadata
        rows = self.database.query_all("""
        SELECT start_year, end_year, calculation_timestamp, status, events_count
        FROM calculation_metadata
        ORDER BY start_year
        """)
        
        for row in rows:
            result['calculated_ranges'].append({
                'start_year': row['start_year'],
                'end_year': row['end_year'],
                'calculation_date': row['calculation_timestamp'],
                'status': row['status'],
                'events_count': row['events_count']
            })
            result['total_events'] += row['events_count']
            
            # Check if default range is calculated
            if row['start_year'] <= 1900 and row['end_year'] >= 2100:
                result['has_default_range'] = True
        
        # Get event counts by type
        result['event_counts'] = {
            'aspects': self._count_table('aspects'),
            'lunar_phases': self._count_table('lunar_phases'),
            'planet_phases': self._count_table('planet_phases'),
            'eclipses': self._count_table('eclipses'),
            'solar_events': self._count_table('solar_events')
        }
        
        return result
    
    def _count_table(self, table_name: str) -> int:
        """Count rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        try:
            result = self.database.query_one(f"SELECT COUNT(*) as count FROM {table_name}")
            return result['count'] if result else 0
        except:
            return 0

    @handle_database_error
    def get_aspects(self, start_date: datetime = None, end_date: datetime = None, 
                 planet1: str = None, planet2: str = None, 
                 aspect_type: str = None, is_major: bool = None) -> List[Dict]:
        """Get aspects from the database with optional filtering.
        
        Args:
            start_date: Optional start date to filter aspects
            end_date: Optional end date to filter aspects
            planet1: Optional first planet to filter aspects
            planet2: Optional second planet to filter aspects
            aspect_type: Optional aspect type to filter aspects
            is_major: Optional flag to filter major/minor aspects
            
        Returns:
            List of aspect records with planet names included
        """
        # Build query with dynamic parameters
        query = """
        SELECT 
            a.id, cb1.name as body1_name, cb2.name as body2_name, 
            a.aspect_type, a.is_major, a.year,
            a.applying_timestamp, a.exact_timestamp, a.separation_timestamp,
            a.exact_position1, a.exact_position2
        FROM aspects a
        JOIN celestial_bodies cb1 ON a.body1_id = cb1.id
        JOIN celestial_bodies cb2 ON a.body2_id = cb2.id
        WHERE 1=1
        """
        
        params = []
        
        # Add date filters if provided
        if start_date:
            query += " AND a.exact_timestamp >= ?"
            params.append(start_date.isoformat())
            
        if end_date:
            query += " AND a.exact_timestamp <= ?"
            params.append(end_date.isoformat())
            
        # Add planet filters if provided
        if planet1:
            query += " AND cb1.name = ?"
            params.append(planet1)
            
        if planet2:
            query += " AND cb2.name = ?"
            params.append(planet2)
            
        # Add aspect type filter if provided
        if aspect_type:
            query += " AND a.aspect_type = ?"
            params.append(aspect_type)
            
        # Add major/minor filter if provided
        if is_major is not None:
            query += " AND a.is_major = ?"
            params.append(1 if is_major else 0)
            
        # Add ordering
        query += " ORDER BY a.exact_timestamp"
        
        # Execute query
        rows = self.database.query_all(query, params)
        
        # Process results
        aspects = []
        for row in rows:
            aspect = dict(row)
            
            # Parse ISO timestamps to datetime objects
            if aspect['applying_timestamp']:
                aspect['applying_timestamp'] = datetime.fromisoformat(aspect['applying_timestamp'])
            if aspect['exact_timestamp']:
                aspect['exact_timestamp'] = datetime.fromisoformat(aspect['exact_timestamp'])
            if aspect['separation_timestamp']:
                aspect['separation_timestamp'] = datetime.fromisoformat(aspect['separation_timestamp'])
                
            aspects.append(aspect)
            
        return aspects

    @handle_database_error
    def verify_aspects_in_database(self, year: int = None) -> Dict:
        """Verify that aspects were properly stored in the database.
        
        Args:
            year: Optional specific year to check, or None for all years
            
        Returns:
            Dictionary with verification results
        """
        try:
            results = {
                'total_aspects': 0,
                'aspects_by_type': {},
                'aspects_by_planet': {},
                'aspects_by_year': {},
                'status': 'success'
            }
            
            # Build the query with optional year filter
            query = """
            SELECT 
                a.aspect_type, 
                cb1.name as body1_name, 
                cb2.name as body2_name,
                a.year,
                COUNT(*) as count
            FROM aspects a
            JOIN celestial_bodies cb1 ON a.body1_id = cb1.id
            JOIN celestial_bodies cb2 ON a.body2_id = cb2.id
            """
            
            params = []
            if year is not None:
                query += " WHERE a.year = ? "
                params.append(year)
            
            # Add grouping
            query += """
            GROUP BY a.aspect_type, cb1.name, cb2.name, a.year
            ORDER BY count DESC
            """
            
            # Execute the query
            rows = self.database.query_all(query, params)
            
            # Process results
            for row in rows:
                aspect_type = row['aspect_type']
                body1 = row['body1_name']
                body2 = row['body2_name']
                year_val = row['year']
                count = row['count']
                
                # Update totals
                results['total_aspects'] += count
                
                # Update by type
                if aspect_type not in results['aspects_by_type']:
                    results['aspects_by_type'][aspect_type] = 0
                results['aspects_by_type'][aspect_type] += count
                
                # Update by planet
                for planet in (body1, body2):
                    if planet not in results['aspects_by_planet']:
                        results['aspects_by_planet'][planet] = 0
                    results['aspects_by_planet'][planet] += count
                
                # Update by year
                if year_val not in results['aspects_by_year']:
                    results['aspects_by_year'][year_val] = 0
                results['aspects_by_year'][year_val] += count
            
            # Log the results
            logger.info(f"Aspect verification results: {results['total_aspects']} total aspects found")
            if year is not None:
                logger.info(f"Aspects for year {year}: {results['aspects_by_year'].get(year, 0)}")
            
            for aspect_type, count in results['aspects_by_type'].items():
                logger.info(f"  - {aspect_type}: {count} aspects")
            
            # Check if any aspects were found
            if results['total_aspects'] == 0:
                results['status'] = 'warning'
                logger.warning("No aspects found in database. Calculation may have failed.")
            
            return results
            
        except Exception as e:
            logger.error(f"Error verifying aspects in database: {e}", exc_info=True)
            return {
                'total_aspects': 0,
                'status': 'error',
                'error': str(e)
            }

    def get_eclipses(self, start_date=None, end_date=None, year=None):
        """Retrieve eclipse events from the database.
        
        Args:
            start_date: Start date for retrieving eclipses
            end_date: End date for retrieving eclipses
            year: Year to retrieve eclipses for (alternative to date range)
            
        Returns:
            List of eclipse events as tuples (timestamp, eclipse_type, sun_position, moon_position, sun_zodiac, moon_zodiac)
        """
        query = "SELECT timestamp, eclipse_type, sun_position, moon_position, sun_zodiac, moon_zodiac FROM eclipses"
        params = []
        
        if year is not None:
            query += " WHERE year = ?"
            params.append(year)
        elif start_date is not None and end_date is not None:
            query += " WHERE timestamp BETWEEN ? AND ?"
            params.extend([start_date.isoformat(), end_date.isoformat()])
        elif start_date is not None:
            query += " WHERE timestamp >= ?"
            params.append(start_date.isoformat())
        elif end_date is not None:
            query += " WHERE timestamp <= ?"
            params.append(end_date.isoformat())
            
        query += " ORDER BY timestamp ASC"
        
        results = self.database.execute(query, params).fetchall()
        return results

    @handle_database_error
    def get_lunar_phases(self, start_date=None, end_date=None, year=None, phase_type=None):
        """Retrieve lunar phase events from the database.
        
        Args:
            start_date: Start date for retrieving lunar phases
            end_date: End date for retrieving lunar phases
            year: Year to retrieve lunar phases for (alternative to date range)
            phase_type: Specific phase type to filter (e.g., 'full_moon', 'new_moon')
            
        Returns:
            List of lunar phase events as dictionaries with timestamp, phase_type, moon_position, sun_position, and zodiac_sign
        """
        query = "SELECT timestamp, phase_type, moon_position, sun_position, zodiac_sign FROM lunar_phases"
        params = []
        
        # Build WHERE clause based on provided parameters
        conditions = []
        
        if year is not None:
            conditions.append("year = ?")
            params.append(year)
        elif start_date is not None and end_date is not None:
            conditions.append("timestamp BETWEEN ? AND ?")
            params.extend([start_date.isoformat(), end_date.isoformat()])
        elif start_date is not None:
            conditions.append("timestamp >= ?")
            params.append(start_date.isoformat())
        elif end_date is not None:
            conditions.append("timestamp <= ?")
            params.append(end_date.isoformat())
            
        if phase_type is not None:
            # Convert the input phase_type to a string value if needed
            phase_type_str = None
            
            # Handle enum objects by getting their value property
            if hasattr(phase_type, 'value'):
                phase_type_str = phase_type.value
            # Handle strings directly
            elif isinstance(phase_type, str):
                phase_type_str = phase_type
            # Any other type, convert to string
            else:
                phase_type_str = str(phase_type)
                
            logger.debug(f"Using lunar phase_type filter: {phase_type_str}")
            conditions.append("phase_type = ?")
            params.append(phase_type_str)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY timestamp ASC"
        
        # Execute query and convert results to dictionaries
        try:
            rows = self.database.execute(query, params).fetchall()
            results = []
            
            for row in rows:
                # Convert SQLite row to dictionary
                lunar_phase = {
                    'timestamp': datetime.fromisoformat(row['timestamp']),
                    'phase_type': row['phase_type'],
                    'moon_position': row['moon_position'],
                    'sun_position': row['sun_position'],
                    'zodiac_sign': row['zodiac_sign']
                }
                results.append(lunar_phase)
                
            return results
        except Exception as e:
            logger.error(f"Error executing lunar phases query: {e}", exc_info=True)
            raise

    @handle_database_error
    def get_planet_phases(self, start_date=None, end_date=None, year=None, body_name=None, phase_type=None):
        """Retrieve planetary phase events from the database.
        
        Args:
            start_date: Start date for retrieving planetary phases
            end_date: End date for retrieving planetary phases
            year: Year to retrieve planetary phases for (alternative to date range)
            body_name: Name of the planet (e.g., 'Mercury', 'Venus')
            phase_type: Specific phase type to filter (e.g., 'retrograde', 'direct')
            
        Returns:
            List of planetary phase events as dictionaries
        """
        query = """
        SELECT p.timestamp, p.phase_type, p.elongation_degree, p.zodiac_sign, cb.name as body_name
        FROM planet_phases p
        JOIN celestial_bodies cb ON p.body_id = cb.id
        """
        
        # Build WHERE clause based on provided parameters
        conditions = []
        params = []
        
        if year is not None:
            conditions.append("p.year = ?")
            params.append(year)
        elif start_date is not None and end_date is not None:
            conditions.append("p.timestamp BETWEEN ? AND ?")
            params.extend([start_date.isoformat(), end_date.isoformat()])
        elif start_date is not None:
            conditions.append("p.timestamp >= ?")
            params.append(start_date.isoformat())
        elif end_date is not None:
            conditions.append("p.timestamp <= ?")
            params.append(end_date.isoformat())
            
        if body_name is not None:
            conditions.append("cb.name = ?")
            params.append(body_name)
            
        if phase_type is not None:
            # Convert the input phase_type to a string value if needed
            phase_type_str = None
            
            # Handle enum objects by getting their value property
            if hasattr(phase_type, 'value'):
                phase_type_str = phase_type.value
            # Handle strings directly
            elif isinstance(phase_type, str):
                phase_type_str = phase_type
            # Any other type, convert to string
            else:
                phase_type_str = str(phase_type)
                
            logger.debug(f"Using planet phase_type filter: {phase_type_str}")
            conditions.append("p.phase_type = ?")
            params.append(phase_type_str)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY p.timestamp ASC"
        
        # Execute query and convert results to dictionaries
        try:
            rows = self.database.execute(query, params).fetchall()
            results = []
            
            for row in rows:
                # Convert SQLite row to dictionary
                planet_phase = {
                    'timestamp': datetime.fromisoformat(row['timestamp']),
                    'phase_type': row['phase_type'],
                    'body_name': row['body_name'],
                    'elongation_degree': row['elongation_degree'],
                    'zodiac_sign': row['zodiac_sign']
                }
                results.append(planet_phase)
                
            return results
        except Exception as e:
            logger.error(f"Error executing planet phases query: {e}", exc_info=True)
            raise

    @handle_database_error
    def get_available_date_range(self) -> Tuple[Optional[int], Optional[int]]:
        """Get the available date range for which calculations are stored in the database.
        
        Returns:
            Tuple of (min_year, max_year) or (None, None) if no data is available
        """
        try:
            # Get the earliest and latest years from calculation_metadata
            min_year_query = """
            SELECT MIN(start_year) as min_year 
            FROM calculation_metadata 
            WHERE status = 'completed'
            """
            
            max_year_query = """
            SELECT MAX(end_year) as max_year 
            FROM calculation_metadata 
            WHERE status = 'completed'
            """
            
            min_result = self.database.query_one(min_year_query)
            max_result = self.database.query_one(max_year_query)
            
            min_year = min_result['min_year'] if min_result and min_result['min_year'] is not None else None
            max_year = max_result['max_year'] if max_result and max_result['max_year'] is not None else None
            
            # If we don't have calculation metadata, try to infer from the data tables
            if min_year is None or max_year is None:
                # Try aspects table
                year_query = """
                SELECT MIN(year) as min_year, MAX(year) as max_year 
                FROM aspects
                """
                
                year_result = self.database.query_one(year_query)
                
                if year_result and 'min_year' in year_result and 'max_year' in year_result:
                    min_year = year_result['min_year'] if min_year is None else min(min_year, year_result['min_year'])
                    max_year = year_result['max_year'] if max_year is None else max(max_year, year_result['max_year'])
                
                # Try lunar_phases table
                year_query = """
                SELECT MIN(year) as min_year, MAX(year) as max_year 
                FROM lunar_phases
                """
                
                year_result = self.database.query_one(year_query)
                
                if year_result and 'min_year' in year_result and 'max_year' in year_result:
                    min_year = year_result['min_year'] if min_year is None else min(min_year, year_result['min_year'])
                    max_year = year_result['max_year'] if max_year is None else max(max_year, year_result['max_year'])
            
            return (min_year, max_year)
            
        except Exception as e:
            logger.error(f"Error getting available date range: {e}")
            return (None, None)

    # Additional query methods will be added as we implement the calculator 