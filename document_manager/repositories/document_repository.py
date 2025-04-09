"""
Purpose: Provides document persistence using SQLite storage.

This file is part of the document_manager pillar and serves as a repository component.
It is responsible for storing and retrieving document metadata and content.

Key components:
- DocumentRepository: Repository class for document CRUD operations

Dependencies:
- sqlite3: For database operations
- pathlib: For file path handling
- document_manager.models.document: For Document model
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from loguru import logger

from document_manager.models.document import Document, DocumentType


class DocumentRepository:
    """Repository for document storage and retrieval using SQLite."""

    def __init__(self, db_path: Union[str, Path] = "data/isopgem.db"):
        """Initialize the document repository.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.storage_dir = self.db_path.parent / "documents"

        # Ensure directories exist
        os.makedirs(self.storage_dir, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create documents table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            creation_date TIMESTAMP NOT NULL,
            last_modified_date TIMESTAMP NOT NULL,
            content TEXT,
            extracted_text TEXT,
            category TEXT,
            notes TEXT,
            author TEXT,
            page_count INTEGER,
            word_count INTEGER,
            metadata TEXT,
            tags TEXT,
            is_deleted INTEGER DEFAULT 0
        )
        """
        )

        # Create index for faster searches
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_name ON documents(name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_creation_date ON documents(creation_date)"
        )

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _document_to_row(self, document: Document) -> Dict:
        """Convert Document object to database row.

        Args:
            document: Document to convert

        Returns:
            Dictionary with database column values
        """
        return {
            "id": document.id,
            "name": document.name,
            "file_path": str(document.file_path),
            "file_type": document.file_type.value,
            "size_bytes": document.size_bytes,
            "creation_date": document.creation_date.isoformat(),
            "last_modified_date": document.last_modified_date.isoformat(),
            "content": document.content,
            "extracted_text": document.extracted_text,
            "category": document.category,
            "notes": document.notes,
            "author": document.author,
            "page_count": document.page_count,
            "word_count": document.word_count,
            "metadata": json.dumps(document.metadata) if document.metadata else None,
            "tags": json.dumps(document.tags) if document.tags else "[]",
        }

    def _row_to_document(self, row: sqlite3.Row) -> Document:
        """Convert database row to Document object.

        Args:
            row: Database row

        Returns:
            Document object
        """
        # Parse JSON data
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        tags = json.loads(row["tags"]) if row["tags"] else []

        # Create document object
        return Document(
            id=row["id"],
            name=row["name"],
            file_path=Path(row["file_path"]),
            file_type=DocumentType(row["file_type"]),
            size_bytes=row["size_bytes"],
            creation_date=datetime.fromisoformat(row["creation_date"]),
            last_modified_date=datetime.fromisoformat(row["last_modified_date"]),
            content=row["content"],
            extracted_text=row["extracted_text"],
            category=row["category"],
            notes=row["notes"],
            author=row["author"],
            page_count=row["page_count"],
            word_count=row["word_count"],
            metadata=metadata,
            tags=tags,
        )

    def save(self, document: Document) -> bool:
        """Save a document to the database.

        This will create a new document if it doesn't exist or update an existing one.

        Args:
            document: Document to save

        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if document already exists
            cursor.execute("SELECT id FROM documents WHERE id = ?", (document.id,))
            existing = cursor.fetchone()

            row = self._document_to_row(document)

            if existing:
                # Update existing document
                placeholders = ", ".join([f"{k} = ?" for k in row.keys() if k != "id"])
                values = [v for k, v in row.items() if k != "id"]
                values.append(document.id)

                cursor.execute(
                    f"UPDATE documents SET {placeholders} WHERE id = ?", values
                )
            else:
                # Insert new document
                placeholders = ", ".join(["?"] * len(row))
                columns = ", ".join(row.keys())

                cursor.execute(
                    f"INSERT INTO documents ({columns}) VALUES ({placeholders})",
                    list(row.values()),
                )

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_document(row)

        return None

    def get_all(self) -> List[Document]:
        """Get all documents.

        Returns:
            List of all documents
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE is_deleted = 0")

        documents = [self._row_to_document(row) for row in cursor.fetchall()]
        conn.close()

        return documents

    def delete(self, document_id: str, permanent: bool = False) -> bool:
        """Delete a document.

        Args:
            document_id: Document ID
            permanent: If True, permanently delete the document; otherwise, mark as deleted

        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if permanent:
                cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            else:
                cursor.execute(
                    "UPDATE documents SET is_deleted = 1 WHERE id = ?", (document_id,)
                )

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def search(
        self,
        query: Optional[str] = None,
        doc_type: Optional[DocumentType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Document], int]:
        """Search for documents with filters.

        Args:
            query: Search text (searches in name, extracted_text, and notes)
            doc_type: Filter by document type
            category: Filter by category
            tags: Filter by tags (documents must have ALL specified tags)
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of matching documents, total count)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build the query
        where_clauses = ["is_deleted = 0"]
        params = []

        if query:
            where_clauses.append(
                "(name LIKE ? OR extracted_text LIKE ? OR notes LIKE ?)"
            )
            params.extend([f"%{query}%"] * 3)

        if doc_type:
            where_clauses.append("file_type = ?")
            params.append(doc_type.value)

        if category:
            where_clauses.append("category = ?")
            params.append(category)

        if date_from:
            where_clauses.append("creation_date >= ?")
            params.append(date_from.isoformat())

        if date_to:
            where_clauses.append("creation_date <= ?")
            params.append(date_to.isoformat())

        # Combine all conditions
        where_clause = " AND ".join(where_clauses)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM documents WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["count"]

        # Execute the main query with pagination
        query_sql = f"""
        SELECT * FROM documents
        WHERE {where_clause}
        ORDER BY creation_date DESC
        LIMIT ? OFFSET ?
        """

        cursor.execute(query_sql, params + [limit, offset])

        documents = []
        for row in cursor.fetchall():
            document = self._row_to_document(row)

            # Filter by tags if needed
            if tags:
                if not all(tag in document.tags for tag in tags):
                    continue

            documents.append(document)

        conn.close()

        return documents, total_count

    def get_by_category(self, category: str) -> List[Document]:
        """Get documents by category.

        Args:
            category: Category name

        Returns:
            List of documents in the category
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM documents WHERE category = ? AND is_deleted = 0", (category,)
        )

        documents = [self._row_to_document(row) for row in cursor.fetchall()]
        conn.close()

        return documents

    def get_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Get documents by type.

        Args:
            doc_type: Document type

        Returns:
            List of documents of the specified type
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM documents WHERE file_type = ? AND is_deleted = 0",
            (doc_type.value,),
        )

        documents = [self._row_to_document(row) for row in cursor.fetchall()]
        conn.close()

        return documents

    def get_by_tag(self, tag: str) -> List[Document]:
        """Get documents with a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of documents with the tag
        """
        # We need to search in the JSON tag array
        documents = self.get_all()
        return [doc for doc in documents if tag in doc.tags]

    def get_document_count(self) -> int:
        """Get the total number of documents.

        Returns:
            Total number of documents
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM documents WHERE is_deleted = 0")
        row = cursor.fetchone()
        count = int(row["count"]) if row else 0

        conn.close()
        return count
