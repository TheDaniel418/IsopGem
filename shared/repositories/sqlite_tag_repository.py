"""
Purpose: Provides persistent storage and retrieval for tag data using SQLite

This file is part of the shared repositories and serves as a repository component.
It is responsible for storing, retrieving, updating, and deleting tag data
in an SQLite database, ensuring consistent categorization across application sessions.

Key components:
- SQLiteTagRepository: Repository class for managing tag data persistence
  with methods for CRUD operations on tags and default tag creation

Dependencies:
- sqlite3: For SQLite database operations
- pathlib: For file path handling
- loguru: For logging
- gematria.models.tag: For the Tag data model
- shared.repositories.database: For database connection management

Related files:
- gematria/models/tag.py: Data model for tags
- gematria/services/calculation_database_service.py: Uses this repository
- shared/repositories/sqlite_calculation_repository.py: Companion repository for calculation data
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from loguru import logger

# Import Tag in a way that avoids circular imports
if TYPE_CHECKING:
    from gematria.models.tag import Tag
from shared.repositories.database import Database


class SQLiteTagRepository:
    """Repository for storing and retrieving tags using SQLite."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the tag repository.

        Args:
            data_dir: Directory where database will be stored
        """
        self.db = Database(data_dir)
        logger.debug("SQLiteTagRepository initialized")

    def get_all_tags(self) -> List["Tag"]:
        """Get all saved tags.

        Returns:
            List of tags
        """
        query = "SELECT * FROM tags ORDER BY name"
        rows = self.db.query_all(query)

        tags = []
        for row in rows:
            tags.append(self._row_to_tag(row))

        logger.debug(f"Retrieved {len(tags)} tags")
        return tags

    def get_tag(self, tag_id: str) -> Optional["Tag"]:
        """Get a tag by ID.

        Args:
            tag_id: The ID of the tag to retrieve

        Returns:
            Tag instance if found, None otherwise
        """
        query = "SELECT * FROM tags WHERE id = ?"
        row = self.db.query_one(query, (tag_id,))

        if row:
            return self._row_to_tag(row)

        logger.debug(f"Tag with ID {tag_id} not found")
        return None

    def create_tag(self, tag: "Tag") -> bool:
        """Create a new tag.

        Args:
            tag: The tag to create

        Returns:
            True if successful, False otherwise
        """
        # Generate ID if not provided
        if not tag.id:
            tag.id = str(uuid.uuid4())

        # Set created_at if not provided
        if not tag.created_at:
            tag.created_at = datetime.now()

        query = """
        INSERT INTO tags (id, name, color, description, created_at)
        VALUES (?, ?, ?, ?, ?)
        """

        try:
            self.db.execute(
                query, (tag.id, tag.name, tag.color, tag.description, tag.created_at)
            )
            logger.debug(f"Created tag: {tag.name} (ID: {tag.id})")
            return True
        except Exception as e:
            logger.error(f"Failed to create tag: {e}")
            return False

    def update_tag(self, tag: "Tag") -> bool:
        """Update an existing tag.

        Args:
            tag: The tag to update

        Returns:
            True if successful, False otherwise
        """
        query = """
        UPDATE tags
        SET name = ?, color = ?, description = ?
        WHERE id = ?
        """

        try:
            cursor = self.db.execute(
                query, (tag.name, tag.color, tag.description, tag.id)
            )

            if cursor.rowcount > 0:
                logger.debug(f"Updated tag: {tag.name} (ID: {tag.id})")
                return True
            else:
                logger.debug(f"Tag not found for update: {tag.id}")
                return False
        except Exception as e:
            logger.error(f"Failed to update tag: {e}")
            return False

    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag.

        Args:
            tag_id: The ID of the tag to delete

        Returns:
            True if successful, False otherwise
        """
        # In SQLite, with foreign key constraints and ON DELETE CASCADE,
        # this will automatically remove all tag associations in the calculation_tags table
        query = "DELETE FROM tags WHERE id = ?"

        try:
            cursor = self.db.execute(query, (tag_id,))

            if cursor.rowcount > 0:
                logger.debug(f"Deleted tag with ID: {tag_id}")
                return True
            else:
                logger.debug(f"Tag not found for deletion: {tag_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete tag: {e}")
            return False

    def create_default_tags(self) -> List["Tag"]:
        """Create default tags if none exist.

        Returns:
            List of created default tags
        """
        # Import Tag here to avoid circular imports
        from gematria.models.tag import Tag

        default_tags = [
            Tag(
                name="Important",
                color="#e74c3c",
                description="Mark calculations that are particularly significant",
            ),
            Tag(
                name="Research",
                color="#3498db",
                description="For calculations related to research projects",
            ),
            Tag(
                name="Personal",
                color="#2ecc71",
                description="For personal calculations and explorations",
            ),
            Tag(
                name="Biblical",
                color="#f39c12",
                description="For calculations related to Biblical texts",
            ),
            Tag(
                name="Reference",
                color="#9b59b6",
                description="For reference values to compare with other calculations",
            ),
        ]

        created_tags = []
        for tag in default_tags:
            if self.create_tag(tag):
                created_tags.append(tag)

        logger.debug(f"Created {len(created_tags)} default tags")
        return created_tags

    def _row_to_tag(self, row: Dict[str, Any]) -> "Tag":
        """Convert a database row to a Tag instance.

        Args:
            row: Database row as a dictionary

        Returns:
            Tag instance
        """
        # Import Tag here to avoid circular imports
        from gematria.models.tag import Tag

        # Ensure created_at is a valid datetime, defaulting to now if not available
        created_at_value = row.get("created_at")
        if isinstance(created_at_value, datetime):
            created_at = created_at_value
        elif isinstance(created_at_value, str):
            created_at = datetime.fromisoformat(created_at_value)
        else:
            created_at = datetime.now()  # Default to current time if missing

        return Tag(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            description=row["description"],
            created_at=created_at,
        )
