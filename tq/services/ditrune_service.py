#!/usr/bin/env python3
"""
Ditrune Service for accessing and managing ditrune data.

This service provides a clean interface for accessing ditrune information
from the database, including hierophants, acolytes, and temples.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger


class DitruneService:
    """Service for accessing and managing ditrune data."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the ditrune service.

        Args:
            db_path: Optional path to the ditrune database. If None, uses the default path.
        """
        if db_path is None:
            # Use default path
            self.db_path = os.path.join(
                os.path.expanduser("~"), ".isopgem", "data", "ditrunes.db"
            )
        else:
            self.db_path = db_path

        # Check if database exists, if not, create it
        if not os.path.exists(self.db_path):
            self._create_database()

    def _ternary_to_decimal(self, ternary: str) -> int:
        """Convert a ternary string to decimal."""
        return sum(int(digit) * (3**i) for i, digit in enumerate(reversed(ternary)))

    def _determine_ditrune_type(self, ternary: str) -> Tuple[str, int, Optional[int]]:
        """
        Determine the type of a ditrune (hierophant, acolyte, or temple).

        Returns:
            Tuple of (type, family, position)
            - type: "hierophant", "acolyte", or "temple"
            - family: 0-8
            - position: 1-8 for acolytes, None for hierophants and temples
        """
        from tq.services.ternary_dimension_interpreter_new import ACOLYTES, HIEROPHANTS

        # Check if it's a hierophant
        for family_id, hierophant in HIEROPHANTS.items():
            if hierophant["ternary"] == ternary:
                return "hierophant", family_id, None

        # Check if it's an acolyte
        for acolyte_id, acolyte in ACOLYTES.items():
            if acolyte.get("ternary") == ternary:
                family = acolyte.get("family")
                # Extract position from acolyte_id (format: "family_position")
                position = int(acolyte_id.split("_")[1])
                return "acolyte", family, position

        # If not hierophant or acolyte, it's a temple
        # Determine family based on first digit (simplified approach)
        family = int(ternary[0])
        return "temple", family, None

    def _get_temple_properties(self, ternary: str) -> Dict[str, str]:
        """Get properties specific to temples."""
        # Determine temple type based on first bigram (positions 1 & 6)
        first_bigram_decimal = int(ternary[0]) * 3 + int(ternary[5])

        # Temple types from docs/kamea/elemental_analysis_reference.md
        temple_types = [
            "The Nexus",  # 0 - Σύνδεσμος (Syndesmos)
            "The Crucible",  # 1 - Χωνευτήριον (Choneuterion)
            "The Beacon",  # 2 - Φρυκτωρία (Phryktoria)
            "The Reservoir",  # 3 - Δεξαμενή (Dexamene)
            "The Threshold",  # 4 - Κατώφλιον (Katophlion)
            "The Conduit",  # 5 - Ὀχετός (Ochetos)
            "The Resonator",  # 6 - Ἠχεῖον (Echeion)
            "The Catalyst",  # 7 - Ἐπιταχυντής (Epitachyntes)
            "The Fulcrum",  # 8 - Ὑπομόχλιον (Hypomochlion)
        ]

        temple_type = (
            temple_types[first_bigram_decimal]
            if 0 <= first_bigram_decimal < len(temple_types)
            else "The Nexus"
        )

        # Determine element descriptor
        element_descriptor = self._determine_element_descriptor(ternary)

        # Get kamea locator
        kamea_locator = f"{ternary[0]}-{ternary[2]}-{ternary[5]}"  # Simplified version

        return {
            "temple_type": temple_type,
            "element_descriptor": element_descriptor,
            "kamea_locator": kamea_locator,
        }

    def _determine_element_descriptor(self, ternary: str) -> str:
        """Determine the element descriptor based on the ternary value."""
        # Count elements
        aperture_count = ternary.count("0")
        surge_count = ternary.count("1")
        lattice_count = ternary.count("2")

        # Check for palindromic pattern
        if ternary == ternary[::-1]:
            return "of Perfect Reflection"

        # Check for ascending pattern (0→1→2)
        if "012" in ternary:
            return "of Rising Power"

        # Check for descending pattern (2→1→0)
        if "210" in ternary:
            return "of Deepening Wisdom"

        # Check for alternating pattern
        if "010" in ternary or "121" in ternary or "202" in ternary:
            return "of Rhythmic Exchange"

        # Check for concentrated pattern (3+ of same digit)
        if aperture_count >= 3:
            return "of Open Mystery"
        elif surge_count >= 3:
            return "of Flowing Energy"
        elif lattice_count >= 3:
            return "of Formed Pattern"

        # Default to balanced
        return "of Harmonic Balance"

    def _create_database(self) -> None:
        """Create the ditrune database if it doesn't exist."""
        try:
            import itertools

            from tq.services.ternary_dimension_interpreter_new import (
                ACOLYTES,
                HIEROPHANTS,
            )

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Create the database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the ditrunes table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS ditrunes (
                id INTEGER PRIMARY KEY,
                ternary TEXT NOT NULL UNIQUE,
                decimal INTEGER NOT NULL,
                type TEXT NOT NULL,
                family INTEGER NOT NULL,
                position INTEGER,
                name TEXT,
                greek TEXT,
                description TEXT,
                kamea_locator TEXT,
                temple_type TEXT,
                element_descriptor TEXT,
                bigram1 INTEGER,
                bigram2 INTEGER,
                bigram3 INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            )

            # Create indices for faster lookups
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ditrunes_ternary ON ditrunes(ternary)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ditrunes_decimal ON ditrunes(decimal)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ditrunes_type ON ditrunes(type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ditrunes_family ON ditrunes(family)"
            )

            # Generate all possible 6-digit ternary numbers
            all_ditrunes = ["".join(p) for p in itertools.product("012", repeat=6)]
            logger.info(f"Generated {len(all_ditrunes)} ditrunes")

            # Process each ditrune
            for ternary in all_ditrunes:
                # Convert to decimal
                decimal = self._ternary_to_decimal(ternary)

                # Determine type, family, and position
                ditrune_type, family, position = self._determine_ditrune_type(ternary)

                # Initialize properties
                name = None
                greek = None
                description = None
                temple_type = None
                element_descriptor = None
                kamea_locator = None

                # Get type-specific properties
                if ditrune_type == "hierophant":
                    hierophant = HIEROPHANTS.get(family, {})
                    name = hierophant.get("name")
                    greek = hierophant.get("greek")
                    description = hierophant.get("description")
                elif ditrune_type == "acolyte":
                    # Find the acolyte in the ACOLYTES dictionary
                    for acolyte_id, acolyte in ACOLYTES.items():
                        if acolyte.get("ternary") == ternary:
                            name = acolyte.get("title")
                            greek = acolyte.get("greek")
                            description = acolyte.get("function")
                            break
                else:  # temple
                    temple_props = self._get_temple_properties(ternary)
                    temple_type = temple_props["temple_type"]
                    element_descriptor = temple_props["element_descriptor"]
                    kamea_locator = temple_props["kamea_locator"]
                    name = f"{temple_type} {element_descriptor}"

                # Calculate bigrams
                bigram1 = int(ternary[0]) * 3 + int(ternary[5])  # Positions 1 & 6
                bigram2 = int(ternary[1]) * 3 + int(ternary[4])  # Positions 2 & 5
                bigram3 = int(ternary[2]) * 3 + int(ternary[3])  # Positions 3 & 4

                # Insert into database
                cursor.execute(
                    """
                INSERT OR REPLACE INTO ditrunes
                (ternary, decimal, type, family, position, name, greek, description,
                 kamea_locator, temple_type, element_descriptor, bigram1, bigram2, bigram3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        ternary,
                        decimal,
                        ditrune_type,
                        family,
                        position,
                        name,
                        greek,
                        description,
                        kamea_locator,
                        temple_type,
                        element_descriptor,
                        bigram1,
                        bigram2,
                        bigram3,
                    ),
                )

            conn.commit()
            conn.close()
            logger.info(f"Created ditrune database at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to create ditrune database: {e}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the ditrune database."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to ditrune database: {e}")
            raise

    def get_ditrune_by_ternary(self, ternary: str) -> Optional[Dict[str, Any]]:
        """Get a ditrune by its ternary representation.

        Args:
            ternary: The 6-digit ternary string

        Returns:
            Dictionary with ditrune properties or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ditrunes WHERE ternary = ?", (ternary,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        # Convert row to dictionary
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    def get_ditrune_by_decimal(self, decimal: int) -> Optional[Dict[str, Any]]:
        """Get a ditrune by its decimal value.

        Args:
            decimal: The decimal value of the ditrune

        Returns:
            Dictionary with ditrune properties or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ditrunes WHERE decimal = ?", (decimal,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        # Convert row to dictionary
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    def get_all_hierophants(self) -> List[Dict[str, Any]]:
        """Get all hierophants (Prime Ditrunes).

        Returns:
            List of dictionaries with hierophant properties
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM ditrunes WHERE type = 'hierophant' ORDER BY family"
        )

        rows = cursor.fetchall()
        conn.close()

        # Convert rows to dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_all_acolytes(self, family: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all acolytes (Composite Ditrunes), optionally filtered by family.

        Args:
            family: Optional family ID to filter by (0-8)

        Returns:
            List of dictionaries with acolyte properties
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if family is not None:
            cursor.execute(
                "SELECT * FROM ditrunes WHERE type = 'acolyte' AND family = ? ORDER BY position",
                (family,),
            )
        else:
            cursor.execute(
                "SELECT * FROM ditrunes WHERE type = 'acolyte' ORDER BY family, position"
            )

        rows = cursor.fetchall()
        conn.close()

        # Convert rows to dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_temples_by_family(
        self, family: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get temples (Concurrent Ditrunes) for a specific family.

        Args:
            family: Family ID (0-8)
            limit: Optional limit on the number of temples to return

        Returns:
            List of dictionaries with temple properties
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if limit is not None:
            cursor.execute(
                "SELECT * FROM ditrunes WHERE type = 'temple' AND family = ? LIMIT ?",
                (family, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM ditrunes WHERE type = 'temple' AND family = ?", (family,)
            )

        rows = cursor.fetchall()
        conn.close()

        # Convert rows to dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_all_ditrunes(
        self, type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all ditrunes, optionally filtered by type.

        Args:
            type_filter: Optional type to filter by ('hierophant', 'acolyte', or 'temple')

        Returns:
            List of dictionaries with ditrune properties
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if type_filter is not None:
            cursor.execute(
                "SELECT * FROM ditrunes WHERE type = ? ORDER BY family, position, ternary",
                (type_filter,),
            )
        else:
            cursor.execute(
                "SELECT * FROM ditrunes ORDER BY type, family, position, ternary"
            )

        rows = cursor.fetchall()
        conn.close()

        # Convert rows to dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_ditrune_count(self, type_filter: Optional[str] = None) -> int:
        """Get the count of ditrunes, optionally filtered by type.

        Args:
            type_filter: Optional type to filter by ('hierophant', 'acolyte', or 'temple')

        Returns:
            Count of ditrunes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if type_filter is not None:
            cursor.execute(
                "SELECT COUNT(*) FROM ditrunes WHERE type = ?", (type_filter,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM ditrunes")

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_governing_acolytes(self, temple_ternary: str) -> List[Dict[str, Any]]:
        """Get the acolytes that govern a temple.

        Args:
            temple_ternary: The ternary representation of the temple

        Returns:
            List of dictionaries with acolyte properties
        """
        # Get the temple's family
        temple = self.get_ditrune_by_ternary(temple_ternary)
        if temple is None or temple["type"] != "temple":
            return []

        family = temple["family"]

        # Get all acolytes in this family
        acolytes = self.get_all_acolytes(family)

        # Find acolytes that share at least 3 digits with the temple
        governing_acolytes = []
        for acolyte in acolytes:
            acolyte_ternary = acolyte["ternary"]
            matches = sum(
                1
                for i in range(min(len(temple_ternary), len(acolyte_ternary)))
                if temple_ternary[i] == acolyte_ternary[i]
            )

            if matches >= 3:
                governing_acolytes.append(acolyte)

        return governing_acolytes

    def get_unique_ditrune_id(self, ditrune: Dict[str, Any]) -> str:
        """Generate a unique ID for a ditrune that can be used across the application.

        Args:
            ditrune: Dictionary with ditrune properties

        Returns:
            Unique ID string
        """
        ditrune_type = ditrune["type"]

        if ditrune_type == "hierophant":
            return f"hierophant_{ditrune['family']}"
        elif ditrune_type == "acolyte":
            return f"acolyte_{ditrune['family']}_{ditrune['position']}"
        else:  # temple
            # Use decimal value for uniqueness
            return f"temple_{ditrune['decimal']}"
