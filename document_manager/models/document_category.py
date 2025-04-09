"""
Purpose: Defines the DocumentCategory model for categorizing documents.

This file is part of the document_manager pillar and serves as a model component.
It is responsible for representing document categories and their hierarchical relationships.

Key components:
- DocumentCategory: Model for representing document categories

Dependencies:
- uuid: For generating unique IDs
- pydantic: For data validation
"""

import uuid
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class DocumentCategory(BaseModel):
    """Represents a category for organizing documents."""

    # Core properties
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str = "#3498db"  # Default to a blue color
    description: Optional[str] = None

    # Hierarchical structure
    parent_id: Optional[str] = None

    # Additional metadata
    icon: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

    def is_root_category(self) -> bool:
        """Check if this is a root category (no parent).

        Returns:
            True if this is a root category, False otherwise
        """
        return self.parent_id is None

    @classmethod
    def create_default_categories(cls) -> List["DocumentCategory"]:
        """Create a set of default categories.

        Returns:
            List of default document categories
        """
        return [
            cls(
                name="General",
                description="General documents",
                color="#3498db",  # Blue
            ),
            cls(
                name="Research",
                description="Research materials and papers",
                color="#2ecc71",  # Green
            ),
            cls(
                name="Reference",
                description="Reference materials and guides",
                color="#e74c3c",  # Red
            ),
            cls(
                name="Correspondence",
                description="Letters, emails and other correspondence",
                color="#f39c12",  # Orange
            ),
            cls(
                name="Projects",
                description="Project-related documents",
                color="#9b59b6",  # Purple
            ),
        ]

    def get_child_categories(
        self, all_categories: List["DocumentCategory"]
    ) -> List["DocumentCategory"]:
        """Get all direct child categories of this category.

        Args:
            all_categories: List of all available categories

        Returns:
            List of direct child categories
        """
        return [
            category for category in all_categories if category.parent_id == self.id
        ]

    def get_all_descendant_ids(
        self, all_categories: List["DocumentCategory"]
    ) -> Set[str]:
        """Get IDs of all descendant categories (recursive).

        Args:
            all_categories: List of all available categories

        Returns:
            Set of all descendant category IDs
        """
        result = set()
        direct_children = self.get_child_categories(all_categories)

        for child in direct_children:
            result.add(child.id)
            result.update(child.get_all_descendant_ids(all_categories))

        return result

    def get_path(self) -> List["DocumentCategory"]:
        """Get the path to this category from the root.

        Returns:
            List of categories from root to this category
        """
        if self.parent_id is None:
            return [self]

        # This needs to be done with a list of all categories
        # For simplicity, use the service to get all categories
        from document_manager.services.category_service import CategoryService

        service = CategoryService()
        all_categories = service.get_all_categories()

        # Use the helper function to get the path
        return get_path_to_category(self.id, all_categories)

    def get_descendant_ids(self) -> Set[str]:
        """Get all descendant category IDs.

        Returns:
            Set of category IDs that are descendants of this category
        """
        # This needs to be done with a list of all categories
        # For simplicity, use the service to get all categories
        from document_manager.services.category_service import CategoryService

        service = CategoryService()
        all_categories = service.get_all_categories()

        # Use the helper function to get descendant IDs
        return get_all_descendant_ids(self.id, all_categories)


