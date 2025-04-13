"""History service for gematria calculations.

This module provides functionality for storing and retrieving
gematria calculation history.
"""

from typing import List

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType


class HistoryService:
    """Service for managing gematria calculation history."""

    def __init__(self) -> None:
        """Initialize the history service."""
        self._history: List[CalculationResult] = []
        # Add a unique identifier to each history service instance for debugging
        import uuid
        self._instance_id = str(uuid.uuid4())[:8]
        logger.debug(f"HistoryService initialized with instance ID: {self._instance_id}")

    def add_calculation(self, calculation: CalculationResult) -> None:
        """Add a calculation to the history.

        Args:
            calculation: The calculation result to add
        """
        # Check if this calculation is already in the history (by ID)
        for existing_calc in self._history:
            if existing_calc.id == calculation.id:
                logger.warning(f"HistoryService[{self._instance_id}]: Calculation with ID {calculation.id} already exists in history")
                return

        # Log the current state of the history
        logger.debug(f"HistoryService[{self._instance_id}]: Current history has {len(self._history)} items")

        # Add the calculation to the history
        self._history.append(calculation)

        # Format calculation type name based on its type
        if isinstance(calculation.calculation_type, CalculationType):
            calc_type_name = calculation.calculation_type.name
        else:
            # Handle string calculation type
            calc_type_name = str(calculation.calculation_type)

        logger.debug(
            f"HistoryService[{self._instance_id}]: Added calculation to history: {calculation.input_text}, "
            f"method: {calc_type_name}, "
            f"result: {calculation.result_value}, "
            f"ID: {calculation.id}"
        )

        # Log the updated state of the history
        logger.debug(f"HistoryService[{self._instance_id}]: History now has {len(self._history)} items")

    def get_history(self) -> List[CalculationResult]:
        """Get the calculation history.

        Returns:
            List of calculation results in chronological order
        """
        logger.debug(f"HistoryService[{self._instance_id}]: get_history called, returning {len(self._history)} items")
        return list(self._history)  # Return a copy of the history list

    def clear_history(self) -> None:
        """Clear all calculation history."""
        self._history.clear()
        logger.info(f"HistoryService[{self._instance_id}]: Calculation history cleared")

    def get_last_calculation(self) -> CalculationResult:
        """Get the most recent calculation.

        Returns:
            The most recent calculation result

        Raises:
            IndexError: If history is empty
        """
        if not self._history:
            raise IndexError("No calculations in history")
        return self._history[-1]
