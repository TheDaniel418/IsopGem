"""
Purpose: Provides database lookup services for TQ (Ternary Qabala) numbers

This file is part of the tq pillar and serves as a service component.
It is responsible for searching and retrieving TQ number information from
various database sources, including calculation database and number properties.

Key components:
- TQDatabaseService: Main service class for TQ database operations
- lookup_number: Function to search for a specific number across databases
- get_number_references: Function to get references to a number

Dependencies:
- PyQt6: For UI integration
- shared.services.number_properties_service: For number property analysis
- shared.services.calculation_database_service: For searching saved calculations
- tq.utils.ternary_converter: For number system conversions

Related files:
- tq/ui/widgets/ternary_transition_widget.py: Uses this service for database lookups
- tq/ui/dialogs/number_database_window.py: Will display database results
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from shared.services.number_properties_service import NumberPropertiesService


class TQDatabaseService(QObject):
    """Service for TQ database operations and lookups."""

    # Signal emitted when a number lookup is completed
    lookup_completed = pyqtSignal(int, object)  # number, results

    # Track singleton instance
    _instance = None

    def __init__(self):
        """Initialize the TQ Database Service."""
        super().__init__()

        # Get references to other services
        self.number_properties = NumberPropertiesService.get_instance()

        # The calculation database service might not be initialized yet in all contexts
        self.calculation_db = None
        try:
            from shared.services.calculation_database_service import (
                CalculationDatabaseService,
            )

            self.calculation_db = CalculationDatabaseService()
        except Exception:
            # Log that the calculation database is not available
            pass

    @classmethod
    def get_instance(cls) -> "TQDatabaseService":
        """Get the TQ Database Service singleton instance.

        Returns:
            The singleton TQDatabaseService instance
        """
        if cls._instance is None:
            cls._instance = get_instance()
        return cls._instance

    def lookup_number(self, number: int) -> Dict[str, Any]:
        """Look up information about a number across all available databases.

        Args:
            number: The decimal number to look up

        Returns:
            Dictionary containing all available information about the number
        """
        results = {
            "number": number,
            "quadset_properties": self._get_quadset_properties(number),
            "number_properties": self._get_number_properties(number),
            "calculation_references": self._get_calculation_references(number),
            "is_in_quadset": self._check_if_in_quadset(number),
        }

        # Emit signal with results
        self.lookup_completed.emit(number, results)

        return results

    def _get_quadset_properties(self, number: int) -> Dict[str, Any]:
        """Get the quadset properties for a number.

        Args:
            number: The decimal number to analyze

        Returns:
            Dictionary of quadset properties
        """
        return self.number_properties.get_quadset_properties(number)

    def _get_number_properties(self, number: int) -> Dict[str, Any]:
        """Get mathematical properties of a number.

        Args:
            number: The decimal number to analyze

        Returns:
            Dictionary of number properties
        """
        # Get basic number properties
        properties = {
            "is_prime": self.number_properties.is_prime(number),
            "is_triangular": self.number_properties.is_triangular(number),
            "is_square": self.number_properties.is_square(number),
            "is_fibonacci": self.number_properties.is_fibonacci(number),
            "factors": self.number_properties.get_prime_factors(number),
            "divisors": self.number_properties.get_divisors(number),
        }

        # Add additional properties if available
        if properties["is_triangular"]:
            properties[
                "triangular_index"
            ] = self.number_properties.get_triangular_index(number)

        if properties["is_fibonacci"]:
            properties["fibonacci_index"] = self.number_properties.get_fibonacci_index(
                number
            )

        return properties

    def _get_calculation_references(self, number: int) -> List[Dict[str, Any]]:
        """Get references to the number in the calculation database.

        Args:
            number: The decimal number to look up

        Returns:
            List of calculation references to the number
        """
        if not self.calculation_db:
            return []

        try:
            # Find calculations with this result value
            calculations = self.calculation_db.find_calculations_by_value(number)

            # Convert to simplified format
            references = []
            for calc in calculations:
                references.append(
                    {
                        "id": calc.id,
                        "input_text": calc.input_text,
                        "method": str(calc.calculation_type)
                        if hasattr(calc, "calculation_type")
                        else calc.method_name,
                        "tags": self.calculation_db.get_calculation_tag_names(calc)
                        if hasattr(self.calculation_db, "get_calculation_tag_names")
                        else [],
                        "created_at": calc.created_at,
                    }
                )

            return references
        except Exception:
            # Return empty list if database access fails
            return []

    def _check_if_in_quadset(self, number: int) -> Dict[str, Any]:
        """Check if a number is part of a quadset (not as the base number).

        Args:
            number: The decimal number to check

        Returns:
            Dictionary with 'is_part_of_quadset' and 'base_number' if found
        """
        try:
            # Initialize the result with default values
            result = {"is_part_of_quadset": False}

            # Get the quadset properties
            quadset = self.number_properties.get_quadset_properties(number)

            # Handle the nested dictionary structure (when quadset has 'base', 'conrune', etc. keys)
            if "base" in quadset and isinstance(quadset["base"], dict):
                # This is the nested structure
                if (
                    number == quadset["base"].get("number")
                    or number == quadset["conrune"].get("number")
                    or number == quadset["ternary_reversal"].get("number")
                    or number == quadset["reversal_conrune"].get("number")
                ):
                    result["is_part_of_quadset"] = True
                    result["base_number"] = quadset["base"].get("number")
                    result["base_quadset"] = quadset
                    return result

                # Try to find a reasonable range of numbers to check
                lower_bound = max(1, number // 10)
                upper_bound = min(
                    number * 10, 10000
                )  # Limit the search to avoid performance issues

                # Check if the number appears in another quadset
                for base in range(lower_bound, upper_bound):
                    if base == number:
                        continue  # Skip the number itself

                    base_quadset = self.number_properties.get_quadset_properties(base)
                    if "base" in base_quadset and isinstance(
                        base_quadset["base"], dict
                    ):
                        if (
                            number == base_quadset["conrune"].get("number")
                            or number == base_quadset["ternary_reversal"].get("number")
                            or number == base_quadset["reversal_conrune"].get("number")
                        ):
                            result["is_part_of_quadset"] = True
                            result["base_number"] = base
                            result["base_quadset"] = base_quadset
                            return result

            # Handle the flat dictionary structure (when quadset has 'number', 'conrune', etc. keys)
            else:
                if (
                    number == quadset.get("number")
                    or number == quadset.get("conrune")
                    or number == quadset.get("reverse_ternary_decimal")
                    or number == quadset.get("reverse_conrune")
                ):
                    result["is_part_of_quadset"] = True
                    result["base_number"] = quadset.get("number")
                    result["base_quadset"] = quadset
                    return result

                # Try to find a reasonable range of numbers to check
                lower_bound = max(1, number // 10)
                upper_bound = min(
                    number * 10, 10000
                )  # Limit the search to avoid performance issues

                # Check if the number appears in another quadset
                for base in range(lower_bound, upper_bound):
                    if base == number:
                        continue  # Skip the number itself

                    base_quadset = self.number_properties.get_quadset_properties(base)
                    if "number" in base_quadset and not isinstance(
                        base_quadset.get("conrune"), dict
                    ):
                        if (
                            number == base_quadset.get("conrune")
                            or number == base_quadset.get("reverse_ternary_decimal")
                            or number == base_quadset.get("reverse_conrune")
                        ):
                            result["is_part_of_quadset"] = True
                            result["base_number"] = base
                            result["base_quadset"] = base_quadset
                            return result

            return result

        except Exception as e:
            # Handle any errors gracefully
            import logging

            logging.error(f"Error checking if number {number} is in quadset: {e}")
            return {"is_part_of_quadset": False, "error": str(e)}


# Singleton instance
instance: Optional[TQDatabaseService] = None


def get_instance() -> TQDatabaseService:
    """Get the TQ Database Service instance.

    Returns:
        The singleton TQDatabaseService instance

    Raises:
        RuntimeError: If the service has not been initialized
    """
    global instance
    if instance is None:
        instance = TQDatabaseService()
    return instance


def initialize() -> TQDatabaseService:
    """Initialize the TQ Database Service.

    Returns:
        The initialized TQDatabaseService instance
    """
    global instance
    if instance is None:
        instance = TQDatabaseService()
        TQDatabaseService._instance = instance
    return instance
