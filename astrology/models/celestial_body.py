"""
Purpose: Defines celestial body models for astrological calculations.

This file is part of the astrology pillar and serves as a data model.
It provides classes for representing planets, asteroids, and fixed stars
with their properties and positions.

Key components:
- CelestialBodyType: Enum for different types of celestial bodies
- CelestialBody: Base class for all celestial bodies
- Planet: Class representing planets and luminaries (Sun, Moon)
- Asteroid: Class representing asteroids
- FixedStar: Class representing fixed stars

Dependencies:
- Python typing: For type hint annotations
- Pydantic: For data validation
- Enum: For enumeration types
"""

from enum import Enum, auto
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CelestialBodyType(Enum):
    """Types of celestial bodies used in astrological calculations."""
    
    # Major bodies
    SUN = auto()
    MOON = auto()
    MERCURY = auto()
    VENUS = auto()
    MARS = auto()
    JUPITER = auto()
    SATURN = auto()
    
    # Modern planets
    URANUS = auto()
    NEPTUNE = auto()
    PLUTO = auto()
    
    # Asteroids
    CERES = auto()
    PALLAS = auto()
    JUNO = auto()
    VESTA = auto()
    CHIRON = auto()
    
    # Mathematical points
    NORTH_NODE = auto()
    SOUTH_NODE = auto()
    
    # Fixed star
    FIXED_STAR = auto()
    
    # Other
    CUSTOM = auto()


class CelestialBody(BaseModel):
    """Base class for all celestial bodies."""
    
    name: str
    type: CelestialBodyType
    glyph: str
    longitude: Optional[float] = None  # Position in zodiac (0-360 degrees)
    latitude: Optional[float] = None   # Position above/below ecliptic
    speed: Optional[float] = None      # Daily motion in degrees
    
    # Optional properties
    retrograde: bool = False
    house: Optional[int] = None
    sign: Optional[str] = None
    sign_longitude: Optional[float] = None  # Position within sign (0-30 degrees)
    
    # Additional properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def is_in_sign(self, sign_name: str) -> bool:
        """Check if the celestial body is in a specific zodiac sign.
        
        Args:
            sign_name: Name of the zodiac sign to check
            
        Returns:
            True if the body is in the specified sign, False otherwise
        """
        return self.sign == sign_name
    
    def is_retrograde(self) -> bool:
        """Check if the celestial body is in retrograde motion.
        
        Returns:
            True if the body is retrograde, False otherwise
        """
        return self.retrograde
    
    def is_in_house(self, house_number: int) -> bool:
        """Check if the celestial body is in a specific house.
        
        Args:
            house_number: House number to check (1-12)
            
        Returns:
            True if the body is in the specified house, False otherwise
        """
        return self.house == house_number


class Planet(CelestialBody):
    """Class representing planets and luminaries (Sun, Moon)."""
    
    # Planet-specific properties
    ruling_sign: List[str] = Field(default_factory=list)
    exaltation_sign: Optional[str] = None
    fall_sign: Optional[str] = None
    detriment_sign: List[str] = Field(default_factory=list)
    
    # Planetary characteristics
    element: Optional[str] = None
    modality: Optional[str] = None
    polarity: Optional[str] = None
    
    # Dignities and debilities
    dignity: Optional[str] = None
    
    def is_luminary(self) -> bool:
        """Check if the planet is a luminary (Sun or Moon).
        
        Returns:
            True if the planet is the Sun or Moon, False otherwise
        """
        return self.type in [CelestialBodyType.SUN, CelestialBodyType.MOON]
    
    def is_personal_planet(self) -> bool:
        """Check if the planet is a personal planet.
        
        Personal planets are Mercury, Venus, and Mars.
        
        Returns:
            True if the planet is a personal planet, False otherwise
        """
        return self.type in [
            CelestialBodyType.MERCURY,
            CelestialBodyType.VENUS,
            CelestialBodyType.MARS
        ]
    
    def is_social_planet(self) -> bool:
        """Check if the planet is a social planet.
        
        Social planets are Jupiter and Saturn.
        
        Returns:
            True if the planet is a social planet, False otherwise
        """
        return self.type in [CelestialBodyType.JUPITER, CelestialBodyType.SATURN]
    
    def is_transpersonal_planet(self) -> bool:
        """Check if the planet is a transpersonal planet.
        
        Transpersonal planets are Uranus, Neptune, and Pluto.
        
        Returns:
            True if the planet is a transpersonal planet, False otherwise
        """
        return self.type in [
            CelestialBodyType.URANUS,
            CelestialBodyType.NEPTUNE,
            CelestialBodyType.PLUTO
        ]


class Asteroid(CelestialBody):
    """Class representing asteroids used in astrological calculations."""
    
    # Asteroid-specific properties
    orbital_period: Optional[float] = None  # In years
    diameter: Optional[float] = None        # In kilometers
    discovery_date: Optional[str] = None
    
    # Astrological significance
    keywords: List[str] = Field(default_factory=list)
    mythology: Optional[str] = None


class FixedStar(CelestialBody):
    """Class representing fixed stars used in astrological calculations."""
    
    # Star-specific properties
    constellation: Optional[str] = None
    magnitude: Optional[float] = None  # Brightness
    right_ascension: Optional[float] = None
    declination: Optional[float] = None
    
    # Astrological significance
    nature: List[str] = Field(default_factory=list)  # Planetary nature (e.g., "Mars-Saturn")
    influence: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
