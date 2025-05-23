"""Regular polygon calculator module.

This module provides a calculator for regular polygon-related calculations.
It supports various properties of regular polygons such as area, perimeter,
interior angles, and more.
"""

import math
from typing import List, Tuple


class Point:
    """A point in 2D space."""

    def __init__(self, x: float, y: float):
        """Initialize a point.

        Args:
            x: X-coordinate
            y: Y-coordinate
        """
        self.x = x
        self.y = y


class RegularPolygonCalculator:
    """Calculator for regular polygon-related calculations."""

    def __init__(self, sides: int = 5, radius: float = 100.0):
        """Initialize the regular polygon calculator.

        Args:
            sides: Number of sides (default: 5)
            radius: Radius of the circumscribed circle (default: 100.0)
        """
        self.sides = max(3, sides)  # Minimum 3 sides
        self.radius = max(1.0, radius)  # Minimum radius of 1.0
        self.orientation = "vertex_top"  # Default orientation

    def set_sides(self, sides: int) -> None:
        """Set the number of sides of the regular polygon.

        Args:
            sides: Number of sides (minimum 3)
        """
        self.sides = max(3, sides)

    def set_radius(self, radius: float) -> None:
        """Set the radius of the circumscribed circle.

        Args:
            radius: Radius of the circumscribed circle (minimum 1.0)
        """
        self.radius = max(1.0, radius)

    def set_orientation(self, orientation: str) -> None:
        """Set the orientation of the regular polygon.

        Args:
            orientation: Orientation of the polygon ('vertex_top' or 'side_top')
        """
        if orientation in ["vertex_top", "side_top"]:
            self.orientation = orientation

    def calculate_interior_angle(self) -> float:
        """Calculate the interior angle of the regular polygon.

        Returns:
            Interior angle in degrees
        """
        return (self.sides - 2) * 180.0 / self.sides

    def calculate_exterior_angle(self) -> float:
        """Calculate the exterior angle of the regular polygon.

        Returns:
            Exterior angle in degrees
        """
        return 360.0 / self.sides

    def calculate_edge_length(self) -> float:
        """Calculate the edge length of the regular polygon.

        Returns:
            Edge length
        """
        return 2 * self.radius * math.sin(math.pi / self.sides)

    def calculate_perimeter(self) -> float:
        """Calculate the perimeter of the regular polygon.

        Returns:
            Perimeter
        """
        return self.sides * self.calculate_edge_length()

    def calculate_area(self) -> float:
        """Calculate the area of the regular polygon.

        Returns:
            Area
        """
        return (
            0.5
            * self.sides
            * self.radius
            * self.radius
            * math.sin(2 * math.pi / self.sides)
        )

    def calculate_inradius(self) -> float:
        """Calculate the inradius (radius of the inscribed circle) of the regular polygon.

        Returns:
            Inradius
        """
        return self.radius * math.cos(math.pi / self.sides)

    def calculate_incircle_area(self) -> float:
        """Calculate the area of the inscribed circle.

        Returns:
            Area of the inscribed circle
        """
        inradius = self.calculate_inradius()
        return math.pi * inradius * inradius

    def calculate_circumcircle_area(self) -> float:
        """Calculate the area of the circumscribed circle.

        Returns:
            Area of the circumscribed circle
        """
        return math.pi * self.radius * self.radius

    def calculate_incircle_circumference(self) -> float:
        """Calculate the circumference of the inscribed circle.

        Returns:
            Circumference of the inscribed circle
        """
        return 2 * math.pi * self.calculate_inradius()

    def calculate_circumcircle_circumference(self) -> float:
        """Calculate the circumference of the circumscribed circle.

        Returns:
            Circumference of the circumscribed circle
        """
        return 2 * math.pi * self.radius

    def get_vertices(self, center_x: float = 0.0, center_y: float = 0.0) -> List[Point]:
        """Get the vertices of the regular polygon.

        Args:
            center_x: X-coordinate of the center (default: 0.0)
            center_y: Y-coordinate of the center (default: 0.0)

        Returns:
            List of vertices as Point objects
        """
        vertices = []

        # Calculate the angle offset based on the orientation
        angle_offset = 0.0
        if self.orientation == "vertex_top":
            angle_offset = math.pi / 2  # 90 degrees
        elif self.orientation == "side_top":
            angle_offset = (
                math.pi / 2 - math.pi / self.sides
            )  # 90 degrees - (180/n) degrees

        # Calculate the vertices
        for i in range(self.sides):
            angle = angle_offset + 2 * math.pi * i / self.sides
            x = center_x + self.radius * math.cos(angle)
            y = center_y - self.radius * math.sin(
                angle
            )  # Negative because y-axis is down in PyQt
            vertices.append(Point(x, y))

        return vertices

    def calculate_diagonals(self) -> List[Tuple[int, int, float]]:
        """Calculate the diagonals of the regular polygon grouped by skip pattern.

        Returns:
            List of tuples (skip, count, length) where:
            - skip: Number of vertices skipped
            - count: Number of diagonals with this skip pattern
            - length: Length of the diagonal
        """
        diagonals = []

        # Special case for triangle (3 sides) - no diagonals
        if self.sides == 3:
            return diagonals

        # Special case for square (4 sides)
        if self.sides == 4:
            # For a square, there's only one type of diagonal (connecting opposite vertices)
            # This is equivalent to skip=2 (skipping 2 vertices)
            length = 2 * self.radius * math.sin(2 * math.pi / self.sides)
            count = 2  # A square has 2 diagonals
            diagonals.append((2, count, length))
            return diagonals

        # For a regular polygon with n sides, we can have diagonals that skip
        # from 2 to (n-1)/2 vertices (rounded down)
        max_skip = (self.sides - 1) // 2

        for skip in range(2, max_skip + 1):
            # Calculate the length of the diagonal using the law of cosines
            # Length = 2 * R * sin(k * pi / n) where k is the number of vertices skipped
            length = 2 * self.radius * math.sin(skip * math.pi / self.sides)

            # Calculate the number of diagonals with this skip pattern
            # For a regular polygon with n sides, the number of diagonals with a specific skip pattern
            # is n/2 (each diagonal connects two vertices, and we don't want to count them twice)
            count = self.sides // 2

            diagonals.append((skip, count, length))

        return diagonals

    def calculate_total_diagonals_count(self) -> int:
        """Calculate the total number of diagonals in the polygon.

        Returns:
            Total number of diagonals
        """
        # Formula for total diagonals in a polygon: n(n-3)/2
        return self.sides * (self.sides - 3) // 2

    def calculate_central_angle(self) -> float:
        """Calculate the central angle of the regular polygon.

        Returns:
            Central angle in degrees
        """
        return 360.0 / self.sides

    def calculate_apothem(self) -> float:
        """Calculate the apothem (distance from center to midpoint of a side) of the regular polygon.

        Returns:
            Apothem
        """
        return self.radius * math.cos(math.pi / self.sides)

    def calculate_area_using_apothem(self) -> float:
        """Calculate the area of the regular polygon using the apothem.

        Returns:
            Area
        """
        apothem = self.calculate_apothem()
        perimeter = self.calculate_perimeter()
        return 0.5 * apothem * perimeter

    def calculate_polygon_to_circle_area_ratio(self) -> float:
        """Calculate the ratio of the polygon area to the circumscribed circle area.

        Returns:
            Ratio of polygon area to circumscribed circle area
        """
        polygon_area = self.calculate_area()
        circle_area = self.calculate_circumcircle_area()
        return polygon_area / circle_area

    def calculate_circle_to_polygon_area_ratio(self) -> float:
        """Calculate the ratio of the inscribed circle area to the polygon area.

        Returns:
            Ratio of inscribed circle area to polygon area
        """
        circle_area = self.calculate_incircle_area()
        polygon_area = self.calculate_area()
        return circle_area / polygon_area

    def is_constructible_with_compass_and_straightedge(self) -> bool:
        """Check if the regular polygon is constructible with compass and straightedge.

        A regular polygon with n sides is constructible with compass and straightedge
        if and only if n is a power of 2 times a product of distinct Fermat primes.
        Fermat primes are primes of the form 2^(2^k) + 1 for some non-negative integer k.
        The known Fermat primes are 3, 5, 17, 257, and 65537.

        Returns:
            True if the polygon is constructible with compass and straightedge, False otherwise
        """
        # Known Fermat primes
        fermat_primes = [3, 5, 17, 257, 65537]

        # Check if the number of sides is a power of 2 times a product of distinct Fermat primes
        n = self.sides

        # Remove factors of 2
        while n % 2 == 0:
            n //= 2

        # Check if the remaining factors are distinct Fermat primes
        for prime in fermat_primes:
            if n % prime == 0:
                n //= prime
                # Check if this prime appears more than once
                if n % prime == 0:
                    return False

        # If n is 1, then the polygon is constructible
        return n == 1
