"""
Purpose: Defines aspect models for astrological calculations.

This file is part of the astrology pillar and serves as a data model.
It provides classes for representing aspects between celestial bodies
and aspect patterns in astrological charts.

Key components:
- AspectType: Enum for different types of aspects
- Aspect: Class representing an aspect between two celestial bodies
- AspectPattern: Class representing a pattern of aspects

Dependencies:
- Python typing: For type hint annotations
- Pydantic: For data validation
- Enum: For enumeration types
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class AspectType(Enum):
    """Types of astrological aspects."""

    CONJUNCTION = "Conjunction"
    OPPOSITION = "Opposition"
    TRINE = "Trine"
    SQUARE = "Square"
    SEXTILE = "Sextile"
    SEMISEXTILE = "Semisextile"
    QUINCUNX = "Quincunx"
    SEMISQUARE = "Semisquare"
    SESQUISQUARE = "Sesquisquare"
    QUINTILE = "Quintile"
    BIQUINTILE = "Biquintile"
    SEPTILE = "Septile"
    NOVILE = "Novile"
    PARALLEL = "Parallel"
    CONTRAPARALLEL = "Contraparallel"


class AspectInfo(BaseModel):
    """Information about an aspect type."""

    type: AspectType
    angle: float
    orb: float = 5.0  # Default orb of 5 degrees
    harmonious: bool = False

    # Symbol and color for display
    symbol: str
    color: str

    # Additional properties
    keywords: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class Aspect(BaseModel):
    """Class representing an aspect between two celestial bodies."""

    body1: str
    body2: str
    aspect_type: AspectType
    angle: float
    orb: float
    exact_angle: float
    applying: bool = False  # True if the aspect is applying, False if separating

    # Additional properties
    properties: Dict[str, Any] = Field(default_factory=dict)

    def is_harmonious(self) -> bool:
        """Check if the aspect is harmonious.

        Returns:
            True if the aspect is harmonious, False otherwise
        """
        harmonious_aspects = [
            AspectType.TRINE,
            AspectType.SEXTILE,
            AspectType.QUINTILE,
            AspectType.BIQUINTILE,
            AspectType.NOVILE,
        ]
        return self.aspect_type in harmonious_aspects

    def is_challenging(self) -> bool:
        """Check if the aspect is challenging.

        Returns:
            True if the aspect is challenging, False otherwise
        """
        challenging_aspects = [
            AspectType.OPPOSITION,
            AspectType.SQUARE,
            AspectType.SEMISQUARE,
            AspectType.SESQUISQUARE,
            AspectType.QUINCUNX,
        ]
        return self.aspect_type in challenging_aspects

    def is_major(self) -> bool:
        """Check if the aspect is a major aspect.

        Returns:
            True if the aspect is a major aspect, False otherwise
        """
        major_aspects = [
            AspectType.CONJUNCTION,
            AspectType.OPPOSITION,
            AspectType.TRINE,
            AspectType.SQUARE,
            AspectType.SEXTILE,
        ]
        return self.aspect_type in major_aspects

    def is_minor(self) -> bool:
        """Check if the aspect is a minor aspect.

        Returns:
            True if the aspect is a minor aspect, False otherwise
        """
        return not self.is_major()

    def is_exact(self, precision: float = 1.0) -> bool:
        """Check if the aspect is exact within a given precision.

        Args:
            precision: Maximum orb to consider the aspect exact

        Returns:
            True if the aspect is exact, False otherwise
        """
        return abs(self.orb) <= precision


class AspectPatternType(Enum):
    """Types of aspect patterns in astrology."""

    GRAND_TRINE = "Grand Trine"
    GRAND_CROSS = "Grand Cross"
    T_SQUARE = "T-Square"
    YOD = "Yod"
    MYSTIC_RECTANGLE = "Mystic Rectangle"
    KITE = "Kite"
    GRAND_SEXTILE = "Grand Sextile"
    STELLIUM = "Stellium"
    CRADLE = "Cradle"
    THOR_HAMMER = "Thor's Hammer"


class AspectPattern(BaseModel):
    """Class representing a pattern of aspects in a chart."""

    pattern_type: AspectPatternType
    bodies: List[str]
    aspects: List[Tuple[str, str, AspectType]]

    # Additional properties
    keywords: List[str] = Field(default_factory=list)
    description: Optional[str] = None

    def get_focal_planet(self) -> Optional[str]:
        """Get the focal planet of the pattern, if applicable.

        Returns:
            The focal planet if the pattern has one, None otherwise
        """
        # For T-Square, the focal planet is the one that receives the two squares
        if self.pattern_type == AspectPatternType.T_SQUARE and len(self.bodies) == 3:
            # Count the number of aspects each planet is involved in
            aspect_count = {body: 0 for body in self.bodies}
            for body1, body2, _ in self.aspects:
                aspect_count[body1] += 1
                aspect_count[body2] += 1

            # The focal planet is the one with the most aspects
            return max(aspect_count.items(), key=lambda x: x[1])[0]

        # For Yod, the focal planet is the one that receives the two quincunxes
        if self.pattern_type == AspectPatternType.YOD and len(self.bodies) == 3:
            quincunx_count = {body: 0 for body in self.bodies}
            for body1, body2, aspect_type in self.aspects:
                if aspect_type == AspectType.QUINCUNX:
                    quincunx_count[body1] += 1
                    quincunx_count[body2] += 1

            # The focal planet is the one with the most quincunxes
            return max(quincunx_count.items(), key=lambda x: x[1])[0]

        return None
