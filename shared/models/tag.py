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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


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

    parent: Optional["Tag"] = None
    """Parent tag of this tag"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Metadata associated with this tag"""

    children: Set["Tag"] = field(default_factory=set)
    """Child tags of this tag"""

    def __eq__(self, other: Any) -> bool:
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

    def __hash__(self) -> int:
        """
        Hash function for Tag, enabling use in sets and as dictionary keys.

        Returns:
            Hash value based on the tag's ID
        """
        return hash(self.id)

    def add_child(self, child: "Tag") -> None:
        """
        Add a child tag to this tag.

        Args:
            child: The tag to add as a child
        """
        if child not in self.children:
            self.children.add(child)
            child.parent = self

    def remove_child(self, child: "Tag") -> None:
        """
        Remove a child tag from this tag.

        Args:
            child: The tag to remove
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def get_ancestors(self) -> List["Tag"]:
        """
        Get all ancestor tags in order from immediate parent to root.

        Returns:
            List of ancestor tags
        """
        ancestors: List["Tag"] = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self) -> List["Tag"]:
        """
        Get all descendant tags in depth-first order.

        Returns:
            List of descendant tags
        """
        descendants: List["Tag"] = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_siblings(self) -> List["Tag"]:
        """
        Get all sibling tags (tags with the same parent).

        Returns:
            List of sibling tags
        """
        if self.parent is None:
            return []
        return [tag for tag in self.parent.children if tag != self]

    def is_ancestor_of(self, other: "Tag") -> bool:
        """
        Check if this tag is an ancestor of another tag.

        Args:
            other: The tag to check

        Returns:
            True if this tag is an ancestor of the other tag
        """
        current = other.parent
        while current is not None:
            if current == self:
                return True
            current = current.parent
        return False

    def is_descendant_of(self, other: "Tag") -> bool:
        """
        Check if this tag is a descendant of another tag.

        Args:
            other: The tag to check

        Returns:
            True if this tag is a descendant of the other tag
        """
        return other.is_ancestor_of(self)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key.

        Args:
            key: The metadata key
            default: Default value if key doesn't exist

        Returns:
            The metadata value or default
        """
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value by key.

        Args:
            key: The metadata key
            value: The value to set
        """
        self.metadata[key] = value
