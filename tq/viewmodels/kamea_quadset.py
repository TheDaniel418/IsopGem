"""
Purpose: Provides quadset calculation functionality for the Kamea of Maut panel

This file is part of the tq pillar and serves as a utility component.
It is responsible for calculating primary and secondary quadsets with clear
separation of concerns.

Key components:
- KameaQuadsetCalculator: Class for calculating different types of quadsets

Dependencies:
- tq.services.kamea_service: For Kamea-related business logic

Related files:
- tq/viewmodels/kamea_viewmodel.py: View model that uses this calculator
- tq/ui/panels/kamea_of_maut_panel.py: UI panel that displays quadsets
"""

from typing import List, Tuple

from loguru import logger

from tq.services.kamea_service import KameaService


class KameaQuadsetCalculator:
    """Calculator for Kamea quadsets with clear separation of concerns."""

    def __init__(self, kamea_service: KameaService):
        """Initialize the calculator.

        Args:
            kamea_service: The Kamea service to use
        """
        self.kamea_service = kamea_service

    def calculate_primary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the primary quadset grid coordinates.

        The primary quadset consists of the original cell and its quadset partners.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (row, col) tuples for the primary quadset
        """
        # Get the quadset coordinates from the service
        quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
        logger.debug(
            f"Primary quadset Cartesian coordinates for ({x}, {y}): {quadset_coords}"
        )

        # Convert to grid positions
        grid_coords = []
        for qx, qy in quadset_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(qx, qy)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                grid_coords.append((grid_row, grid_col))
                logger.debug(
                    f"Added primary cell at ({grid_row}, {grid_col}) from Cartesian ({qx}, {qy})"
                )

        logger.debug(f"Primary quadset: {len(grid_coords)} cells")
        return grid_coords

    def calculate_secondary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the secondary quadset grid coordinates.

        The secondary quadset consists of the direct diagonal cells.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (row, col) tuples for the secondary quadset
        """
        # Define the secondary quadset coordinates
        if x == 0 and y == 0:
            # Origin cell - empty secondary quadset
            logger.debug("Origin cell: Empty secondary quadset")
            return []
        elif x == 0 or y == 0:
            # Axis cells - empty secondary quadset
            logger.debug("Axis cell: Empty secondary quadset")
            return []

        # For regular cells, calculate the direct diagonal
        secondary_coords = [
            (y, x),  # Conrune cell
            (-x, -y),  # Opposite cell
            (-y, -x),  # Opposite conrune cell
            (x, -y),  # Additional cell
            (-x, y),  # Additional cell
            (y, -x),  # Additional cell
            (-y, x),  # Additional cell
        ]

        logger.debug(
            f"Secondary quadset Cartesian coordinates for ({x}, {y}): {secondary_coords}"
        )

        # Convert to grid positions
        grid_coords = []
        for qx, qy in secondary_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(qx, qy)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                grid_coords.append((grid_row, grid_col))
                logger.debug(
                    f"Added secondary cell at ({grid_row}, {grid_col}) from Cartesian ({qx}, {qy})"
                )

        logger.debug(f"Secondary quadset: {len(grid_coords)} cells")
        return grid_coords

    def calculate_quadset_sum(self, grid_coords: List[Tuple[int, int]]) -> int:
        """Calculate the sum of values in the given grid coordinates.

        Args:
            grid_coords: List of (row, col) tuples

        Returns:
            Sum of decimal values
        """
        total_sum = 0
        for grid_row, grid_col in grid_coords:
            value = self.kamea_service.get_kamea_value(grid_row, grid_col, True)
            if value is not None:
                total_sum += value
        return total_sum

    def ensure_no_overlap(
        self,
        primary_cells: List[Tuple[int, int]],
        secondary_cells: List[Tuple[int, int]],
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Ensure there is no overlap between primary and secondary cells.

        Args:
            primary_cells: List of primary quadset cells
            secondary_cells: List of secondary quadset cells

        Returns:
            Tuple of (primary_cells, secondary_cells) with no overlap
        """
        # Convert primary cells to a set for efficient lookups
        primary_set = set(primary_cells)

        # Remove any secondary cells that are also in the primary set
        secondary_cells = [cell for cell in secondary_cells if cell not in primary_set]

        logger.debug(
            f"After ensuring no overlap: {len(primary_cells)} primary cells, {len(secondary_cells)} secondary cells"
        )
        return primary_cells, secondary_cells
