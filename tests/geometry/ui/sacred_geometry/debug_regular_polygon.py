"""Debug script for regular polygon vertices."""

import math
from geometry.ui.sacred_geometry.model import Point
from geometry.ui.sacred_geometry.tools import RegularPolygonTool

def main():
    """Print the vertices of a regular polygon."""
    tool = RegularPolygonTool()
    tool.set_sides(6)
    tool.set_orientation(RegularPolygonTool.ORIENTATION_VERTEX_TOP)
    
    center = Point(0, 0)
    radius = 100
    
    vertices = tool._calculate_regular_polygon_vertices(center, radius)
    
    print(f"Hexagon with vertex at top, {len(vertices)} vertices:")
    for i, vertex in enumerate(vertices):
        print(f"Vertex {i}: ({vertex.x:.5f}, {vertex.y:.5f})")
    
    # Calculate expected values
    print("\nExpected values:")
    for i in range(6):
        angle = 2 * math.pi * i / 6 + math.pi / 2
        x = radius * math.cos(angle)
        y = -radius * math.sin(angle)  # Note the negative sign for y
        print(f"Vertex {i}: ({x:.5f}, {y:.5f})")

if __name__ == "__main__":
    main()
