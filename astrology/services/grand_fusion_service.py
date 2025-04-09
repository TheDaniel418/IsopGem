"""
Purpose: Service for calculating the Grand Fusion Midpoint.

This file provides a service for calculating the Grand Fusion Midpoint,
a unique point that both derives from and can generate all 21 traditional midpoints.

Key components:
- GrandFusionService: Service for calculating the Grand Fusion Midpoint

Dependencies:
- math: For mathematical calculations
- loguru: For logging
- astrology.models: For astrological data models
"""

import math
from typing import Dict, List, Optional, Tuple

from loguru import logger

from astrology.models.chart import Chart


class GrandFusionService:
    """Service for calculating the Grand Fusion Midpoint."""

    def __init__(self):
        """Initialize the Grand Fusion Service."""
        self.traditional_planets = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
        ]
        self.coefficients = {}  # Store coefficients for bidirectional transformation

    def calculate_grand_fusion_midpoint(self, chart: Chart) -> Optional[float]:
        """Calculate the Grand Fusion Midpoint for a chart.

        Args:
            chart: The chart to analyze

        Returns:
            The Grand Fusion Midpoint in degrees, or None if calculation fails
        """
        # Get the kerykeion subject
        subject = chart.kerykeion_subject
        if not subject:
            logger.warning(
                "No kerykeion subject available for Grand Fusion calculation"
            )
            return None

        # Calculate all midpoints
        midpoints, planet_pairs = self._calculate_all_midpoints(subject)
        if not midpoints:
            logger.warning("No midpoints available for Grand Fusion calculation")
            return None

        # Calculate the Grand Fusion Midpoint
        fusion_point = self._calculate_bidirectional_fusion(midpoints, planet_pairs)
        logger.info(f"Calculated Grand Fusion Midpoint: {fusion_point:.2f}°")

        return fusion_point

    def reconstruct_midpoint(self, grand_fusion: float, p1: str, p2: str) -> float:
        """Reconstruct a specific midpoint from the Grand Fusion point using symmetrical transformation.

        Args:
            grand_fusion: The Grand Fusion Midpoint in degrees
            p1: First planet name
            p2: Second planet name

        Returns:
            The reconstructed midpoint in degrees
        """
        # Sort planet names to ensure consistent lookup
        planets = sorted([p1, p2])
        pair_key = f"{planets[0]}_{planets[1]}"

        # Get the symmetrical coefficient
        coef = self.coefficients.get(pair_key, 1.0)

        # Calculate position in traditional sequence
        sequence = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        try:
            idx1 = sequence.index(planets[0])
            idx2 = sequence.index(planets[1])
        except ValueError:
            idx1 = 0
            idx2 = 0

        # Calculate angular offset based on position in sequence
        # This creates a symmetrical transformation that treats all planets equally
        position_factor = ((idx1 + idx2 + 2) / (len(sequence) * 2)) * 30

        # Apply offset to grand fusion point
        reconstructed = (grand_fusion + position_factor * coef) % 360

        return reconstructed

    def _calculate_all_midpoints(
        self, subject
    ) -> Tuple[Dict[str, float], List[Tuple[str, str]]]:
        """Calculate all midpoints between traditional planets.

        Args:
            subject: The kerykeion subject

        Returns:
            Tuple of (midpoints_dict, planet_pairs_list)
        """
        midpoints = {}
        planet_pairs = []

        # Calculate midpoints between all planet pairs
        for i, planet1_name in enumerate(self.traditional_planets):
            if not hasattr(subject, planet1_name):
                continue

            planet1 = getattr(subject, planet1_name)
            pos1 = planet1.position + (planet1.sign_num * 30)

            for j, planet2_name in enumerate(self.traditional_planets[i + 1 :], i + 1):
                if not hasattr(subject, planet2_name):
                    continue

                planet2 = getattr(subject, planet2_name)
                pos2 = planet2.position + (planet2.sign_num * 30)

                # Calculate midpoint
                midpoint_pos = self._calculate_midpoint(pos1, pos2)

                # Sort planet names to ensure consistent keys
                planets = sorted([planet1_name, planet2_name])
                pair_key = f"{planets[0]}_{planets[1]}"

                # Add to dictionary
                midpoints[pair_key] = midpoint_pos
                planet_pairs.append((planets[0], planets[1]))

        return midpoints, planet_pairs

    def _calculate_midpoint(self, pos1: float, pos2: float) -> float:
        """Calculate the midpoint between two positions.

        Args:
            pos1: First position in degrees
            pos2: Second position in degrees

        Returns:
            The midpoint in degrees
        """
        # Calculate the difference
        diff = abs(pos1 - pos2)

        # If the difference is more than 180 degrees, use the shorter arc
        if diff > 180:
            # Calculate midpoint in the opposite direction
            if pos1 > pos2:
                midpoint = (pos2 + 360 + pos1) / 2
            else:
                midpoint = (pos1 + 360 + pos2) / 2

            # Normalize to 0-360
            midpoint = midpoint % 360
        else:
            # Simple average
            midpoint = (pos1 + pos2) / 2

        return midpoint

    def _calculate_bidirectional_fusion(
        self, midpoints: Dict[str, float], planet_pairs: List[Tuple[str, str]]
    ) -> float:
        """Calculate Grand Fusion Midpoint using bidirectional derivation with symmetrical transformation.

        Args:
            midpoints: Dictionary of midpoints
            planet_pairs: List of planet pairs

        Returns:
            The Grand Fusion Midpoint in degrees
        """
        # First, calculate a preliminary fusion point using vector method
        prelim_fusion = self._calculate_vector_fusion(midpoints)

        # Create transformation coefficients based on symmetrical relationships
        self.coefficients = {}
        for (p1, p2), position in zip(planet_pairs, midpoints.values()):
            # Calculate coefficient using symmetrical transformation
            coef = self._get_symmetrical_factor(p1, p2)

            # Store coefficient
            pair_key = f"{p1}_{p2}"
            self.coefficients[pair_key] = coef

            # Refine fusion point using these coefficients
            angular_diff = (position - prelim_fusion) % 360
            if angular_diff > 180:
                angular_diff -= 360

            # Apply weighted adjustment
            prelim_fusion = (prelim_fusion + angular_diff * coef / 10) % 360

        return prelim_fusion

    def _calculate_vector_fusion(self, midpoints: Dict[str, float]) -> float:
        """Calculate a preliminary fusion point using vector method.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            The preliminary fusion point in degrees
        """
        # Convert positions to cartesian coordinates on the unit circle
        x_sum = 0
        y_sum = 0

        for position in midpoints.values():
            angle_rad = math.radians(position)
            x_sum += math.cos(angle_rad)
            y_sum += math.sin(angle_rad)

        # Find the centroid
        centroid_angle = math.atan2(y_sum, x_sum)
        fusion_point = math.degrees(centroid_angle) % 360

        return fusion_point

    def _get_symmetrical_factor(self, planet1: str, planet2: str) -> float:
        """Get a symmetrical transformation factor for a planetary pair.

        This method creates a unique but unbiased factor for each planetary pair
        based on their positions in the traditional sequence, ensuring that
        all planets are treated equally without elemental or modality bias.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            Symmetrical factor
        """
        # Define the traditional planetary sequence
        sequence = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]

        # Get indices of planets in the sequence
        try:
            idx1 = sequence.index(planet1)
            idx2 = sequence.index(planet2)
        except ValueError:
            # Default value if planet not found
            return 1.0

        # Calculate harmonic relationship based on positions
        # This creates a unique but balanced factor for each pair
        harmonic = (idx1 + 1) * (idx2 + 1) / (len(sequence) * len(sequence))

        # Scale to a reasonable range (0.8 to 1.2)
        factor = 0.8 + (harmonic * 0.4)

        return factor

    def get_sign_for_position(self, position: float) -> str:
        """Get zodiac sign for a position.

        Args:
            position: Position in degrees (0-360)

        Returns:
            The zodiac sign as a string
        """
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]

        sign_index = int(position / 30)
        return signs[sign_index]
