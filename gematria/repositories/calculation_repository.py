"""
Purpose: Provides persistent storage and retrieval for gematria calculation results

This file is part of the gematria pillar and serves as a repository component.
It is responsible for storing, retrieving, updating, and deleting calculation
results in the file system, ensuring data persistence across application sessions.

Key components:
- CalculationRepository: Repository class for managing calculation data persistence
  with methods for CRUD operations on calculation results

Dependencies:
- json: For serializing calculation data to file storage
- pathlib: For cross-platform file path handling
- logging: For tracking repository operations
- gematria.models.calculation_result: For the CalculationResult data model

Related files:
- gematria/models/calculation_result.py: Data model for calculation results
- gematria/services/calculation_database_service.py: Uses this repository 
- gematria/repositories/tag_repository.py: Companion repository for tag data
"""

import os
import json
from typing import Dict, List, Optional, Set, Any, Union, cast
from datetime import datetime
from pathlib import Path

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType


class CalculationRepository:
    """Repository for managing calculation results."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the calculation repository.

        Args:
            data_dir: Directory where calculation data will be stored
        """
        # Set default data directory if none provided
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".isopgem", "data")

        self._data_dir = Path(data_dir)
        self._calculations_file = self._data_dir / "calculations.json"

        # Create data directory if it doesn't exist
        os.makedirs(self._data_dir, exist_ok=True)

        logger.debug(
            f"CalculationRepository initialized with data directory: {self._data_dir}"
        )

    def get_all_calculations(self) -> List[CalculationResult]:
        """Get all saved calculation results.

        Returns:
            List of calculation results
        """
        calculations: List[CalculationResult] = []

        # Create empty file if it doesn't exist
        if not self._calculations_file.exists():
            with open(self._calculations_file, "w") as f:
                json.dump([], f)
            return calculations

        # Load calculations from file
        try:
            with open(self._calculations_file, "r") as f:
                data = json.load(f)

            for item in data:
                calculations.append(CalculationResult.from_dict(item))

            logger.debug(f"Loaded {len(calculations)} calculations")
        except Exception as e:
            logger.error(f"Error loading calculations: {e}")

        return calculations

    def get_calculation(self, calculation_id: str) -> Optional[CalculationResult]:
        """Get a specific calculation by ID.

        Args:
            calculation_id: The ID of the calculation to retrieve

        Returns:
            The calculation result or None if not found
        """
        all_calculations = self.get_all_calculations()

        for calc in all_calculations:
            if calc.id == calculation_id:
                return calc

        logger.debug(f"Calculation with ID {calculation_id} not found")
        return None

    def save_calculation(self, calculation: CalculationResult) -> bool:
        """Save a calculation result.

        If the calculation with the same ID exists, it will be updated.
        Otherwise, a new calculation will be added.

        Args:
            calculation: The calculation result to save

        Returns:
            True if successful, False otherwise
        """
        all_calculations = self.get_all_calculations()

        # Check if calculation already exists
        exists = False
        for i, calc in enumerate(all_calculations):
            if calc.id == calculation.id:
                # Update existing calculation
                all_calculations[i] = calculation
                exists = True
                break

        # Add new calculation if it doesn't exist
        if not exists:
            all_calculations.append(calculation)

        # Save calculations to file
        try:
            self._save_to_file(all_calculations)
            logger.debug(f"Saved calculation with ID {calculation.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving calculation: {e}")
            return False

    def delete_calculation(self, calculation_id: str) -> bool:
        """Delete a calculation by ID.

        Args:
            calculation_id: The ID of the calculation to delete

        Returns:
            True if successful, False otherwise
        """
        all_calculations = self.get_all_calculations()

        # Find and remove the calculation
        for i, calc in enumerate(all_calculations):
            if calc.id == calculation_id:
                all_calculations.pop(i)

                # Save calculations to file
                try:
                    self._save_to_file(all_calculations)
                    logger.debug(f"Deleted calculation with ID {calculation_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error deleting calculation: {e}")
                    return False

        logger.debug(f"Calculation with ID {calculation_id} not found for deletion")
        return False

    def _save_to_file(self, calculations: List[CalculationResult]) -> None:
        """Save calculations to file.

        Args:
            calculations: List of calculation results to save
        """
        # Convert calculations to dictionaries
        data = [calc.to_dict() for calc in calculations]

        # Save to file
        with open(self._calculations_file, "w") as f:
            json.dump(data, f, indent=2)

    def find_by_value(self, value: int) -> List[CalculationResult]:
        """Find calculations by result value.

        Args:
            value: The value to search for

        Returns:
            List of matching calculation results
        """
        all_calculations = self.get_all_calculations()

        return [calc for calc in all_calculations if calc.result_value == value]

    def find_by_text(self, text: str) -> List[CalculationResult]:
        """Find calculations by input text.

        Args:
            text: The text to search for

        Returns:
            List of matching calculation results
        """
        all_calculations = self.get_all_calculations()

        return [
            calc for calc in all_calculations if text.lower() in calc.input_text.lower()
        ]

    def find_by_tag(self, tag_id: str) -> List[CalculationResult]:
        """Find calculations by tag ID.

        Args:
            tag_id: The tag ID to search for

        Returns:
            List of matching calculation results
        """
        all_calculations = self.get_all_calculations()

        return [calc for calc in all_calculations if tag_id in calc.tags]

    def find_favorites(self) -> List[CalculationResult]:
        """Find all favorite calculations.

        Returns:
            List of favorite calculation results
        """
        all_calculations = self.get_all_calculations()

        return [calc for calc in all_calculations if calc.favorite]

    def find_by_method(self, method: Union[str, int]) -> List[CalculationResult]:
        """Find calculations by calculation method.

        Args:
            method: The calculation method to search for (string or integer)

        Returns:
            List of matching calculation results
        """
        all_calculations = self.get_all_calculations()

        # Ensure method is comparable with calculation_type
        method_str = str(method)

        return [
            calc
            for calc in all_calculations
            if (
                # Compare string values
                (
                    isinstance(calc.calculation_type, str)
                    and calc.calculation_type == method_str
                )
                or
                # Handle CalculationType objects
                (
                    hasattr(calc.calculation_type, "value")
                    and str(calc.calculation_type.value) == method_str
                )
            )
        ]

    def get_unique_values(self) -> Set[int]:
        """Get all unique calculation values.

        Returns:
            Set of unique values
        """
        all_calculations = self.get_all_calculations()

        return set(calc.result_value for calc in all_calculations)

    def get_recent_calculations(self, limit: int = 10) -> List[CalculationResult]:
        """Get most recent calculations.

        Args:
            limit: Maximum number of calculations to return

        Returns:
            List of recent calculation results
        """
        all_calculations = self.get_all_calculations()

        # Sort by timestamp (newest first)
        sorted_calculations = sorted(
            all_calculations, key=lambda x: x.timestamp, reverse=True
        )

        # Return limited number
        return sorted_calculations[:limit]

    def find_calculations_by_text(self, text: str) -> List[CalculationResult]:
        """Find all calculations containing the specified text.

        Args:
            text: Text to search for in input_text or notes

        Returns:
            List of calculation results containing the specified text
        """
        text_lower = text.lower()
        return [
            calc
            for calc in self.get_all_calculations()
            if text_lower in calc.input_text.lower()
            or (calc.notes and text_lower in calc.notes.lower())
        ]

    def find_calculations_by_value(self, value: int) -> List[CalculationResult]:
        """Find all calculations with the specified result value.

        Args:
            value: Numeric result value to search for

        Returns:
            List of calculation results with the specified value
        """
        return self.find_by_value(value)

    def find_calculations_by_method(
        self, method: Union[CalculationType, str]
    ) -> List[CalculationResult]:
        """Find all calculations using a specific calculation method.

        Args:
            method: Calculation method (enum or custom method name)

        Returns:
            List of calculation results using the specified method
        """
        if isinstance(method, CalculationType):
            # Convert enum value to string to match how it's stored in the database
            return self.find_by_method(str(method.value))
        else:
            # Search by custom method name
            return self.find_by_method(method)

    def find_recent_calculations(self, limit: int = 10) -> List[CalculationResult]:
        """Find the most recent calculations.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent calculation results, sorted by timestamp (newest first)
        """
        return self.get_recent_calculations(limit)

    def find_calculations_by_tag(self, tag_id: str) -> List[CalculationResult]:
        """Find all calculations with a specific tag.

        Args:
            tag_id: ID of the tag to filter by

        Returns:
            List of calculation results with the specified tag
        """
        return self.find_by_tag(tag_id)
