"""
Concordance Repository for Document Manager.

This module handles the persistence and retrieval of KWIC concordance data
using SQLite database operations.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from document_manager.models.kwic_concordance import (
    ConcordanceEntry,
    ConcordanceFilter,
    ConcordanceSettings,
    ConcordanceTable,
)
from shared.repositories.database import Database


class ConcordanceRepository:
    """Repository for managing KWIC concordance data persistence."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the concordance repository.
        
        Args:
            db_path: Optional path to the SQLite database file (for testing)
        """
        if db_path:
            # For testing with custom database path
            self._db_path = db_path
            self._custom_db = True
        else:
            # Use the shared database instance
            self.db = Database()
            self._custom_db = False
        
        self._create_tables()
    
    def get_connection(self):
        """Get a database connection."""
        if self._custom_db:
            # For testing - create direct connection
            conn = sqlite3.connect(self._db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        else:
            # Use shared database connection
            return self.db.connection()
    
    def _create_tables(self):
        """Create the necessary tables for concordance data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create concordance_tables table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concordance_tables (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    keywords TEXT NOT NULL,  -- JSON array
                    document_ids TEXT NOT NULL,  -- JSON array
                    settings TEXT NOT NULL,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT,
                    tags TEXT,  -- JSON array
                    UNIQUE(name)
                )
            """)
            
            # Create concordance_entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concordance_entries (
                    id TEXT PRIMARY KEY,
                    concordance_table_id TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    left_context TEXT NOT NULL,
                    right_context TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    line_number INTEGER,
                    sentence_number INTEGER,
                    paragraph_number INTEGER,
                    document_id TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (concordance_table_id) REFERENCES concordance_tables (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_concordance_entries_keyword 
                ON concordance_entries (keyword)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_concordance_entries_document 
                ON concordance_entries (document_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_concordance_entries_position 
                ON concordance_entries (position)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_concordance_entries_table 
                ON concordance_entries (concordance_table_id)
            """)
            
            conn.commit()
    
    def save_concordance_table(self, table: ConcordanceTable) -> str:
        """Save a concordance table to the database.
        
        Args:
            table: The concordance table to save
            
        Returns:
            The ID of the saved table
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update the updated_at timestamp
            table.updated_at = datetime.now()
            
            # Insert or update the concordance table
            cursor.execute("""
                INSERT OR REPLACE INTO concordance_tables 
                (id, name, description, keywords, document_ids, settings, 
                 created_at, updated_at, created_by, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                table.id,
                table.name,
                table.description,
                json.dumps(table.keywords),
                json.dumps(table.document_ids),
                table.settings.json(),
                table.created_at.isoformat(),
                table.updated_at.isoformat(),
                table.created_by,
                json.dumps(table.tags)
            ))
            
            # Delete existing entries for this table
            cursor.execute("""
                DELETE FROM concordance_entries WHERE concordance_table_id = ?
            """, (table.id,))
            
            # Insert all entries
            for entry in table.entries:
                cursor.execute("""
                    INSERT INTO concordance_entries 
                    (id, concordance_table_id, keyword, left_context, right_context,
                     position, line_number, sentence_number, paragraph_number,
                     document_id, document_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    table.id,
                    entry.keyword,
                    entry.left_context,
                    entry.right_context,
                    entry.position,
                    entry.line_number,
                    entry.sentence_number,
                    entry.paragraph_number,
                    entry.document_id,
                    entry.document_name,
                    entry.created_at.isoformat()
                ))
            
            conn.commit()
            return table.id
    
    def get_concordance_table(self, table_id: str) -> Optional[ConcordanceTable]:
        """Retrieve a concordance table by ID.
        
        Args:
            table_id: The ID of the table to retrieve
            
        Returns:
            The concordance table if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the table metadata
            cursor.execute("""
                SELECT id, name, description, keywords, document_ids, settings,
                       created_at, updated_at, created_by, tags
                FROM concordance_tables WHERE id = ?
            """, (table_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get all entries for this table
            cursor.execute("""
                SELECT id, keyword, left_context, right_context, position,
                       line_number, sentence_number, paragraph_number,
                       document_id, document_name, created_at
                FROM concordance_entries WHERE concordance_table_id = ?
                ORDER BY keyword, position
            """, (table_id,))
            
            entry_rows = cursor.fetchall()
            
            # Build the concordance table object
            entries = []
            for entry_row in entry_rows:
                entry = ConcordanceEntry(
                    id=entry_row[0],
                    keyword=entry_row[1],
                    left_context=entry_row[2],
                    right_context=entry_row[3],
                    position=entry_row[4],
                    line_number=entry_row[5],
                    sentence_number=entry_row[6],
                    paragraph_number=entry_row[7],
                    document_id=entry_row[8],
                    document_name=entry_row[9],
                    created_at=datetime.fromisoformat(entry_row[10])
                )
                entries.append(entry)
            
            # Parse settings JSON
            settings_data = json.loads(row[5])
            settings = ConcordanceSettings(**settings_data)
            
            table = ConcordanceTable(
                id=row[0],
                name=row[1],
                description=row[2],
                keywords=json.loads(row[3]),
                document_ids=json.loads(row[4]),
                settings=settings,
                created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7]),
                created_by=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                entries=entries
            )
            
            return table
    
    def get_concordance_table_by_name(self, name: str) -> Optional[ConcordanceTable]:
        """Retrieve a concordance table by name.
        
        Args:
            name: The name of the table to retrieve
            
        Returns:
            The concordance table if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM concordance_tables WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            if row:
                return self.get_concordance_table(row[0])
            
            return None
    
    def list_concordance_tables(self) -> List[Dict]:
        """List all concordance tables with basic metadata.
        
        Returns:
            List of dictionaries containing table metadata
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ct.id, ct.name, ct.description, ct.created_at, ct.updated_at,
                       ct.created_by, ct.tags, COUNT(ce.id) as entry_count
                FROM concordance_tables ct
                LEFT JOIN concordance_entries ce ON ct.id = ce.concordance_table_id
                GROUP BY ct.id, ct.name, ct.description, ct.created_at, 
                         ct.updated_at, ct.created_by, ct.tags
                ORDER BY ct.updated_at DESC
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_info = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': datetime.fromisoformat(row[3]),
                    'updated_at': datetime.fromisoformat(row[4]),
                    'created_by': row[5],
                    'tags': json.loads(row[6]) if row[6] else [],
                    'entry_count': row[7]
                }
                tables.append(table_info)
            
            return tables
    
    def delete_concordance_table(self, table_id: str) -> bool:
        """Delete a concordance table and all its entries.
        
        Args:
            table_id: The ID of the table to delete
            
        Returns:
            True if the table was deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) FROM concordance_tables WHERE id = ?
            """, (table_id,))
            
            if cursor.fetchone()[0] == 0:
                return False
            
            # Delete the table (entries will be deleted by CASCADE)
            cursor.execute("""
                DELETE FROM concordance_tables WHERE id = ?
            """, (table_id,))
            
            conn.commit()
            return True
    
    def search_concordance_entries(
        self, 
        table_id: Optional[str] = None,
        filter_criteria: Optional[ConcordanceFilter] = None
    ) -> List[ConcordanceEntry]:
        """Search for concordance entries with optional filtering.
        
        Args:
            table_id: Optional table ID to limit search to specific table
            filter_criteria: Optional filter criteria
            
        Returns:
            List of matching concordance entries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the query
            query = """
                SELECT ce.id, ce.keyword, ce.left_context, ce.right_context,
                       ce.position, ce.line_number, ce.sentence_number,
                       ce.paragraph_number, ce.document_id, ce.document_name,
                       ce.created_at
                FROM concordance_entries ce
            """
            
            conditions = []
            params = []
            
            if table_id:
                conditions.append("ce.concordance_table_id = ?")
                params.append(table_id)
            
            if filter_criteria:
                if filter_criteria.keywords:
                    keyword_conditions = " OR ".join(["ce.keyword LIKE ?" for _ in filter_criteria.keywords])
                    conditions.append(f"({keyword_conditions})")
                    params.extend([f"%{kw}%" for kw in filter_criteria.keywords])
                
                if filter_criteria.document_ids:
                    doc_conditions = " OR ".join(["ce.document_id = ?" for _ in filter_criteria.document_ids])
                    conditions.append(f"({doc_conditions})")
                    params.extend(filter_criteria.document_ids)
                
                if filter_criteria.document_names:
                    name_conditions = " OR ".join(["ce.document_name LIKE ?" for _ in filter_criteria.document_names])
                    conditions.append(f"({name_conditions})")
                    params.extend([f"%{name}%" for name in filter_criteria.document_names])
                
                if filter_criteria.left_context_contains:
                    conditions.append("ce.left_context LIKE ?")
                    params.append(f"%{filter_criteria.left_context_contains}%")
                
                if filter_criteria.right_context_contains:
                    conditions.append("ce.right_context LIKE ?")
                    params.append(f"%{filter_criteria.right_context_contains}%")
                
                if filter_criteria.min_position is not None:
                    conditions.append("ce.position >= ?")
                    params.append(filter_criteria.min_position)
                
                if filter_criteria.max_position is not None:
                    conditions.append("ce.position <= ?")
                    params.append(filter_criteria.max_position)
                
                if filter_criteria.date_from:
                    conditions.append("ce.created_at >= ?")
                    params.append(filter_criteria.date_from.isoformat())
                
                if filter_criteria.date_to:
                    conditions.append("ce.created_at <= ?")
                    params.append(filter_criteria.date_to.isoformat())
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY ce.keyword, ce.position"
            
            cursor.execute(query, params)
            
            entries = []
            for row in cursor.fetchall():
                entry = ConcordanceEntry(
                    id=row[0],
                    keyword=row[1],
                    left_context=row[2],
                    right_context=row[3],
                    position=row[4],
                    line_number=row[5],
                    sentence_number=row[6],
                    paragraph_number=row[7],
                    document_id=row[8],
                    document_name=row[9],
                    created_at=datetime.fromisoformat(row[10])
                )
                entries.append(entry)
            
            return entries
    
    def get_concordance_statistics(self) -> Dict[str, int]:
        """Get overall statistics about concordance data.
        
        Returns:
            Dictionary containing various statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM concordance_tables")
            table_count = cursor.fetchone()[0]
            
            # Get total entry count
            cursor.execute("SELECT COUNT(*) FROM concordance_entries")
            entry_count = cursor.fetchone()[0]
            
            # Get unique keyword count
            cursor.execute("SELECT COUNT(DISTINCT keyword) FROM concordance_entries")
            keyword_count = cursor.fetchone()[0]
            
            # Get unique document count
            cursor.execute("SELECT COUNT(DISTINCT document_id) FROM concordance_entries")
            document_count = cursor.fetchone()[0]
            
            return {
                'total_tables': table_count,
                'total_entries': entry_count,
                'unique_keywords': keyword_count,
                'unique_documents': document_count
            } 