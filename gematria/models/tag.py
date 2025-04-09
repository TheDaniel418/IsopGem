"""
Purpose: Defines the Tag model for categorizing and organizing gematria calculations

This file is part of the gematria pillar and serves as a model component.
It is responsible for the data structure that represents tags used to categorize
calculation results throughout the application.

Key components:
- Tag: Data class representing a category/label with customizable properties
  including name, color, and description

Dependencies:
- dataclasses: For creating a proper data class with minimal boilerplate
- uuid: For generating unique identifiers for tags

Related files:
- gematria/repositories/tag_repository.py: Handles persistence of Tag objects
- gematria/services/calculation_database_service.py: Uses Tag for categorization
- gematria/ui/panels/calculation_history_panel.py: Displays tags in the UI
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class Tag(BaseModel):
    """Model representing a tag for organizing calculations."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the tag",
    )
    name: str = Field(description="Display name of the tag")
    color: str = Field(
        default="#3498db", description="Color code for the tag (hex format)"
    )
    description: Optional[str] = Field(
        default=None, description="Optional description of the tag"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the tag was created"
    )
    modified_at: datetime = Field(
        default_factory=datetime.now, description="When the tag was last modified"
    )

    def to_dict(self) -> Dict:
        """Convert the tag to a dictionary for serialization.

        Returns:
            Dictionary representation of the tag
        """
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Tag":
        """Create a tag from a dictionary.

        Args:
            data: Dictionary containing tag data

        Returns:
            Tag instance
        """
        # Convert ISO format strings back to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("modified_at"), str):
            data["modified_at"] = datetime.fromisoformat(data["modified_at"])

        return cls(**data)
