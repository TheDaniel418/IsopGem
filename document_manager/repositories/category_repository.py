"""
Purpose: Provides document category persistence using SQLite storage.

This file is part of the document_manager pillar and serves as a repository component.
It is responsible for storing and retrieving document categories.

Key components:
- CategoryRepository: Repository class for document category CRUD operations

Dependencies:
- sqlite3: For database operations
- document_manager.models.document_category: For DocumentCategory model
"""

import json
import sqlite3
from typing import Dict, List, Optional, Union

from loguru import logger

from document_manager.models.document_category import DocumentCategory


class CategoryRepository:
    """Repository for document category storage and retrieval using SQLite."""

    def __init__(self, db_path: str = "data/isopgem.db"):
        """Initialize the category repository.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create categories table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS document_categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            description TEXT,
            parent_id TEXT,
            icon TEXT,
            metadata TEXT,
            FOREIGN KEY (parent_id) REFERENCES document_categories(id)
        )
        """
        )

        # Create index for faster searches
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_document_categories_name ON document_categories(name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_document_categories_parent_id ON document_categories(parent_id)"
        )

        conn.commit()
        conn.close()

        # Create default categories if not exist
        if self.get_count() == 0:
            self._create_default_categories()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _category_to_row(self, category: DocumentCategory) -> Dict:
        """Convert DocumentCategory object to database row.

        Args:
            category: Category to convert

        Returns:
            Dictionary with database column values
        """
        return {
            "id": category.id,
            "name": category.name,
            "color": category.color,
            "description": category.description,
            "parent_id": category.parent_id,
            "icon": category.icon,
            "metadata": json.dumps(category.metadata) if category.metadata else None,
        }

    def _row_to_category(self, row: sqlite3.Row) -> DocumentCategory:
        """Convert database row to DocumentCategory object.

        Args:
            row: Database row

        Returns:
            DocumentCategory object
        """
        # Parse JSON data
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        # Create category object
        return DocumentCategory(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            description=row["description"],
            parent_id=row["parent_id"],
            icon=row["icon"],
            metadata=metadata,
        )

    def _create_default_categories(self) -> None:
        """Create default categories if none exist."""
        default_categories = DocumentCategory.create_default_categories()

        for category in default_categories:
            self.save(category)

        logger.info(f"Created {len(default_categories)} default document categories")

    def save(self, category: DocumentCategory) -> bool:
        """Save a category to the database.

        This will create a new category if it doesn't exist or update an existing one.

        Args:
            category: Category to save

        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if category already exists
            cursor.execute(
                "SELECT id FROM document_categories WHERE id = ?", (category.id,)
            )
            existing = cursor.fetchone()

            row = self._category_to_row(category)

            if existing:
                # Update existing category
                placeholders = ", ".join([f"{k} = ?" for k in row.keys() if k != "id"])
                values = [v for k, v in row.items() if k != "id"]
                values.append(category.id)

                cursor.execute(
                    f"UPDATE document_categories SET {placeholders} WHERE id = ?",
                    values,
                )
            else:
                # Insert new category
                placeholders = ", ".join(["?"] * len(row))
                columns = ", ".join(row.keys())

                cursor.execute(
                    f"INSERT INTO document_categories ({columns}) VALUES ({placeholders})",
                    list(row.values()),
                )

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving category: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_by_id(self, category_id: str) -> Optional[DocumentCategory]:
        """Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM document_categories WHERE id = ?", (category_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_category(row)

        return None

    def get_all(self) -> List[DocumentCategory]:
        """Get all categories.

        Returns:
            List of all categories
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM document_categories ORDER BY name")

        categories = [self._row_to_category(row) for row in cursor.fetchall()]
        conn.close()

        return categories

    def get_root_categories(self) -> List[DocumentCategory]:
        """Get all root categories (categories without a parent).

        Returns:
            List of root categories
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM document_categories WHERE parent_id IS NULL ORDER BY name"
        )

        categories = [self._row_to_category(row) for row in cursor.fetchall()]
        conn.close()

        return categories

    def get_child_categories(self, parent_id: str) -> List[DocumentCategory]:
        """Get child categories of a parent category.

        Args:
            parent_id: Parent category ID

        Returns:
            List of child categories
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM document_categories WHERE parent_id = ? ORDER BY name",
            (parent_id,),
        )

        categories = [self._row_to_category(row) for row in cursor.fetchall()]
        conn.close()

        return categories

    def delete(self, category_id: str) -> bool:
        """Delete a category.

        Note: This will fail if there are documents assigned to this category
        or if there are child categories.

        Args:
            category_id: Category ID

        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check for child categories
            cursor.execute(
                "SELECT COUNT(*) as count FROM document_categories WHERE parent_id = ?",
                (category_id,),
            )
            child_count = cursor.fetchone()["count"]

            if child_count > 0:
                logger.error(
                    f"Cannot delete category {category_id}: has {child_count} child categories"
                )
                return False

            # Delete the category
            cursor.execute(
                "DELETE FROM document_categories WHERE id = ?", (category_id,)
            )

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def search(self, query: str) -> List[DocumentCategory]:
        """Search for categories by name or description.

        Args:
            query: Search query

        Returns:
            List of matching categories
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM document_categories WHERE name LIKE ? OR description LIKE ? ORDER BY name",
            (f"%{query}%", f"%{query}%"),
        )

        categories = [self._row_to_category(row) for row in cursor.fetchall()]
        conn.close()

        return categories

    def get_count(self) -> int:
        """Get the total number of categories.

        Returns:
            Total category count
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM document_categories")
        row = cursor.fetchone()
        count = int(row["count"]) if row else 0

        conn.close()
        return count
