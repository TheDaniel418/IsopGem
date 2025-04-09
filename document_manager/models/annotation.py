"""
Purpose: Defines the Annotation data model for document annotations.

This file is part of the document_manager pillar and serves as a model component.
It is responsible for representing annotations made on documents, including highlighting,
notes, and other markup types.

Key components:
- AnnotationType: Enum defining the types of annotations
- Annotation: Model class representing an annotation on a document
- TextPosition: Helper class for text position information

Dependencies:
- uuid: For generating unique IDs
- enum: For annotation type enumeration
- datetime: For handling timestamps
- pydantic: For model definition
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AnnotationType(str, Enum):
    """Types of document annotations."""

    HIGHLIGHT = "highlight"
    NOTE = "note"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    BOOKMARK = "bookmark"
    LINK = "link"
    COMMENT = "comment"


class TextPosition(BaseModel):
    """Represents a position within a text document."""

    # For text-based position
    start_index: Optional[int] = None
    end_index: Optional[int] = None

    # For visual/page-based position
    page: Optional[int] = None
    x1: Optional[float] = None
    y1: Optional[float] = None
    x2: Optional[float] = None
    y2: Optional[float] = None

    @property
    def is_text_based(self) -> bool:
        """Check if position is text-based.

        Returns:
            True if position is text-based, False otherwise
        """
        return self.start_index is not None and self.end_index is not None

    @property
    def is_visual_based(self) -> bool:
        """Check if position is visual/page-based.

        Returns:
            True if position is visual/page-based, False otherwise
        """
        return self.page is not None and all(
            coord is not None for coord in [self.x1, self.y1, self.x2, self.y2]
        )

    @classmethod
    def from_text_indices(cls, start_index: int, end_index: int) -> "TextPosition":
        """Create a text-based position.

        Args:
            start_index: Start index in the text
            end_index: End index in the text

        Returns:
            TextPosition instance
        """
        return cls(start_index=start_index, end_index=end_index)

    @classmethod
    def from_coordinates(
        cls, page: int, x1: float, y1: float, x2: float, y2: float
    ) -> "TextPosition":
        """Create a visual/page-based position.

        Args:
            page: Page number (0-based)
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate

        Returns:
            TextPosition instance
        """
        return cls(page=page, x1=x1, y1=y1, x2=x2, y2=y2)


class Annotation(BaseModel):
    """Represents an annotation on a document."""

    # Core fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    annotation_type: AnnotationType
    creation_date: datetime = Field(default_factory=datetime.now)

    # Content
    text: str  # The annotated text or comment content
    note: Optional[str] = None  # Additional notes about the annotation

    # Position
    position: TextPosition

    # Styling
    color: str = "#ffff00"  # Default yellow for highlights

    # Metadata
    author: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

    @classmethod
    def create_highlight(
        cls, document_id: str, text: str, position: TextPosition, color: str = "#ffff00"
    ) -> "Annotation":
        """Create a highlight annotation.

        Args:
            document_id: ID of the document
            text: Text to highlight
            position: Position in the document
            color: Highlight color

        Returns:
            Highlight annotation
        """
        return cls(
            document_id=document_id,
            annotation_type=AnnotationType.HIGHLIGHT,
            text=text,
            position=position,
            color=color,
        )

    @classmethod
    def create_note(
        cls, document_id: str, text: str, note: str, position: TextPosition
    ) -> "Annotation":
        """Create a note annotation.

        Args:
            document_id: ID of the document
            text: Annotated text
            note: Note content
            position: Position in the document

        Returns:
            Note annotation
        """
        return cls(
            document_id=document_id,
            annotation_type=AnnotationType.NOTE,
            text=text,
            note=note,
            position=position,
            color="#42aaf5",  # Light blue
        )

    @classmethod
    def create_bookmark(
        cls, document_id: str, text: str, position: TextPosition
    ) -> "Annotation":
        """Create a bookmark annotation.

        Args:
            document_id: ID of the document
            text: Bookmark title or annotated text
            position: Position in the document

        Returns:
            Bookmark annotation
        """
        return cls(
            document_id=document_id,
            annotation_type=AnnotationType.BOOKMARK,
            text=text,
            position=position,
            color="#e74c3c",  # Red
        )
