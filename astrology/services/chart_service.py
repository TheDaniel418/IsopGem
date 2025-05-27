"""
Purpose: Provides services for astrological chart creation and calculations.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to create various types of astrological charts,
including natal, transit, and composite charts, and to perform calculations on them.

Key components:
- ChartService: Service for creating and managing astrological charts
- calculate_aspects: Function to calculate aspects between planets
- identify_aspect_patterns: Function to identify aspect patterns

Dependencies:
- astrology.models: For chart and aspect data models
- astrology.services.kerykeion_service: For accessing Kerykeion library
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from loguru import logger

from astrology.models.aspect import Aspect, AspectPattern
from astrology.models.chart import (
    Chart,
    ChartType,
    CompositeChart,
    NatalChart,
    TransitChart,
)
from astrology.models.zodiac import HouseSystem
from astrology.services.kerykeion_service import KerykeionService

T = TypeVar("T", bound="ChartService[Any]")


class ChartService(Generic[T]):
    """Service for creating and managing astrological charts."""

    # Singleton instance
    _instance: Optional[T] = None
    kerykeion_service: KerykeionService

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        """Get the singleton instance of the service.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cast(T, cls._instance)

    def __init__(self) -> None:
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
        perspective_type: str = "Apparent Geocentric",
        timezone_str: Optional[str] = None,
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
            timezone_str: Timezone string (e.g., 'UTC', 'America/New_York')

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
            HouseSystem.ALCABITIUS: "B",
        }
        house_system_code = house_system_codes.get(
            house_system, "P"
        )  # Default to Placidus

        # Get the timezone string if not provided
        if not timezone_str:
            try:
                import tzlocal
                timezone_str = str(tzlocal.get_localzone())
                logger.debug(f"Using local timezone {timezone_str} for chart creation")
            except Exception as e:
                timezone_str = "UTC"
                logger.warning(f"Error getting local timezone, using UTC: {e}")
        else:
            logger.debug(f"Using provided timezone {timezone_str} for chart creation")

        # Use kerykeion service to create the chart
        chart = self.kerykeion_service.create_natal_chart(
            name=name,
            birth_date=birth_date,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            house_system=house_system_code,
            perspective_type=perspective_type,
        )

        # Convert Chart to NatalChart
        natal_chart = cast(NatalChart, chart)

        # Only set birth_time_known if the chart is indeed a NatalChart
        if isinstance(chart, NatalChart):
            natal_chart.birth_time_known = birth_time_known
        elif not hasattr(chart, "birth_time_known"):
            # If it's just a base Chart, convert it to a NatalChart
            natal_chart = NatalChart(
                name=chart.name,
                type=ChartType.NATAL,
                date=chart.date,
                kerykeion_subject=chart.kerykeion_subject,
                latitude=chart.latitude,
                longitude=chart.longitude,
                location_name=chart.location_name,
                planets=chart.planets,
                houses=chart.houses,
                aspects=chart.aspects,
                house_system=chart.house_system,
                birth_date=birth_date,
                birth_time_known=birth_time_known,
            )

        # Add location name and house system explicitly
        natal_chart.location_name = location_name
        natal_chart.house_system = house_system
        
        # Explicitly set the timezone on the chart
        natal_chart.timezone = timezone_str

        logger.debug(f"Created natal chart for {name} using kerykeion")
        return natal_chart

    def create_transit_chart(
        self,
        name: str,
        date: datetime,
        reference_chart: Chart,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
        timezone_str: Optional[str] = None,
    ) -> TransitChart:
        """Create a transit chart.

        Args:
            name: Name of the chart
            date: Date and time for the transit
            reference_chart: Reference chart (usually a natal chart)
            latitude: Latitude for the transit (defaults to reference chart)
            longitude: Longitude for the transit (defaults to reference chart)
            location_name: Name of the location (defaults to reference chart)
            timezone_str: Timezone string (e.g., 'UTC', 'America/New_York')

        Returns:
            The created transit chart
        """
        # Use reference chart location if not provided
        chart_latitude = latitude if latitude is not None else reference_chart.latitude
        chart_longitude = (
            longitude if longitude is not None else reference_chart.longitude
        )
        chart_location = (
            location_name
            if location_name is not None
            else reference_chart.location_name
        )

        if chart_latitude is None or chart_longitude is None:
            raise ValueError(
                "No valid latitude/longitude available from reference chart"
            )

        # Create the chart
        chart = TransitChart(
            name=name,
            date=date,
            latitude=chart_latitude,
            longitude=chart_longitude,
            location_name=chart_location,
            house_system=reference_chart.house_system,
            reference_chart=reference_chart,
        )

        # Get the timezone string if not provided
        if not timezone_str:
            try:
                import tzlocal
                timezone_str = str(tzlocal.get_localzone())
                logger.debug(f"Using local timezone {timezone_str} for transit chart creation")
            except Exception as e:
                timezone_str = "UTC"
                logger.warning(f"Error getting local timezone for transit chart, using UTC: {e}")
        else:
            logger.debug(f"Using provided timezone {timezone_str} for transit chart creation")

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
            HouseSystem.ALCABITIUS: "B",
        }
        house_system_code = house_system_codes.get(
            reference_chart.house_system, "P"
        )  # Default to Placidus

        # Create a temporary chart for the transit date
        transit_data = self.kerykeion_service.create_natal_chart(
            name=name,
            birth_date=date,
            latitude=chart_latitude,
            longitude=chart_longitude,
            timezone_str=timezone_str,
            house_system=house_system_code,
        )

        # Copy the planets from the transit chart to our chart
        chart.planets = transit_data.planets

        # Use houses from reference chart
        chart.houses = reference_chart.houses

        return chart

    def create_composite_chart(
        self, name: str, chart1: Chart, chart2: Chart, midpoint_method: bool = True
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
        midpoint_date = date1 + timedelta(days=days_diff)

        # Calculate midpoint location (simplified)
        latitude = (
            (chart1.latitude + chart2.latitude) / 2
            if chart1.latitude and chart2.latitude
            else None
        )
        longitude = (
            (chart1.longitude + chart2.longitude) / 2
            if chart1.longitude and chart2.longitude
            else None
        )

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
            midpoint_method=midpoint_method,
        )

        # Note: Composite charts are not directly supported by kerykeion
        # We'll need to implement custom logic for this in the future
        logger.warning("Composite charts are not fully implemented with kerykeion yet")

        return chart

    def calculate_aspects(
        self,
        chart: Chart,
        major_only: bool = False,
        custom_orbs: Optional[Dict[str, float]] = None,
    ) -> List[Aspect]:
        """Calculate aspects in a chart.

        Args:
            chart: The chart to calculate aspects for
            major_only: Whether to only calculate major aspects
            custom_orbs: Custom orbs for aspects

        Returns:
            List of aspects
        """
        # Convert zodiac.Aspect objects to aspect.Aspect objects
        raw_aspects = chart.aspects if hasattr(chart, "aspects") else []
        converted_aspects: List[Aspect] = []

        for raw_aspect in raw_aspects:
            # Create Aspect object with required fields
            aspect = Aspect(
                body1=raw_aspect.planet1,
                body2=raw_aspect.planet2,
                aspect_type=raw_aspect.aspect_type,
                angle=raw_aspect.angle,
                orb=raw_aspect.orb,
                exact_angle=raw_aspect.angle,
                applying=False,  # Default value since Kerykeion doesn't provide this
            )
            converted_aspects.append(aspect)

        return converted_aspects

    def identify_aspect_patterns(
        self, chart: Chart, aspects: List[Aspect]
    ) -> List[AspectPattern]:
        """Identify aspect patterns in a chart.

        Args:
            chart: The chart to identify patterns in
            aspects: List of aspects in the chart

        Returns:
            List of aspect patterns
        """
        # Aspect pattern identification is not implemented yet
        logger.warning(
            "Aspect pattern identification is not implemented with kerykeion yet"
        )
        return []
