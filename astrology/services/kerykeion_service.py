"""
Purpose: Provides a service for astrological calculations using the kerykeion library.

This file is part of the astrology pillar and serves as a service component.
It provides a service for calculating planetary positions, houses, and aspects
using the kerykeion library.

Key components:
- KerykeionService: Service for astrological calculations

Dependencies:
- kerykeion: For astrological calculations
"""

import os
import webbrowser
from datetime import datetime
from typing import List, Optional

from kerykeion import AstrologicalSubject
from kerykeion.aspects import NatalAspects
from kerykeion.charts.kerykeion_chart_svg import KerykeionChartSVG
from loguru import logger

from astrology.models.chart import Chart
from astrology.models.zodiac import Aspect, House, Planet


class KerykeionService:
    """Service for astrological calculations using the kerykeion library."""

    def __init__(self):
        """Initialize the kerykeion service."""
        logger.debug("KerykeionService initialized")
        
        # Configure SwissEphemeris path
        try:
            import swisseph as swe
            import sys
            import os
            
            # Try to find the path of the swisseph ephemeris files
            # First check if they're in the kerykeion package
            kerykeion_path = None
            for path in sys.path:
                possible_path = os.path.join(path, 'kerykeion', 'sweph')
                if os.path.exists(possible_path):
                    kerykeion_path = possible_path
                    break
            
            if kerykeion_path:
                logger.debug(f"Setting SwissEph path to: {kerykeion_path}")
                swe.set_ephe_path(kerykeion_path)
                
                # Verify if the files exist
                files_to_check = ['seas_12.se1', 'semo_12.se1', 'sepl_12.se1']
                missing_files = [f for f in files_to_check if not os.path.exists(os.path.join(kerykeion_path, f))]
                
                if missing_files:
                    logger.warning(f"Missing SwissEph files in {kerykeion_path}: {', '.join(missing_files)}")
                    
                    # Try to find them in the current directory
                    current_dir_path = os.path.abspath(os.path.dirname(__file__))
                    project_root = os.path.abspath(os.path.join(current_dir_path, '..', '..'))
                    sweph_dirs = [
                        os.path.join(project_root, 'sweph'),
                        os.path.join(project_root, 'data', 'sweph'),
                        os.path.join(project_root, 'assets', 'sweph')
                    ]
                    
                    for sweph_dir in sweph_dirs:
                        if os.path.exists(sweph_dir) and any(os.path.exists(os.path.join(sweph_dir, f)) for f in files_to_check):
                            logger.debug(f"Found alternative SwissEph path: {sweph_dir}")
                            swe.set_ephe_path(sweph_dir)
                            break
                        
                    # If still not found, try to download them (in future implementation)
                    logger.warning("Consider downloading Swiss Ephemeris files if chart generation fails")
            else:
                logger.warning("Could not find kerykeion sweph path. Chart generation might fail.")
        except Exception as e:
            logger.error(f"Error configuring SwissEph path: {e}", exc_info=True)

    def create_natal_chart(
        self,
        name: str,
        birth_date: datetime,
        latitude: float,
        longitude: float,
        timezone_str: str,
        house_system: str = "P",
        perspective_type: str = "Apparent Geocentric",
    ) -> Chart:
        """Create a natal chart for the given parameters.

        Args:
            name: Name of the person
            birth_date: Birth date and time
            latitude: Latitude of the birth location
            longitude: Longitude of the birth location
            timezone_str: Timezone string (e.g., 'America/New_York')
            house_system: House system to use (default: "P" for Placidus)
            perspective_type: Perspective type to use (default: "Apparent Geocentric")

        Returns:
            A Chart object containing the calculated data
        """
        logger.debug(
            f"Creating natal chart for {name} with perspective {perspective_type}"
        )

        # Create a kerykeion subject
        subject = AstrologicalSubject(
            name=name,
            year=birth_date.year,
            month=birth_date.month,
            day=birth_date.day,
            hour=birth_date.hour,
            minute=birth_date.minute,
            city="Custom",  # We're providing coordinates directly
            nation="",
            lat=latitude,
            lng=longitude,
            tz_str=timezone_str,
            houses_system_identifier=house_system,
            perspective_type=perspective_type,
        )

        # Calculate aspects
        aspects = NatalAspects(subject)

        # Create a chart object
        from astrology.models.chart import ChartType

        chart = Chart(
            name=name,
            type=ChartType.NATAL,  # Set the chart type
            date=birth_date,  # Set the date field
            birth_date=birth_date,  # Also set the birth_date field
            latitude=latitude,
            longitude=longitude,
            timezone=timezone_str,
            kerykeion_subject=subject,  # Store the kerykeion subject directly
        )

        # Add planets to the chart
        chart.planets = self._extract_planets(subject)

        # Add houses to the chart
        chart.houses = self._extract_houses(subject)

        # Add aspects to the chart
        chart.aspects = self._extract_aspects(aspects)

        # Assign planets to houses
        self._assign_planets_to_houses(chart)

        logger.debug(f"Natal chart created for {name}")
        return chart

    def generate_chart_svg(
        self,
        chart: Chart,
        output_path: Optional[str] = None,
        open_in_browser: bool = False,
    ) -> str:
        """Generate an SVG chart for the given chart data.

        Args:
            chart: The chart data
            output_path: Path to save the SVG file (optional)
            open_in_browser: Whether to open the chart in the browser (default: False)

        Returns:
            Path to the generated SVG file
        """
        try:
            # Make sure we have a timezone string
            timezone_str = chart.timezone if hasattr(chart, 'timezone') and chart.timezone else 'UTC'
            logger.debug(f"Using timezone: {timezone_str} for chart generation")
            
            # Create a kerykeion subject from the chart data
            subject = AstrologicalSubject(
                name=chart.name,
                year=chart.birth_date.year,
                month=chart.birth_date.month,
                day=chart.birth_date.day,
                hour=chart.birth_date.hour,
                minute=chart.birth_date.minute,
                city="Custom",  # We're providing coordinates directly
                nation="",
                lat=chart.latitude,
                lng=chart.longitude,
                tz_str=timezone_str,
            )

            # Create the chart
            kerykeion_chart = KerykeionChartSVG(subject)

            # Generate the SVG - this saves to a default location in /home/daniel
            logger.debug(f"Generating SVG for {chart.name}...")
            kerykeion_chart.makeSVG()

            # Default path where Kerykeion saves the chart
            svg_path = f"/home/daniel/{subject.name} - Natal Chart.svg"
            
            if os.path.exists(svg_path):
                logger.debug(f"SVG Generated Correctly in: {svg_path}")
            else:
                logger.warning(f"Expected SVG file not found at {svg_path}")
                # Try to find the file with a glob pattern
                import glob
                possible_files = glob.glob(f"/home/daniel/*Natal Chart.svg")
                if possible_files:
                    svg_path = possible_files[0]
                    logger.debug(f"Found alternative SVG at: {svg_path}")

            # If the chart exists and we want a different location, move it
            if output_path and os.path.exists(svg_path) and output_path != svg_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                os.rename(svg_path, output_path)
                logger.debug(f"Moved chart from {svg_path} to {output_path}")
                svg_path = output_path

            # Open in browser if requested
            if open_in_browser and os.path.exists(svg_path):
                file_url = f"file://{os.path.abspath(svg_path)}"
                logger.debug(f"Opening chart in browser: {file_url}")
                webbrowser.open(file_url)
            elif open_in_browser:
                logger.error(f"Cannot open chart in browser - file not found at {svg_path}")

            return svg_path if os.path.exists(svg_path) else ""

        except Exception as e:
            logger.error(f"Error generating chart SVG: {e}", exc_info=True)
            return ""

    def _extract_planets(self, subject: AstrologicalSubject) -> List[Planet]:
        """Extract planet data from a kerykeion subject.

        Args:
            subject: The kerykeion subject

        Returns:
            A list of Planet objects
        """
        planets = []

        # Map kerykeion planet names to our planet names
        planet_name_map = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mercury",
            "Venus": "Venus",
            "Mars": "Mars",
            "Jupiter": "Jupiter",
            "Saturn": "Saturn",
            "Uranus": "Uranus",
            "Neptune": "Neptune",
            "Pluto": "Pluto",
        }

        # Extract planet data
        for kerykeion_name, our_name in planet_name_map.items():
            if kerykeion_name.lower() in dir(subject):
                kerykeion_planet = getattr(subject, kerykeion_name.lower())

                planet = Planet(
                    name=our_name,
                    sign=kerykeion_planet.sign,
                    degree=kerykeion_planet.position,
                    retrograde=kerykeion_planet.retrograde,
                    house=kerykeion_planet.house.replace("_House", ""),
                )

                planets.append(planet)

        return planets

    def _extract_houses(self, subject: AstrologicalSubject) -> List[House]:
        """Extract house data from a kerykeion subject.

        Args:
            subject: The kerykeion subject

        Returns:
            A list of House objects
        """
        houses = []

        # Extract house data directly from kerykeion's house attributes
        logger.debug(f"Extracting houses from kerykeion subject: {subject.name}")

        # Kerykeion uses lowercase attributes like first_house, second_house, etc.
        house_names = [
            "first_house",
            "second_house",
            "third_house",
            "fourth_house",
            "fifth_house",
            "sixth_house",
            "seventh_house",
            "eighth_house",
            "ninth_house",
            "tenth_house",
            "eleventh_house",
            "twelfth_house",
        ]

        # Check if the subject has house attributes
        house_objects = []
        for i, house_name in enumerate(house_names, 1):
            if hasattr(subject, house_name):
                kerykeion_house = getattr(subject, house_name)
                logger.debug(
                    f"Found house {i} ({house_name}): {kerykeion_house.sign} at {kerykeion_house.position}°"
                )
                house_objects.append((i, kerykeion_house))
            else:
                logger.warning(
                    f"House {i} ({house_name}) not found in kerykeion subject"
                )

        # Create House objects
        if house_objects:
            for i in range(len(house_objects)):
                current_house = house_objects[i]
                next_house = house_objects[(i + 1) % len(house_objects)]

                house_num = current_house[0]
                kerykeion_house = current_house[1]
                next_kerykeion_house = next_house[1]

                # Create the House object
                house = House(
                    number=house_num,
                    sign=kerykeion_house.sign,
                    cusp_degree=kerykeion_house.position,
                    end_degree=next_kerykeion_house.position,
                )

                houses.append(house)
        else:
            logger.warning("No house attributes found in kerykeion subject")

        logger.debug(f"Extracted {len(houses)} houses from kerykeion subject")
        return houses

    def _extract_aspects(self, aspects: NatalAspects) -> List[Aspect]:
        """Extract aspect data from kerykeion aspects.

        Args:
            aspects: The kerykeion aspects

        Returns:
            A list of Aspect objects
        """
        result = []

        # Extract aspect data
        for kerykeion_aspect in aspects.all_aspects:
            aspect = Aspect(
                planet1=kerykeion_aspect.p1_name,
                planet2=kerykeion_aspect.p2_name,
                aspect_type=kerykeion_aspect.aspect,
                orb=kerykeion_aspect.orbit,
            )

            result.append(aspect)

        return result

    def _assign_planets_to_houses(self, chart: Chart) -> None:
        """Assign planets to houses in the chart.

        Args:
            chart: The chart to update
        """
        # Clear existing planet assignments
        for house in chart.houses:
            house.planets = []

        # Assign planets to houses
        logger.debug(
            f"Assigning {len(chart.planets)} planets to {len(chart.houses)} houses"
        )

        # Map from kerykeion house names to house numbers
        house_name_to_number = {
            # Capital format (used in planet.house)
            "First_House": 1,
            "Second_House": 2,
            "Third_House": 3,
            "Fourth_House": 4,
            "Fifth_House": 5,
            "Sixth_House": 6,
            "Seventh_House": 7,
            "Eighth_House": 8,
            "Ninth_House": 9,
            "Tenth_House": 10,
            "Eleventh_House": 11,
            "Twelfth_House": 12,
            # Lowercase format (used as attribute names)
            "first_house": 1,
            "second_house": 2,
            "third_house": 3,
            "fourth_house": 4,
            "fifth_house": 5,
            "sixth_house": 6,
            "seventh_house": 7,
            "eighth_house": 8,
            "ninth_house": 9,
            "tenth_house": 10,
            "eleventh_house": 11,
            "twelfth_house": 12,
        }

        for planet in chart.planets:
            # Find the house by number
            try:
                # Try to convert house to int, handling various formats
                if planet.house is None:
                    logger.warning(f"Planet {planet.name} has no house assignment")
                    continue

                # Handle different house formats from kerykeion
                house_number = None

                # Direct house number
                if isinstance(planet.house, int):
                    house_number = planet.house
                # String digit
                elif planet.house.isdigit():
                    house_number = int(planet.house)
                # Format like 'First_House'
                elif planet.house in house_name_to_number:
                    house_number = house_name_to_number[planet.house]
                # Format like 'house_1'
                elif "_" in planet.house and planet.house.split("_")[1].isdigit():
                    house_number = int(planet.house.split("_")[1])
                # Try to extract digits as last resort
                else:
                    import re

                    digits = re.findall(r"\d+", planet.house)
                    if digits:
                        house_number = int(digits[0])
                    else:
                        logger.warning(
                            f"Could not parse house number from {planet.house} for {planet.name}"
                        )
                        continue

                logger.debug(f"Assigning {planet.name} to house {house_number}")

                # Find the house with this number
                for house in chart.houses:
                    if house.number == house_number:
                        # Add the planet to the house
                        house.planets.append(planet.name)
                        logger.debug(f"Added {planet.name} to house {house.number}")
                        break
                else:
                    logger.warning(
                        f"House {house_number} not found for planet {planet.name}"
                    )
            except Exception as e:
                logger.error(f"Error assigning {planet.name} to house: {e}")
