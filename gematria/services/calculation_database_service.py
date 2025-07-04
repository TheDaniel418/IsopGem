"""
Purpose: Provides unified access to calculation and tag data persistence using SQLite

This file is part of the gematria pillar and serves as a service component.
It is responsible for coordinating operations between the calculation and tag
repositories, providing a higher-level API for managing gematria calculation
results and their associated tags using an SQLite database.

Key components:
- CalculationDatabaseService: Service class that combines tag and calculation
  repositories to provide a unified interface for data management

Dependencies:
- shared.repositories.sqlite_calculation_repository: For storing calculation results
- shared.repositories.sqlite_tag_repository: For managing tags
- gematria.models.calculation_result: For the data structure of calculations
- gematria.models.calculation_type: For the data structure of calculation types
- gematria.models.tag: For the data structure of tags

Related files:
- gematria/services/gematria_service.py: Uses this service for data persistence
- gematria/ui/panels/calculation_history_panel.py: UI for displaying stored data
- gematria/ui/dialogs/save_calculation_dialog.py: UI for saving calculations
"""

from typing import Any, Dict, List, Optional, Set, Union

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from gematria.models.tag import Tag

# Import repositories directly to avoid circular imports
from shared.repositories.sqlite_calculation_repository import (
    SQLiteCalculationRepository,
)
from shared.repositories.sqlite_tag_repository import SQLiteTagRepository


