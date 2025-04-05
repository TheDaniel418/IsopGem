"""
Purpose: Provides SQLite database connection and management

This file is part of the shared utilities and serves as a repository component.
It is responsible for establishing and maintaining SQLite database connections,
creating necessary tables, and providing transaction management.

Key components:
- Database: Core class for SQLite database operations and connection management

Dependencies:
- sqlite3: For SQLite database operations
- pathlib: For file path operations
- logging: For error tracking
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from loguru import logger

# Define a shorter type alias for the cursor type
Cursor = sqlite3.Cursor


class Database:
    """Core class for SQLite database management."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, data_dir: Optional[str] = None):
        """Implement singleton pattern for database connections.

        Args:
            data_dir: Optional directory for database file location

        Returns:
            Database singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                instance = super(Database, cls).__new__(cls)
                instance._initialize(data_dir)
                cls._instance = instance
            return cls._instance

    def _initialize(self, data_dir: Optional[str] = None) -> None:
        """Initialize the database.

        Args:
            data_dir: Optional directory for database file location
        """
        # Set default data directory if none provided
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".isopgem", "data")

        self._data_dir = Path(data_dir)
        self._db_file = self._data_dir / "isopgem.db"

        # Create data directory if it doesn't exist
        os.makedirs(self._data_dir, exist_ok=True)

        # Create connection pool
        self._local = threading.local()

        # Initialize database
        self._create_tables()

        logger.debug(f"Database initialized with file: {self._db_file}")

    @contextmanager
    def connection(self):
        """Get a database connection from the pool.

        Yields:
            SQLite connection object
        """
        # Create connection if it doesn't exist for this thread
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(
                self._db_file,
                detect_types=sqlite3.PARSE_DECLTYPES,
                isolation_level=None,  # Autocommit mode
            )
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrent access
            self._local.connection.execute("PRAGMA journal_mode = WAL")
            # Row factory for dictionary-like access
            self._local.connection.row_factory = sqlite3.Row

        try:
            yield self._local.connection
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise

    @contextmanager
    def transaction(self):
        """Start a database transaction.

        Yields:
            SQLite connection object in a transaction
        """
        with self.connection() as conn:
            try:
                # Begin transaction
                conn.execute("BEGIN")
                yield conn
                # Commit if no exception
                conn.execute("COMMIT")
            except Exception as e:
                # Rollback on exception
                conn.execute("ROLLBACK")
                logger.error(f"Transaction error: {e}")
                raise

    def execute(
        self, query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> Cursor:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            SQLite cursor object
        """
        with self.connection() as conn:
            try:
                if params is None:
                    # Explicitly cast the return value to Cursor
                    return cast(Cursor, conn.execute(query))
                else:
                    # Explicitly cast the return value to Cursor
                    return cast(Cursor, conn.execute(query, params))
            except sqlite3.Error as e:
                logger.error(f"SQL error [{query}]: {e}")
                raise

    def executemany(
        self, query: str, param_seq: List[Union[Tuple, Dict[str, Any]]]
    ) -> Cursor:
        """Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string
            param_seq: List of parameter sets

        Returns:
            SQLite cursor object
        """
        with self.connection() as conn:
            try:
                # Explicitly cast the return value to Cursor
                return cast(Cursor, conn.executemany(query, param_seq))
            except sqlite3.Error as e:
                logger.error(f"SQL error [{query}]: {e}")
                raise

    def query_one(
        self, query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query and return the first result row.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            First result row as dictionary, or None if no results
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def query_all(
        self, query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return all result rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        self._create_tags_table()
        self._create_calculations_table()
        self._create_indices()

    def _create_tags_table(self) -> None:
        """Create the tags table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS tags (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(query)

    def _create_calculations_table(self) -> None:
        """Create the calculations table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS calculations (
            id TEXT PRIMARY KEY,
            input_text TEXT NOT NULL,
            calculation_type TEXT NOT NULL,
            custom_method_name TEXT,
            result_value INTEGER NOT NULL,
            favorite BOOLEAN NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(query)

        # Create the calculation_tags junction table
        query = """
        CREATE TABLE IF NOT EXISTS calculation_tags (
            calculation_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            PRIMARY KEY (calculation_id, tag_id),
            FOREIGN KEY (calculation_id) REFERENCES calculations(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
        """
        self.execute(query)

    def _create_indices(self) -> None:
        """Create database indices for better query performance."""
        # Calculations indices
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_calculations_input_text ON calculations(input_text);
        """
        )
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_calculations_result_value ON calculations(result_value);
        """
        )
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_calculations_calculation_type ON calculations(calculation_type);
        """
        )
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_calculations_favorite ON calculations(favorite);
        """
        )
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_calculations_created_at ON calculations(created_at);
        """
        )

        # Tags indices
        self.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
        """
        )

    def close(self) -> None:
        """Close all database connections."""
        if hasattr(self._local, "connection"):
            try:
                self._local.connection.close()
                delattr(self._local, "connection")
                logger.debug("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
