"""
Purpose: Provides persistent storage and retrieval for calculation results using SQLite

This file is part of the shared repositories and serves as a repository component.
It is responsible for storing, retrieving, updating, and deleting calculation
results in an SQLite database, ensuring data persistence across application sessions.

Key components:
- SQLiteCalculationRepository: Repository class for managing calculation data persistence
  with methods for CRUD operations on calculation results

Dependencies:
- sqlite3: For SQLite database operations
- typing: For type annotations
- datetime: For timestamp handling
- loguru: For logging
- gematria.models.calculation_result: For the CalculationResult data model
- gematria.models.calculation_type: For the CalculationType data model
- shared.repositories.database: For database connection management

Related files:
- gematria/models/calculation_result.py: Data model for calculation results
- gematria/services/calculation_database_service.py: Uses this repository
- shared/repositories/sqlite_tag_repository.py: Companion repository for tag data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from shared.repositories.database import Database


class SQLiteCalculationRepository:
    """Repository for managing calculation results using SQLite."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the calculation repository.

        Args:
            data_dir: Directory where database will be stored
        """
        self.db = Database(data_dir)
        logger.debug("SQLiteCalculationRepository initialized")

    def get_all_calculations(self) -> List[CalculationResult]:
        """
        Get all calculations from the database.

        Returns:
            List[CalculationResult]: All calculations
        """
        query = """
            SELECT id, input_text, result_value, calculation_type, custom_method_name, 
                   created_at, favorite, notes
            FROM calculations
            ORDER BY created_at DESC
        """

        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            calculations = []

            for row in rows:
                calculation_id = row[0]

                # Get tags for this calculation
                tags = self._get_tags_for_calculation(cursor, calculation_id)

                # Create CalculationResult object
                calculation = CalculationResult(
                    id=calculation_id,
                    input_text=row[1],
                    result_value=row[2],
                    calculation_type=row[3],
                    custom_method_name=row[4],
                    timestamp=row[5],
                    favorite=bool(row[6]),
                    notes=row[7],
                    tags=tags,
                )

                calculations.append(calculation)

            return calculations

    def count_calculations(self) -> int:
        """
        Count the total number of calculations in the database.

        Returns:
            int: Total number of calculations
        """
        query = "SELECT COUNT(*) FROM calculations"

        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count

    def get_calculations_page(
        self,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
    ) -> List[CalculationResult]:
        """
        Get a paginated list of calculations with sorting.

        Args:
            offset: Starting index for pagination
            limit: Maximum number of items to return
            sort_by: Column to sort by (created_at, input_text, result_value)
            sort_order: Sort direction (ASC or DESC)

        Returns:
            List[CalculationResult]: Paginated calculation results
        """
        # Validate sort column to prevent SQL injection
        valid_sort_columns = {
            "created_at",
            "input_text",
            "result_value",
            "calculation_type",
        }
        if sort_by not in valid_sort_columns:
            sort_by = "created_at"  # Default to date if invalid

        # Validate sort order
        if sort_order.upper() not in {"ASC", "DESC"}:
            sort_order = "DESC"  # Default to DESC if invalid

        query = f"""
            SELECT id, input_text, result_value, calculation_type, custom_method_name, 
                   created_at, favorite, notes
            FROM calculations
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """

        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            calculations = []

            for row in rows:
                calculation_id = row[0]

                # Get tags for this calculation
                tags = self._get_tags_for_calculation(cursor, calculation_id)

                # Create CalculationResult object
                calculation = CalculationResult(
                    id=calculation_id,
                    input_text=row[1],
                    result_value=row[2],
                    calculation_type=row[3],
                    custom_method_name=row[4],
                    timestamp=row[5],
                    favorite=bool(row[6]),
                    notes=row[7],
                    tags=tags,
                )

                calculations.append(calculation)

            return calculations

    def get_unique_calculation_methods(self) -> List[str]:
        """
        Get a list of all unique calculation methods used in the database.

        Returns:
            List[str]: List of calculation method names
        """
        query = """
            SELECT DISTINCT calculation_method
            FROM calculations
            ORDER BY calculation_method
        """

        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            methods = [row[0] for row in rows]
            return methods

    def get_calculation(self, calculation_id: str) -> Optional[CalculationResult]:
        """Get a specific calculation result by ID.

        Args:
            calculation_id: ID of the calculation result to retrieve

        Returns:
            CalculationResult instance or None if not found
        """
        query = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
        WHERE c.id = ?
        GROUP BY c.id
        """

        row = self.db.query_one(query, (calculation_id,))

        if row:
            return self._row_to_calculation(row)

        logger.debug(f"Calculation with ID {calculation_id} not found")
        return None

    def save_calculation(self, calculation: CalculationResult) -> bool:
        """Save a calculation to the database.

        Args:
            calculation: The calculation to save

        Returns:
            True if successful, False otherwise
        """

        # Set timestamp if not provided
        if not calculation.timestamp:
            calculation.timestamp = datetime.now()

        # Convert calculation_type to string for storage
        calculation_type_str = self._calculation_type_to_str(
            calculation.calculation_type
        )

        # Check if calculation exists
        existing = self.get_calculation(calculation.id)

        try:
            with self.db.transaction() as conn:
                if existing:
                    # Update existing calculation
                    query = """
                    UPDATE calculations
                    SET input_text = ?, calculation_type = ?, custom_method_name = ?,
                        result_value = ?, favorite = ?, notes = ?
                    WHERE id = ?
                    """

                    conn.execute(
                        query,
                        (
                            calculation.input_text,
                            calculation_type_str,
                            calculation.custom_method_name,
                            calculation.result_value,
                            1 if calculation.favorite else 0,
                            calculation.notes,
                            calculation.id,
                        ),
                    )

                    # Delete existing tag associations and re-add them
                    conn.execute(
                        "DELETE FROM calculation_tags WHERE calculation_id = ?",
                        (calculation.id,),
                    )

                    logger.debug(f"Updated calculation: {calculation.id}")
                else:
                    # Insert new calculation
                    query = """
                    INSERT INTO calculations (
                        id, input_text, calculation_type, custom_method_name,
                        result_value, favorite, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    conn.execute(
                        query,
                        (
                            calculation.id,
                            calculation.input_text,
                            calculation_type_str,
                            calculation.custom_method_name,
                            calculation.result_value,
                            1 if calculation.favorite else 0,
                            calculation.notes,
                            calculation.timestamp,  # Use timestamp instead of created_at
                        ),
                    )

                    logger.debug(f"Created calculation: {calculation.id}")

                # Add tag associations
                if calculation.tags:
                    tag_params = [
                        (calculation.id, tag_id) for tag_id in calculation.tags
                    ]
                    conn.executemany(
                        "INSERT INTO calculation_tags (calculation_id, tag_id) VALUES (?, ?)",
                        tag_params,
                    )

            return True
        except Exception as e:
            logger.error(f"Failed to save calculation: {e}")
            return False

    def delete_calculation(self, calculation_id: str) -> bool:
        """Delete a calculation by ID.

        Args:
            calculation_id: The ID of the calculation to delete

        Returns:
            True if successful, False otherwise
        """
        query = "DELETE FROM calculations WHERE id = ?"

        try:
            cursor = self.db.execute(query, (calculation_id,))

            if cursor.rowcount > 0:
                logger.debug(f"Deleted calculation with ID: {calculation_id}")
                return True
            else:
                logger.debug(f"Calculation not found for deletion: {calculation_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete calculation: {e}")
            return False

    def find_calculations_by_tag(self, tag_id: str) -> List[CalculationResult]:
        """Find calculations by tag ID.

        Args:
            tag_id: The tag ID to search for

        Returns:
            List of matching calculation results
        """
        query = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        JOIN calculation_tags ct ON c.id = ct.calculation_id
        WHERE ct.tag_id = ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """

        rows = self.db.query_all(query, (tag_id,))
        return [self._row_to_calculation(row) for row in rows]

    def find_calculations_by_text(self, text: str) -> List[CalculationResult]:
        """Find all calculations containing the specified text.

        Args:
            text: Text to search for in input_text or notes

        Returns:
            List of calculation results containing the specified text
        """
        query = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
        WHERE c.input_text LIKE ? OR c.notes LIKE ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """

        search_param = f"%{text}%"
        rows = self.db.query_all(query, (search_param, search_param))
        return [self._row_to_calculation(row) for row in rows]

    def find_calculations_by_value(self, value: int) -> List[CalculationResult]:
        """Find all calculations with the specified result value.

        Args:
            value: Numeric result value to search for

        Returns:
            List of calculation results with the specified value
        """
        query = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
        WHERE c.result_value = ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """

        rows = self.db.query_all(query, (value,))
        return [self._row_to_calculation(row) for row in rows]

    def find_calculations_by_method(
        self, method: Union[CalculationType, str]
    ) -> List[CalculationResult]:
        """Find all calculations using a specific calculation method.

        Args:
            method: Calculation method (enum or custom method name)

        Returns:
            List of calculation results using the specified method
        """
        if isinstance(method, CalculationType):
            # Convert enum value to string for database lookup
            method_str = self._calculation_type_to_str(method)
            query = """
            SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
            FROM calculations c
            LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
            WHERE c.calculation_type = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
            rows = self.db.query_all(query, (method_str,))
        else:
            # Search by custom method name
            query = """
            SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
            FROM calculations c
            LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
            WHERE c.custom_method_name = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
            rows = self.db.query_all(query, (method,))

        return [self._row_to_calculation(row) for row in rows]

    def find_favorites(self) -> List[CalculationResult]:
        """Find all favorite calculations.

        Returns:
            List of favorite calculation results
        """
        query = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
        WHERE c.favorite = 1
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """

        rows = self.db.query_all(query)
        return [self._row_to_calculation(row) for row in rows]

    def find_recent_calculations(self, limit: int = 10) -> List[CalculationResult]:
        """Find the most recent calculations.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent calculation results, sorted by timestamp (newest first)
        """
        query = f"""
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT {limit}
        """

        rows = self.db.query_all(query)
        return [self._row_to_calculation(row) for row in rows]

    def get_unique_values(self) -> Set[int]:
        """Get a set of all unique calculation result values.

        Returns:
            Set of unique calculation result values
        """
        query = "SELECT DISTINCT result_value FROM calculations"
        rows = self.db.query_all(query)
        return {row["result_value"] for row in rows}

    def search_calculations(self, criteria: Dict[str, Any]) -> List[CalculationResult]:
        """Search for calculations based on multiple criteria.

        Args:
            criteria: Dictionary of search criteria, which can include:
                - input_text: Exact text match
                - input_text_like: Text pattern match
                - result_value: Exact value match
                - result_value_min: Minimum value (inclusive)
                - result_value_max: Maximum value (inclusive)
                - calculation_type: Specific calculation method
                - custom_method_name: Custom calculation method name
                - favorite: True to find only favorites
                - has_tags: True to find only results with tags
                - has_notes: True to find only results with notes
                - tag_id: Specific tag ID to match
                - created_after: datetime for results created after this date
                - created_before: datetime for results created before this date
                - limit: Maximum number of results to return

        Returns:
            List of calculation results matching the criteria
        """
        # Build query parts
        select = """
        SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
        FROM calculations c
        """

        # Tags join clause depends on criteria
        if criteria.get("tag_id") or criteria.get("has_tags"):
            join = "JOIN calculation_tags ct ON c.id = ct.calculation_id"
        else:
            join = "LEFT JOIN calculation_tags ct ON c.id = ct.calculation_id"

        where_clauses = []
        params = []

        # Add criteria to WHERE clause
        if "input_text" in criteria:
            where_clauses.append("c.input_text = ?")
            params.append(criteria["input_text"])

        if "input_text_like" in criteria:
            where_clauses.append("c.input_text LIKE ?")
            params.append(f"%{criteria['input_text_like']}%")

        if "result_value" in criteria:
            where_clauses.append("c.result_value = ?")
            params.append(criteria["result_value"])

        if "result_value_min" in criteria:
            where_clauses.append("c.result_value >= ?")
            params.append(criteria["result_value_min"])

        if "result_value_max" in criteria:
            where_clauses.append("c.result_value <= ?")
            params.append(criteria["result_value_max"])

        if "calculation_type" in criteria:
            calc_type = criteria["calculation_type"]
            if isinstance(calc_type, CalculationType):
                where_clauses.append("c.calculation_type = ?")
                params.append(self._calculation_type_to_str(calc_type))
            else:
                where_clauses.append("c.calculation_type = ?")
                params.append(str(calc_type))

        if "custom_method_name" in criteria:
            where_clauses.append("c.custom_method_name = ?")
            params.append(criteria["custom_method_name"])

        if criteria.get("favorite"):
            where_clauses.append("c.favorite = 1")

        if criteria.get("has_notes"):
            where_clauses.append("c.notes IS NOT NULL AND c.notes != ''")

        if "tag_id" in criteria:
            where_clauses.append("ct.tag_id = ?")
            params.append(criteria["tag_id"])

        if "created_after" in criteria:
            where_clauses.append("c.created_at >= ?")
            params.append(criteria["created_after"])

        if "created_before" in criteria:
            where_clauses.append("c.created_at <= ?")
            params.append(criteria["created_before"])

        # Construct WHERE clause
        where = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Group by and order by
        group_by = "GROUP BY c.id"
        order_by = "ORDER BY c.created_at DESC"

        # Add limit if specified
        limit_clause = ""
        if "limit" in criteria and isinstance(criteria["limit"], int):
            limit_clause = f"LIMIT {criteria['limit']}"

        # Construct full query
        query = f"{select}\n{join}\n{where}\n{group_by}\n{order_by}\n{limit_clause}"

        # Execute query
        rows = self.db.query_all(query, tuple(params))
        return [self._row_to_calculation(row) for row in rows]

    def _row_to_calculation(self, row: Dict[str, Any]) -> CalculationResult:
        """Convert a database row to a CalculationResult object.

        Args:
            row: Database row dictionary

        Returns:
            CalculationResult instance
        """
        # Convert calculation type
        calculation_type = self._str_to_calculation_type(row["calculation_type"])

        # Parse tags (comma-separated list)
        tag_ids = []
        if row["tag_ids"] and row["tag_ids"] != "":
            tag_ids = row["tag_ids"].split(",")

        # Convert created_at
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return CalculationResult(
            id=row["id"],
            input_text=row["input_text"],
            calculation_type=calculation_type,
            custom_method_name=row["custom_method_name"],
            result_value=row["result_value"],
            favorite=bool(row["favorite"]),
            notes=row["notes"],
            tags=tag_ids,
            timestamp=created_at,
        )

    def _calculation_type_to_str(
        self, calculation_type: Union[CalculationType, str]
    ) -> str:
        """Convert a CalculationType enum to a string for storage.

        Args:
            calculation_type: CalculationType enum or string

        Returns:
            String representation
        """
        if isinstance(calculation_type, CalculationType):
            return str(calculation_type.value)
        return calculation_type

    def _str_to_calculation_type(self, type_str: str) -> Union[CalculationType, str]:
        """Convert a string to a CalculationType enum.

        Args:
            type_str: String representation of a calculation type

        Returns:
            CalculationType enum or string if not a valid enum
        """
        try:
            # Try to convert to int and then to enum
            value = int(type_str)
            return CalculationType(value)
        except (ValueError, TypeError):
            # If not a valid enum value, return as-is
            return type_str

    def _get_tags_for_calculation(self, cursor, calculation_id: str) -> List[str]:
        """
        Get all tags associated with a calculation.

        Args:
            cursor: Database cursor to use
            calculation_id: ID of the calculation

        Returns:
            List[str]: List of tag IDs
        """
        query = """
            SELECT tag_id
            FROM calculation_tags
            WHERE calculation_id = ?
        """

        cursor.execute(query, (calculation_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
