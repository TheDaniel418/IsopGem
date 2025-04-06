"""
Purpose: Defines the Document data model for representing documents in the system.

This file is part of the document_manager pillar and serves as a model component.
It is responsible for representing documents and their metadata within the application.

Key components:
- Document: Core model class representing a document with metadata and content
- DocumentType: Enum representing supported document types

Dependencies:
- datetime: For handling timestamps
- enum: For DocumentType enumeration
- pathlib: For handling file paths
- uuid: For generating unique IDs
"""

import uuid
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Optional, Set, TypeVar, Union

from pydantic import BaseModel, Field


class ExtractionStatus(Enum):
    """Status of text extraction for a document."""

    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()


# Define a type variable for the DocumentType return annotation
Self = TypeVar("Self", bound="DocumentType")


class DocumentType(str, Enum):
    """Document type enum."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    EXCEL = "xlsx"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "md"
    IMAGE = "img"
    MEMORY = "memory"
    OTHER = "other"
    QTDOC = "qtdoc"  # QGem rich text document

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentType":
        """Get DocumentType from file extension.

        Args:
            extension: File extension (without dot)

        Returns:
            DocumentType corresponding to the extension
        """
        extension = extension.lower()
        for doc_type in cls:
            if doc_type.value == extension:
                return doc_type

        # Handle special cases
        if extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
            return cls.IMAGE
        elif extension in ["xls", "xlsx"]:
            return cls.EXCEL
        elif extension in ["doc", "docx"]:
            return cls.DOCX

        # Default to OTHER if no match
        return cls.OTHER


class DocumentExtractionStatus(str, Enum):
    """Document text extraction status."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(BaseModel):
    """Represents a document in the document manager system."""

    # Core metadata
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    file_path: Path
    file_type: DocumentType
    size_bytes: int
    creation_date: datetime = Field(default_factory=datetime.now)
    last_modified_date: datetime = Field(default_factory=datetime.now)

    # Content and extracted data
    content: Optional[str] = None
    extracted_text: Optional[str] = None

    # Organization metadata
    tags: Set[str] = Field(default_factory=set)
    category: Optional[str] = None
    notes: Optional[str] = None

    # Additional metadata
    author: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict
    )

    # Integrity status
    document_extraction_status: ExtractionStatus = ExtractionStatus.NOT_STARTED
    checksum: Optional[str] = None
    integrity_status: str = "UNKNOWN"

    class Config:
        """Pydantic config for the Document model."""

        arbitrary_types_allowed = True

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Document":
        """Create a Document instance from a file.

        Args:
            file_path: Path to the file

        Returns:
            Document instance with basic metadata

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Get file extension and validate
        extension = path.suffix.lower()
        doc_type = DocumentType.from_extension(extension[1:] if extension else "")

        # Get file stats
        stat = path.stat()

        return cls(
            name=path.name,
            file_path=path,
            file_type=doc_type,
            size_bytes=stat.st_size,
            creation_date=datetime.fromtimestamp(stat.st_ctime),
            last_modified_date=datetime.fromtimestamp(stat.st_mtime),
        )

    def get_file_size_display(self) -> str:
        """Get human-readable file size.

        Returns:
            Human-readable file size (e.g., '2.5 MB')
        """
        size_float = float(self.size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_float < 1024 or unit == "TB":
                break
            size_float /= 1024
        return f"{size_float:.2f} {unit}"

    def is_text_extracted(self) -> bool:
        """Check if text has been extracted from the document.

        Returns:
            True if text has been extracted, False otherwise
        """
        return self.extracted_text is not None and len(self.extracted_text) > 0

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document.

        Args:
            tag: Tag to add
        """
        # Initialize tags as empty set if it doesn't exist
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = set()

        # Add the tag to the set
        self.tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document.

        Args:
            tag: Tag to remove
        """
        # Do nothing if tags doesn't exist
        if not hasattr(self, "tags") or self.tags is None:
            return

        # Remove the tag if it exists in the set
        self.tags.discard(tag)  # discard doesn't raise an error if tag doesn't exist

    @property
    def extraction_status(self) -> DocumentExtractionStatus:
        """Get the document extraction status."""
        if not self.metadata:
            return DocumentExtractionStatus.NOT_STARTED

        status = self.metadata.get(
            "extraction_status", DocumentExtractionStatus.NOT_STARTED.value
        )
        return DocumentExtractionStatus(status)

    @extraction_status.setter
    def extraction_status(self, status: DocumentExtractionStatus):
        """Set the document extraction status."""
        if not self.metadata:
            self.metadata = {}
        self.metadata["extraction_status"] = status.value

    @property
    def is_memory_document(self) -> bool:
        """Check if this is a memory document (no file)."""
        return self.file_type == DocumentType.MEMORY
