"""
Purpose: Provides persistent storage and retrieval for tag data used in categorizing calculations

This file is part of the gematria pillar and serves as a repository component.
It is responsible for storing, retrieving, updating, and deleting tag data
in the file system, ensuring consistent categorization across application sessions.

Key components:
- TagRepository: Repository class for managing tag data persistence
  with methods for CRUD operations on tags and default tag creation

Dependencies:
- json: For serializing tag data to file storage
- pathlib: For cross-platform file path handling
- logging: For tracking repository operations
- gematria.models.tag: For the Tag data model

Related files:
- gematria/models/tag.py: Data model for tags
- gematria/services/calculation_database_service.py: Uses this repository
- gematria/repositories/calculation_repository.py: Companion repository for calculation data
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from loguru import logger

from gematria.models.tag import Tag


class TagRepository:
    """Repository for storing and retrieving tags."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the tag repository.

        Args:
            data_dir: Directory where tag data will be stored
        """
        # Set default data directory if none provided
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".isopgem", "data")

        self._data_dir = Path(data_dir)
        self._tags_file = self._data_dir / "tags.json"

        # Create data directory if it doesn't exist
        os.makedirs(self._data_dir, exist_ok=True)

        logger.debug(f"TagRepository initialized with data directory: {self._data_dir}")

    def get_all_tags(self) -> List[Tag]:
        """Get all saved tags.

        Returns:
            List of tags
        """
        tags: List[Tag] = []

        # Create empty file if it doesn't exist
        if not self._tags_file.exists():
            with open(self._tags_file, "w") as f:
                json.dump([], f)
            return tags

        # Load tags from file
        try:
            with open(self._tags_file, "r") as f:
                data = json.load(f)

            for item in data:
                tags.append(Tag.from_dict(item))

            logger.debug(f"Loaded {len(tags)} tags")
        except Exception as e:
            logger.error(f"Error loading tags: {e}")

        return tags

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Get a specific tag by ID.

        Args:
            tag_id: The ID of the tag to retrieve

        Returns:
            The tag or None if not found
        """
        all_tags = self.get_all_tags()

        for tag in all_tags:
            if tag.id == tag_id:
                return tag

        logger.debug(f"Tag with ID {tag_id} not found")
        return None

    def create_tag(self, tag: Tag) -> bool:
        """Create a new tag.

        Args:
            tag: The tag to create

        Returns:
            True if successful, False otherwise
        """
        all_tags = self.get_all_tags()

        # Check if tag with same ID already exists
        for existing_tag in all_tags:
            if existing_tag.id == tag.id:
                logger.debug(f"Tag with ID {tag.id} already exists")
                return False

        # Add new tag
        all_tags.append(tag)

        # Save tags to file
        try:
            self._save_to_file(all_tags)
            logger.debug(f"Created tag with ID {tag.id}")
            return True
        except Exception as e:
            logger.error(f"Error creating tag: {e}")
            return False

    def update_tag(self, tag: Tag) -> bool:
        """Update an existing tag.

        Args:
            tag: The tag to update

        Returns:
            True if successful, False otherwise
        """
        all_tags = self.get_all_tags()

        # Find and update the tag
        for i, existing_tag in enumerate(all_tags):
            if existing_tag.id == tag.id:
                all_tags[i] = tag

                # Save tags to file
                try:
                    self._save_to_file(all_tags)
                    logger.debug(f"Updated tag with ID {tag.id}")
                    return True
                except Exception as e:
                    logger.error(f"Error updating tag: {e}")
                    return False

        logger.debug(f"Tag with ID {tag.id} not found for update")
        return False

    def save_tag(self, tag: Tag) -> bool:
        """Save a tag to the repository.

        This is a convenience method that calls create_tag for new tags
        and update_tag for existing tags.

        Args:
            tag: Tag instance to save

        Returns:
            True if successful, False otherwise
        """
        existing_tag = self.get_tag(tag.id)
        if existing_tag:
            return self.update_tag(tag)
        else:
            return self.create_tag(tag)

    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag by ID.

        Args:
            tag_id: The ID of the tag to delete

        Returns:
            True if successful, False otherwise
        """
        all_tags = self.get_all_tags()

        # Find and remove the tag
        for i, tag in enumerate(all_tags):
            if tag.id == tag_id:
                all_tags.pop(i)

                # Save tags to file
                try:
                    self._save_to_file(all_tags)
                    logger.debug(f"Deleted tag with ID {tag_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error deleting tag: {e}")
                    return False

        logger.debug(f"Tag with ID {tag_id} not found for deletion")
        return False

    def _save_to_file(self, tags: List[Tag]) -> None:
        """Save tags to file.

        Args:
            tags: List of tags to save
        """
        # Convert tags to dictionaries
        data = [tag.to_dict() for tag in tags]

        # Save to file
        with open(self._tags_file, "w") as f:
            json.dump(data, f, indent=2)

    def create_default_tags(self) -> List[Tag]:
        """Create default tags if none exist.

        Returns:
            List of created default tags
        """
        # Check if tags already exist
        existing_tags = self.get_all_tags()
        if existing_tags:
            logger.debug("Default tags not created, tags already exist")
            return existing_tags

        # Create default tags
        default_tags: List[Tag] = [
            Tag(
                name="Important",
                color="#FF0000",
                description="Important findings to review",
            ),
            Tag(
                name="Biblical",
                color="#0000FF",
                description="References to biblical texts",
            ),
            Tag(
                name="Research",
                color="#00AA00",
                description="Items requiring further research",
            ),
            Tag(
                name="Correspondence",
                color="#AA00AA",
                description="Correspondence with other concepts",
            ),
            Tag(
                name="Follow Up",
                color="#FFA500",
                description="Items to follow up on later",
            ),
            Tag(
                name="Egypt", color="#8B4513", description="Related to Egyptian studies"
            ),
        ]

        # Save default tags
        all_tags: List[Tag] = []
        for tag in default_tags:
            self.create_tag(tag)
            all_tags.append(tag)

        logger.debug(f"Created {len(default_tags)} default tags")
        return all_tags
