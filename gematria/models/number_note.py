"""
Number Note model for the Number Dictionary.

This module defines the data structure for storing notes about specific numbers,
including rich text content, attachments, and links to other numbers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class NumberNote:
    """Model for storing notes about a specific number."""
    
    id: Optional[int] = None
    number: int = 0
    title: str = ""
    content: str = ""  # Rich text HTML content
    attachments: List[str] = None  # File paths to attachments
    linked_numbers: List[int] = None  # Numbers this note links to
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.attachments is None:
            self.attachments = []
        if self.linked_numbers is None:
            self.linked_numbers = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now() 