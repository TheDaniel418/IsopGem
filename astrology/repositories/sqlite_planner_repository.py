"""
Purpose: Provides SQLite repository for planner events.

This file is part of the astrology pillar and serves as a repository component.
It provides functionality to store and retrieve planner events using SQLite.

Key components:
- SQLitePlannerRepository: Repository for planner events

Dependencies:
- sqlite3: For database operations
- astrology.models: For planner event models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger

from astrology.models.planner import EventType, PlannerEvent
from shared.repositories.database import Database


class SQLitePlannerRepository:
    """Repository for storing planner events in SQLite."""

    def __init__(self, database: Database):
        """Initialize the planner repository.

        Args:
            database: Database instance
        """
        self.database = database
        self._initialize_tables()
        self._migrate_database()
        logger.debug("SQLitePlannerRepository initialized")

    def _initialize_tables(self) -> None:
        """Initialize the database tables."""
        # Create events table
        query = """
        CREATE TABLE IF NOT EXISTS planner_events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            color TEXT NOT NULL,
            repeats_yearly INTEGER NOT NULL DEFAULT 0
        )
        """
        self.database.execute(query)

        # Create settings table
        query = """
        CREATE TABLE IF NOT EXISTS planner_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),  -- Ensure only one settings row
            default_event_duration INTEGER NOT NULL DEFAULT 60,
            show_lunar_phases INTEGER NOT NULL DEFAULT 1,
            show_planetary_hours INTEGER NOT NULL DEFAULT 1,
            show_planetary_aspects INTEGER NOT NULL DEFAULT 1,
            show_retrogrades INTEGER NOT NULL DEFAULT 1,
            show_eclipses INTEGER NOT NULL DEFAULT 1,
            show_venus_cycles INTEGER NOT NULL DEFAULT 1,
            default_location_name TEXT,
            default_location_display TEXT,
            default_location_latitude REAL,
            default_location_longitude REAL,
            default_location_country TEXT,
            default_location_state TEXT,
            default_location_city TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.database.execute(query)

        # Create index for faster date-based lookups
        self.database.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_planner_events_start_time
        ON planner_events(start_time)
        """
        )

    def _migrate_database(self) -> None:
        """Perform database migrations if needed."""
        # Check if location columns exist
        try:
            # Try to get columns in planner_settings table
            pragma_result = self.database.query_all(
                "PRAGMA table_info(planner_settings)"
            )

            # Extract column names
            column_names = [row["name"] for row in pragma_result]

            # Check if location columns are missing
            if "default_location_name" not in column_names:
                logger.info("Migrating planner_settings table to add location columns")

                # Add location columns with ALTER TABLE statements
                with self.database.transaction() as conn:
                    migrations = [
                        "ALTER TABLE planner_settings ADD COLUMN default_location_name TEXT;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_display TEXT;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_latitude REAL;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_longitude REAL;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_country TEXT;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_state TEXT;",
                        "ALTER TABLE planner_settings ADD COLUMN default_location_city TEXT;",
                    ]

                    for migration in migrations:
                        conn.execute(migration)

                logger.info("Migration completed successfully")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")

    def save_event(self, event: PlannerEvent) -> bool:
        """Save a planner event.

        Args:
            event: Event to save

        Returns:
            True if successful
        """
        try:
            with self.database.transaction() as conn:
                params = (
                    event.id,
                    event.title,
                    event.description,
                    event.event_type.name,
                    event.start_time.isoformat(),
                    event.end_time.isoformat() if event.end_time else None,
                    event.color,
                    1 if event.repeats_yearly else 0,
                )

                conn.execute(
                    """
                    INSERT OR REPLACE INTO planner_events (
                        id, title, description, event_type, start_time,
                        end_time, color, repeats_yearly
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    params,
                )
                return True
        except Exception as e:
            logger.error(f"Error saving event: {e}", exc_info=True)
            return False

    def get_events_for_date(self, date: datetime.date) -> List[PlannerEvent]:
        """Get events for a specific date.

        Args:
            date: Date to get events for

        Returns:
            List of events
        """
        try:
            # Query for both exact date matches and yearly repeating events
            rows = self.database.query_all(
                """
                SELECT * FROM planner_events
                WHERE date(start_time) = ?
                OR (repeats_yearly = 1
                    AND strftime('%m-%d', start_time) = strftime('%m-%d', ?))
                ORDER BY start_time
            """,
                (date.isoformat(), date.isoformat()),
            )

            return [self._row_to_event(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting events: {e}", exc_info=True)
            return []

    def get_events_for_month(
        self, year: int, month: int
    ) -> Dict[int, List[PlannerEvent]]:
        """Get events for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Dictionary mapping days to events
        """
        try:
            # Query for events in the specified month and yearly repeating events
            rows = self.database.query_all(
                """
                SELECT * FROM planner_events
                WHERE (strftime('%Y-%m', start_time) = ?
                OR repeats_yearly = 1)
                ORDER BY start_time
            """,
                (f"{year:04d}-{month:02d}",),
            )

            events_by_day = {}
            for row in rows:
                event = self._row_to_event(row)
                day = event.start_time.day
                if day not in events_by_day:
                    events_by_day[day] = []
                events_by_day[day].append(event)

            return events_by_day
        except Exception as e:
            logger.error(f"Error getting events: {e}", exc_info=True)
            return {}

    def _row_to_event(self, row: Dict[str, any]) -> PlannerEvent:
        """Convert a database row to a PlannerEvent.

        Args:
            row: Database row as dictionary

        Returns:
            PlannerEvent object
        """
        # Parse start_time and ensure it's naive
        start_time = datetime.fromisoformat(row["start_time"])
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)

        # Parse end_time if present and ensure it's naive
        end_time = None
        if row["end_time"]:
            end_time = datetime.fromisoformat(row["end_time"])
            if end_time.tzinfo is not None:
                end_time = end_time.replace(tzinfo=None)

        return PlannerEvent(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            event_type=EventType[row["event_type"]],
            start_time=start_time,
            end_time=end_time,
            color=row["color"],
            repeats_yearly=bool(row["repeats_yearly"]),
        )

    def delete_event(self, event_id: str) -> bool:
        """Delete a planner event.

        Args:
            event_id: ID of event to delete

        Returns:
            True if successful
        """
        try:
            with self.database.transaction() as conn:
                conn.execute("DELETE FROM planner_events WHERE id = ?", (event_id,))
                return True
        except Exception as e:
            logger.error(f"Error deleting event: {e}", exc_info=True)
            return False

    def get_event_by_id(self, event_id: str) -> Optional[PlannerEvent]:
        """Get a specific event by ID.

        Args:
            event_id: ID of event to retrieve

        Returns:
            PlannerEvent if found, None otherwise
        """
        try:
            row = self.database.query_one(
                "SELECT * FROM planner_events WHERE id = ?", (event_id,)
            )
            return self._row_to_event(row) if row else None
        except Exception as e:
            logger.error(f"Error getting event: {e}", exc_info=True)
            return None

    def get_events_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[PlannerEvent]:
        """Get events within a date range.

        Args:
            start_date: Start of range (inclusive)
            end_date: End of range (inclusive)

        Returns:
            List of events in the range
        """
        try:
            # Query for events in date range and yearly repeating events
            rows = self.database.query_all(
                """
                SELECT * FROM planner_events
                WHERE (date(start_time) BETWEEN ? AND ?)
                OR (repeats_yearly = 1
                    AND strftime('%m-%d', start_time) BETWEEN
                        strftime('%m-%d', ?) AND strftime('%m-%d', ?))
                ORDER BY start_time
            """,
                (
                    start_date.isoformat(),
                    end_date.isoformat(),
                    start_date.isoformat(),
                    end_date.isoformat(),
                ),
            )

            return [self._row_to_event(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting events in range: {e}", exc_info=True)
            return []

    def get_upcoming_events(self, days: int = 7) -> List[PlannerEvent]:
        """Get upcoming events for the next N days.

        Args:
            days: Number of days to look ahead (default: 7)

        Returns:
            List of upcoming events
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.get_events_in_range(start_date, end_date)

    def get_events_by_type(self, event_type: EventType) -> List[PlannerEvent]:
        """Get all events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of events of the specified type
        """
        try:
            rows = self.database.query_all(
                "SELECT * FROM planner_events WHERE event_type = ? ORDER BY start_time",
                (event_type.name,),
            )
            return [self._row_to_event(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting events by type: {e}", exc_info=True)
            return []

    def clear_old_events(self, before_date: datetime) -> int:
        """Delete events older than the specified date (non-repeating only).

        Args:
            before_date: Delete events before this date

        Returns:
            Number of events deleted
        """
        try:
            with self.database.transaction() as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM planner_events
                    WHERE repeats_yearly = 0
                    AND date(start_time) < ?
                """,
                    (before_date.isoformat(),),
                )
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error clearing old events: {e}", exc_info=True)
            return 0
