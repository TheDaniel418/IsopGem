"""
Polygonal Numbers Calculator.

This module provides a calculator for generating and analyzing polygonal numbers
and centered polygonal numbers.
"""

import math
from typing import Any, Dict, List, Tuple


class PolygonalNumbersCalculator:
    """Calculator for polygonal numbers and centered polygonal numbers."""

    def __init__(self, sides: int = 3, index: int = 5):
        """Initialize the calculator.

        Args:
            sides: Number of sides for the polygonal number (3=triangular, 4=square, etc.)
            index: Index of the polygonal number (which number in the sequence)
        """
        self.sides = max(3, sides)  # Minimum 3 sides (triangular)
        self.index = max(1, index)  # Minimum index of 1
        self.is_centered = False    # Regular polygonal by default
        self.is_star = False        # Regular non-star polygonal by default

    def set_sides(self, sides: int) -> None:
        """Set the number of sides for the polygonal number.

        Args:
            sides: Number of sides (minimum 3)
        """
        self.sides = max(3, sides)

    def set_index(self, index: int) -> None:
        """Set the index of the polygonal number.

        Args:
            index: Index (minimum 1)
        """
        self.index = max(1, index)

    def set_centered(self, centered: bool) -> None:
        """Set whether to use centered polygonal numbers.

        Args:
            centered: True for centered polygonal numbers, False for regular
        """
        self.is_centered = centered

    def set_star(self, star: bool) -> None:
        """Set whether to use star polygonal numbers.

        Args:
            star: True for star polygonal numbers, False for regular
        """
        self.is_star = star
        # Star polygons require at least 5 sides to be well-defined
        if star and self.sides < 5:
            self.sides = 5

    def calculate_value(self) -> int:
        """Calculate the value of the polygonal number.

        Returns:
            The value of the polygonal number
        """
        if self.is_centered:
            return self._calculate_centered_polygonal()
        else:
            return self._calculate_regular_polygonal()

    def get_actual_dot_count(self) -> int:
        """Get the actual number of dots that will be drawn.
        This may differ from calculate_value() in some cases.

        Returns:
            The actual number of dots that will be drawn
        """
        # Count the actual dots that will be drawn
        return len(self.get_coordinates())

    def count_dots_for_current_type(self) -> int:
        """Get the theoretical number of dots for the current polygonal number type.

        Returns:
            The theoretical number of dots based on the formula for the current type
        """
        if self.is_centered:
            return self._calculate_centered_polygonal()
        else:
            return self._calculate_regular_polygonal()

    def _calculate_regular_polygonal(self) -> int:
        """Calculate the value of a regular polygonal number.

        Returns:
            The value of the regular polygonal number
        """
        # Formula for k-gonal number: P_k(n) = (k-2)*n*(n-1)/2 + n
        k = self.sides
        n = self.index
        return (k - 2) * n * (n - 1) // 2 + n

    def _calculate_centered_polygonal(self) -> int:
        """Calculate the value of a centered polygonal number.

        Returns:
            The value of the centered polygonal number
        """
        # Formula for centered k-gonal number: C_k(n) = k*n*(n-1)/2 + 1
        k = self.sides
        n = self.index
        return k * n * (n - 1) // 2 + 1

    def get_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get the coordinates for visualizing the polygonal number.

        Returns:
            List of (x, y, layer) coordinates for each dot in the pattern
        """
        if self.is_star and self.sides >= 5:
            return self._get_star_coordinates()
        elif self.is_centered:
            return self._get_centered_coordinates()
        else:
            return self._get_regular_coordinates()

    def _get_regular_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for a regular polygonal number.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        # Different implementation based on the number of sides
        if self.sides == 3:  # Triangular numbers
            return self._get_triangular_coordinates()
        elif self.sides == 4:  # Square numbers
            return self._get_square_coordinates()
        elif self.sides == 5:  # Pentagonal numbers
            return self._get_pentagonal_coordinates()
        else:  # General implementation for polygonal numbers with 6+ sides
            return self._get_general_polygonal_coordinates()

    def _get_triangular_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for triangular numbers.

        For triangular numbers (s=3), the formula for dots added in layer n is:
        (3-2)*n - (3-3) = n

        We arrange dots in rows, with the first dot at the origin,
        and each subsequent row having one more dot than the previous.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # Start with the first dot at the origin (0,0)
        # This represents the '1' in the triangular number sequence
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        # For each subsequent layer (1 to index-1)
        for layer in range(1, self.index):
            # For triangular numbers, each layer adds (layer+1) dots
            # These form a new row in the triangle

            # Calculate the y-coordinate for this row
            # We use sqrt(3)/2 for the height of an equilateral triangle
            y = layer * math.sqrt(3) / 2

            # Add dots for this row (layer+1 dots in each row)
            for i in range(layer + 1):
                # Calculate the x-coordinate for this dot
                # We offset each row to maintain the triangular shape
                x = i - layer / 2

                # Add the dot with its layer information and sequential number
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))

        return coordinates

    def _get_square_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for square numbers.

        For square numbers (s=4), the formula for dots added in layer n is:
        (4-2)*n - (4-3) = 2n-1

        We arrange dots in a square pattern, with the first dot at the origin,
        and each subsequent layer forming an L-shape around the previous square.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # Start with the first dot at the origin (0,0)
        # This represents the '1' in the square number sequence
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        # For each subsequent layer (1 to index-1)
        for layer in range(1, self.index):
            # For square numbers, each layer forms an L-shape around the previous square
            # The size of the previous square is layer x layer

            # Add dots along the top edge (excluding the top-right corner)
            for i in range(layer):
                dot_number = len(coordinates) + 1
                coordinates.append((i, layer, layer, dot_number))

            # Add dots along the right edge (including the top-right corner)
            for i in range(layer + 1):
                dot_number = len(coordinates) + 1
                coordinates.append((layer, i, layer, dot_number))

        return coordinates

    def _get_pentagonal_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for pentagonal numbers.

        For pentagonal numbers (s=5), the formula for dots added in layer n is:
        (5-2)*n - (5-3) = 3n-2

        We arrange dots in a pentagonal pattern, with the first dot at the bottom left corner,
        and subsequent dots forming a proper pentagon shape.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # Define the scale factor for better visualization
        scale = 1.0

        # Start with the first dot at the bottom left corner
        # This represents the '1' in the pentagonal number sequence
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        # For a regular pentagon, the interior angle is (5-2)*180/5 = 108 degrees
        # The exterior angle is 72 degrees (360/5)
        # We'll build the pentagon with the first dot at the origin
        # and the first side extending horizontally to the right

        # For each layer (1 to index-1)
        for layer in range(1, self.index):
            # Calculate the side length for this layer
            side_length = layer * scale

            # Calculate the number of dots per side for this layer (including vertices)
            dots_per_side = layer + 1

            # Calculate the angles for the pentagon vertices (in radians)
            # Starting from the bottom left corner (0,0) and going counterclockwise
            angles = [
                0,                  # Bottom left (origin)
                0,                  # Bottom right
                72 * math.pi / 180,  # Upper right
                144 * math.pi / 180, # Upper left
                216 * math.pi / 180  # Left
            ]

            # Calculate the vertex positions
            vertices = []
            vertices.append((0, 0))  # First vertex is at the origin

            # Calculate the remaining vertices
            current_x, current_y = 0, 0
            for i in range(1, 5):  # 4 more vertices to calculate
                # Move in the direction of the current angle
                dx = side_length * math.cos(angles[i])
                dy = side_length * math.sin(angles[i])

                # Update the current position
                current_x += dx
                current_y += dy

                # Add the vertex
                vertices.append((current_x, current_y))

            # Add dots for each side of the pentagon
            for i in range(5):
                # Get the two vertices that define this side
                v1 = vertices[i]
                v2 = vertices[(i+1) % 5]

                # Skip the first vertex of the first side (it's the origin, already added)
                start_j = 1 if i == 0 else 0

                # Add dots along this side
                for j in range(start_j, dots_per_side):
                    # Skip the last dot if it's not the last side (to avoid duplicating vertices)
                    if j == dots_per_side - 1 and i < 4:
                        continue

                    # Calculate position along the side
                    t = j / (dots_per_side - 1)
                    x = v1[0] + t * (v2[0] - v1[0])
                    y = v1[1] + t * (v2[1] - v1[1])

                    # Add the dot with its layer information and sequential number
                    dot_number = len(coordinates) + 1
                    coordinates.append((x, y, layer, dot_number))

        return coordinates

    def _get_general_polygonal_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for general polygonal numbers with 6 or more sides.

        For s-sided polygonal numbers, the formula for dots added in layer n is:
        (s-2)*n - (s-3)

        We arrange dots in a polygonal pattern, with the first dot at the bottom left corner,
        and subsequent dots forming a proper polygon shape with s sides.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # Define the scale factor for better visualization
        scale = 1.0

        # Start with the first dot at the bottom left corner
        # This represents the '1' in the polygonal number sequence
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        # For a regular polygon with s sides, the exterior angle is 360/s degrees
        # We'll build the polygon with the first dot at the origin
        # and the first side extending horizontally to the right

        # For each layer (1 to index-1)
        for layer in range(1, self.index):
            # Calculate the side length for this layer
            side_length = layer * scale

            # Calculate the number of dots per side for this layer (including vertices)
            dots_per_side = layer + 1

            # Calculate the exterior angle in radians
            exterior_angle = 2 * math.pi / self.sides

            # Calculate the angles for the polygon vertices (in radians)
            # Starting from the bottom left corner (0,0) and going counterclockwise
            angles = [0]  # the First angle is 0 (bottom left, origin)

            # Calculate the remaining vertex angles
            for i in range(1, self.sides):
                angles.append(i * exterior_angle)

            # Calculate the vertex positions
            vertices = []
            vertices.append((0, 0))  # First vertex is at the origin

            # Calculate the remaining vertices
            current_x, current_y = 0, 0
            for i in range(1, self.sides):  # Remaining vertices to calculate
                # Move in the direction of the current angle
                dx = side_length * math.cos(angles[i])
                dy = side_length * math.sin(angles[i])

                # Update the current position
                current_x += dx
                current_y += dy

                # Add the vertex
                vertices.append((current_x, current_y))

            # Add dots for each side of the polygon
            for i in range(self.sides):
                # Get the two vertices that define this side
                v1 = vertices[i]
                v2 = vertices[(i+1) % self.sides]

                # Skip the first vertex of the first side (it's the origin, already added)
                start_j = 1 if i == 0 else 0

                # Add dots along this side
                for j in range(start_j, dots_per_side):
                    # Skip the last dot if it's not the last side (to avoid duplicating vertices)
                    if j == dots_per_side - 1 and i < self.sides - 1:
                        # Skip this dot to avoid duplicating vertices
                        # Add a special marker to indicate this is a skipped vertex
                        # We'll use this in the visualization to avoid drawing labels for these points
                        x = v1[0] + (j / (dots_per_side - 1)) * (v2[0] - v1[0])
                        y = v1[1] + (j / (dots_per_side - 1)) * (v2[1] - v1[1])
                        # Use -1 as the layer to mark this as a skipped vertex
                        coordinates.append((x, y, -1, -1))
                        continue

                    # Calculate position along the side
                    t = j / (dots_per_side - 1)
                    x = v1[0] + t * (v2[0] - v1[0])
                    y = v1[1] + t * (v2[1] - v1[1])

                    # Just use a simple sequential dot number
                    # We'll handle the proper numbering in the visualization
                    dot_number = len(coordinates) + 1
                    coordinates.append((x, y, layer, dot_number))

        return coordinates

    def _get_centered_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for a centered polygonal number.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []
        target_count = self.calculate_value()  # Get the exact number of dots we need

        # For centered triangular numbers, we need a special approach
        if self.sides == 3:
            return self._get_centered_triangular_coordinates(target_count)

        # For other centered polygonal numbers
        # Always start with the center point (layer 0)
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1
        dots_so_far = 1

        if self.index == 1 or dots_so_far >= target_count:
            # Just the center point for index 1
            return coordinates

        # For centered polygonal numbers, we arrange in concentric layers
        # Each layer forms a complete polygon around the center
        # For a k-sided polygon, layer n has k*n dots (n dots per side)

        # Calculate how many complete layers we can add
        max_layers = self.index - 1  # Index 1 has 0 layers beyond center, index 2 has 1 layer, etc.

        # Add layers until we reach the target count or max layers
        for layer in range(1, max_layers + 1):
            # Calculate how many dots in this layer
            dots_in_layer = self.sides * layer

            # Check if adding this layer would exceed the target count
            if dots_so_far + dots_in_layer > target_count:
                # We can't add the full layer, so add dots until we reach the target
                dots_to_add = target_count - dots_so_far
                self._add_partial_polygon_layer(coordinates, layer, dots_to_add)
                dots_so_far = target_count
                break

            # Add the full layer
            self._add_polygon_layer(coordinates, layer)
            dots_so_far += dots_in_layer

        return coordinates

    def _add_polygon_layer(self, coordinates: List[Tuple[float, float, int, int]], layer: int) -> None:
        """Add a complete layer of dots for a centered polygonal number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
        """
        # Calculate the vertices of the polygon for this layer
        vertices = []
        for i in range(self.sides):
            angle = 2 * math.pi * i / self.sides + math.pi / self.sides  # Rotate for better orientation
            x = layer * math.cos(angle)
            y = layer * math.sin(angle)
            vertices.append((x, y))

        # For each side of the polygon, add dots
        for i in range(self.sides):
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % self.sides]

            # Add dots along this side (excluding the ending vertex to avoid duplicates)
            dots_per_side = layer
            for j in range(dots_per_side):
                # Calculate position along the side
                t = j / dots_per_side
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))

    def calculate_star(self, index: int) -> Dict[str, Any]:
        """Calculate a star polygon with dots on both sides of each point.

        Args:
            index: The index of the star (how many layers and dots)

        Returns:
            Dict with coordinates data for the star
        """
        # Initialize collections for coordinates
        all_coords = []
        layers_data = []

        # Add center point
        center = (0, 0, 0, 1)
        all_coords.append(center)

        # Get the appropriate skip value for this star pattern
        if self.sides == 5:
            skip = 2  # Classic pentagram
        elif self.sides == 6:
            skip = 2  # Hexagram
        elif self.sides == 7:
            skip = 3  # Heptagram
        elif self.sides == 8:
            skip = 3  # Octagram
        elif self.sides == 9:
            skip = 4  # Nonagram
        elif self.sides == 10:
            skip = 3  # Decagram
        else:
            # For other numbers, use a formula that generally works well
            skip = self.sides // 2
            if skip % 2 == 0 and self.sides % 2 == 0:
                skip = skip - 1

        # For each layer (1 to index), add star points
        for layer in range(1, index + 1):
            # Calculate the vertices of the star (outer points)
            outer_vertices = []
            math_vertices = []  # For intersection calculations

            for i in range(self.sides):
                angle = 2 * math.pi * i / self.sides
                x = layer * math.cos(angle)
                y = layer * math.sin(angle)
                math_vertices.append((x, y))

                dot_number = len(all_coords) + 1
                vertex = (x, y, layer, dot_number)
                outer_vertices.append(vertex)
                all_coords.append(vertex)

            # Calculate all possible intersections
            all_intersections = []
            for i in range(self.sides):
                i_next = (i + skip) % self.sides
                for j in range(i + 1, self.sides):
                    j_next = (j + skip) % self.sides

                    # Skip if lines are adjacent in the star pattern
                    if i_next == j or j_next == i:
                        continue

                    p1 = math_vertices[i]
                    p2 = math_vertices[i_next]
                    p3 = math_vertices[j]
                    p4 = math_vertices[j_next]

                    intersection = self._calculate_line_intersection(p1, p2, p3, p4)

                    if intersection:
                        # Check if point is inside the star
                        center_dist = math.sqrt(intersection[0]**2 + intersection[1]**2)
                        vertex_dist = math.sqrt(math_vertices[0][0]**2 + math_vertices[0][1]**2)

                        if center_dist < vertex_dist * 0.9:
                            # Check if it's a new point (avoid duplicates)
                            is_new = True
                            for existing in all_intersections:
                                if (abs(existing[0] - intersection[0]) < 1e-6 and
                                    abs(existing[1] - intersection[1]) < 1e-6):
                                    is_new = False
                                    break

                            if is_new:
                                all_intersections.append(intersection)

            # Add inner vertices to coordinates
            inner_vertex_coords = []
            for x, y in all_intersections:
                dot_number = len(all_coords) + 1
                vertex = (x, y, layer - 0.5, dot_number)
                inner_vertex_coords.append(vertex)
                all_coords.append(vertex)

            # For index 3 and higher, add dots along both sides of each star point
            if index >= 3:
                # Determine how many dots to place on each side of the point
                # Index 3: 1 dot per side, Index 4: 2 dots per side, etc.
                dots_per_side = index - 2  # Adjusted formula

                # For each outer vertex (star point)
                for i, vertex_data in enumerate(outer_vertices):
                    outer_x, outer_y = vertex_data[0], vertex_data[1]

                    # Find connected inner vertices by computing which lines from this vertex
                    # according to the skip pattern
                    connected_inner_points = []

                    # Get the two vertices this point connects to in the star pattern
                    target1 = (i + skip) % self.sides
                    target2 = (i - skip) % self.sides

                    # Find intersections along these two paths
                    for x, y in all_intersections:
                        # Check if this inner point lies on the line from outer_vertex to target1
                        p1 = math_vertices[i]
                        p2 = math_vertices[target1]
                        if self._point_on_line_segment(p1, p2, (x, y)):
                            connected_inner_points.append((x, y))

                        # Check if this inner point lies on the line from outer_vertex to target2
                        p1 = math_vertices[i]
                        p2 = math_vertices[target2]
                        if self._point_on_line_segment(p1, p2, (x, y)):
                            connected_inner_points.append((x, y))

                    # If we found connected inner points, use them for dot placement
                    if len(connected_inner_points) >= 2:
                        # For each connected inner point, add dots along the side
                        for inner_point in connected_inner_points[:2]:  # Use at most 2
                            inner_x, inner_y = inner_point

                            # Add dots along the side (outer to inner)
                            for j in range(1, dots_per_side + 1):
                                t = j / (dots_per_side + 1)  # Evenly space the dots
                                x = outer_x * (1 - t) + inner_x * t
                                y = outer_y * (1 - t) + inner_y * t
                                dot_number = len(all_coords) + 1
                                all_coords.append((x, y, layer, dot_number))

            # Add this layer's data
            layers_data.append({
                'layer': layer,
                'outer_vertices': outer_vertices,
                'inner_vertices': inner_vertex_coords,
                'skip': skip  # Include the skip value for visualization
            })

        # Return the complete structure
        return {
            'all': all_coords,
            'center': center,
            'layers': layers_data
        }

    def _point_on_line_segment(self, p1, p2, p):
        """Check if point p is on the line segment from p1 to p2.

        Args:
            p1, p2: Line segment endpoints (x1, y1), (x2, y2)
            p: Point to check (x, y)

        Returns:
            bool: True if the point is on the line segment
        """
        # Unpack points
        x1, y1 = p1
        x2, y2 = p2
        x, y = p

        # Calculate line length squared
        line_length_squared = (x2 - x1)**2 + (y2 - y1)**2

        # If the line has zero length, p is on the segment if it equals p1
        if line_length_squared == 0:
            return (x == x1 and y == y1)

        # Calculate projection ratio
        r = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / line_length_squared

        # If r is between 0 and 1, the point projects onto the segment
        if r < 0 or r > 1:
            return False

        # Calculate distance from point to line
        dist = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt(line_length_squared)

        # If the distance is very small, the point is on the line
        return dist < 1e-6

    def _calculate_line_intersection(self, p1, p2, p3, p4):
        """Calculate the intersection point of two line segments.

        Args:
            p1, p2: First line segment endpoints (x1, y1), (x2, y2)
            p3, p4: Second line segment endpoints (x3, y3), (x4, y4)

        Returns:
            tuple: (x, y) coordinates of intersection point, or None if no intersection
        """
        # Line 1 represented as a1x + b1y = c1
        a1 = p2[1] - p1[1]
        b1 = p1[0] - p2[0]
        c1 = a1 * p1[0] + b1 * p1[1]

        # Line 2 represented as a2x + b2y = c2
        a2 = p4[1] - p3[1]
        b2 = p3[0] - p4[0]
        c2 = a2 * p3[0] + b2 * p3[1]

        # Determinant
        determinant = a1 * b2 - a2 * b1

        if determinant == 0:
            # Lines are parallel
            return None
        else:
            # Calculate intersection point
            x = (b2 * c1 - b1 * c2) / determinant
            y = (a1 * c2 - a2 * c1) / determinant

            return (x, y)

        def _calculate_star_inner_vertices(self, outer_vertices, skip):
            """Calculate the inner vertices of a star polygon.

            Args:
                outer_vertices: List of (x, y) outer vertex coordinates
                skip: Skip value for the star pattern

            Returns:
                List of (x, y) coordinates for inner vertices
            """
            inner_vertices = []
            n = len(outer_vertices)

            # For each pair of non-adjacent star lines
            for i in range(n):
                i_next = (i + skip) % n
                line1 = (outer_vertices[i], outer_vertices[i_next])

                # Check intersection with next star line
                j = (i + 1) % n
                j_next = (j + skip) % n
                line2 = (outer_vertices[j], outer_vertices[j_next])

                # Calculate intersection
                intersection = self._line_intersection(line1[0], line1[1], line2[0], line2[1])

                if intersection:
                    # Add to list if it's a new intersection point
                    is_new = True
                    for existing in inner_vertices:
                        if (abs(existing[0] - intersection[0]) < 1e-6 and
                            abs(existing[1] - intersection[1]) < 1e-6):
                            is_new = False
                            break

                    if is_new:
                        # Check if point is inside the star (not an outer extension)
                        # This can be done by checking distance from center
                        center_dist = math.sqrt(intersection[0]**2 + intersection[1]**2)
                        vertex_dist = math.sqrt(outer_vertices[0][0]**2 + outer_vertices[0][1]**2)

                        if center_dist < vertex_dist * 0.95:
                            inner_vertices.append(intersection)

            return inner_vertices

        def _line_intersection(self, p1, p2, p3, p4):
            """Calculate the intersection point of two line segments.

            Args:
                p1, p2: First line segment endpoints (x1, y1), (x2, y2)
                p3, p4: Second line segment endpoints (x3, y3), (x4, y4)

            Returns:
                tuple: (x, y) coordinates of intersection point, or None if no intersection
            """
            # Line 1 represented as a1x + b1y = c1
            a1 = p2[1] - p1[1]
            b1 = p1[0] - p2[0]
            c1 = a1 * p1[0] + b1 * p1[1]

            # Line 2 represented as a2x + b2y = c2
            a2 = p4[1] - p3[1]
            b2 = p3[0] - p4[0]
            c2 = a2 * p3[0] + b2 * p3[1]

            # Determinant
            determinant = a1 * b2 - a2 * b1

            if determinant == 0:
                # Lines are parallel
                return None
            else:
                # Calculate intersection point
                x = (b2 * c1 - b1 * c2) / determinant
                y = (a1 * c2 - a2 * c1) / determinant

                return (x, y)

        def _get_star_skip(self, num_points):
            """Get the optimal skip value for drawing a star with the given number of points.

            Args:
                num_points: The number of points in the star

            Returns:
                int: The skip value to use when connecting points
            """
            # Standard skip values for common polygons
            if num_points == 5:
                return 2  # Classic pentagram
            elif num_points == 6:
                return 2  # Hexagram
            elif num_points == 7:
                return 3  # Heptagram
            elif num_points == 8:
                return 3  # Octagram
            elif num_points == 9:
                return 4  # Nonagram
            elif num_points == 10:
                return 3  # Decagram
            elif num_points == 11:
                return 5  # Hendecagram
            elif num_points == 12:
                return 5  # Dodecagram

            # For other numbers, use a formula that generally works well
            skip = num_points // 2
            if skip % 2 == 0 and num_points % 2 == 0:
                skip = skip - 1

            return skip

        def _find_connected_inner_vertices(self, outer_vertex, inner_vertices):
            """Find the inner vertices connected to a specific outer vertex.

            Args:
                outer_vertex: The outer vertex (x, y)
                inner_vertices: List of inner vertices (x, y)

            Returns:
                List of (x, y) coordinates for connected inner vertices
            """
            # Get coordinates of the outer vertex
            outer_x, outer_y = outer_vertex

            # Calculate distances from outer vertex to each inner vertex
            distances = []
            for inner_vertex in inner_vertices:
                inner_x, inner_y = inner_vertex
                dist = math.sqrt((outer_x - inner_x)**2 + (outer_y - inner_y)**2)
                distances.append((dist, inner_vertex))

            # Sort by distance
            distances.sort(key=lambda x: x[0])

            # Return the two closest inner vertices
            connected = []
            if len(distances) >= 2:
                connected = [vertex for _, vertex in distances[:2]]

            return connected

        def _calculate_star_skip(self, sides):
            """Calculate the optimal skip value for a star with given number of sides.

            Args:
                sides: Number of sides

            Returns:
                int: Skip value for star pattern
            """
            # Standard skip values for common polygons
            if sides == 5:
                return 2  # Classic pentagram
            elif sides == 6:
                return 2  # Hexagram
            elif sides == 7:
                return 3  # Heptagram
            elif sides == 8:
                return 3  # Octagram
            elif sides == 9:
                return 4  # Nonagram
            elif sides == 10:
                return 3  # Decagram
            elif sides == 11:
                return 5  # Hendecagram
            elif sides == 12:
                return 5  # Dodecagram

            # For other numbers, use a formula that generally works well
            skip = sides // 2
            if skip % 2 == 0 and sides % 2 == 0:
                skip = skip - 1

            return skip

        def calculate_star_polygon(self, index: int) -> Dict[str, Any]:
            """Calculate a star polygon figure.

            Args:
                index: The index of the polygonal number (how many layers to show)

            Returns:
                Dict containing coordinate data for the star polygon
            """
            # For a star polygon, we need to:
            # 1. Create the basic star shape with outer and inner vertices
            # 2. Add dots along both sides of each star point based on the index

            # Initialize collections for coordinates
            all_coords = []
            layers_data = []

            # Add center point
            center = (0, 0, 0, 1)
            all_coords.append(center)

            # Calculate the skip value for this star
            skip = self._calculate_star_skip(self.sides)

            # For each layer (1 to index), add star points
            for layer in range(1, index + 1):
                layer_coords = []

                # Calculate outer vertices of the star
                outer_vertices = []
                for i in range(self.sides):
                    angle = 2 * math.pi * i / self.sides
                    x = layer * math.cos(angle)
                    y = layer * math.sin(angle)
                    dot_number = len(all_coords) + 1
                    vertex = (x, y, layer, dot_number)
                    outer_vertices.append(vertex)
                    layer_coords.append(vertex)
                    all_coords.append(vertex)

                # Calculate inner vertices (intersections)
                inner_vertices = self._calculate_star_inner_vertices(layer, skip)
                inner_vertex_coords = []

                # Add inner vertices to coordinates
                for x, y in inner_vertices:
                    dot_number = len(all_coords) + 1
                    # Inner vertices are at a lower layer
                    vertex = (x, y, layer - 0.5, dot_number)
                    inner_vertex_coords.append(vertex)
                    layer_coords.append(vertex)
                    all_coords.append(vertex)

                # For indices greater than 2, add dots along both sides of each star point
                if index > 2:
                    # The number of dots to add on each side of a point depends on the index
                    dots_per_side = layer - 1

                    # For each point in the star, connect outer vertex to its two adjacent inner vertices
                    for i in range(self.sides):
                        # Get the outer vertex (tip of the star point)
                        outer_vertex = outer_vertices[i]
                        outer_x, outer_y = outer_vertex[0], outer_vertex[1]

                        # Find the two inner vertices connected to this outer vertex
                        connected_inner_vertices = self._find_connected_inner_vertices(
                            outer_vertex, inner_vertices, layer
                        )

                        # Add dots along each side of the point
                        if connected_inner_vertices and len(connected_inner_vertices) >= 2:
                            # First side
                            inner_x1, inner_y1 = connected_inner_vertices[0]
                            for j in range(1, dots_per_side + 1):
                                t = j / (dots_per_side + 1)
                                x = outer_x + t * (inner_x1 - outer_x)
                                y = outer_y + t * (inner_y1 - outer_y)
                                dot_number = len(all_coords) + 1
                                dot = (x, y, layer, dot_number)
                                layer_coords.append(dot)
                                all_coords.append(dot)

                            # Second side
                            inner_x2, inner_y2 = connected_inner_vertices[1]
                            for j in range(1, dots_per_side + 1):
                                t = j / (dots_per_side + 1)
                                x = outer_x + t * (inner_x2 - outer_x)
                                y = outer_y + t * (inner_y2 - outer_y)
                                dot_number = len(all_coords) + 1
                                dot = (x, y, layer, dot_number)
                                layer_coords.append(dot)
                                all_coords.append(dot)

                # Add this layer's data
                layers_data.append({
                    'layer': layer,
                    'outer_vertices': outer_vertices,
                    'inner_vertices': inner_vertex_coords
                })

            # Return the complete structure
            return {
                'all': all_coords,
                'center': center,
                'layers': layers_data
            }

        def _calculate_star_inner_vertices(self, layer, skip):
            """Calculate the inner vertices (intersection points) of a star.

            Args:
                layer: The current layer
                skip: The skip value for the star pattern

            Returns:
                List of (x, y) coordinates for inner vertices
            """
            # Calculate the outer vertices
            outer_vertices = []
            for i in range(self.sides):
                angle = 2 * math.pi * i / self.sides
                x = layer * math.cos(angle)
                y = layer * math.sin(angle)
                outer_vertices.append((x, y))

            # Calculate intersections
            intersections = []
            for i in range(self.sides):
                # Get the line from this vertex to the skipped vertex
                i_next = (i + skip) % self.sides
                line1 = (outer_vertices[i], outer_vertices[i_next])

                # Get the next line
                j = (i + 1) % self.sides
                j_next = (j + skip) % self.sides
                line2 = (outer_vertices[j], outer_vertices[j_next])

                # Find intersection
                intersection = self._line_intersection(line1[0], line1[1], line2[0], line2[1])

                if intersection:
                    # Check if this is a new intersection
                    is_new = True
                    for existing in intersections:
                        if (abs(existing[0] - intersection[0]) < 1e-6 and
                            abs(existing[1] - intersection[1]) < 1e-6):
                            is_new = False
                            break

                    if is_new:
                        intersections.append(intersection)

            return intersections

        def _line_intersection(self, p1, p2, p3, p4):
            """Calculate the intersection of two lines.

            Args:
                p1, p2: First line endpoints
                p3, p4: Second line endpoints

            Returns:
                (x, y) coordinates of intersection or None
            """
            # Line 1 represented as a1x + b1y = c1
            a1 = p2[1] - p1[1]
            b1 = p1[0] - p2[0]
            c1 = a1 * p1[0] + b1 * p1[1]

            # Line 2 represented as a2x + b2y = c2
            a2 = p4[1] - p3[1]
            b2 = p3[0] - p4[0]
            c2 = a2 * p3[0] + b2 * p3[1]

            # Determinant
            determinant = a1 * b2 - a2 * b1

            if determinant == 0:
                # Lines are parallel
                return None
            else:
                # Calculate intersection point
                x = (b2 * c1 - b1 * c2) / determinant
                y = (a1 * c2 - a2 * c1) / determinant

                # Check if the point is inside the star
                center_dist = math.sqrt(x*x + y*y)
                outer_dist = math.sqrt(p1[0]*p1[0] + p1[1]*p1[1])

                if center_dist < outer_dist:
                    return (x, y)
                return None

        def _find_connected_inner_vertices(self, outer_vertex, inner_vertices, layer):
            """Find the inner vertices connected to a specific outer vertex.

            Args:
                outer_vertex: The outer vertex (x, y, layer, number)
                inner_vertices: List of inner vertices (x, y)
                layer: Current layer

            Returns:
                List of (x, y) coordinates for connected inner vertices
            """
            outer_x, outer_y = outer_vertex[0], outer_vertex[1]

            # Calculate distances from the outer vertex to each inner vertex
            distances = []
            for inner_x, inner_y in inner_vertices:
                dist = math.sqrt((outer_x - inner_x)**2 + (outer_y - inner_y)**2)
                distances.append((dist, (inner_x, inner_y)))

            # Sort by distance
            distances.sort()

            # The two closest inner vertices are the ones connected to this outer vertex
            connected = []
            for dist, vertex in distances[:2]:
                # Verify the distance is reasonable (should be less than the layer distance)
                if dist < layer * 1.5:
                    connected.append(vertex)

            return connected

    def _add_partial_polygon_layer(self, coordinates: List[Tuple[float, float, int, int]],
                                  layer: int, dots_to_add: int) -> None:
        """Add a partial layer of dots for a centered polygonal number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
            dots_to_add: Number of dots to add from this layer
        """
        # Calculate the vertices of the polygon for this layer
        vertices = []
        for i in range(self.sides):
            angle = 2 * math.pi * i / self.sides + math.pi / self.sides  # Rotate for better orientation
            x = layer * math.cos(angle)
            y = layer * math.sin(angle)
            vertices.append((x, y))

        # Add dots evenly around the perimeter
        dots_added = 0

        # For each side of the polygon
        for i in range(self.sides):
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % self.sides]

            # Calculate how many dots to add on this side
            dots_per_side = layer
            dots_for_this_side = min(dots_per_side, dots_to_add - dots_added)

            # Add dots along this side
            for j in range(dots_for_this_side):
                # Calculate position along the side
                t = j / dots_per_side
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))
                dots_added += 1

                if dots_added >= dots_to_add:
                    return

    def _get_centered_triangular_coordinates(self, target_count: int) -> List[Tuple[float, float, int, int]]:
        """Get coordinates specifically for centered triangular numbers.

        Args:
            target_count: The exact number of dots needed

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # Always start with the center point (layer 0)
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        if self.index == 1 or target_count <= 1:
            return coordinates

        # For centered triangular numbers, the number of dots in each layer follows a pattern:
        # Layer 0 (center): 1 dot
        # Layer 1: 3 dots (3 vertices)
        # Layer 2: 6 dots (2 dots per side)
        # Layer 3: 9 dots (3 dots per side)
        # Layer n: 3*n dots (n dots per side)

        dots_so_far = 1  # Center dot

        # Calculate how many complete layers we can add
        max_layers = self.index - 1  # Index 1 has 0 layers beyond center, index 2 has 1 layer, etc.

        # Add layers until we reach the target count or max layers
        for layer in range(1, max_layers + 1):
            # Calculate how many dots in this layer
            dots_in_layer = 3 * layer

            # Check if adding this layer would exceed the target count
            if dots_so_far + dots_in_layer > target_count:
                # We can't add the full layer, so add dots until we reach the target
                dots_to_add = target_count - dots_so_far
                self._add_partial_triangular_layer(coordinates, layer, dots_to_add)
                dots_so_far = target_count
                break

            # Add the full layer
            self._add_triangular_layer(coordinates, layer)
            dots_so_far += dots_in_layer

        return coordinates

    def _add_triangular_layer(self, coordinates: List[Tuple[float, float, int, int]], layer: int) -> None:
        """Add a complete layer of dots for a centered triangular number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
        """
        # Calculate the vertices of the triangle for this layer
        vertices = []
        for i in range(3):  # Triangle has 3 sides
            angle = 2 * math.pi * i / 3 + math.pi / 6  # Rotate for better orientation
            x = layer * math.cos(angle)
            y = layer * math.sin(angle)
            vertices.append((x, y))

        # For each side of the triangle, add dots
        for i in range(3):  # Triangle has 3 sides
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 3]

            # Add dots along this side (excluding the ending vertex to avoid duplicates)
            dots_per_side = layer
            for j in range(dots_per_side):
                # Calculate position along the side
                t = j / dots_per_side
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))

    def _add_partial_triangular_layer(self, coordinates: List[Tuple[float, float, int, int]],
                                     layer: int, dots_to_add: int) -> None:
        """Add a partial layer of dots for a centered triangular number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
            dots_to_add: Number of dots to add from this layer
        """
        # Calculate the vertices of the triangle for this layer
        vertices = []
        for i in range(3):  # Triangle has 3 sides
            angle = 2 * math.pi * i / 3 + math.pi / 6  # Rotate for better orientation
            x = layer * math.cos(angle)
            y = layer * math.sin(angle)
            vertices.append((x, y))

        # Add dots evenly around the perimeter
        dots_added = 0

        # For each side of the triangle
        for i in range(3):
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 3]

            # Calculate how many dots to add on this side
            dots_per_side = layer
            dots_for_this_side = min(dots_per_side, dots_to_add - dots_added)

            # Add dots along this side
            for j in range(dots_for_this_side):
                # Calculate position along the side
                t = j / dots_per_side
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))
                dots_added += 1

                if dots_added >= dots_to_add:
                    return

    def _get_star_coordinates(self) -> List[Tuple[float, float, int, int]]:
        """Get coordinates for star-shaped polygonal numbers.

        Star polygons are created by drawing lines between non-adjacent vertices
        of a regular polygon. This creates a star-like shape.

        Returns:
            List of (x, y, layer) coordinates with layer information for coloring
        """
        coordinates = []

        # We need at least 5 sides for a proper star
        if self.sides < 5:
            return coordinates

        # Start with the center point
        coordinates.append((0, 0, 0, 1))  # Layer 0, dot number 1

        # For a star with n points, we'll build n layers
        max_layers = self.index - 1  # Index 1 has just the center, index 2 has 1 layer, etc.

        # Add complete layers
        for layer in range(1, max_layers + 1):
            self._add_star_layer(coordinates, layer)

        return coordinates

    def _add_star_layer(self, coordinates: List[Tuple[float, float, int, int]], layer: int) -> None:
        """Add a complete layer of dots for a star-shaped polygonal number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
        """
        # Define the scale factor for better visualization
        scale = layer * 1.0

        # Calculate inner and outer radii for the star
        outer_radius = scale
        inner_radius = scale * 0.4  # Adjust this for different star appearances

        # Calculate the vertices of the star for this layer
        vertices = []

        # Create the star by alternating between outer and inner points
        for i in range(self.sides * 2):  # Double the points for inner and outer vertices
            # Determine if this is an outer or inner vertex
            is_outer = i % 2 == 0
            radius = outer_radius if is_outer else inner_radius

            # Calculate angle - distribute points evenly around the circle
            # Add an offset to rotate the star for better orientation
            angle = math.pi / self.sides + math.pi / 2 + (math.pi / self.sides) * i

            # Calculate coordinates
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            vertices.append((x, y))

        # Add dots along each edge of the star
        for i in range(self.sides * 2):
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % (self.sides * 2)]

            # Calculate how many dots to put on this edge
            # We want to scale this based on layer to ensure proper density
            dots_per_edge = max(2, layer + 1)  # Minimum 2 dots per edge (the endpoints)

            # For each dot position along the edge
            for j in range(dots_per_edge):
                # Skip the last dot of each edge except for the last edge
                # to avoid duplicating vertices
                if j == dots_per_edge - 1 and i < self.sides * 2 - 1:
                    continue

                # Calculate position along the edge
                t = j / (dots_per_edge - 1)
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])

                # Add the dot with its layer information and sequential number
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))

    def _add_partial_star_layer(self, coordinates: List[Tuple[float, float, int, int]],
                               layer: int, dots_to_add: int) -> None:
        """Add a partial layer of dots for a star-shaped polygonal number.

        Args:
            coordinates: List to append coordinates to
            layer: Layer number (1-based)
            dots_to_add: Number of dots to add from this layer
        """
        # Define the scale factor for better visualization
        scale = layer * 1.0

        # Calculate inner and outer radii for the star
        outer_radius = scale
        inner_radius = scale * 0.4  # Adjust this for different star appearances

        # Calculate the vertices of the star for this layer
        vertices = []

        # Create the star by alternating between outer and inner points
        for i in range(self.sides * 2):  # Double the points for inner and outer vertices
            # Determine if this is an outer or inner vertex
            is_outer = i % 2 == 0
            radius = outer_radius if is_outer else inner_radius

            # Calculate angle - distribute points evenly around the circle
            # Add an offset to rotate the star for better orientation
            angle = math.pi / self.sides + math.pi / 2 + (math.pi / self.sides) * i

            # Calculate coordinates
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            vertices.append((x, y))

        # Add dots evenly around the perimeter
        dots_added = 0

        # Add dots along each edge of the star
        for i in range(self.sides * 2):
            # Get current vertex and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % (self.sides * 2)]

            # Calculate how many dots to put on this edge
            # We want to scale this based on layer to ensure proper density
            dots_per_edge = max(2, layer + 1)  # Minimum 2 dots per edge (the endpoints)

            # Calculate how many dots to add on this edge
            dots_for_this_edge = min(dots_per_edge, dots_to_add - dots_added)

            # For each dot position along the edge
            for j in range(dots_for_this_edge):
                # Skip the last dot of each edge except for the last edge
                # to avoid duplicating vertices
                if j == dots_per_edge - 1 and i < self.sides * 2 - 1:
                    continue

                # Calculate position along the edge
                t = j / (dots_per_edge - 1)
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])

                # Add the dot with its layer information and sequential number
                dot_number = len(coordinates) + 1
                coordinates.append((x, y, layer, dot_number))
                dots_added += 1

                if dots_added >= dots_to_add:
                    return

    def get_formula_string(self) -> str:
        """Get the formula for the current polygonal number as a string.

        Returns:
            Formula string
        """
        k = self.sides
        n = self.index

        if self.is_star:
            # Formula for star numbers (simplified approximation)
            return f"S_{k}({n}) ≈ {k}n(n-1) + 1 = {self.calculate_value()}"
        elif self.is_centered:
            return f"C_{k}({n}) = {k}n(n-1)/2 + 1 = {self.calculate_value()}"
        else:
            return f"P_{k}({n}) = (k-2)n(n-1)/2 + n = {self.calculate_value()}"

    def get_polygonal_name(self) -> str:
        """Get the name of the current polygonal number type.

        Returns:
            Name of the polygonal number type
        """
        if self.is_star:
            star_names = {
                5: "Pentagram",
                6: "Hexagram",
                7: "Heptagram",
                8: "Octagram",
                9: "Nonagram",
                10: "Decagram",
                11: "Hendecagram",
                12: "Dodecagram",
                15: "Pentadecagram",
                20: "Icosagram"
            }
            if self.sides in star_names:
                return f"{star_names[self.sides]} Star"
            else:
                return f"{self.sides}-gram Star"
        else:
            prefix = "Centered " if self.is_centered else ""

            shape_names = {
                3: "Triangular",
                4: "Square",
                5: "Pentagonal",
                6: "Hexagonal",
                7: "Heptagonal",
                8: "Octagonal",
                9: "Nonagonal",
                10: "Decagonal",
                11: "Hendecagonal",
                12: "Dodecagonal",
                13: "Triskaidecagonal",
                14: "Tetrakaidecagonal",
                15: "Pentadecagonal",
                16: "Hexakaidecagonal",
                17: "Heptadecagonal",
                18: "Octakaidecagonal",
                19: "Enneadecagonal",
                20: "Icosagonal",
                30: "Triacontagonal",
                40: "Tetracontagonal",
                50: "Pentacontagonal",
                60: "Hexacontagonal",
                70: "Heptacontagonal",
                80: "Octacontagonal",
                90: "Enneacontagonal",
                100: "Hectagonal"
            }

            if self.sides in shape_names:
                return f"{prefix}{shape_names[self.sides]}"
            else:
                return f"{prefix}{self.sides}-gonal"
