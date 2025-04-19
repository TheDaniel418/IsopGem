"""
Platonic Solid Calculator.

This module provides a calculator for computing properties of Platonic solids.
"""

import math
from enum import Enum, auto
from typing import Optional


class PlatonicSolidType(Enum):
    """Types of Platonic solids."""

    TETRAHEDRON = auto()
    CUBE = auto()
    OCTAHEDRON = auto()
    DODECAHEDRON = auto()
    ICOSAHEDRON = auto()
    CUBOCTAHEDRON = auto()


class PlatonicSolidCalculator:
    """Calculator for Platonic solids properties."""

    def __init__(self, solid_type: PlatonicSolidType = PlatonicSolidType.TETRAHEDRON):
        """Initialize the calculator with a solid type.

        Args:
            solid_type: The type of Platonic solid to calculate properties for.
        """
        self.solid_type = solid_type
        self.edge_length = 1.0  # Default edge length

        # Constants for calculations
        self.PHI = (1 + math.sqrt(5)) / 2  # Golden ratio

    def set_solid_type(self, solid_type: PlatonicSolidType) -> None:
        """Set the solid type.

        Args:
            solid_type: The type of Platonic solid.
        """
        self.solid_type = solid_type

    def set_edge_length(self, edge_length: float) -> None:
        """Set the edge length.

        Args:
            edge_length: The length of each edge.
        """
        if edge_length <= 0:
            raise ValueError("Edge length must be positive")
        self.edge_length = edge_length

    def get_face_count(self) -> int:
        """Get the number of faces.

        Returns:
            The number of faces.
        """
        face_counts = {
            PlatonicSolidType.TETRAHEDRON: 4,
            PlatonicSolidType.CUBE: 6,
            PlatonicSolidType.OCTAHEDRON: 8,
            PlatonicSolidType.DODECAHEDRON: 12,
            PlatonicSolidType.ICOSAHEDRON: 20,
            PlatonicSolidType.CUBOCTAHEDRON: 14,
        }
        return face_counts[self.solid_type]

    def get_vertex_count(self) -> int:
        """Get the number of vertices.

        Returns:
            The number of vertices.
        """
        vertex_counts = {
            PlatonicSolidType.TETRAHEDRON: 4,
            PlatonicSolidType.CUBE: 8,
            PlatonicSolidType.OCTAHEDRON: 6,
            PlatonicSolidType.DODECAHEDRON: 20,
            PlatonicSolidType.ICOSAHEDRON: 12,
            PlatonicSolidType.CUBOCTAHEDRON: 12,
        }
        return vertex_counts[self.solid_type]

    def get_edge_count(self) -> int:
        """Get the number of edges.

        Returns:
            The number of edges.
        """
        edge_counts = {
            PlatonicSolidType.TETRAHEDRON: 6,
            PlatonicSolidType.CUBE: 12,
            PlatonicSolidType.OCTAHEDRON: 12,
            PlatonicSolidType.DODECAHEDRON: 30,
            PlatonicSolidType.ICOSAHEDRON: 30,
            PlatonicSolidType.CUBOCTAHEDRON: 24,
        }
        return edge_counts[self.solid_type]

    def get_face_type(self) -> str:
        """Get the type of face.

        Returns:
            The type of face.
        """
        face_types = {
            PlatonicSolidType.TETRAHEDRON: "Equilateral Triangle",
            PlatonicSolidType.CUBE: "Square",
            PlatonicSolidType.OCTAHEDRON: "Equilateral Triangle",
            PlatonicSolidType.DODECAHEDRON: "Regular Pentagon",
            PlatonicSolidType.ICOSAHEDRON: "Equilateral Triangle",
            PlatonicSolidType.CUBOCTAHEDRON: "8 triangles, 6 squares",
        }
        return face_types[self.solid_type]

    def get_vertex_configuration(self) -> str:
        """Get the vertex configuration.

        Returns:
            The vertex configuration.
        """
        vertex_configs = {
            PlatonicSolidType.TETRAHEDRON: "3 triangles at each vertex",
            PlatonicSolidType.CUBE: "3 squares at each vertex",
            PlatonicSolidType.OCTAHEDRON: "4 triangles at each vertex",
            PlatonicSolidType.DODECAHEDRON: "3 pentagons at each vertex",
            PlatonicSolidType.ICOSAHEDRON: "5 triangles at each vertex",
            PlatonicSolidType.CUBOCTAHEDRON: "2 triangles + 2 squares at each vertex",
        }
        return vertex_configs[self.solid_type]

    def get_schlaefli_symbol(self) -> str:
        """Get the Schläfli symbol.

        Returns:
            The Schläfli symbol.
        """
        symbols = {
            PlatonicSolidType.TETRAHEDRON: "{3, 3}",
            PlatonicSolidType.CUBE: "{4, 3}",
            PlatonicSolidType.OCTAHEDRON: "{3, 4}",
            PlatonicSolidType.DODECAHEDRON: "{5, 3}",
            PlatonicSolidType.ICOSAHEDRON: "{3, 5}",
            PlatonicSolidType.CUBOCTAHEDRON: "r{4,3}",
        }
        return symbols[self.solid_type]

    def get_dual_polyhedron(self) -> str:
        """Get the dual polyhedron.

        Returns:
            The name of the dual polyhedron.
        """
        duals = {
            PlatonicSolidType.TETRAHEDRON: "Tetrahedron (self-dual)",
            PlatonicSolidType.CUBE: "Octahedron",
            PlatonicSolidType.OCTAHEDRON: "Cube",
            PlatonicSolidType.DODECAHEDRON: "Icosahedron",
            PlatonicSolidType.ICOSAHEDRON: "Dodecahedron",
            PlatonicSolidType.CUBOCTAHEDRON: "Rhombic dodecahedron",
        }
        return duals[self.solid_type]

    def get_face_area(self) -> float:
        """Get the area of a single face.

        Returns:
            The area of a single face.
        """
        a = self.edge_length

        if self.solid_type in [
            PlatonicSolidType.TETRAHEDRON,
            PlatonicSolidType.OCTAHEDRON,
            PlatonicSolidType.ICOSAHEDRON,
        ]:
            # Equilateral triangle
            return (math.sqrt(3) / 4) * a**2
        elif self.solid_type == PlatonicSolidType.CUBE:
            # Square
            return a**2
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            # Regular pentagon
            return (1 / 4) * math.sqrt(25 + 10 * math.sqrt(5)) * a**2
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            # Return average face area (8 triangles, 6 squares)
            return (8 * (math.sqrt(3) / 4) * a**2 + 6 * a**2) / 14

        return 0.0

    def get_total_surface_area(self) -> float:
        """Get the total surface area.

        Returns:
            The total surface area.
        """
        a = self.edge_length
        if self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            return 2 * (2 + math.sqrt(3)) * a**2
        return self.get_face_count() * self.get_face_area()

    def get_volume(self) -> float:
        """Get the volume.

        Returns:
            The volume.
        """
        a = self.edge_length

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            return (math.sqrt(2) / 12) * a**3
        elif self.solid_type == PlatonicSolidType.CUBE:
            return a**3
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            return (math.sqrt(2) / 3) * a**3
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            return (1 / 4) * (15 + 7 * math.sqrt(5)) * a**3
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            return (5 / 12) * (3 + math.sqrt(5)) * a**3
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            return (5 * math.sqrt(2) / 3) * a**3

        return 0.0

    def get_insphere_radius(self) -> float:
        """Get the insphere radius.

        Returns:
            The insphere radius.
        """
        a = self.edge_length

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            return a / (2 * math.sqrt(6))
        elif self.solid_type == PlatonicSolidType.CUBE:
            return a / 2
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            return a * math.sqrt(6) / 6
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            return a * math.sqrt(250 + 110 * math.sqrt(5)) / 20
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            return a * math.sqrt(10 + 2 * math.sqrt(5)) / 10
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            return a * (1 + math.sqrt(2)) / 2

        return 0.0

    def get_midsphere_radius(self) -> float:
        """Get the midsphere radius.

        Returns:
            The midsphere radius.
        """
        a = self.edge_length

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            return a / math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.CUBE:
            return a * math.sqrt(2) / 2
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            return a / math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            return a * math.sqrt(10 + 2 * math.sqrt(5)) / 4
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            return a * (1 + math.sqrt(5)) / 4
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            return a * math.sqrt(2) / 2

        return 0.0

    def get_circumsphere_radius(self) -> float:
        """Get the circumsphere radius.

        Returns:
            The circumsphere radius.
        """
        a = self.edge_length

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            return a * math.sqrt(6) / 4
        elif self.solid_type == PlatonicSolidType.CUBE:
            return a * math.sqrt(3) / 2
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            return a * math.sqrt(2) / 2
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            return a * math.sqrt(3) * (1 + math.sqrt(5)) / 4
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            return a * math.sqrt(10 + 2 * math.sqrt(5)) / 4
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            return a
        return 0.0

    def get_sphere_surface_area(self, radius: float) -> float:
        """Get the surface area of a sphere.

        Args:
            radius: The radius of the sphere.

        Returns:
            The surface area of the sphere.
        """
        return 4 * math.pi * radius**2

    def get_sphere_volume(self, radius: float) -> float:
        """Get the volume of a sphere.

        Args:
            radius: The radius of the sphere.

        Returns:
            The volume of the sphere.
        """
        return (4 / 3) * math.pi * radius**3

    def get_insphere_surface_area(self) -> float:
        """Get the insphere surface area.

        Returns:
            The insphere surface area.
        """
        return self.get_sphere_surface_area(self.get_insphere_radius())

    def get_insphere_volume(self) -> float:
        """Get the insphere volume.

        Returns:
            The insphere volume.
        """
        return self.get_sphere_volume(self.get_insphere_radius())

    def get_midsphere_surface_area(self) -> float:
        """Get the midsphere surface area.

        Returns:
            The midsphere surface area.
        """
        return self.get_sphere_surface_area(self.get_midsphere_radius())

    def get_midsphere_volume(self) -> float:
        """Get the midsphere volume.

        Returns:
            The midsphere volume.
        """
        return self.get_sphere_volume(self.get_midsphere_radius())

    def get_circumsphere_surface_area(self) -> float:
        """Get the circumsphere surface area.

        Returns:
            The circumsphere surface area.
        """
        return self.get_sphere_surface_area(self.get_circumsphere_radius())

    def get_circumsphere_volume(self) -> float:
        """Get the circumsphere volume.

        Returns:
            The circumsphere volume.
        """
        return self.get_sphere_volume(self.get_circumsphere_radius())

    def get_dihedral_angle(self) -> float:
        """Get the dihedral angle in degrees.

        Returns:
            The dihedral angle in degrees.
        """
        if self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            # Return triangle-square dihedral angle (the non-90 one)
            return math.degrees(math.acos(-1 / 3))
        angles = {
            PlatonicSolidType.TETRAHEDRON: math.acos(1 / 3),
            PlatonicSolidType.CUBE: math.pi / 2,  # 90 degrees
            PlatonicSolidType.OCTAHEDRON: math.acos(-1 / 3),
            PlatonicSolidType.DODECAHEDRON: math.acos(-math.sqrt(5) / 5),
            PlatonicSolidType.ICOSAHEDRON: math.acos(-math.sqrt(5) / 3),
        }

        # Convert to degrees
        return math.degrees(angles[self.solid_type])

    def get_face_diagonal(self) -> Optional[float]:
        """Get the face diagonal (only for cube).

        Returns:
            The face diagonal or None if not applicable.
        """
        if self.solid_type == PlatonicSolidType.CUBE:
            return self.edge_length * math.sqrt(2)
        return None

    def get_space_diagonal(self) -> Optional[float]:
        """Get the space diagonal (only for cube).

        Returns:
            The space diagonal or None if not applicable.
        """
        if self.solid_type == PlatonicSolidType.CUBE:
            return self.edge_length * math.sqrt(3)
        return None

    def get_height(self) -> float:
        """Get the height (distance from center to any face).

        Returns:
            The height.
        """
        # This is the same as the insphere radius
        return self.get_insphere_radius()

    def get_symmetry_group(self) -> str:
        """Get the symmetry group.

        Returns:
            The symmetry group.
        """
        groups = {
            PlatonicSolidType.TETRAHEDRON: "Td (tetrahedral)",
            PlatonicSolidType.CUBE: "Oh (octahedral)",
            PlatonicSolidType.OCTAHEDRON: "Oh (octahedral)",
            PlatonicSolidType.DODECAHEDRON: "Ih (icosahedral)",
            PlatonicSolidType.ICOSAHEDRON: "Ih (icosahedral)",
            PlatonicSolidType.CUBOCTAHEDRON: "Oh (octahedral)",
        }
        return groups[self.solid_type]

    def calculate_from_insphere_radius(self, radius: float) -> None:
        """Calculate edge length from insphere radius.

        Args:
            radius: The insphere radius.
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = radius * 2 * math.sqrt(6)
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = radius * 2
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = radius * 6 / math.sqrt(6)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = radius * 20 / math.sqrt(250 + 110 * math.sqrt(5))
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = radius * 10 / math.sqrt(10 + 2 * math.sqrt(5))
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = radius * 2 * (1 + math.sqrt(2))

    def calculate_from_midsphere_radius(self, radius: float) -> None:
        """Calculate edge length from midsphere radius.

        Args:
            radius: The midsphere radius.
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = radius * math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = radius * 2 / math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = radius * math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = radius * 4 / math.sqrt(10 + 2 * math.sqrt(5))
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = radius * 4 / (1 + math.sqrt(5))
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = radius * 2 * math.sqrt(2)

    def calculate_from_circumsphere_radius(self, radius: float) -> None:
        """Calculate edge length from circumsphere radius.

        Args:
            radius: The circumsphere radius.
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = radius * 4 / math.sqrt(6)
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = radius * 2 / math.sqrt(3)
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = radius * 2 / math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = radius * 4 / (math.sqrt(3) * (1 + math.sqrt(5)))
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = radius * 4 / math.sqrt(10 + 2 * math.sqrt(5))
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = radius * 2

    def calculate_from_volume(self, volume: float) -> None:
        """Calculate edge length from volume.

        Args:
            volume: The volume.
        """
        if volume <= 0:
            raise ValueError("Volume must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = (volume * 12 / math.sqrt(2)) ** (1 / 3)
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = volume ** (1 / 3)
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = (volume * 3 / math.sqrt(2)) ** (1 / 3)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = (volume * 4 / (15 + 7 * math.sqrt(5))) ** (1 / 3)
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = (volume * 12 / (5 * (3 + math.sqrt(5)))) ** (1 / 3)
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = (volume * 6 / (2 + math.sqrt(3))) ** (1 / 3)

    def calculate_from_surface_area(self, area: float) -> None:
        """Calculate edge length from total surface area.

        Args:
            area: The total surface area.
        """
        if area <= 0:
            raise ValueError("Surface area must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = math.sqrt(area / math.sqrt(3))
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = math.sqrt(area / 6)
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = math.sqrt(area / (2 * math.sqrt(3)))
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = math.sqrt(area / (3 * math.sqrt(25 + 10 * math.sqrt(5))))
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = math.sqrt(area / (5 * math.sqrt(3)))
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = math.sqrt(area / (2 * (2 + math.sqrt(3))))

    def calculate_from_face_area(self, area: float) -> None:
        """Calculate edge length from face area.

        Args:
            area: The area of a single face.
        """
        if area <= 0:
            raise ValueError("Face area must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = math.sqrt(area * 4 / math.sqrt(3))
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = math.sqrt(area)
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = math.sqrt(area * 4 / math.sqrt(3))
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            self.edge_length = math.sqrt(area * 4 / (math.sqrt(25 + 10 * math.sqrt(5))))
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            self.edge_length = math.sqrt(area * 4 / math.sqrt(3))
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = math.sqrt(area * 4 / (2 * (2 + math.sqrt(3))))

    def calculate_from_face_diagonal(self, diagonal: float) -> None:
        """Calculate edge length from face diagonal (cube only).

        Args:
            diagonal: The face diagonal.
        """
        if diagonal <= 0:
            raise ValueError("Face diagonal must be positive")

        if self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = diagonal / math.sqrt(2)
        else:
            raise ValueError("Face diagonal is only defined for cubes")

    def calculate_from_space_diagonal(self, diagonal: float) -> None:
        """Calculate edge length from space diagonal (cube only).

        Args:
            diagonal: The space diagonal.
        """
        if diagonal <= 0:
            raise ValueError("Space diagonal must be positive")

        if self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = diagonal / math.sqrt(3)
        else:
            raise ValueError("Space diagonal is only defined for cubes")

    def calculate_from_height(self, height: float) -> None:
        """Calculate edge length from height.

        Args:
            height: The height of the solid.
        """
        if height <= 0:
            raise ValueError("Height must be positive")

        if self.solid_type == PlatonicSolidType.TETRAHEDRON:
            self.edge_length = height * math.sqrt(6) / 3
        elif self.solid_type == PlatonicSolidType.CUBE:
            self.edge_length = height
        elif self.solid_type == PlatonicSolidType.OCTAHEDRON:
            self.edge_length = height / math.sqrt(2)
        elif self.solid_type == PlatonicSolidType.DODECAHEDRON:
            # For dodecahedron, height is approximately 2.226 * edge_length
            self.edge_length = height / 2.226
        elif self.solid_type == PlatonicSolidType.ICOSAHEDRON:
            # For icosahedron, height is approximately 2.478 * edge_length
            self.edge_length = height / 2.478
        elif self.solid_type == PlatonicSolidType.CUBOCTAHEDRON:
            self.edge_length = height / math.sqrt(2)
