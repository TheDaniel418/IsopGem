"""
Purpose: Defines zodiac-related models for astrological calculations.

This file is part of the astrology pillar and serves as a data model.
It provides classes for representing zodiac signs, houses, and related
astrological concepts.

Key components:
- Element: Enum for the four elements (Fire, Earth, Air, Water)
- Modality: Enum for the three modalities (Cardinal, Fixed, Mutable)
- Polarity: Enum for the two polarities (Masculine/Positive, Feminine/Negative)
- ZodiacSign: Class representing a zodiac sign
- House: Class representing an astrological house
- HouseSystem: Enum for different house systems

Dependencies:
- Python typing: For type hint annotations
- Pydantic: For data validation
- Enum: For enumeration types
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Element(Enum):
    """The four classical elements in astrology."""

    FIRE = "Fire"
    EARTH = "Earth"
    AIR = "Air"
    WATER = "Water"


class Modality(Enum):
    """The three modalities or qualities in astrology."""

    CARDINAL = "Cardinal"
    FIXED = "Fixed"
    MUTABLE = "Mutable"


class Polarity(Enum):
    """The two polarities in astrology."""

    MASCULINE = "Masculine"  # Also known as Positive/Yang
    FEMININE = "Feminine"  # Also known as Negative/Yin


class ZodiacSign(BaseModel):
    """Class representing a zodiac sign."""

    name: str
    symbol: str
    element: Element
    modality: Modality
    polarity: Polarity
    ruling_planet: List[str]  # Some signs have multiple rulers

    # Degrees in the zodiac
    start_degree: float
    end_degree: float

    # Additional properties
    keywords: List[str] = Field(default_factory=list)
    body_associations: List[str] = Field(default_factory=list)

    def contains_degree(self, degree: float) -> bool:
        """Check if a degree falls within this sign.

        Args:
            degree: Degree in the zodiac (0-360)

        Returns:
            True if the degree is within this sign, False otherwise
        """
        # Normalize degree to 0-360 range
        normalized_degree = degree % 360

        return self.start_degree <= normalized_degree < self.end_degree

    def degree_in_sign(self, zodiac_degree: float) -> float:
        """Convert a zodiac degree to a degree within this sign.

        Args:
            zodiac_degree: Degree in the zodiac (0-360)

        Returns:
            Degree within the sign (0-30)

        Raises:
            ValueError: If the degree is not within this sign
        """
        # Normalize degree to 0-360 range
        normalized_degree = zodiac_degree % 360

        if not self.contains_degree(normalized_degree):
            raise ValueError(f"Degree {zodiac_degree} is not in sign {self.name}")

        return normalized_degree - self.start_degree


class HouseSystem(Enum):
    """Different house systems used in astrology."""

    PLACIDUS = "Placidus"
    KOCH = "Koch"
    EQUAL = "Equal"
    WHOLE_SIGN = "Whole Sign"
    REGIOMONTANUS = "Regiomontanus"
    CAMPANUS = "Campanus"
    TOPOCENTRIC = "Topocentric"
    MORINUS = "Morinus"
    PORPHYRY = "Porphyry"
    ALCABITIUS = "Alcabitius"


class PerspectiveType(Enum):
    """Different perspective types used in astrology."""

    GEOCENTRIC = (
        "Apparent Geocentric"  # Earth-centered view with apparent positions (default)
    )
    TRUE_GEOCENTRIC = "True Geocentric"  # Earth-centered view with true positions
    TOPOCENTRIC = (
        "Topocentric"  # Observer-centered view from a specific location on Earth
    )
    HELIOCENTRIC = "Heliocentric"  # Sun-centered view


class House(BaseModel):
    """Class representing an astrological house."""

    number: int  # 1-12
    name: Optional[str] = None

    # Degrees in the zodiac
    cusp_degree: float
    end_degree: float  # Usually the next house's cusp

    # Sign on the cusp
    sign: Optional[str] = None

    # Planets in this house
    planets: List[str] = Field(default_factory=list)

    # Additional properties
    keywords: List[str] = Field(default_factory=list)
    natural_sign: Optional[str] = None  # The sign naturally associated with this house

    def contains_degree(self, degree: float) -> bool:
        """Check if a degree falls within this house.

        Args:
            degree: Degree in the zodiac (0-360)

        Returns:
            True if the degree is within this house, False otherwise
        """
        # Normalize degree to 0-360 range
        normalized_degree = degree % 360

        # Handle houses that cross the 0° Aries point
        if self.end_degree < self.cusp_degree:
            return (
                normalized_degree >= self.cusp_degree
                or normalized_degree < self.end_degree
            )

        return self.cusp_degree <= normalized_degree < self.end_degree

    def add_planet(self, planet_name: str) -> None:
        """Add a planet to this house.

        Args:
            planet_name: Name of the planet to add
        """
        if planet_name not in self.planets:
            self.planets.append(planet_name)


class Planet(BaseModel):
    """Class representing a planet or other celestial body."""

    name: str
    sign: str
    degree: float
    retrograde: bool = False
    house: Optional[str] = None

    # Additional properties
    speed: Optional[float] = None  # Degrees per day
    latitude: Optional[float] = None  # Celestial latitude
    declination: Optional[float] = None  # Declination

    def __str__(self) -> str:
        """Get a string representation of the planet.

        Returns:
            String representation
        """
        retrograde_symbol = "R" if self.retrograde else ""
        return f"{self.name}: {self.sign} {self.degree:.2f}° {retrograde_symbol}"


class Aspect(BaseModel):
    """Class representing an aspect between two planets."""

    planet1: str
    planet2: str
    aspect_type: str  # Conjunction, Opposition, Trine, etc.
    orb: float  # Orb in degrees

    # Additional properties
    applying: Optional[
        bool
    ] = None  # True if the aspect is applying, False if separating
    exact: Optional[bool] = None  # True if the aspect is exact

    def __str__(self) -> str:
        """Get a string representation of the aspect.

        Returns:
            String representation
        """
        return (
            f"{self.planet1} {self.aspect_type} {self.planet2} (Orb: {self.orb:.2f}°)"
        )


class AspectPattern(BaseModel):
    """Class representing a pattern of aspects between planets."""

    name: str  # E.g., Grand Trine, T-Square, Yod
    aspects: List[Aspect]  # The aspects forming this pattern
    planets: List[str]  # The planets involved in this pattern
    
    # Additional properties
    description: Optional[str] = None  # Description of what this pattern means
    power: Optional[float] = None  # Strength/potency of the pattern (0-10)
    keywords: List[str] = Field(default_factory=list)
    
    def __str__(self) -> str:
        """Get a string representation of the aspect pattern.

        Returns:
            String representation
        """
        planet_str = ", ".join(self.planets)
        return f"{self.name} involving {planet_str}"
