"""
Repository for managing number notes in the database.

This module provides database operations for storing and retrieving notes
about specific numbers in the Number Dictionary.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from loguru import logger

from gematria.models.number_note import NumberNote


class NumberNoteRepository:
    """Repository for managing number notes in the database."""
    
    def __init__(self, db_path: str):
        """Initialize the repository with database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self) -> None:
        """Create the number_notes table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS number_notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number INTEGER NOT NULL,
                        title TEXT NOT NULL DEFAULT '',
                        content TEXT NOT NULL DEFAULT '',
                        attachments TEXT DEFAULT '[]',
                        linked_numbers TEXT DEFAULT '[]',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(number)
                    )
                """)
                
                # Create index on number for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_number_notes_number 
                    ON number_notes(number)
                """)
                
                conn.commit()
                logger.debug("Number notes table created/verified")
                
        except Exception as e:
            logger.error(f"Error creating number_notes table: {e}")
            raise
    
    def save_note(self, note: NumberNote) -> NumberNote:
        """Save a number note to the database.
        
        Args:
            note: The note to save
            
        Returns:
            The saved note with updated ID and timestamps
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update timestamp
                note.updated_at = datetime.now()
                
                if note.id is None:
                    # Insert new note
                    cursor.execute("""
                        INSERT OR REPLACE INTO number_notes 
                        (number, title, content, attachments, linked_numbers, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        note.number,
                        note.title,
                        note.content,
                        json.dumps(note.attachments),
                        json.dumps(note.linked_numbers),
                        note.created_at.isoformat(),
                        note.updated_at.isoformat()
                    ))
                    note.id = cursor.lastrowid
                else:
                    # Update existing note
                    cursor.execute("""
                        UPDATE number_notes 
                        SET title = ?, content = ?, attachments = ?, 
                            linked_numbers = ?, updated_at = ?
                        WHERE id = ?
                    """, (
                        note.title,
                        note.content,
                        json.dumps(note.attachments),
                        json.dumps(note.linked_numbers),
                        note.updated_at.isoformat(),
                        note.id
                    ))
                
                conn.commit()
                logger.debug(f"Saved note for number {note.number}")
                return note
                
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            raise
    
    def get_note_by_number(self, number: int) -> Optional[NumberNote]:
        """Get a note by number.
        
        Args:
            number: The number to get the note for
            
        Returns:
            The note if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, number, title, content, attachments, linked_numbers, 
                           created_at, updated_at
                    FROM number_notes 
                    WHERE number = ?
                """, (number,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_note(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting note for number {number}: {e}")
            return None
    
    def get_note_by_id(self, note_id: int) -> Optional[NumberNote]:
        """Get a note by ID.
        
        Args:
            note_id: The note ID
            
        Returns:
            The note if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, number, title, content, attachments, linked_numbers, 
                           created_at, updated_at
                    FROM number_notes 
                    WHERE id = ?
                """, (note_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_note(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting note by ID {note_id}: {e}")
            return None
    
    def get_all_notes(self) -> List[NumberNote]:
        """Get all notes.
        
        Returns:
            List of all notes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, number, title, content, attachments, linked_numbers, 
                           created_at, updated_at
                    FROM number_notes 
                    ORDER BY number
                """)
                
                rows = cursor.fetchall()
                return [self._row_to_note(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting all notes: {e}")
            return []
    
    def delete_note(self, number: int) -> bool:
        """Delete a note by number.
        
        Args:
            number: The number whose note to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM number_notes WHERE number = ?", (number,))
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.debug(f"Deleted note for number {number}")
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting note for number {number}: {e}")
            return False
    
    def search_notes(self, query: str) -> List[NumberNote]:
        """Search notes by title or content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching notes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, number, title, content, attachments, linked_numbers, 
                           created_at, updated_at
                    FROM number_notes 
                    WHERE title LIKE ? OR content LIKE ?
                    ORDER BY number
                """, (f"%{query}%", f"%{query}%"))
                
                rows = cursor.fetchall()
                return [self._row_to_note(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            return []
    
    def _row_to_note(self, row) -> NumberNote:
        """Convert a database row to a NumberNote object.
        
        Args:
            row: Database row tuple
            
        Returns:
            NumberNote object
        """
        return NumberNote(
            id=row[0],
            number=row[1],
            title=row[2],
            content=row[3],
            attachments=json.loads(row[4]) if row[4] else [],
            linked_numbers=json.loads(row[5]) if row[5] else [],
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7])
        ) 