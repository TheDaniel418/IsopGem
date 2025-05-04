"""Star numbers calculator module."""

import math
from typing import List, Tuple


class StarNumbersCalculator:
    """Calculator for star numbers and their visualization coordinates."""

    def __init__(self, points: int = 5, index: int = 1):
        """Initialize the calculator.

        Args:
            points: Number of points in the star (default: 5 for pentagram)
            index: Index of the star number (default: 1)
        """
        self.points = max(5, points)  # Minimum 5 points for a proper star
        self.index = max(1, index)

    def calculate_value(self) -> int:
        """Calculate the star number value.

        Returns:
            The star number value
        """
        # The formula for the nth star number with p points is:
        # S_p(n) = p*n*(n-1) + 1
        #
        # This formula accounts for:
        # - The center dot (1)
        # - The inner and outer vertices and dots between them in a way that
        #   matches the standard sequence for star numbers

        return self.points * self.index * (self.index - 1) + 1

    def get_coordinates(self):
        """Get structured coordinates for visualizing the star number.

        Returns:
            dict with keys:
                - 'all': flat list of (x, y, layer, dot_number)
                - 'center': (x, y, layer, dot_number) for the center
                - 'layers': list of dicts, one per layer, each with:
                    - 'outer_vertices': list of (x, y, layer, dot_number)
                    - 'inner_vertices': list of (x, y, layer, dot_number)
                    - 'segment_dots': list of (x, y, layer, dot_number)
        """
        coordinates = []
        layers = []
        dot_number = 1

        # Center point
        center = (0, 0, 0, dot_number)
        coordinates.append(center)

        if self.index == 1:
            return {
                'all': coordinates,
                'center': center,
                'layers': []
            }

        for layer in range(2, self.index + 1):
            star_geometry = self._calculate_star_geometry(layer)
            outer_vertices = []
            inner_vertices = []
            segment_dots = []

            # Add outer vertices
            for x, y in star_geometry['outer_vertices']:
                dot_number += 1
                outer_vertices.append((x, y, layer, dot_number))
                coordinates.append((x, y, layer, dot_number))

            # Add inner vertices
            for x, y in star_geometry['inner_vertices']:
                dot_number += 1
                inner_vertices.append((x, y, layer, dot_number))
                coordinates.append((x, y, layer, dot_number))

            # For index 3+, add dots along the line segments for this star
            if layer > 2:
                # Get the vertices for this star
                ov = star_geometry['outer_vertices']
                iv = star_geometry['inner_vertices']
                # Add dots along the line segments, but collect them separately
                before = len(coordinates)
                dot_number = self._add_dots_on_line_segments(
                    coordinates,
                    ov,
                    iv,
                    layer,
                    dot_number
                )
                # The new dots are those just added
                segment_dots.extend(coordinates[before:])

            layers.append({
                'outer_vertices': outer_vertices,
                'inner_vertices': inner_vertices,
                'segment_dots': segment_dots,
                'layer': layer
            })

        # Verify the total number of dots matches the mathematical formula
        expected_dots = self.calculate_value()
        actual_dots = len(coordinates)
        if actual_dots != expected_dots:
            diff = expected_dots - actual_dots
            if diff > 0:
                for i in range(actual_dots, expected_dots):
                    coordinates.append((0, 0, 0, i + 1))
            else:
                coordinates = coordinates[:expected_dots]

        return {
            'all': coordinates,
            'center': center,
            'layers': layers
        }

    def _calculate_star_geometry(self, layer: int) -> dict:
        """Calculate the geometry of the star for a specific layer.

        Args:
            layer: The layer number (2-based, since layer 1 is just the center dot)

        Returns:
            Dictionary containing star geometry information
        """
        # Scale factor for the star (based on layer)
        # Each layer creates a larger concentric star
        scale = layer
        print(f"DEBUG: Calculating star geometry for layer {layer} with scale {scale}")

        # Apply rotation to ensure the top point is at exactly 90 degrees (straight up)
        rotation_offset = math.pi / 2  # 90 degrees to put a point at the top

        # Calculate outer vertex positions
        outer_vertices = []
        outer_angles = []
        for i in range(self.points):
            # Calculate angle for each outer vertex, with first point at the top (90 degrees)
            angle = 2 * math.pi * i / self.points + rotation_offset
            outer_angles.append(angle)

            # Calculate position
            x = scale * math.cos(angle)
            y = scale * math.sin(angle)
            outer_vertices.append((x, y))

        # Calculate inner vertex positions
        inner_vertices = []
        inner_radius = self._get_inner_radius(scale)

        # Calculate inner vertices by finding the intersection of lines
        # from non-adjacent outer vertices
        skip = self._get_skip_value()

        # For each inner vertex
        for i in range(self.points):
            # Find the two lines that intersect to form this inner vertex
            # Line 1: from vertex i to vertex (i+skip) % points
            # Line 2: from vertex (i+1) % points to vertex (i+1+skip) % points

            # Get the four vertices that define the two lines
            v1 = outer_vertices[i]
            v2 = outer_vertices[(i + skip) % self.points]
            v3 = outer_vertices[(i + 1) % self.points]
            v4 = outer_vertices[(i + 1 + skip) % self.points]

            # Calculate the intersection of these two lines
            # Line 1: v1 to v2
            # Line 2: v3 to v4

            # Convert to line equations: ax + by + c = 0
            # Line 1
            a1 = v2[1] - v1[1]  # y2 - y1
            b1 = v1[0] - v2[0]  # x1 - x2
            c1 = v2[0] * v1[1] - v1[0] * v2[1]  # x2*y1 - x1*y2

            # Line 2
            a2 = v4[1] - v3[1]  # y4 - y3
            b2 = v3[0] - v4[0]  # x3 - x4
            c2 = v4[0] * v3[1] - v3[0] * v4[1]  # x4*y3 - x3*y4

            # Calculate determinant
            det = a1 * b2 - a2 * b1

            # Check if lines are parallel (det = 0)
            if abs(det) < 1e-10:
                # If parallel, use the inner radius method as fallback
                angle = (outer_angles[i] + outer_angles[(i + 1) % self.points]) / 2
                x = inner_radius * math.cos(angle)
                y = inner_radius * math.sin(angle)
            else:
                # Calculate intersection point
                x = (b1 * c2 - b2 * c1) / det
                y = (a2 * c1 - a1 * c2) / det

                # Calculate distance from center to this point
                dist = math.sqrt(x**2 + y**2)

                # If the intersection is too far away or too close,
                # normalize to the inner radius
                if dist > 2 * scale or dist < 0.1 * scale:
                    # Normalize to inner radius
                    if dist > 0:
                        x = x * inner_radius / dist
                        y = y * inner_radius / dist
                    else:
                        # Fallback if dist is 0
                        angle = outer_angles[i]
                        x = inner_radius * math.cos(angle)
                        y = inner_radius * math.sin(angle)

            inner_vertices.append((x, y))

        # Return the calculated vertices
        return {
            'outer_vertices': outer_vertices,
            'inner_vertices': inner_vertices
        }

    def _get_skip_value(self) -> int:
        """Get the appropriate skip value for this star type.

        Returns:
            Skip value
        """
        if self.points == 5:  # Pentagram
            return 2
        elif self.points == 6:  # Hexagram
            return 2
        elif self.points == 7:  # Heptagram
            return 3
        elif self.points == 8:  # Octagram
            return 3
        elif self.points == 9:  # Enneagram
            return 4
        elif self.points == 10:  # Decagram
            return 3
        elif self.points == 11:  # Hendecagram
            return 5
        elif self.points == 12:  # Dodecagram
            return 5
        else:
            # For other star polygons, use a skip value that:
            # 1. Is coprime to num_outer (for a proper star)
            # 2. Is approximately num_outer/2 (for visual appeal)
            skip = self.points // 2
            # Adjust if skip is even and num_points is even (not coprime)
            if skip % 2 == 0 and self.points % 2 == 0:
                skip = skip - 1
            return skip

    def _add_dots_on_line_segments(
        self, 
        coordinates: List[Tuple[float, float, int, int]], 
        outer_vertices: List[Tuple[float, float]], 
        inner_vertices: List[Tuple[float, float]], 
        layer: int, 
        dot_number: int
    ) -> int:
        """Add dots along the line segments of the star.
        
        Args:
            coordinates: List of coordinates to add to
            outer_vertices: List of outer vertex coordinates
            inner_vertices: List of inner vertex coordinates
            layer: Current layer number
            dot_number: Current dot number
            
        Returns:
            Updated dot number
        """
        # Calculate how many dots to add on each line segment for this layer
        # For a p-pointed star with n layers, the mathematical definition
        # requires exactly (n-2) dots between each inner and outer vertex
        dots_per_line_segment = layer - 2
        
        # For a complete star pattern, we need to place dots along ALL the line segments
        # that form the star. For a p-pointed star, there are 2p line segments total:
        # - Each line segment connects an outer vertex to an inner vertex
        # - For a pentagram (p=5), there are 10 line segments forming the classic star shape
        
        # For each line segment, we need to place (n-2) dots for a star of index n
        # - At index 3: 1 dot in the middle of each line segment
        # - At index 4: 2 dots evenly spaced along each line segment
        # - At index 5: 3 dots evenly spaced along each line segment
        
        # Create a list of all line segments in the star
        line_segments = []
        
        # For each point of the star, add the two line segments that connect
        # the outer vertex to its adjacent inner vertices
        for i in range(self.points):
            # Get the current outer vertex
            outer_vertex = outer_vertices[i]
            
            # First line segment: to inner vertex with same index
            inner_vertex1 = inner_vertices[i]
            line_segments.append((outer_vertex, inner_vertex1))
            
            # Second line segment: to previous inner vertex
            prev_idx = (i - 1) % self.points
            inner_vertex2 = inner_vertices[prev_idx]
            line_segments.append((outer_vertex, inner_vertex2))
        
        print(f"DEBUG: Created {len(line_segments)} line segments for a {self.points}-pointed star")
        
        # Now place dots along each line segment
        for start_vertex, end_vertex in line_segments:
            start_x, start_y = start_vertex
            end_x, end_y = end_vertex
            
            # Calculate the direction vector of the line segment
            dir_x = end_x - start_x
            dir_y = end_y - start_y
            
            # Calculate the length of the line segment
            length = math.sqrt(dir_x**2 + dir_y**2)
            
            # Place dots evenly along the line segment
            if length > 0:
                # Normalize the direction vector
                dir_x /= length
                dir_y /= length
                
                # Place (n-2) dots evenly along the line segment
                dots_placed = 0
                for j in range(1, dots_per_line_segment + 1):
                    # Calculate the distance from the start vertex for this dot
                    # This formula places dots evenly along the line segment
                    distance = (j / (dots_per_line_segment + 1)) * length
                    
                    # Calculate the exact position
                    x = start_x + distance * dir_x
                    y = start_y + distance * dir_y
                    
                    dot_number += 1
                    coordinates.append((x, y, layer, dot_number))
                    dots_placed += 1
                
                print(f"DEBUG: Placed {dots_placed} dots on line segment from ({start_x:.2f}, {start_y:.2f}) to ({end_x:.2f}, {end_y:.2f})")
        
        return dot_number
        
    def _get_inner_radius(self, scale: float) -> float:
        """Get the inner radius for this star type.

        Args:
            scale: Scale factor for the star

        Returns:
            Inner radius
        """
        if self.points == 5:  # Pentagram
            return scale * 0.382  # Golden ratio for pentagram
        elif self.points == 6:  # Hexagram
            return scale * 0.5
        elif self.points == 7:  # Heptagram
            return scale * 0.435
        elif self.points == 8:  # Octagram
            return scale * 0.414
        else:
            # For other star polygons, use an approximation
            # The formula sin(π/n) / sin(π*(1-2/n)) gives a good approximation
            # for the ratio of inner to outer radius
            n = self.points
            return scale * (math.sin(math.pi/n) / math.sin(math.pi*(1-2/n)))

    def get_formula_string(self) -> str:
        """Get the formula for the current star number as a string.

        Returns:
            Formula string
        """
        p = self.points
        n = self.index
        return f"S_{p}({n}) = {p}×{n}×({n}-1) + 1 = {self.calculate_value()}"

    def calculate_gnomon(self, n: int) -> int:
        """Calculate the number of dots in the nth gnomon.

        Args:
            n: The gnomon index (1-based)

        Returns:
            Number of dots in the nth gnomon
        """
        # For a p-pointed star, the formula for the nth gnomon is:
        # G_n = p * (2n - 1)
        # This is derived from the difference between consecutive star numbers:
        # S_n - S_(n-1) = p*n*(n-1) + 1 - [p*(n-1)*(n-2) + 1] = p*(2n-1)
        #
        # This matches our geometric understanding:
        # - For n=1 (center dot): G_1 = 1 dot
        # - For n=2 (basic star): G_2 = 2p dots (p outer vertices + p inner vertices)
        # - For n=3+: G_n = 2p dots (one additional dot on each of the 2p rays)

        return self.points * (2*n - 1)

    def get_star_name(self) -> str:
        """Get the name of the current star number type.

        Returns:
            Name of the star number type
        """
        star_names = {
            5: "Pentagram",
            6: "Hexagram",
            7: "Heptagram",
            8: "Octagram",
            9: "Nonagram",
            10: "Decagram",
            11: "Hendecagram",
            12: "Dodecagram"
        }

        if self.points in star_names:
            return f"{star_names[self.points]}"
        else:
            return f"{self.points}-pointed Star"
