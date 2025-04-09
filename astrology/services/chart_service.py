"""
Purpose: Creates and manages astrological charts.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to create and manage different types of astrological
charts, including natal charts, transit charts, and composite charts.

Key components:
- ChartService: Service for creating and managing astrological charts

Dependencies:
- Python typing: For type hint annotations
- datetime: For date and time handling
- astrology.models: For astrological data models
- astrology.services: For other astrological services
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from loguru import logger

from astrology.models.chart import Chart, NatalChart, TransitChart, CompositeChart, ChartType
from astrology.models.celestial_body import CelestialBody
from astrology.models.zodiac import House, HouseSystem
from astrology.services.kerykeion_service import KerykeionService


class ChartService:
    """Service for creating and managing astrological charts."""

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the chart service."""
        # Create kerykeion service
        self.kerykeion_service = KerykeionService()

        logger.debug("ChartService initialized")

    def create_natal_chart(
        self,
        name: str,
        birth_date: datetime,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        house_system: HouseSystem = HouseSystem.PLACIDUS,
        birth_time_known: bool = True,
        perspective_type: str = "Apparent Geocentric"
    ) -> NatalChart:
        """Create a natal chart.

        Args:
            name: Name of the chart
            birth_date: Date and time of birth
            latitude: Latitude of birth location
            longitude: Longitude of birth location
            location_name: Name of birth location
            house_system: House system to use
            birth_time_known: Whether the birth time is known
            perspective_type: Perspective type to use

        Returns:
            The created natal chart
        """
        # Map house system to kerykeion code
        house_system_codes = {
            HouseSystem.PLACIDUS: "P",
            HouseSystem.KOCH: "K",
            HouseSystem.EQUAL: "E",
            HouseSystem.WHOLE_SIGN: "W",
            HouseSystem.REGIOMONTANUS: "R",
            HouseSystem.CAMPANUS: "C",
            HouseSystem.TOPOCENTRIC: "T",
            HouseSystem.MORINUS: "M",
            HouseSystem.PORPHYRY: "O",
            HouseSystem.ALCABITIUS: "B"
        }
        house_system_code = house_system_codes.get(house_system, "P")  # Default to Placidus

        # Get the timezone string
        try:
            import tzlocal
            timezone_str = str(tzlocal.get_localzone())
        except Exception:
            timezone_str = "UTC"

        # Use kerykeion service to create the chart
        chart = self.kerykeion_service.create_natal_chart(
            name=name,
            birth_date=birth_date,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            house_system=house_system_code,
            perspective_type=perspective_type
        )

        # Add additional information to the chart
        chart.location_name = location_name
        chart.house_system = house_system

        logger.debug(f"Created natal chart for {name} using kerykeion")

        return chart

    def create_transit_chart(
        self,
        name: str,
        date: datetime,
        reference_chart: Chart,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None
    ) -> TransitChart:
        """Create a transit chart.

        Args:
            name: Name of the chart
            date: Date and time for the transit
            reference_chart: Reference chart (usually a natal chart)
            latitude: Latitude for the transit (defaults to reference chart)
            longitude: Longitude for the transit (defaults to reference chart)
            location_name: Name of the location (defaults to reference chart)

        Returns:
            The created transit chart
        """
        # Use reference chart location if not provided
        if latitude is None:
            latitude = reference_chart.latitude
        if longitude is None:
            longitude = reference_chart.longitude
        if location_name is None:
            location_name = reference_chart.location_name

        # Create the chart
        chart = TransitChart(
            name=name,
            date=date,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            house_system=reference_chart.house_system,
            reference_chart=reference_chart
        )

        # Use kerykeion service to create a new chart for the transit date
        # Get the timezone string
        try:
            import tzlocal
            timezone_str = str(tzlocal.get_localzone())
        except Exception:
            timezone_str = "UTC"

        # Map house system to kerykeion code
        house_system_codes = {
            HouseSystem.PLACIDUS: "P",
            HouseSystem.KOCH: "K",
            HouseSystem.EQUAL: "E",
            HouseSystem.WHOLE_SIGN: "W",
            HouseSystem.REGIOMONTANUS: "R",
            HouseSystem.CAMPANUS: "C",
            HouseSystem.TOPOCENTRIC: "T",
            HouseSystem.MORINUS: "M",
            HouseSystem.PORPHYRY: "O",
            HouseSystem.ALCABITIUS: "B"
        }
        house_system_code = house_system_codes.get(reference_chart.house_system, "P")  # Default to Placidus

        # Create a temporary chart for the transit date
        transit_data = self.kerykeion_service.create_natal_chart(
            name=name,
            birth_date=date,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            house_system=house_system_code
        )

        # Copy the planets from the transit chart to our chart
        chart.planets = transit_data.planets

        # Use houses from reference chart
        chart.houses = reference_chart.houses

        return chart

    def create_composite_chart(
        self,
        name: str,
        chart1: Chart,
        chart2: Chart,
        midpoint_method: bool = True
    ) -> CompositeChart:
        """Create a composite chart for a relationship.

        Args:
            name: Name of the chart
            chart1: First chart
            chart2: Second chart
            midpoint_method: Whether to use the midpoint method

        Returns:
            The created composite chart
        """
        # Calculate midpoint date (simplified)
        date1 = chart1.date
        date2 = chart2.date
        days_diff = (date2 - date1).days / 2
        midpoint_date = date1 + datetime.timedelta(days=days_diff)

        # Calculate midpoint location (simplified)
        latitude = (chart1.latitude + chart2.latitude) / 2 if chart1.latitude and chart2.latitude else None
        longitude = (chart1.longitude + chart2.longitude) / 2 if chart1.longitude and chart2.longitude else None

        # Create the chart
        chart = CompositeChart(
            name=name,
            date=midpoint_date,
            latitude=latitude,
            longitude=longitude,
            location_name=f"Composite: {chart1.location_name} & {chart2.location_name}",
            house_system=chart1.house_system,
            chart1=chart1,
            chart2=chart2,
            midpoint_method=midpoint_method
        )

        # Note: Composite charts are not directly supported by kerykeion
        # We'll need to implement custom logic for this in the future
        logger.warning("Composite charts are not fully implemented with kerykeion yet")

        return chart

    def calculate_aspects(
        self,
        chart: Chart,
        major_only: bool = False,
        custom_orbs: Optional[Dict[str, float]] = None
    ) -> List:
        """Calculate aspects in a chart.

        Args:
            chart: The chart to calculate aspects for
            major_only: Whether to only calculate major aspects
            custom_orbs: Custom orbs for aspects

        Returns:
            List of aspects
        """
        # Kerykeion calculates aspects automatically
        # We just need to return the aspects from the chart
        return chart.aspects if hasattr(chart, 'aspects') else []

    def identify_aspect_patterns(self, chart: Chart, aspects: List) -> List:
        """Identify aspect patterns in a chart.

        Args:
            chart: The chart to identify patterns in
            aspects: List of aspects in the chart

        Returns:
            List of aspect patterns
        """
        # Aspect pattern identification is not supported by kerykeion
        # This would need to be implemented separately
        logger.warning("Aspect pattern identification is not implemented with kerykeion yet")
        return []
