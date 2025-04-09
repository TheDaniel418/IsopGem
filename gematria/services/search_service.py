"""
Purpose: Provides search functionality for the gematria pillar.

This file is part of the gematria pillar and serves as a service component.
It is responsible for searching numbers and their gematria values across
different calculation methods.

Key components:
- SearchService: Main service class that handles search operations
- search_by_number: Search for gematria calculations by number
- search_by_text: Search for gematria calculations by Hebrew text

Dependencies:
- gematria.services.calculation_database_service: For database operations
- gematria.models.calculation_result: Data model for calculation results
"""

from typing import List

from gematria.models.calculation_result import CalculationResult
from gematria.services.calculation_database_service import CalculationDatabaseService


class SearchService:
    """Service for searching gematria calculations and results."""

    def __init__(self, calculation_db: CalculationDatabaseService):
        """Initialize the search service.

        Args:
            calculation_db: The calculation database service to use for searches
        """
        self.calculation_db = calculation_db

    def search_by_number(self, number: int) -> List[CalculationResult]:
        """Search for gematria calculations by number.

        Args:
            number: The number to search for

        Returns:
            List of calculation results matching the number
        """
        criteria = {"value": number}
        return self.calculation_db.search_calculations(criteria)

    def search_by_text(self, text: str) -> List[CalculationResult]:
        """Search for gematria calculations by Hebrew text.

        Args:
            text: The Hebrew text to search for

        Returns:
            List of calculation results matching the text
        """
        criteria = {"hebrew_text": text}
        return self.calculation_db.search_calculations(criteria)
