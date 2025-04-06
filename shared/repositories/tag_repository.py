"""
Purpose: Defines the interface and implementation for tag data access

This file is part of the shared repositories layer and provides the interface
and SQLite implementation for tag data persistence. It handles storing and 
retrieving tags from the database.

Key components:
- TagRepository: Abstract base class defining the tag repository interface
- SQLiteTagRepository: SQLite implementation of the tag repository

Dependencies:
- abc: For abstract base class definition
- sqlite3: For database access
- shared.models: For data models
- loguru: For logging

Related files:
- shared/models/tag.py: Model for tag data
- shared/services/tag_service.py: Service using this repository
"""

import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from loguru import logger

from shared.models.tag import Tag


class TagRepository(ABC):
    """Abstract base class for tag repositories."""
    
    @abstractmethod
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """
        Get a tag by its ID.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            The tag or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_tags(self) -> List[Tag]:
        """
        Get all tags.
        
        Returns:
            List of all tags
        """
        pass
    
    @abstractmethod
    def save_tag(self, tag: Tag) -> bool:
        """
        Save a tag (create or update).
        
        Args:
            tag: The tag to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_tags_for_entity(self, entity_type: str, entity_id: str) -> List[Tag]:
        """
        Get all tags for a specific entity.
        
        Args:
            entity_type: Type of entity (e.g., 'calculation', 'document')
            entity_id: The entity's unique identifier
            
        Returns:
            List of tags associated with the entity
        """
        pass


class SQLiteTagRepository(TagRepository):
    """SQLite implementation of the tag repository."""
    
    def __init__(self, db_path: str):
        """
        Initialize the repository with a database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tags table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,
                    description TEXT
                )
                ''')
                
                # Create entity_tags table for mapping entities to tags
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS entity_tags (
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    PRIMARY KEY (entity_type, entity_id, tag_id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
                ''')
                
                conn.commit()
                logger.debug("Tag repository tables initialized")
        except sqlite3.Error as e:
            logger.error(f"Error initializing tag database: {str(e)}")
    
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """
        Get a tag by its ID.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            The tag or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id, name, color, description FROM tags WHERE id = ?",
                    (tag_id,)
                )
                
                row = cursor.fetchone()
                
                if row:
                    return Tag(
                        id=row['id'],
                        name=row['name'],
                        color=row['color'],
                        description=row['description'] or ""
                    )
                
                return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving tag {tag_id}: {str(e)}")
            return None
    
    def get_all_tags(self) -> List[Tag]:
        """
        Get all tags.
        
        Returns:
            List of all tags
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT id, name, color, description FROM tags ORDER BY name")
                
                return [
                    Tag(
                        id=row['id'],
                        name=row['name'],
                        color=row['color'],
                        description=row['description'] or ""
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all tags: {str(e)}")
            return []
    
    def save_tag(self, tag: Tag) -> bool:
        """
        Save a tag (create or update).
        
        Args:
            tag: The tag to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if the tag exists
                cursor.execute("SELECT id FROM tags WHERE id = ?", (tag.id,))
                exists = cursor.fetchone() is not None
                
                if exists:
                    # Update existing tag
                    cursor.execute(
                        "UPDATE tags SET name = ?, color = ?, description = ? WHERE id = ?",
                        (tag.name, tag.color, tag.description, tag.id)
                    )
                else:
                    # Insert new tag
                    cursor.execute(
                        "INSERT INTO tags (id, name, color, description) VALUES (?, ?, ?, ?)",
                        (tag.id, tag.name, tag.color, tag.description)
                    )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error saving tag {tag.id}: {str(e)}")
            return False
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete from entity_tags first to maintain referential integrity
                cursor.execute("DELETE FROM entity_tags WHERE tag_id = ?", (tag_id,))
                
                # Then delete the tag
                cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting tag {tag_id}: {str(e)}")
            return False
    
    def get_tags_for_entity(self, entity_type: str, entity_id: str) -> List[Tag]:
        """
        Get all tags for a specific entity.
        
        Args:
            entity_type: Type of entity (e.g., 'calculation', 'document')
            entity_id: The entity's unique identifier
            
        Returns:
            List of tags associated with the entity
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.name, t.color, t.description 
                    FROM tags t 
                    JOIN entity_tags et ON t.id = et.tag_id 
                    WHERE et.entity_type = ? AND et.entity_id = ?
                    ORDER BY t.name
                """, (entity_type, entity_id))
                
                return [
                    Tag(
                        id=row['id'],
                        name=row['name'],
                        color=row['color'],
                        description=row['description'] or ""
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving tags for {entity_type} {entity_id}: {str(e)}")
            return []
    
    def add_tag_to_entity(self, entity_type: str, entity_id: str, tag_id: str) -> bool:
        """
        Associate a tag with an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'calculation', 'document')
            entity_id: The entity's unique identifier
            tag_id: The tag's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT OR IGNORE INTO entity_tags (entity_type, entity_id, tag_id) VALUES (?, ?, ?)",
                    (entity_type, entity_id, tag_id)
                )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding tag {tag_id} to {entity_type} {entity_id}: {str(e)}")
            return False
    
    def remove_tag_from_entity(self, entity_type: str, entity_id: str, tag_id: str) -> bool:
        """
        Remove a tag association from an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'calculation', 'document')
            entity_id: The entity's unique identifier
            tag_id: The tag's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM entity_tags WHERE entity_type = ? AND entity_id = ? AND tag_id = ?",
                    (entity_type, entity_id, tag_id)
                )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error removing tag {tag_id} from {entity_type} {entity_id}: {str(e)}")
            return False
    
    def update_entity_tags(self, entity_type: str, entity_id: str, tag_ids: List[str]) -> bool:
        """
        Update all tags for an entity (replace existing associations).
        
        Args:
            entity_type: Type of entity (e.g., 'calculation', 'document')
            entity_id: The entity's unique identifier
            tag_ids: List of tag IDs to associate with the entity
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove all existing tag associations
                cursor.execute(
                    "DELETE FROM entity_tags WHERE entity_type = ? AND entity_id = ?",
                    (entity_type, entity_id)
                )
                
                # Add new associations
                for tag_id in tag_ids:
                    cursor.execute(
                        "INSERT INTO entity_tags (entity_type, entity_id, tag_id) VALUES (?, ?, ?)",
                        (entity_type, entity_id, tag_id)
                    )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error updating tags for {entity_type} {entity_id}: {str(e)}")
            return False