"""
Purpose: Defines chart models for astrological calculations.

This file is part of the astrology pillar and serves as a data model.
It provides classes for representing different types of astrological charts
including natal charts, transit charts, and composite charts.

Key components:
- ChartType: Enum for different types of charts
- Chart: Base class for all chart types
- NatalChart: Class representing a birth chart
- TransitChart: Class representing a transit chart
- CompositeChart: Class representing a relationship chart

Dependencies:
- Python typing: For type hint annotations
- Pydantic: For data validation
- Enum: For enumeration types
- datetime: For date and time handling
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from astrology.models.zodiac import Aspect, House, HouseSystem, Planet

# Import kerykeion types for type hints
try:
    from kerykeion import AstrologicalSubject
except ImportError:
    # Define a placeholder for type hints if kerykeion is not available
    class AstrologicalSubject:
        pass


class ChartType(Enum):
    """Types of astrological charts."""

    NATAL = "Natal"
    TRANSIT = "Transit"
    PROGRESSED = "Progressed"
    SOLAR_RETURN = "Solar Return"
    LUNAR_RETURN = "Lunar Return"
    COMPOSITE = "Composite"
    SYNASTRY = "Synastry"
    HORARY = "Horary"
    ELECTIONAL = "Electional"
    MUNDANE = "Mundane"


class Chart(BaseModel):
    """Base class for all astrological charts."""

    # Configure the model to allow arbitrary types (like AstrologicalSubject)
    model_config = {"arbitrary_types_allowed": True}

    name: str
    type: ChartType
    date: datetime
    kerykeion_subject: Optional[AstrologicalSubject] = None

    # Location information
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None

    # Chart data
    planets: List[Planet] = Field(default_factory=list)
    houses: List[House] = Field(default_factory=list)
    aspects: List[Aspect] = Field(default_factory=list)
    house_system: HouseSystem = HouseSystem.PLACIDUS

    # Additional data
    birth_date: Optional[datetime] = None
    timezone: Optional[str] = None

    # Additional properties
    properties: Dict[str, Any] = Field(default_factory=dict)

    def add_planet(self, planet: Planet) -> None:
        """Add a planet to the chart.

        Args:
            planet: The planet to add
        """
        self.planets.append(planet)

    def get_planet(self, name: str) -> Optional[Planet]:
        """Get a planet by name.

        Args:
            name: Name of the planet

        Returns:
            The planet if found, None otherwise
        """
        for planet in self.planets:
            if planet.name == name:
                return planet
        return None

    def get_house(self, number: int) -> Optional[House]:
        """Get a house by number.

        Args:
            number: House number (1-12)

        Returns:
            The house if found, None otherwise
        """
        for house in self.houses:
            if house.number == number:
                return house
        return None

    def get_ascendant(self) -> Optional[float]:
        """Get the ascendant degree.

        Returns:
            The ascendant degree if available, None otherwise
        """
        first_house = self.get_house(1)
        return first_house.cusp_degree if first_house else None

    def get_midheaven(self) -> Optional[float]:
        """Get the midheaven degree.

        Returns:
            The midheaven degree if available, None otherwise
        """
        tenth_house = self.get_house(10)
        return tenth_house.cusp_degree if tenth_house else None


class NatalChart(Chart):
    """Class representing a birth chart."""

    # Birth information
    birth_time_known: bool = True
    birth_time_accuracy: Optional[str] = None

    # Rectification information
    rectified: bool = False
    rectification_method: Optional[str] = None

    def __init__(self, **data):
        """Initialize a natal chart."""
        # Set the chart type to NATAL
        data["type"] = ChartType.NATAL

        # Set the date field from birth_date if not provided
        if "birth_date" in data and "date" not in data:
            data["date"] = data["birth_date"]

        super().__init__(**data)


class TransitChart(Chart):
    """Class representing a transit chart."""

    # Reference chart (usually a natal chart)
    reference_chart: Optional[Chart] = None

    def __init__(self, **data):
        """Initialize a transit chart."""
        # Set the chart type to TRANSIT
        data["type"] = ChartType.TRANSIT
        super().__init__(**data)


class CompositeChart(Chart):
    """Class representing a composite chart for relationships."""

    # Component charts
    chart1: Optional[Chart] = None
    chart2: Optional[Chart] = None

    # Composite method
    midpoint_method: bool = True  # True for midpoint, False for time-space

    def __init__(self, **data):
        """Initialize a composite chart."""
        # Set the chart type to COMPOSITE
        data["type"] = ChartType.COMPOSITE
        super().__init__(**data)
