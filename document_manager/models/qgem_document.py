"""
Purpose: Defines the QGem document model for rich text document storage.

This file is part of the document_manager pillar and serves as a model component.
It extends the base Document model to support QTextDocument serialization.

Key components:
- QGemDocument: Document model with QTextDocument support
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field

from document_manager.models.document import Document, DocumentType
from shared.ui.widgets.rtf_editor.models.document_format import DocumentFormat


class QGemDocumentType(str, Enum):
    """Specific document types for QGem documents."""

    RICHTEXT = "richtext"
    NOTE = "note"
    ARTICLE = "article"
    TRANSLATION = "translation"
    ANALYSIS = "analysis"


class QGemDocument(Document):
    """Document model with QTextDocument support."""

    # Add QGem-specific fields
    html_content: Optional[str] = None

    # Track rich content features
    has_tables: bool = False
    has_images: bool = False
    has_annotations: bool = False

    # QGem document specific type
    qgem_type: QGemDocumentType = QGemDocumentType.RICHTEXT

    # Metadata field for storing document format related info
    format_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_document_format(cls, doc_format: DocumentFormat) -> "QGemDocument":
        """Create a QGemDocument from a DocumentFormat.

        Args:
            doc_format: The DocumentFormat instance

        Returns:
            A new QGemDocument instance
        """
        # Create the document with all required parameters
        document = cls(
            id=doc_format.id,
            name=doc_format.name,
            content=doc_format.plain_text,
            html_content=doc_format.html_content,
            word_count=doc_format.word_count
            if hasattr(doc_format, "word_count")
            else 0,
            creation_date=doc_format.created_at,
            last_modified_date=doc_format.modified_at,
            has_tables=len(doc_format.tables) > 0
            if hasattr(doc_format, "tables") and doc_format.tables
            else False,
            has_images=len(doc_format.images) > 0
            if hasattr(doc_format, "images") and doc_format.images
            else False,
            has_annotations=len(doc_format.annotations) > 0
            if hasattr(doc_format, "annotations") and doc_format.annotations
            else False,
            file_type=DocumentType.QTDOC,
            file_path=Path("memory"),  # Use memory file path for in-memory documents
            size_bytes=len(doc_format.html_content.encode("utf-8"))
            if doc_format.html_content
            else 0,  # Use size of HTML content
            author=doc_format.metadata.get("author", "")
            if hasattr(doc_format, "metadata") and doc_format.metadata
            else "",
        )

        # Store additional metadata if available
        document.metadata = {}
        if hasattr(doc_format, "metadata") and doc_format.metadata:
            # Copy metadata but handle annotation_types separately
            metadata_copy = doc_format.metadata.copy()
            if "annotation_types" in metadata_copy:
                del metadata_copy["annotation_types"]
            document.metadata.update(metadata_copy)

        # Update the metadata with information about annotations
        if hasattr(doc_format, "annotations") and doc_format.annotations:
            document.metadata["annotation_count"] = len(doc_format.annotations)
            # Store the annotation types separately to avoid type conflicts
            annotation_types = []
            for anno in doc_format.annotations:
                if hasattr(anno, "type"):
                    annotation_types.append(anno.type)
            document.format_metadata = {"annotation_types": annotation_types}
        else:
            document.metadata["annotation_count"] = 0
            document.format_metadata = {"annotation_types": []}

        # Track image and table info in metadata
        if hasattr(doc_format, "images") and doc_format.images:
            document.metadata["image_count"] = len(doc_format.images)
        else:
            document.metadata["image_count"] = 0

        if hasattr(doc_format, "tables") and doc_format.tables:
            document.metadata["table_count"] = len(doc_format.tables)
        else:
            document.metadata["table_count"] = 0

        return document

    def to_document_format(self) -> DocumentFormat:
        """Convert to DocumentFormat.

        Returns:
            DocumentFormat instance
        """
        # Extract metadata for annotations, images, and tables if available
        metadata = {}
        if self.metadata:
            metadata = self.metadata.copy()

        # Create document format
        doc_format = DocumentFormat(
            id=self.id,
            name=self.name,
            html_content=self.html_content if self.html_content else "",
            plain_text=self.content if self.content else "",
            created_at=self.creation_date,
            modified_at=self.last_modified_date,
            metadata=metadata,
        )

        # Add annotation types from format_metadata if available
        if (
            hasattr(self, "format_metadata")
            and self.format_metadata
            and "annotation_types" in self.format_metadata
        ):
            doc_format.metadata["annotation_types"] = self.format_metadata[
                "annotation_types"
            ]

        # Add annotations if available
        if (
            hasattr(self, "annotations")
            and self.annotations
            and isinstance(self.annotations, list)
        ):
            doc_format.annotations = self.annotations

        # Add images if available
        if hasattr(self, "images") and self.images and isinstance(self.images, list):
            doc_format.images = self.images

        # Add tables if available
        if hasattr(self, "tables") and self.tables and isinstance(self.tables, list):
            doc_format.tables = self.tables

        return doc_format
