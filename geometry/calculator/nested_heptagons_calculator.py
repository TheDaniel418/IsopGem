"""Nested heptagons calculator module.

This module provides a calculator for nested heptagon-related calculations.
It supports various properties of nested heptagons including the outer, middle,
and inner heptagons based on golden trisection ratios.
"""

import math
from typing import List


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


class NestedHeptagonsCalculator:
    """Calculator for nested heptagons-related calculations."""

    # Constants from the Golden Trisection ratios for heptagons
    SIGMA = (
        2.24697960371747  # Σ (sigma uppercase) - Long diagonal in unit-edge heptagon
    )
    RHO = 1.80193773580484  # Ρ (rho uppercase) - Short diagonal in unit-edge heptagon
    ALPHA = 0.246979603717467  # α (alpha) - Nested heptagon edge ratio, also InnerEdge/MiddleEdge

    def __init__(
        self, middle_edge_length: float = 1.0
    ):  # Changed from outer_edge_length, default to 1 like spreadsheet
        """Initialize the nested heptagons calculator.

        Args:
            middle_edge_length: Edge length of the middle heptagon (default: 1.0)
        """
        self.sides = 7  # Fixed at 7 sides for heptagons
        # self.outer_edge_length = max(1.0, outer_edge_length) # Old line
        self.middle_edge_length = max(
            0.01, middle_edge_length
        )  # New primary state, min value 0.01
        self.orientation = "vertex_top"  # Default orientation

    # def set_outer_edge_length(self, edge_length: float) -> None: # Old method, to be replaced
    #     """Set the edge length of the outer heptagon.
    #
    #     Args:
    #         edge_length: Edge length of the outer heptagon (minimum 1.0)
    #     """
    #     self.outer_edge_length = max(1.0, edge_length)

    def set_middle_edge_length(self, middle_edge: float) -> None:
        """Set the edge length of the middle heptagon, which drives all calculations.

        Args:
            middle_edge: Edge length of the middle heptagon (minimum 0.01)
        """
        self.middle_edge_length = max(0.01, middle_edge)

    def set_value_from_outer_edge(self, outer_edge: float) -> None:
        """Set calculator state based on a new outer edge length.
        This will calculate the corresponding middle_edge_length and set it.
        E_outer = E_middle * RHO * SIGMA  => E_middle = E_outer / (RHO * SIGMA)
        Args:
            outer_edge: New edge length for the outer heptagon.
        """
        corresponding_middle_edge = outer_edge / (self.RHO * self.SIGMA)
        self.set_middle_edge_length(corresponding_middle_edge)

    def set_value_from_inner_edge(self, inner_edge: float) -> None:
        """Set calculator state based on a new inner edge length.
        This will calculate the corresponding middle_edge_length and set it.
        E_inner = E_middle * ALPHA => E_middle = E_inner / ALPHA
        Args:
            inner_edge: New edge length for the inner heptagon.
        """
        corresponding_middle_edge = inner_edge / self.ALPHA
        self.set_middle_edge_length(corresponding_middle_edge)

    def set_value_from_outer_perimeter(self, perimeter: float) -> None:
        """Set calculator state based on outer heptagon perimeter."""
        if self.sides == 0:
            return  # Avoid division by zero
        outer_edge = perimeter / self.sides
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_area(self, area: float) -> None:
        """Set calculator state based on outer heptagon area."""
        # A = (n/4) * a² * cot(π/n) => a = sqrt( (4*A) / (n * cot(π/n)) )
        cot_pi_over_n = 1 / math.tan(math.pi / self.sides)
        if self.sides == 0 or cot_pi_over_n == 0:
            return  # Avoid division by zero
        outer_edge_squared = (4 * area) / (self.sides * cot_pi_over_n)
        outer_edge = math.sqrt(
            max(0, outer_edge_squared)
        )  # Ensure non-negative for sqrt
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_short_diagonal(self, short_diagonal: float) -> None:
        """Set calculator state based on outer heptagon short diagonal."""
        if self.RHO == 0:
            return  # Avoid division by zero
        outer_edge = short_diagonal / self.RHO
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_long_diagonal(self, long_diagonal: float) -> None:
        """Set calculator state based on outer heptagon long diagonal."""
        if self.SIGMA == 0:
            return  # Avoid division by zero
        outer_edge = long_diagonal / self.SIGMA
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_inradius(self, inradius: float) -> None:
        """Set calculator state based on outer heptagon inradius."""
        outer_edge = self._calculate_edge_from_inradius(inradius)
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_circumradius(self, circumradius: float) -> None:
        """Set calculator state based on outer heptagon circumradius."""
        outer_edge = self._calculate_edge_from_circumradius(circumradius)
        self.set_value_from_outer_edge(outer_edge)

    def set_value_from_outer_incircle_circumference(self, circumference: float) -> None:
        """Set calculator state based on outer heptagon's incircle circumference."""
        if math.pi == 0:
            return  # Avoid division by zero
        inradius = circumference / (2 * math.pi)
        self.set_value_from_outer_inradius(inradius)

    def set_value_from_outer_circumcircle_circumference(
        self, circumference: float
    ) -> None:
        """Set calculator state based on outer heptagon's circumcircle circumference."""
        if math.pi == 0:
            return  # Avoid division by zero
        circumradius = circumference / (2 * math.pi)
        self.set_value_from_outer_circumradius(circumradius)

    def set_value_from_middle_perimeter(self, perimeter: float) -> None:
        """Set calculator state based on middle heptagon perimeter."""
        if self.sides == 0:
            return
        middle_edge = perimeter / self.sides
        self.set_middle_edge_length(middle_edge)  # Directly set the middle edge

    def set_value_from_middle_area(self, area: float) -> None:
        """Set calculator state based on middle heptagon area."""
        cot_pi_over_n = 1 / math.tan(math.pi / self.sides)
        if self.sides == 0 or cot_pi_over_n == 0:
            return
        middle_edge_squared = (4 * area) / (self.sides * cot_pi_over_n)
        middle_edge = math.sqrt(max(0, middle_edge_squared))
        self.set_middle_edge_length(middle_edge)

    def set_value_from_middle_short_diagonal(self, short_diagonal: float) -> None:
        """Set calculator state based on middle heptagon short diagonal."""
        if self.RHO == 0:
            return
        middle_edge = short_diagonal / self.RHO
        self.set_middle_edge_length(middle_edge)

    def set_value_from_middle_long_diagonal(self, long_diagonal: float) -> None:
        """Set calculator state based on middle heptagon long diagonal."""
        if self.SIGMA == 0:
            return
        middle_edge = long_diagonal / self.SIGMA
        self.set_middle_edge_length(middle_edge)

    def set_value_from_middle_inradius(self, inradius: float) -> None:
        """Set calculator state based on middle heptagon inradius."""
        middle_edge = self._calculate_edge_from_inradius(inradius)
        self.set_middle_edge_length(middle_edge)

    def set_value_from_middle_circumradius(self, circumradius: float) -> None:
        """Set calculator state based on middle heptagon circumradius."""
        middle_edge = self._calculate_edge_from_circumradius(circumradius)
        self.set_middle_edge_length(middle_edge)

    def set_value_from_middle_incircle_circumference(
        self, circumference: float
    ) -> None:
        """Set calculator state based on middle heptagon's incircle circumference."""
        if math.pi == 0:
            return
        inradius = circumference / (2 * math.pi)
        self.set_value_from_middle_inradius(
            inradius
        )  # Call the inradius setter for middle

    def set_value_from_middle_circumcircle_circumference(
        self, circumference: float
    ) -> None:
        """Set calculator state based on middle heptagon's circumcircle circumference."""
        if math.pi == 0:
            return
        circumradius = circumference / (2 * math.pi)
        self.set_value_from_middle_circumradius(
            circumradius
        )  # Call the circumradius setter for middle

    def set_value_from_inner_perimeter(self, perimeter: float) -> None:
        """Set calculator state based on inner heptagon perimeter."""
        if self.sides == 0:
            return
        inner_edge = perimeter / self.sides
        self.set_value_from_inner_edge(
            inner_edge
        )  # Uses existing E_middle = E_inner / ALPHA

    def set_value_from_inner_area(self, area: float) -> None:
        """Set calculator state based on inner heptagon area."""
        cot_pi_over_n = 1 / math.tan(math.pi / self.sides)
        if self.sides == 0 or cot_pi_over_n == 0:
            return
        inner_edge_squared = (4 * area) / (self.sides * cot_pi_over_n)
        inner_edge = math.sqrt(max(0, inner_edge_squared))
        self.set_value_from_inner_edge(inner_edge)

    def set_value_from_inner_short_diagonal(self, short_diagonal: float) -> None:
        """Set calculator state based on inner heptagon short diagonal."""
        if self.RHO == 0:
            return
        inner_edge = short_diagonal / self.RHO
        self.set_value_from_inner_edge(inner_edge)

    def set_value_from_inner_long_diagonal(self, long_diagonal: float) -> None:
        """Set calculator state based on inner heptagon long diagonal."""
        if self.SIGMA == 0:
            return
        inner_edge = long_diagonal / self.SIGMA
        self.set_value_from_inner_edge(inner_edge)

    def set_value_from_inner_inradius(self, inradius: float) -> None:
        """Set calculator state based on inner heptagon inradius."""
        inner_edge = self._calculate_edge_from_inradius(inradius)
        self.set_value_from_inner_edge(inner_edge)

    def set_value_from_inner_circumradius(self, circumradius: float) -> None:
        """Set calculator state based on inner heptagon circumradius."""
        inner_edge = self._calculate_edge_from_circumradius(circumradius)
        self.set_value_from_inner_edge(inner_edge)

    def set_value_from_inner_incircle_circumference(self, circumference: float) -> None:
        """Set calculator state based on inner heptagon's incircle circumference."""
        if math.pi == 0:
            return
        inradius = circumference / (2 * math.pi)
        self.set_value_from_inner_inradius(
            inradius
        )  # Call the inradius setter for inner

    def set_value_from_inner_circumcircle_circumference(
        self, circumference: float
    ) -> None:
        """Set calculator state based on inner heptagon's circumcircle circumference."""
        if math.pi == 0:
            return
        circumradius = circumference / (2 * math.pi)
        self.set_value_from_inner_circumradius(
            circumradius
        )  # Call the circumradius setter for inner

    def set_orientation(self, orientation: str) -> None:
        """Set the orientation of the heptagons.

        Args:
            orientation: Orientation of the polygon ('vertex_top' or 'side_top')
        """
        if orientation in ["vertex_top", "side_top"]:
            self.orientation = orientation

    # Common methods for regular polygons
    def calculate_interior_angle(self) -> float:
        """Calculate the interior angle of a regular heptagon.

        Returns:
            Interior angle in degrees
        """
        return (self.sides - 2) * 180.0 / self.sides  # (7-2)*180/7 = 128.57°

    def calculate_exterior_angle(self) -> float:
        """Calculate the exterior angle of a regular heptagon.

        Returns:
            Exterior angle in degrees
        """
        return 360.0 / self.sides  # 360/7 = 51.43°

    def calculate_central_angle(self) -> float:
        """Calculate the central angle of a regular heptagon.

        Returns:
            Central angle in degrees
        """
        return 360.0 / self.sides  # 360/7 = 51.43°

    # Base methods for any size heptagon
    def _calculate_circumradius_from_edge(self, edge_length: float) -> float:
        """Calculate the circumradius of a heptagon given its edge length.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Circumradius of the heptagon
        """
        # R = a/(2*sin(π/n)) where a is the edge length and n is the number of sides
        return edge_length / (2 * math.sin(math.pi / self.sides))

    def _calculate_inradius_from_edge(self, edge_length: float) -> float:
        """Calculate the inradius of a heptagon given its edge length.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Inradius of the heptagon
        """
        # r = a/(2*tan(π/n)) where a is the edge length and n is the number of sides
        return edge_length / (2 * math.tan(math.pi / self.sides))

    def _calculate_edge_from_circumradius(self, radius: float) -> float:
        """Calculate the edge length of a heptagon given its circumradius.

        Args:
            radius: Circumradius of the heptagon

        Returns:
            Edge length of the heptagon
        """
        # a = 2*R*sin(π/n) where R is the circumradius and n is the number of sides
        return 2 * radius * math.sin(math.pi / self.sides)

    def _calculate_edge_from_inradius(self, inradius: float) -> float:
        """Calculate the edge length of a heptagon given its inradius.

        Args:
            inradius: Inradius of the heptagon

        Returns:
            Edge length of the heptagon
        """
        # a = 2*r*tan(π/n) where r is the inradius and n is the number of sides
        return 2 * inradius * math.tan(math.pi / self.sides)

    def _calculate_perimeter(self, edge_length: float) -> float:
        """Calculate the perimeter of a heptagon given its edge length.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Perimeter of the heptagon
        """
        return self.sides * edge_length

    def _calculate_area(self, edge_length: float) -> float:
        """Calculate the area of a heptagon given its edge length.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Area of the heptagon
        """
        # A = (n/4) * a² * cot(π/n) where a is the edge length and n is the number of sides
        return (
            (self.sides / 4)
            * edge_length
            * edge_length
            * (1 / math.tan(math.pi / self.sides))
        )

    def _calculate_short_diagonal(self, edge_length: float) -> float:
        """Calculate the length of the shortest diagonal in a heptagon.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Length of the shortest diagonal
        """
        # For a unit-edge heptagon, the short diagonal is RHO (≈1.802)
        return edge_length * self.RHO

    def _calculate_long_diagonal(self, edge_length: float) -> float:
        """Calculate the length of the longest diagonal in a heptagon.

        Args:
            edge_length: Edge length of the heptagon

        Returns:
            Length of the longest diagonal
        """
        # For a unit-edge heptagon, the long diagonal is SIGMA (≈2.247)
        return edge_length * self.SIGMA

    # Outer heptagon calculations
    def calculate_outer_edge_length(self) -> float:  # New method
        """Calculate the edge length of the outer heptagon.
        Derived from middle_edge_length: E_outer = E_middle * RHO * SIGMA.
        Returns:
            Edge length of the outer heptagon.
        """
        return self.middle_edge_length * self.RHO * self.SIGMA

    def calculate_outer_circumradius(self) -> float:
        """Calculate the circumradius of the outer heptagon.

        Returns:
            Circumradius of the outer heptagon
        """
        # return self._calculate_circumradius_from_edge(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_circumradius_from_edge(outer_edge)

    def calculate_outer_inradius(self) -> float:
        """Calculate the inradius of the outer heptagon.

        Returns:
            Inradius of the outer heptagon
        """
        # return self._calculate_inradius_from_edge(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_inradius_from_edge(outer_edge)

    def calculate_outer_perimeter(self) -> float:
        """Calculate the perimeter of the outer heptagon.

        Returns:
            Perimeter of the outer heptagon
        """
        # return self._calculate_perimeter(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_perimeter(outer_edge)

    def calculate_outer_area(self) -> float:
        """Calculate the area of the outer heptagon.

        Returns:
            Area of the outer heptagon
        """
        # return self._calculate_area(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_area(outer_edge)

    def calculate_outer_short_diagonal(self) -> float:
        """Calculate the length of the short diagonal of the outer heptagon.

        Returns:
            Length of the short diagonal of the outer heptagon
        """
        # return self._calculate_short_diagonal(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_short_diagonal(outer_edge)

    def calculate_outer_long_diagonal(self) -> float:
        """Calculate the length of the long diagonal of the outer heptagon.

        Returns:
            Length of the long diagonal of the outer heptagon
        """
        # return self._calculate_long_diagonal(self.outer_edge_length) # Old
        outer_edge = self.calculate_outer_edge_length()
        return self._calculate_long_diagonal(outer_edge)

    def calculate_outer_incircle_circumference(self) -> float:
        """Calculate the circumference of the incircle of the outer heptagon.

        Returns:
            Circumference of the incircle of the outer heptagon
        """
        return 2 * math.pi * self.calculate_outer_inradius()

    def calculate_outer_circumcircle_circumference(self) -> float:
        """Calculate the circumference of the circumcircle of the outer heptagon.

        Returns:
            Circumference of the circumcircle of the outer heptagon
        """
        return 2 * math.pi * self.calculate_outer_circumradius()

    # Middle heptagon calculations
    def calculate_middle_edge_length(
        self,
    ) -> float:  # Was calculating from outer, now just returns state
        """Return the edge length of the middle heptagon (the primary state).

        Returns:
            Edge length of the middle heptagon.
        """
        # return self.outer_edge_length / (self.RHO * self.SIGMA) # Old calculation
        return self.middle_edge_length  # New: returns the state variable

    def calculate_middle_circumradius(self) -> float:
        """Calculate the circumradius of the middle heptagon.

        Returns:
            Circumradius of the middle heptagon
        """
        return self._calculate_circumradius_from_edge(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_inradius(self) -> float:
        """Calculate the inradius of the middle heptagon.

        Returns:
            Inradius of the middle heptagon
        """
        return self._calculate_inradius_from_edge(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_perimeter(self) -> float:
        """Calculate the perimeter of the middle heptagon.

        Returns:
            Perimeter of the middle heptagon
        """
        return self._calculate_perimeter(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_area(self) -> float:
        """Calculate the area of the middle heptagon.

        Returns:
            Area of the middle heptagon
        """
        return self._calculate_area(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_short_diagonal(self) -> float:
        """Calculate the length of the short diagonal of the middle heptagon.

        Returns:
            Length of the short diagonal of the middle heptagon
        """
        return self._calculate_short_diagonal(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_long_diagonal(self) -> float:
        """Calculate the length of the long diagonal of the middle heptagon.

        Returns:
            Length of the long diagonal of the middle heptagon
        """
        return self._calculate_long_diagonal(
            self.middle_edge_length
        )  # Now uses middle_edge_length directly

    def calculate_middle_incircle_circumference(self) -> float:
        """Calculate the circumference of the incircle of the middle heptagon.

        Returns:
            Circumference of the incircle of the middle heptagon
        """
        return 2 * math.pi * self.calculate_middle_inradius()

    def calculate_middle_circumcircle_circumference(self) -> float:
        """Calculate the circumference of the circumcircle of the middle heptagon.

        Returns:
            Circumference of the circumcircle of the middle heptagon
        """
        return 2 * math.pi * self.calculate_middle_circumradius()

    # Inner heptagon calculations
    def calculate_inner_edge_length(
        self,
    ) -> float:  # Logic was correct, just ensure it uses middle_edge_length
        """Calculate the edge length of the inner heptagon.

        The inner heptagon's edge length is ALPHA (≈0.247) times the middle
        heptagon's edge length, as per the user's spreadsheet logic.

        Returns:
            Edge length of the inner heptagon
        """
        # middle_edge = self.calculate_middle_edge_length() # No longer needed as self.middle_edge_length is state
        return self.middle_edge_length * self.ALPHA  # Correct: Inner = Middle * ALPHA

    def calculate_inner_circumradius(self) -> float:
        """Calculate the circumradius of the inner heptagon.

        Returns:
            Circumradius of the inner heptagon
        """
        # return self._calculate_circumradius_from_edge(self.calculate_inner_edge_length()) # Old, inner_edge_length was complex
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_circumradius_from_edge(inner_edge)

    def calculate_inner_inradius(self) -> float:
        """Calculate the inradius of the inner heptagon.

        Returns:
            Inradius of the inner heptagon
        """
        # return self._calculate_inradius_from_edge(self.calculate_inner_edge_length()) # Old
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_inradius_from_edge(inner_edge)

    def calculate_inner_perimeter(self) -> float:
        """Calculate the perimeter of the inner heptagon.

        Returns:
            Perimeter of the inner heptagon
        """
        # return self._calculate_perimeter(self.calculate_inner_edge_length()) # Old
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_perimeter(inner_edge)

    def calculate_inner_area(self) -> float:
        """Calculate the area of the inner heptagon.

        Returns:
            Area of the inner heptagon
        """
        # return self._calculate_area(self.calculate_inner_edge_length()) # Old
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_area(inner_edge)

    def calculate_inner_short_diagonal(self) -> float:
        """Calculate the length of the short diagonal of the inner heptagon.

        Returns:
            Length of the short diagonal of the inner heptagon
        """
        # return self._calculate_short_diagonal(self.calculate_inner_edge_length()) # Old
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_short_diagonal(inner_edge)

    def calculate_inner_long_diagonal(self) -> float:
        """Calculate the length of the long diagonal of the inner heptagon.

        Returns:
            Length of the long diagonal of the inner heptagon
        """
        # return self._calculate_long_diagonal(self.calculate_inner_edge_length()) # Old
        inner_edge = self.calculate_inner_edge_length()
        return self._calculate_long_diagonal(inner_edge)

    def calculate_inner_incircle_circumference(self) -> float:
        """Calculate the circumference of the incircle of the inner heptagon.

        Returns:
            Circumference of the incircle of the inner heptagon
        """
        return 2 * math.pi * self.calculate_inner_inradius()

    def calculate_inner_circumcircle_circumference(self) -> float:
        """Calculate the circumference of the circumcircle of the inner heptagon.

        Returns:
            Circumference of the circumcircle of the inner heptagon
        """
        return 2 * math.pi * self.calculate_inner_circumradius()

    # Vertex calculation methods
    def calculate_outer_vertices(self) -> List[Point]:
        """Calculate the vertices of the outer heptagon.

        Returns:
            List of Point objects representing the vertices
        """
        vertices = []
        radius = (
            self.calculate_outer_circumradius()
        )  # This will now correctly use the new outer_edge calc
        angle_offset = 0

        if self.orientation == "vertex_top":
            angle_offset = -math.pi / 2  # Start at the top (270 degrees)
        else:  # "side_top"
            angle_offset = (
                -math.pi / 2 + math.pi / self.sides
            )  # Rotate by half a segment

        for i in range(self.sides):
            angle = angle_offset + (2 * math.pi * i) / self.sides
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append(Point(x, y))

        return vertices

    def calculate_middle_vertices(self) -> List[Point]:
        """Calculate the vertices of the middle heptagon.

        Returns:
            List of Point objects representing the vertices
        """
        # The middle heptagon vertices match the outer heptagon vertices, # This comment might be outdated now
        # but in a different order (skipping one vertex)
        # outer_vertices = self.calculate_outer_vertices() # Old approach
        # middle_vertices = []
        #
        # for i in range(self.sides):
        #     middle_vertices.append(outer_vertices[(i * 2) % self.sides])
        #
        # return middle_vertices

        vertices = []
        radius = (
            self.calculate_middle_circumradius()
        )  # Calculate directly from middle circumradius
        angle_offset = 0

        if self.orientation == "vertex_top":
            angle_offset = -math.pi / 2  # Start at the top (270 degrees)
        else:  # "side_top"
            angle_offset = (
                -math.pi / 2 + math.pi / self.sides
            )  # Rotate by half a segment

        for i in range(self.sides):
            angle = angle_offset + (2 * math.pi * i) / self.sides
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append(Point(x, y))

        return vertices

    def calculate_inner_vertices(self) -> List[Point]:
        """Calculate the vertices of the inner heptagon.

        Returns:
            List of Point objects representing the vertices
        """
        vertices = []
        radius = (
            self.calculate_inner_circumradius()
        )  # This will now correctly use the new inner_edge calc
        angle_offset = 0

        if self.orientation == "vertex_top":
            angle_offset = -math.pi / 2  # Start at the top (270 degrees)
        else:  # "side_top"
            angle_offset = (
                -math.pi / 2 + math.pi / self.sides
            )  # Rotate by half a segment

        for i in range(self.sides):
            angle = angle_offset + (2 * math.pi * i) / self.sides
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append(Point(x, y))

        return vertices
