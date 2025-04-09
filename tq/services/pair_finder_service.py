"""
Purpose: Provides services for finding and analyzing pairs of numbers with specific properties

This file is part of the tq pillar and serves as a service component.
It is responsible for finding pairs of numbers that satisfy specific TQ relationships,
calculating their properties, and managing the analysis results.

Key components:
- PairFinderService: Main service class for finding and analyzing number pairs
- find_pairs: Core function for finding pairs with specific properties
- analyze_pair: Analyzes properties of a given pair

Dependencies:
- tq.utils.ternary_converter: For ternary number conversions
- shared.services.number_properties_service: For analyzing number properties

Related files:
- tq/ui/panels/pair_finder_panel.py: UI that uses this service
- tq/models/pair_result.py: Data model for pair analysis results
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from loguru import logger

from shared.services.number_properties_service import NumberPropertiesService
from tq.utils.ternary_converter import (
    decimal_to_balanced_ternary,
    decimal_to_ternary,
)


@dataclass
class PairResult:
    """Result of a pair analysis."""

    number1: int
    number2: int
    ternary1: str
    ternary2: str
    balanced1: str
    balanced2: str
    properties1: Dict[str, Any]
    properties2: Dict[str, Any]
    relationship: str


class PairFinderService:
    """Service for finding and analyzing pairs of numbers."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "PairFinderService":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = PairFinderService()
        return cls._instance

    def __init__(self):
        """Initialize the service."""
        self._properties_service = NumberPropertiesService.get_instance()
        logger.debug("PairFinderService initialized")

    def find_pairs(self, start: int, end: int, relationship: str) -> List[PairResult]:
        """Find pairs of numbers within a range that satisfy a relationship.

        Args:
            start: Start of range (inclusive)
            end: End of range (inclusive)
            relationship: Type of relationship to look for

        Returns:
            List of PairResult objects for matching pairs
        """
        pairs = []

        for n1 in range(start, end + 1):
            for n2 in range(n1, end + 1):  # Start from n1 to avoid duplicates
                if self._check_relationship(n1, n2, relationship):
                    pair = self.analyze_pair(n1, n2, relationship)
                    pairs.append(pair)

        return pairs

    def analyze_pair(self, n1: int, n2: int, relationship: str) -> PairResult:
        """Analyze a pair of numbers and their relationship.

        Args:
            n1: First number
            n2: Second number
            relationship: Type of relationship between the numbers

        Returns:
            PairResult object with analysis details
        """
        return PairResult(
            number1=n1,
            number2=n2,
            ternary1=decimal_to_ternary(n1),
            ternary2=decimal_to_ternary(n2),
            balanced1=decimal_to_balanced_ternary(n1),
            balanced2=decimal_to_balanced_ternary(n2),
            properties1=self._properties_service.get_number_properties(n1),
            properties2=self._properties_service.get_number_properties(n2),
            relationship=relationship,
        )

    def _check_relationship(self, n1: int, n2: int, relationship: str) -> bool:
        """Check if two numbers satisfy a specific relationship.

        Args:
            n1: First number
            n2: Second number
            relationship: Type of relationship to check

        Returns:
            True if the numbers satisfy the relationship
        """
        if relationship == "consecutive":
            return abs(n2 - n1) == 1
        elif relationship == "complementary":
            t1 = decimal_to_ternary(n1)
            t2 = decimal_to_ternary(n2)
            return len(t1) == len(t2) and all(
                int(d1) + int(d2) == 2 for d1, d2 in zip(t1, t2)
            )
        elif relationship == "mirror":
            t1 = decimal_to_ternary(n1)
            t2 = decimal_to_ternary(n2)
            return t1 == t2[::-1]
        else:
            logger.warning(f"Unknown relationship type: {relationship}")
            return False
