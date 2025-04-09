"""
Purpose: Provides document category management business logic for the application.

This file is part of the document_manager pillar and serves as a service component.
It is responsible for handling document category operations and hierarchies.

Key components:
- CategoryService: Service class for document category management operations

Dependencies:
- document_manager.models.document_category: For DocumentCategory model
- document_manager.repositories.category_repository: For category persistence
"""

from typing import Dict, List, Optional

from loguru import logger

from document_manager.models.document_category import DocumentCategory
from document_manager.repositories.category_repository import CategoryRepository


class CategoryService:
    """Service for document category management operations."""

    def __init__(self, category_repository: Optional[CategoryRepository] = None):
        """Initialize the category service.

        Args:
            category_repository: Repository for category storage, created if not provided
        """
        self.category_repository = category_repository or CategoryRepository()

    def get_category(self, category_id: str) -> Optional[DocumentCategory]:
        """Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category if found, None otherwise
        """
        return self.category_repository.get_by_id(category_id)

    def get_all_categories(self) -> List[DocumentCategory]:
        """Get all categories.

        Returns:
            List of all categories
        """
        return self.category_repository.get_all()

    def get_root_categories(self) -> List[DocumentCategory]:
        """Get all root categories (categories without a parent).

        Returns:
            List of root categories
        """
        return self.category_repository.get_root_categories()

    def get_child_categories(self, parent_id: str) -> List[DocumentCategory]:
        """Get child categories of a parent category.

        Args:
            parent_id: Parent category ID

        Returns:
            List of child categories
        """
        return self.category_repository.get_child_categories(parent_id)

    def save_category(self, category: DocumentCategory) -> bool:
        """Save a category.

        This will create a new category if it doesn't exist or update an existing one.

        Args:
            category: Category to save

        Returns:
            True if successful, False otherwise
        """
        return self.category_repository.save(category)

    def delete_category(self, category_id: str) -> bool:
        """Delete a category.

        Note: This will fail if there are documents assigned to this category
        or if there are child categories.

        Args:
            category_id: Category ID

        Returns:
            True if successful, False otherwise
        """
        return self.category_repository.delete(category_id)

    def search_categories(self, query: str) -> List[DocumentCategory]:
        """Search for categories by name or description.

        Args:
            query: Search query

        Returns:
            List of matching categories
        """
        return self.category_repository.search(query)

    def create_category(
        self,
        name: str,
        color: str = "#1976D2",
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Optional[DocumentCategory]:
        """Create a new category.

        Args:
            name: Category name
            color: Category color (hex code)
            description: Category description
            parent_id: Parent category ID (if any)
            icon: Category icon (if any)

        Returns:
            Created category if successful, None otherwise
        """
        # Validate parent category if provided
        if parent_id and not self.category_repository.get_by_id(parent_id):
            logger.error(f"Parent category not found: {parent_id}")
            return None

        # Create new category
        category = DocumentCategory(
            name=name,
            color=color,
            description=description,
            parent_id=parent_id,
            icon=icon,
        )

        # Save category
        if self.category_repository.save(category):
            return category

        return None

    def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Optional[DocumentCategory]:
        """Update an existing category.

        Args:
            category_id: Category ID
            name: New category name (if changing)
            color: New category color (if changing)
            description: New category description (if changing)
            parent_id: New parent category ID (if changing)
            icon: New category icon (if changing)

        Returns:
            Updated category if successful, None otherwise
        """
        # Get existing category
        category = self.category_repository.get_by_id(category_id)

        if not category:
            logger.error(f"Category not found: {category_id}")
            return None

        # Validate parent category if provided
        if parent_id and parent_id != category.parent_id:
            if not self.category_repository.get_by_id(parent_id):
                logger.error(f"Parent category not found: {parent_id}")
                return None

            # Prevent circular references in hierarchy
            if self._would_create_cycle(category_id, parent_id):
                logger.error(
                    f"Cannot set parent to {parent_id}: would create circular reference"
                )
                return None

        # Update category fields
        if name is not None:
            category.name = name

        if color is not None:
            category.color = color

        if description is not None:
            category.description = description

        if parent_id is not None:
            category.parent_id = parent_id

        if icon is not None:
            category.icon = icon

        # Save updated category
        if self.category_repository.save(category):
            return category

        return None

    def _would_create_cycle(self, category_id: str, new_parent_id: str) -> bool:
        """Check if setting new_parent_id as parent would create a cycle.

        Args:
            category_id: Category being modified
            new_parent_id: Potential new parent category ID

        Returns:
            True if a cycle would be created, False otherwise
        """
        if category_id == new_parent_id:
            return True

        # Get the potential parent
        parent = self.category_repository.get_by_id(new_parent_id)

        if not parent:
            return False

        # Check if this category is an ancestor of the new parent
        current_id = parent.parent_id
        visited = set()

        while current_id:
            if current_id in visited:
                # Cycle in existing hierarchy
                return True

            if current_id == category_id:
                return True

            visited.add(current_id)
            current_parent = self.category_repository.get_by_id(current_id)

            if not current_parent:
                break

            current_id = current_parent.parent_id

        return False

    def get_category_tree(self) -> List[Dict]:
        """Get the category tree as a hierarchical structure.

        Returns:
            List of root categories with nested children
        """
        all_categories = {cat.id: cat for cat in self.category_repository.get_all()}

        # Build tree structure
        def build_tree(category_id):
            if category_id not in all_categories:
                return None

            category = all_categories[category_id]
            children = []

            for cat_id, cat in all_categories.items():
                if cat.parent_id == category_id:
                    child_tree = build_tree(cat_id)
                    if child_tree:
                        children.append(child_tree)

            return {
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "description": category.description,
                "icon": category.icon,
                "children": sorted(children, key=lambda x: x["name"]),
            }

        # Start with root categories
        tree = []
        for cat_id, cat in all_categories.items():
            if not cat.parent_id:  # Root category
                tree_node = build_tree(cat_id)
                if tree_node:
                    tree.append(tree_node)

        return sorted(tree, key=lambda x: x["name"])

    def get_category_path(self, category_id: str) -> List[DocumentCategory]:
        """Get the path from root to a specific category.

        Args:
            category_id: Category ID

        Returns:
            List of categories from root to the given category (inclusive)
        """
        path: List[DocumentCategory] = []
        current_category = self.category_repository.get_by_id(category_id)

        while current_category:
            path.insert(0, current_category)

            if not current_category.parent_id:
                break

            current_category = self.category_repository.get_by_id(
                current_category.parent_id
            )

        return path
