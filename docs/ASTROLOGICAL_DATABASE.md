# Astrological Events Database

## Overview

The astrological events database is a long-term storage solution for pre-calculated astronomical events spanning multiple centuries. Rather than calculating these events on-demand, which can be computationally expensive and lead to redundant calculations, this database maintains a permanent record of events including:

- Planetary aspects (major and minor)
- Lunar phases (8 phases)
- Mercury and Venus cycle phases
- Solar events (equinoxes and solstices)
- Solar and lunar eclipses

By pre-calculating these events and storing them in a database, the application can:
- Provide near-instant results for astrological queries
- Eliminate duplicate calculations and inconsistent results
- Support complex pattern matching across long time periods
- Reduce CPU load during regular operation

## Database Schema

The database consists of several interconnected tables:

### Main Tables

1. **celestial_bodies**: Catalog of celestial objects
   - id: Unique identifier
   - name: Standard name (e.g., "Moon")
   - traditional_name: Historical name
   - type: Body type (planet, luminary, point)

2. **positions**: Planetary positions at specific times
   - body_id: Reference to celestial body
   - timestamp: Date and time
   - year: Year component for partitioning
   - is_heliocentric: Geocentric vs heliocentric
   - absolute_position: Position in degrees (0-360)
   - zodiac_sign: Sign index (0-11)
   - degree_in_sign, minute, second: Position components

3. **aspects**: Planetary aspects
   - body1_id, body2_id: Bodies involved
   - aspect_type: Type of aspect
   - is_major: Major vs minor aspect
   - year: Year component for partitioning
   - applying_timestamp, exact_timestamp, separation_timestamp: Aspect timing
   - position fields: Planetary positions at each point

4. **lunar_phases**: Moon phases
   - timestamp: Date and time
   - year: Year component for partitioning
   - phase_type: Type of phase
   - moon_position, sun_position: Positions
   - zodiac_sign: Sign index (0-11)

5. **planet_phases**: Mercury and Venus phases
   - body_id: Reference to planet
   - phase_type: Type of phase
   - timestamp: Date and time
   - year: Year component for partitioning
   - elongation_degree: For elongation events
   - zodiac_sign: Sign index (0-11)

6. **eclipses**: Solar and lunar eclipses
   - timestamp: Date and time
   - year: Year component for partitioning
   - eclipse_type: Type of eclipse
   - eclipse_classification: Total, partial, etc.
   - position fields: Positions of bodies
   - zodiac_sign: Sign index (0-11)

7. **solar_events**: Equinoxes and solstices
   - timestamp: Date and time
   - year: Year component for partitioning
   - event_type: Type of event
   - sun_position: Position of sun
   - zodiac_sign: Sign index (0-11)

8. **calculation_metadata**: Status of calculations
   - start_year, end_year: Range calculated
   - calculation_timestamp: When calculated
   - status: Status of calculation
   - events_count: Number of events calculated

## Architecture Components

### Repository Layer

The `AstrologicalEventsRepository` class provides:
- Database schema initialization
- Methods for retrieving events by type, date, or range
- Status reporting and management
- Error handling and validation

### Calculation Service

The `AstrologicalEventCalculator` service:
- Calculates astronomical events using Swiss Ephemeris
- Populates the database with calculated events
- Supports progress tracking and reporting
- Handles year-by-year or range-based calculations

### UI Components

The `AstrologicalDatabaseManager` dialog provides:
- Status information about the database
- Controls for initializing the default range (1900-2100)
- Options for calculating custom time ranges
- Progress tracking and notifications

## Usage

### Initializing the Database

1. Access the Database Manager from the Astrology tab
2. Click "Initialize Default Range (1900-2100)" for standard coverage
3. For custom ranges, set the start/end years and click "Calculate Range"
4. Wait for the calculation to complete (this may take time)

### Integrating with Other Components

The astrological database is designed to work with:
- The Planner service for daily events
- The Cycle Calculator for pattern matching
- Other components requiring astronomical data

## Implementation Notes

- Calculations are performed in a background thread to maintain UI responsiveness
- Data is partitioned by year for efficient queries
- Progress updates are provided during long calculations
- All timestamps are stored in ISO format
- Events are indexed for fast retrieval by date or type

## Future Enhancements

- Implement the detailed calculation methods for each event type
- Expand query capabilities for pattern matching
- Add support for additional astronomical phenomena
- Create visualization tools for long-term patterns
- Optimize storage for very large time ranges

## Technical Requirements

- Swiss Ephemeris library for astronomical calculations
- SQLite database for storage
- PyQt6 for the user interface components 