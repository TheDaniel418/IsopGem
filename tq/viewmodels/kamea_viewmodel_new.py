"""
Purpose: Provides a view model for the Kamea of Maut panel

This file is part of the tq pillar and serves as a view model component.
It is responsible for mediating between the KameaService and the UI components,
managing UI state and coordinating operations.

Key components:
- KameaViewModel: Main view model class for Kamea-related UI operations

Dependencies:
- tq.services.kamea_service: For Kamea-related business logic

Related files:
- tq/ui/panels/kamea_of_maut_panel.py: UI panel that uses this view model
- tq/ui/widgets/kamea_grid_widget.py: Grid widget that displays the Kamea
- tq/services/kamea_service.py: Service that provides business logic
"""

from typing import Dict, List, Optional, Tuple, Union

from loguru import logger

from tq.services.kamea_service import KameaService


class KameaViewModel:
    """View model for the Kamea of Maut panel."""

    def __init__(self, kamea_service: Optional[KameaService] = None):
        """Initialize the view model.

        Args:
            kamea_service: The Kamea service to use (creates a new one if None)
        """
        self.kamea_service = kamea_service or KameaService()

        # UI state
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.highlighted_cells: List[Tuple[int, int]] = []
        self.secondary_highlighted_cells: List[Tuple[int, int]] = []
        self.vectors: List[Tuple[int, int, int, int, int]] = []
        self.show_vectors: bool = False
        self.color_by_diff: bool = True
        self.decimal_mode: bool = True
        self.min_vector_diff: int = 0
        self.max_vector_diff: int = 1

    def select_cell(
        self, row: int, col: int
    ) -> Dict[str, Union[int, str, Tuple[int, int]]]:
        """Handle cell selection.

        Args:
            row: The selected row
            col: The selected column

        Returns:
            Dictionary with cell information
        """
        self.selected_cell = (row, col)

        # Get cell values
        decimal_value = self.kamea_service.get_kamea_value(row, col, True)
        ternary_value = self.kamea_service.get_kamea_value(row, col, False)

        # Ensure ternary value is padded to 6 digits
        if ternary_value is not None:
            ternary_value = str(ternary_value).zfill(6)

        # Convert to Cartesian coordinates
        x, y = self.kamea_service.convert_grid_to_cartesian(row, col)

        # Calculate Kamea Locator
        kamea_locator = ""
        if ternary_value:
            kamea_locator = self.kamea_service.calculate_kamea_locator(ternary_value)

        # Return cell information
        return {
            "row": row,
            "col": col,
            "x": x,
            "y": y,
            "decimal_value": decimal_value,
            "ternary_value": ternary_value,
            "kamea_locator": kamea_locator,
        }

    def show_quadset(
        self, x: int, y: int
    ) -> Dict[str, Union[List[Tuple[int, int]], int]]:
        """Show the quadset for a cell.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            Dictionary with quadset information
        """
        # Clear any existing highlights
        self.clear_highlights()

        # Calculate primary quadset
        primary_grid_coords = self._calculate_primary_quadset(x, y)

        # Calculate secondary quadset (completely separate from primary)
        secondary_grid_coords = self._calculate_secondary_quadset(x, y)

        # Calculate sums
        quad_sum = self._calculate_sum(primary_grid_coords)
        secondary_sum = self._calculate_sum(secondary_grid_coords)

        # Update highlighted cells
        self.highlighted_cells = primary_grid_coords
        self.secondary_highlighted_cells = secondary_grid_coords

        # Return quadset information
        return {
            "primary_grid_coords": primary_grid_coords,
            "secondary_grid_coords": secondary_grid_coords,
            "quad_sum": quad_sum,
            "secondary_sum": secondary_sum,
            "octa_sum": quad_sum + secondary_sum,
        }

    def _calculate_primary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the primary quadset grid coordinates.

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

    def _calculate_secondary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the secondary quadset grid coordinates.

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

        # For regular cells, include the direct diagonal and additional cells
        secondary_coords = [
            # Direct diagonal (excluding the original cell which is in the primary quadset)
            (y, x),  # Conrune cell
            (-x, -y),  # Opposite cell
            (-y, -x),  # Opposite conrune cell
            # Additional cells to complete the octaset
            (y, -x),  # Additional cell 1
            (-y, x),  # Additional cell 2
            (x, -y),  # Additional cell 3
            (-x, y),  # Additional cell 4
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

    def _calculate_sum(self, grid_coords: List[Tuple[int, int]]) -> int:
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

    def show_difference_vectors(
        self, min_diff: int = 0, max_diff: int = 364
    ) -> Dict[str, Union[List[Tuple[int, int, int, int, int]], int]]:
        """Show difference vectors.

        Args:
            min_diff: Minimum difference to include
            max_diff: Maximum difference to include

        Returns:
            Dictionary with vector information
        """
        # Calculate the difference vectors
        vectors = self.kamea_service.calculate_difference_vectors(min_diff, max_diff)

        # Update vectors
        self.vectors = vectors
        self.show_vectors = True

        # Calculate min and max differences for color scaling
        if vectors:
            self.min_vector_diff = min(v[4] for v in vectors)
            self.max_vector_diff = max(v[4] for v in vectors)
        else:
            self.min_vector_diff = 0
            self.max_vector_diff = 1

        # Return vector information
        return {
            "vectors": vectors,
            "count": len(vectors),
            "min_diff": self.min_vector_diff,
            "max_diff": self.max_vector_diff,
        }

    def show_quadset_vectors(
        self, x: int, y: int
    ) -> Dict[
        str, Union[List[Tuple[int, int, int, int, int]], List[Tuple[int, int]], int]
    ]:
        """Show vectors for a quadset.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            Dictionary with quadset vector information
        """
        # Get the quadset coordinates
        quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)

        # Convert to grid positions
        quadset_grid_positions = []
        for qx, qy in quadset_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(qx, qy)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                quadset_grid_positions.append((grid_row, grid_col))

        # Update highlighted cells
        self.highlighted_cells = quadset_grid_positions
        self.secondary_highlighted_cells = []

        # Calculate vectors
        vectors = self.kamea_service.get_quadset_vectors(x, y)

        # Update vectors
        self.vectors = vectors
        self.show_vectors = True

        # Calculate min and max differences for color scaling
        if vectors:
            self.min_vector_diff = min(v[4] for v in vectors)
            self.max_vector_diff = max(v[4] for v in vectors)
        else:
            self.min_vector_diff = 0
            self.max_vector_diff = 1

        # Return quadset vector information
        return {
            "quadset_grid_positions": quadset_grid_positions,
            "vectors": vectors,
            "count": len(vectors),
        }

    def clear_highlights(self) -> None:
        """Clear all cell highlights."""
        logger.debug("Clearing all highlights")
        self.highlighted_cells = []
        self.secondary_highlighted_cells = []

    def clear_vectors(self) -> None:
        """Clear the vector field."""
        self.show_vectors = False

    def set_view_mode(self, decimal_mode: bool) -> None:
        """Set the view mode.

        Args:
            decimal_mode: Whether to show decimal values (True) or ternary (False)
        """
        self.decimal_mode = decimal_mode

    def show_bigram_analysis(self, row: int, col: int) -> Dict[str, Union[str, int]]:
        """Show bigram analysis for a cell.

        Args:
            row: The row index
            col: The column index

        Returns:
            Dictionary with bigram information
        """
        # Get the ternary value
        ternary_value = self.kamea_service.get_kamea_value(row, col, False)
        if ternary_value is None:
            return {"error": "No ternary value found"}

        # Extract bigrams
        bigram1, bigram2, bigram3 = self.kamea_service.extract_bigrams(ternary_value)

        # Convert to decimal for easier understanding
        bigram1_dec = int(bigram1, 3)  # Base 3 to decimal
        bigram2_dec = int(bigram2, 3)
        bigram3_dec = int(bigram3, 3)

        # Return bigram information
        return {
            "ternary_value": str(ternary_value).zfill(6),
            "bigram1": bigram1,
            "bigram2": bigram2,
            "bigram3": bigram3,
            "bigram1_dec": bigram1_dec,
            "bigram2_dec": bigram2_dec,
            "bigram3_dec": bigram3_dec,
        }

    def highlight_cells_with_bigram(
        self, bigram_index: int, bigram_value: str
    ) -> Dict[str, Union[List[Tuple[int, int]], int]]:
        """Highlight cells with a matching bigram.

        Args:
            bigram_index: 0 for first bigram, 1 for second, 2 for third
            bigram_value: The bigram value to match

        Returns:
            Dictionary with highlight information
        """
        # Find matching cells
        matching_cells = self.kamea_service.find_cells_with_bigram(
            bigram_index, bigram_value
        )

        # Update highlighted cells
        self.highlighted_cells = matching_cells
        self.secondary_highlighted_cells = []

        # Calculate sum
        total_sum = 0
        for r, c in matching_cells:
            value = self.kamea_service.get_kamea_value(r, c, True)
            if value is not None:
                total_sum += value

        # Return highlight information
        return {
            "matching_cells": matching_cells,
            "count": len(matching_cells),
            "sum": total_sum,
            "bigram_index": bigram_index,
            "bigram_value": bigram_value,
        }
