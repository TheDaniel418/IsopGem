"""
Purpose: Defines the Tag model for categorizing and organizing entities

This file is part of the shared models layer and provides a data structure 
for representing tags used throughout the application. Tags are used to categorize 
and organize different entities like documents and calculations.

Key components:
- Tag: Data class representing a tag with ID, name, color, and description

Dependencies:
- dataclasses: For simplified class creation

Related files:
- shared/services/tag_service.py: Service for managing tags
- shared/repositories/tag_repository.py: Repository for tag persistence
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Tag:
    """
    Represents a tag used to categorize and group entities in the application.
    Tags can be applied to calculations, documents, and other entities.
    """
    
    id: str
    """Unique identifier for the tag"""
    
    name: str
    """Display name of the tag"""
    
    color: str
    """Color code for the tag (hex format, e.g., '#FF5733')"""
    
    description: str = ""
    """Optional description of the tag's purpose or meaning"""
    
    def __eq__(self, other):
        """
        Compare tags for equality based on their IDs.
        
        Args:
            other: Another tag to compare with
            
        Returns:
            True if the tags have the same ID, False otherwise
        """
        if not isinstance(other, Tag):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """
        Hash function for Tag, enabling use in sets and as dictionary keys.
        
        Returns:
            Hash value based on the tag's ID
        """
        return hash(self.id) 