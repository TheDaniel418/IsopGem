"""
Purpose: Provides services for managing tags in the application

This file is part of the shared services layer and manages operations related to tags.
It provides functionality for creating, retrieving, updating, and deleting tags, as well
as associating tags with other entities like calculations and documents.

Key components:
- TagService: Service class for tag operations

Dependencies:
- shared.services.service_locator: For dependency management
- shared.repositories: For data access

Related files:
- gematria/ui/dialogs/tag_selection_dialog.py: UI for selecting tags
- gematria/ui/dialogs/calculation_details_dialog.py: Uses tags for calculations
"""

import uuid
from typing import List, Optional, Dict, Any

from loguru import logger

from shared.models.tag import Tag
from shared.repositories.tag_repository import TagRepository


class TagService:
    """Service for managing tags in the application."""
    
    def __init__(self, tag_repository: TagRepository):
        """
        Initialize the tag service.
        
        Args:
            tag_repository: Repository for tag data access
        """
        self.tag_repository = tag_repository
    
    def create_tag(self, name: str, color: str, description: str = "") -> Optional[Tag]:
        """
        Create a new tag.
        
        Args:
            name: Tag name
            color: Tag color (hex format)
            description: Optional tag description
            
        Returns:
            The created tag or None if creation failed
        """
        try:
            tag = Tag(
                id=str(uuid.uuid4()),
                name=name,
                color=color,
                description=description
            )
            
            success = self.tag_repository.save_tag(tag)
            if success:
                logger.debug(f"Created tag: {name} with ID {tag.id}")
                return tag
            else:
                logger.error(f"Failed to create tag: {name}")
                return None
        except Exception as e:
            logger.error(f"Error creating tag: {str(e)}")
            return None
    
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """
        Get a tag by its ID.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            The tag or None if not found
        """
        try:
            return self.tag_repository.get_tag(tag_id)
        except Exception as e:
            logger.error(f"Error retrieving tag {tag_id}: {str(e)}")
            return None
    
    def get_all_tags(self) -> List[Tag]:
        """
        Get all tags.
        
        Returns:
            List of all tags
        """
        try:
            return self.tag_repository.get_all_tags()
        except Exception as e:
            logger.error(f"Error retrieving all tags: {str(e)}")
            return []
    
    def update_tag(self, tag: Tag) -> bool:
        """
        Update an existing tag.
        
        Args:
            tag: The tag to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.tag_repository.save_tag(tag)
        except Exception as e:
            logger.error(f"Error updating tag {tag.id}: {str(e)}")
            return False
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag.
        
        Args:
            tag_id: The tag's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.tag_repository.delete_tag(tag_id)
        except Exception as e:
            logger.error(f"Error deleting tag {tag_id}: {str(e)}")
            return False
    
    def search_tags(self, query: str) -> List[Tag]:
        """
        Search for tags by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tags
        """
        try:
            # Simple case-insensitive search
            all_tags = self.get_all_tags()
            query = query.lower()
            
            return [
                tag for tag in all_tags 
                if query in tag.name.lower() or 
                   (tag.description and query in tag.description.lower())
            ]
        except Exception as e:
            logger.error(f"Error searching tags: {str(e)}")
            return [] 