class CalculationDatabaseService:
    """Service for managing gematria calculation database operations using SQLite."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the calculation database service.

        Args:
            data_dir: Optional base directory path for storing data
        """
        # Initialize repositories
        self.calculation_repo = SQLiteCalculationRepository(data_dir)
        self.tag_repo = SQLiteTagRepository(data_dir)

        # Ensure we have some default tags
        if not self.tag_repo.get_all_tags():
            self.tag_repo.create_default_tags()

        logger.debug("CalculationDatabaseService initialized with SQLite repositories")

    # ===== Tag Methods =====

    def get_all_tags(self) -> List[Tag]:
        """Get all tags.

        Returns:
            List of all tags
        """
        return self.tag_repo.get_all_tags()

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Get a specific tag by ID.

        Args:
            tag_id: ID of the tag to retrieve

        Returns:
            Tag instance or None if not found
        """
        return self.tag_repo.get_tag(tag_id)

    def create_tag(
        self, name: str, color: str = "#3498db", description: Optional[str] = None
    ) -> Optional[Tag]:
        """Create a new tag.

        Args:
            name: Name of the tag
            color: Color code for the tag (hex format)
            description: Optional description of the tag

        Returns:
            Created Tag instance or None if creation failed
        """
        tag = Tag(name=name, color=color, description=description)
        if self.tag_repo.create_tag(tag):
            return tag
        return None

    def update_tag(self, tag: Tag) -> bool:
        """Update an existing tag.

        Args:
            tag: Tag instance to update

        Returns:
            True if successful, False otherwise
        """
        return self.tag_repo.update_tag(tag)

    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag.

        Args:
            tag_id: ID of the tag to delete

        Returns:
            True if successful, False otherwise
        """
        # In SQLite with foreign key constraints, deleting a tag will automatically
        # remove tag references from all calculations using ON DELETE CASCADE.
        # This is handled in the database schema.
        return self.tag_repo.delete_tag(tag_id)

    # ===== Calculation Methods =====

    def get_all_calculations(self) -> List[CalculationResult]:
        """Get all saved calculations.

        Returns:
            List of all saved calculations
        """
        return self.calculation_repo.get_all_calculations()

    def count_calculations(self) -> int:
        """Count the total number of calculations in the database.

        Returns:
            Total number of calculations
        """
        return self.calculation_repo.count_calculations()

    def get_calculations_page(
        self,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "timestamp",
        sort_order: str = "DESC",
    ) -> List[CalculationResult]:
        """Get a page of calculations with sorting.

        Args:
            offset: Starting index for pagination
            limit: Maximum number of items to return
            sort_by: Column to sort by (timestamp, input_text, result_value)
            sort_order: Sort direction (ASC or DESC)

        Returns:
            List of calculations for the requested page
        """
        return self.calculation_repo.get_calculations_page(
            offset=offset, limit=limit, sort_by=sort_by, sort_order=sort_order
        )

    def get_unique_calculation_methods(self) -> List[str]:
        """Get a list of all unique calculation methods used in the database.

        Returns:
            List of method names/identifiers
        """
        return self.calculation_repo.get_unique_calculation_methods()

    def get_calculation(self, calculation_id: str) -> Optional[CalculationResult]:
        """Get a specific calculation result by ID.

        Args:
            calculation_id: ID of the calculation result to retrieve

        Returns:
            CalculationResult instance or None if not found
        """
        return self.calculation_repo.get_calculation(calculation_id)

    def save_calculation(self, calculation: CalculationResult) -> bool:
        """Save a calculation result.

        Args:
            calculation: CalculationResult instance to save

        Returns:
            True if successful, False otherwise
        """
        return self.calculation_repo.save_calculation(calculation)

    def delete_calculation(self, calculation_id: str) -> bool:
        """Delete a calculation result.

        Args:
            calculation_id: ID of the calculation result to delete

        Returns:
            True if successful, False otherwise
        """
        return self.calculation_repo.delete_calculation(calculation_id)

    def add_tag_to_calculation(self, calculation_id: str, tag_id: str) -> bool:
        """Add a tag to a calculation.

        Args:
            calculation_id: ID of the calculation
            tag_id: ID of the tag to add

        Returns:
            True if successful, False otherwise
        """
        calculation = self.get_calculation(calculation_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calculation_id}")
            return False

        tag = self.get_tag(tag_id)
        if not tag:
            logger.warning(f"Tag not found: {tag_id}")
            return False

        if tag_id not in calculation.tags:
            calculation.tags.append(tag_id)
            return self.save_calculation(calculation)

        return True  # Tag already exists on the calculation

    def remove_tag_from_calculation(self, calculation_id: str, tag_id: str) -> bool:
        """Remove a tag from a calculation.

        Args:
            calculation_id: ID of the calculation
            tag_id: ID of the tag to remove

        Returns:
            True if successful, False otherwise
        """
        calculation = self.get_calculation(calculation_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calculation_id}")
            return False

        if tag_id in calculation.tags:
            calculation.tags.remove(tag_id)
            return self.save_calculation(calculation)

        return True  # Tag was not on the calculation

    def toggle_favorite_calculation(self, calculation_id: str) -> bool:
        """Toggle the favorite status of a calculation.

        Args:
            calculation_id: ID of the calculation

        Returns:
            True if successful, False otherwise
        """
        calculation = self.get_calculation(calculation_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calculation_id}")
            return False

        calculation.favorite = not calculation.favorite
        return self.save_calculation(calculation)

    def update_calculation_notes(self, calculation_id: str, notes: str) -> bool:
        """Update the notes for a calculation.

        Args:
            calculation_id: ID of the calculation
            notes: New notes content

        Returns:
            True if successful, False otherwise
        """
        calculation = self.get_calculation(calculation_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calculation_id}")
            return False

        calculation.notes = notes
        return self.save_calculation(calculation)

    # ===== Search Methods =====

    def find_calculations_by_tag(self, tag_id: str) -> List[CalculationResult]:
        """Find all calculations with a specific tag.

        Args:
            tag_id: ID of the tag to filter by

        Returns:
            List of calculation results with the specified tag
        """
        return self.calculation_repo.find_calculations_by_tag(tag_id)

    def find_calculations_by_text(self, text: str) -> List[CalculationResult]:
        """Find all calculations containing the specified text.

        Args:
            text: Text to search for in input_text or notes

        Returns:
            List of calculation results containing the specified text
        """
        return self.calculation_repo.find_calculations_by_text(text)

    def find_calculations_by_value(self, value: int) -> List[CalculationResult]:
        """Find all calculations with the specified result value.

        Args:
            value: Numeric result value to search for

        Returns:
            List of calculation results with the specified value
        """
        return self.calculation_repo.find_calculations_by_value(value)

    def find_favorites(self) -> List[CalculationResult]:
        """Find all calculations marked as favorites.

        Returns:
            List of calculation results marked as favorites
        """
        return self.calculation_repo.find_favorites()

    def find_calculations_by_method(
        self, method: Union[CalculationType, str]
    ) -> List[CalculationResult]:
        """Find all calculations using a specific calculation method.

        Args:
            method: Calculation method (enum or custom method name)

        Returns:
            List of calculation results using the specified method
        """
        return self.calculation_repo.find_calculations_by_method(method)

    def find_calculations_by_method_name(self, method_name: str) -> List[CalculationResult]:
        """Find all calculations using a specific calculation method name.

        This method is particularly useful for finding calculations that used
        deprecated/removed calculation types that no longer exist as enum values.

        Args:
            method_name: String name of the calculation method

        Returns:
            List of calculation results using the specified method name
        """
        # Build search criteria to find calculations with this method name
        criteria = {
            "calculation_type": method_name  # This will search the string representation
        }

        # Also check custom cipher methods
        custom_results = []
        if method_name.startswith("CUSTOM_"):
            # For custom methods, also search the custom_method_name field
            custom_criteria = {
                "custom_method_name": method_name
            }
            custom_results = self.search_calculations(custom_criteria)

        # Get standard method results
        standard_results = self.search_calculations(criteria)

        # Combine results (avoiding duplicates by using IDs as keys)
        all_results = {}
        for calc in standard_results + custom_results:
            all_results[calc.id] = calc

        return list(all_results.values())

    def find_recent_calculations(self, limit: int = 10) -> List[CalculationResult]:
        """Find the most recent calculations.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent calculation results, sorted by timestamp (newest first)
        """
        return self.calculation_repo.find_recent_calculations(limit)

    def get_unique_values(self) -> Set[int]:
        """Get a set of all unique calculation result values.

        Returns:
            Set of unique calculation result values
        """
        return self.calculation_repo.get_unique_values()

    def get_calculation_tag_names(self, calculation: CalculationResult) -> List[str]:
        """Get the tag names for a calculation.

        Args:
            calculation: Calculation result to get tag names for

        Returns:
            List of tag names
        """
        tag_names = []
        for tag_id in calculation.tags:
            tag = self.get_tag(tag_id)
            if tag:
                tag_names.append(tag.name)
        return tag_names

    def search_calculations(self, criteria: Dict[str, Any]) -> List[CalculationResult]:
        """Search for calculations that match specific criteria.

        Args:
            criteria: Dictionary of search criteria, such as:
                - input_text: Text to search for in the input (exact match)
                - input_text_like: Text pattern to search for in the input (partial match)
                - result_value: Value to search for
                - result_value_min: Minimum value (inclusive)
                - result_value_max: Maximum value (inclusive)
                - calculation_type: Standard calculation method to filter by
                - custom_method_name: Custom cipher method name to filter by
                - language: Filter by language (Language enum)
                - favorite: True to only return favorites
                - has_tags: True to only return calculations with tags
                - has_notes: True to only return calculations with notes
                - tag_id: Specific tag ID to match
                - created_after: datetime for results created after this date
                - created_before: datetime for results created before this date
                - limit: Maximum number of results to return

        Returns:
            List of matching calculations
        """
        # Log the search criteria for debugging
        logger.debug(f"Searching calculations with criteria: {criteria}")

        # Use the repository's search method which handles all the complex filtering
        # including the language filter at the database level
        results = self.calculation_repo.search_calculations(criteria)

        # Log the number of results found
        logger.debug(f"Search found {len(results)} matching calculations")

        return results

    def get_filtered_calculations(
        self,
        search_term: Optional[str] = None,
        tag_id: Optional[str] = None,
        calculation_type: Optional[Union[CalculationType, str]] = None,
        favorites_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[CalculationResult], int]:
        """Get calculations filtered by various criteria with pagination.

        Args:
            search_term: Optional text to search for in input text, notes, or result
            tag_id: Optional tag ID to filter by
            calculation_type: Optional calculation method to filter by
            favorites_only: Whether to only include favorites
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (list of filtered calculations, total count of matching calculations)
        """
        # Build criteria dictionary
        criteria = {}
        if search_term:
            criteria["input_text"] = search_term
        if tag_id:
            criteria["tags"] = [tag_id]
        if calculation_type:
            # Handle different types of calculation methods
            if isinstance(calculation_type, CalculationType):
                criteria["calculation_type"] = calculation_type
            elif isinstance(calculation_type, str):
                # Check if it's a custom cipher method name
                if calculation_type.startswith("Custom:"):
                    criteria["custom_method_name"] = calculation_type.replace(
                        "Custom: ", ""
                    )
                else:
                    criteria["calculation_type"] = calculation_type
        if favorites_only:
            criteria["favorites_only"] = True

        # First get all matching calculations to count them
        all_matching = self.search_calculations(criteria)
        total_count = len(all_matching)

        # Then get the paginated subset
        end_idx = min(offset + limit, total_count)
        if offset >= total_count:
            return [], total_count

        paginated_results = all_matching[offset:end_idx]
        return paginated_results, total_count

    def get_distinct_calculation_types(self) -> List[Union[CalculationType, str]]:
        """Get a list of all distinct calculation types used in saved calculations.

        Returns:
            List of unique calculation types
        """
        # Get all calculations and extract unique calculation types
        calculations = self.get_all_calculations()

        # Use a set to track unique types
        unique_types = set()

        for calc in calculations:
            unique_types.add(calc.calculation_type)

        return list(unique_types)