class CategoryHierarchy:
    """Helper class to manage a hierarchy of document categories."""

    def __init__(self, categories: Optional[List[DocumentCategory]] = None):
        """Initialize with a list of categories.

        Args:
            categories: List of document categories
        """
        self.categories_by_id: Dict[str, DocumentCategory] = {}
        self.children_by_parent_id: Dict[str, List[str]] = {}

        # Root categories (those without a parent)
        self.root_category_ids: Set[str] = set()

        if categories:
            self.add_categories(categories)

    def add_categories(self, categories: List[DocumentCategory]) -> None:
        """Add categories to the hierarchy.

        Args:
            categories: List of document categories to add
        """
        for category in categories:
            self.add_category(category)

    def add_category(self, category: DocumentCategory) -> None:
        """Add a category to the hierarchy.

        Args:
            category: Document category to add
        """
        self.categories_by_id[category.id] = category

        if category.parent_id is None:
            # This is a root category
            self.root_category_ids.add(category.id)
        else:
            # Add as child to parent
            if category.parent_id not in self.children_by_parent_id:
                self.children_by_parent_id[category.parent_id] = []

            self.children_by_parent_id[category.parent_id].append(category.id)

    def get_category(self, category_id: str) -> Optional[DocumentCategory]:
        """Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            DocumentCategory or None if not found
        """
        return self.categories_by_id.get(category_id)

    def get_children(self, category_id: str) -> List[DocumentCategory]:
        """Get children of a category.

        Args:
            category_id: Category ID

        Returns:
            List of child categories
        """
        child_ids = self.children_by_parent_id.get(category_id, [])
        return [self.categories_by_id[child_id] for child_id in child_ids]

    def get_parent(self, category_id: str) -> Optional[DocumentCategory]:
        """Get parent of a category.

        Args:
            category_id: Category ID

        Returns:
            Parent category or None if it's a root category
        """
        category = self.get_category(category_id)
        if category and category.parent_id:
            return self.get_category(category.parent_id)
        return None

    def get_root_categories(self) -> List[DocumentCategory]:
        """Get all root categories.

        Returns:
            List of root categories
        """
        return [
            self.categories_by_id[category_id] for category_id in self.root_category_ids
        ]

    def get_category_path(self, category_id: str) -> List[DocumentCategory]:
        """Get path from root to this category.

        Args:
            category_id: Category ID

        Returns:
            List of categories from root to this category (inclusive)
        """
        path: List[DocumentCategory] = []
        current_category = self.get_category(category_id)

        # If category doesn't exist, return empty path
        if not current_category:
            return path

        # Add categories from the target up to the root
        while current_category:
            path.append(current_category)
            current_category = self.get_parent(current_category.id)

        # Reverse to get root->target order
        path.reverse()

        return path

    def get_descendant_ids(self, category_id: str) -> Set[str]:
        """Get IDs of all descendants of a category.

        Args:
            category_id: Category ID

        Returns:
            Set of descendant category IDs
        """
        descendant_ids: Set[str] = set()
        self._collect_descendant_ids(category_id, descendant_ids)
        return descendant_ids

    def _collect_descendant_ids(self, category_id: str, result: Set[str]) -> None:
        """Helper method to recursively collect descendant IDs.

        Args:
            category_id: Category ID
            result: Set to collect descendant IDs
        """
        child_ids = self.children_by_parent_id.get(category_id, [])

        for child_id in child_ids:
            result.add(child_id)
            self._collect_descendant_ids(child_id, result)


def get_nested_categories(
    categories: Optional[List[DocumentCategory]] = None,
) -> Dict[str, Any]:
    """Convert a flat list of categories to a nested dictionary structure.

    Args:
        categories: List of categories to convert.
            If not provided, all categories will be loaded.

    Returns:
        Dictionary with nested category structure
    """
    from document_manager.services.category_service import CategoryService

    # If categories not provided, load all categories
    if categories is None:
        service = CategoryService()
        categories = service.get_all_categories()

    # Create a hierarchy helper
    hierarchy = CategoryHierarchy(categories)

    # Build nested structure
    result: Dict[str, Any] = {}

    # Start with root categories
    for root in hierarchy.get_root_categories():
        result[root.id] = {
            "id": root.id,
            "name": root.name,
            "color": root.color,
            "children": _build_category_subtree(root.id, hierarchy),
        }

    return result


def _build_category_subtree(
    category_id: str, hierarchy: CategoryHierarchy
) -> Dict[str, Any]:
    """Helper function to build a nested category subtree.

    Args:
        category_id: ID of the parent category
        hierarchy: CategoryHierarchy instance

    Returns:
        Dictionary with nested children
    """
    result: Dict[str, Any] = {}

    children = hierarchy.get_children(category_id)
    for child in children:
        result[child.id] = {
            "id": child.id,
            "name": child.name,
            "color": child.color,
            "children": _build_category_subtree(child.id, hierarchy),
        }

    return result


def get_path_to_category(
    category_id: str, categories: List[DocumentCategory]
) -> List[DocumentCategory]:
    """Get the path from root to a specific category.

    Args:
        category_id: ID of the target category
        categories: List of all categories

    Returns:
        List of categories from root to target
    """
    # Initialize path
    path: List[DocumentCategory] = []

    # Find the category
    target = next((c for c in categories if c.id == category_id), None)
    if not target:
        return path

    # Add the target
    path.append(target)

    # Traverse up to the root
    current = target
    while current.parent_id:
        parent = next((c for c in categories if c.id == current.parent_id), None)
        if not parent:
            break
        path.insert(0, parent)
        current = parent

    return path


def get_all_descendant_ids(
    category_id: str, categories: List[DocumentCategory]
) -> Set[str]:
    """Get all descendant category IDs for a category.

    Args:
        category_id: ID of the parent category
        categories: List of all categories

    Returns:
        Set of descendant category IDs
    """
    # Initialize result set
    descendant_ids: Set[str] = set()

    # Find direct children
    children = [c for c in categories if c.parent_id == category_id]

    # Add children and their descendants
    for child in children:
        descendant_ids.add(child.id)
        descendant_ids.update(get_all_descendant_ids(child.id, categories))

    return descendant_ids
