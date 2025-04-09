"""
Purpose: Defines the document format model for RTF editor.

This file is part of the shared UI widgets and serves as a model component.
It provides a standardized format for storing and retrieving rich text documents.

Key components:
- DocumentFormat: Model for document serialization and storage
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    """Metadata for an image in a rich text document."""

    position: int
    name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None  # e.g., "png", "jpg"
    data_uri: Optional[str] = None  # Base64 encoded image data


class TableMetadata(BaseModel):
    """Metadata for a table in a rich text document."""

    position: int
    rows: int
    columns: int
    border: int = 1
    cell_padding: int = 5
    cell_spacing: int = 0


class AnnotationMetadata(BaseModel):
    """Metadata for an annotation in a rich text document."""

    id: str
    start_position: int
    end_position: int
    content: Optional[str] = None
    type: str = "highlight"  # highlight, underline, note, strikethrough
    color: str = "#ffff00"  # Default yellow
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)

    # Gematria-specific information
    gematria_value: Optional[int] = None
    gematria_method: Optional[str] = None


class DocumentFormat(BaseModel):
    """Format for rich text document storage and serialization."""

    # Document identity
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)

    # Content
    html_content: str
    plain_text: str

    # Metadata
    word_count: int = 0
    character_count: int = 0

    # Rich content
    images: List[ImageMetadata] = Field(default_factory=list)
    tables: List[TableMetadata] = Field(default_factory=list)
    annotations: List[AnnotationMetadata] = Field(default_factory=list)

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def update_counts(self):
        """Update word and character counts based on plain text content."""
        self.word_count = len(self.plain_text.split())
        self.character_count = len(self.plain_text)

    def add_annotation(self, annotation: AnnotationMetadata):
        """Add an annotation to the document.

        Args:
            annotation: The annotation to add
        """
        # Check if an annotation with this ID already exists
        for i, existing in enumerate(self.annotations):
            if existing.id == annotation.id:
                # Update existing annotation
                self.annotations[i] = annotation
                return

        # Add new annotation
        self.annotations.append(annotation)

    def remove_annotation(self, annotation_id: str) -> bool:
        """Remove an annotation from the document.

        Args:
            annotation_id: The ID of the annotation to remove

        Returns:
            bool: True if removed, False if not found
        """
        initial_count = len(self.annotations)
        self.annotations = [a for a in self.annotations if a.id != annotation_id]
        return len(self.annotations) < initial_count
