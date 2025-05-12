"""Golden Mean service module.

This module provides services for calculating Golden Mean ratios and relationships.
"""

import math
from typing import Dict, List, Tuple

from loguru import logger


class GoldenMeanService:
    """Service for calculating Golden Mean ratios and relationships."""

    _instance = None

    def __new__(cls):
        """Create a singleton instance of the service."""
        if cls._instance is None:
            cls._instance = super(GoldenMeanService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls()

    def _initialize(self) -> None:
        """Initialize the service."""
        # Calculate the value of Phi (Golden Mean)
        self.PHI = (1 + math.sqrt(5)) / 2
        self.PHI_INVERSE = 1 / self.PHI
        self.PHI_CONJUGATE = 1 - self.PHI_INVERSE  # Same as PHI - 1
        logger.debug(f"Golden Mean initialized with phi value: {self.PHI}")

    def get_phi(self) -> float:
        """Get the value of Phi.

        Returns:
            The value of Phi (≈ 1.618034...)
        """
        return self.PHI

    def get_phi_inverse(self) -> float:
        """Get the value of the inverse of Phi (1/Φ).

        Returns:
            The value of 1/Phi (≈ 0.618034...)
        """
        return self.PHI_INVERSE

    def get_phi_conjugate(self) -> float:
        """Get the value of the conjugate of Phi (Φ-1 or 1-1/Φ).

        Returns:
            The value of Phi conjugate (≈ 0.618034...)
        """
        return self.PHI_CONJUGATE

    def get_fibonacci_sequence(self, n: int) -> List[int]:
        """Get the first n numbers in the Fibonacci sequence.

        Args:
            n: Number of elements to return

        Returns:
            List of the first n Fibonacci numbers
        """
        if n <= 0:
            return []

        if n == 1:
            return [0]

        if n == 2:
            return [0, 1]

        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i - 1] + fib[i - 2])

        return fib

    def get_lucas_sequence(self, n: int) -> List[int]:
        """Get the first n numbers in the Lucas sequence.

        Args:
            n: Number of elements to return

        Returns:
            List of the first n Lucas numbers
        """
        if n <= 0:
            return []

        if n == 1:
            return [2]

        if n == 2:
            return [2, 1]

        lucas = [2, 1]
        for i in range(2, n):
            lucas.append(lucas[i - 1] + lucas[i - 2])

        return lucas

    def calculate_golden_ratio_points(self, length: float) -> Dict[str, float]:
        """Calculate key points in a line segment divided by Golden Ratio.

        Args:
            length: Length of the original line segment

        Returns:
            Dictionary with key points in the golden ratio division
        """
        major = length * self.PHI_INVERSE
        minor = length - major

        return {
            "total_length": length,
            "major_segment": major,
            "minor_segment": minor,
        }

    def calculate_golden_rectangle(self, width: float) -> Dict[str, float]:
        """Calculate dimensions of a golden rectangle given the width.

        Args:
            width: Width of the rectangle

        Returns:
            Dictionary with dimensions of the golden rectangle
        """
        height = width * self.PHI_INVERSE
        return {
            "width": width,
            "height": height,
            "area": width * height,
            "perimeter": 2 * (width + height),
        }

    def calculate_golden_spiral_points(
        self, width: float, num_points: int = 16
    ) -> List[Tuple[float, float]]:
        """Calculate points for drawing a golden spiral.

        Args:
            width: Starting width of the spiral
            num_points: Number of points to calculate

        Returns:
            List of (x, y) coordinates for the golden spiral
        """
        points = []
        a = 0.0
        b = 1.0
        theta_start = 0.0
        theta_end = math.pi / 2

        x_offset = 0.0
        y_offset = 0.0

        for i in range(num_points):
            theta = theta_start + i * (theta_end - theta_start) / (num_points - 1)
            r = a + b * math.exp(theta / self.PHI)
            x = r * math.cos(theta) + x_offset
            y = r * math.sin(theta) + y_offset
            points.append((x * width, y * width))

            # After each quarter turn, update offsets for the next segment
            if i % (num_points // 4) == 0 and i > 0:
                x_offset = points[-1][0]
                y_offset = points[-1][1]
                a = math.sqrt(x_offset**2 + y_offset**2)
                theta_start = math.atan2(y_offset, x_offset)
                theta_end = theta_start + math.pi / 2

        return points

    def calculate_pentagram_points(
        self, center_x: float, center_y: float, radius: float
    ) -> List[Tuple[float, float]]:
        """Calculate points for drawing a pentagram.

        Args:
            center_x: X coordinate of the center
            center_y: Y coordinate of the center
            radius: Radius from center to outer points

        Returns:
            List of (x, y) coordinates for the pentagram vertices
        """
        points = []
        for i in range(5):
            # Outer points (the five points of the star)
            angle = math.pi / 2 + 2 * math.pi * i / 5
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        return points

    def calculate_golden_trisection(self, length: float) -> Dict[str, float]:
        """Calculate the golden trisection of a line segment.

        In a golden trisection, a line is divided into three segments (a, b, c) where
        the segments follow the proportion 1:ρ:σ, derived from the heptagon diagonals.

        Args:
            length: Total length of the line segment

        Returns:
            Dictionary with the three segment lengths and related values
        """
        # Constants from the Golden Trisection ratios
        # These values come from the diagonals of a unit-edge heptagon
        SIGMA = 2.24697960371747  # Σ (sigma uppercase) - Long diagonal in unit-edge heptagon
        RHO = (
            1.80193773580484  # Ρ (rho uppercase) - Short diagonal in unit-edge heptagon
        )

        # Alpha is the edge length of a nested heptagon inside a unit-edge heptagon
        alpha = 0.246979603717467  # α (alpha)

        # Calculate the unit length that creates the proper proportion 1:ρ:σ
        unit_length = length / (1 + RHO + SIGMA)

        # Calculate segments using the correct mathematical proportion 1:ρ:σ
        first_segment = unit_length * 1  # First segment (unit length)
        second_segment = unit_length * RHO  # Second segment (ρ × unit)
        third_segment = unit_length * SIGMA  # Third segment (σ × unit)

        # Calculate proportions relative to total length (for reference)
        first_ratio = first_segment / length
        second_ratio = second_segment / length
        third_ratio = third_segment / length

        return {
            "total_length": length,
            "first_segment": first_segment,  # First segment (unit length)
            "second_segment": second_segment,  # Second segment (ρ × unit)
            "third_segment": third_segment,  # Third segment (σ × unit)
            "rho": RHO,  # Uppercase Rho (≈ 1.802) - short diagonal
            "sigma": SIGMA,  # Uppercase Sigma (≈ 2.247) - long diagonal
            "alpha": alpha,  # Alpha (≈ 0.247) - nested heptagon edge
            "rho_lowercase": first_ratio,  # First segment ratio to total length
            "sigma_lowercase": second_ratio,  # Second segment ratio to total length
            "third_ratio": third_ratio,  # Third segment ratio to total length
        }
