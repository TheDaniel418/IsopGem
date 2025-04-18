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

from tq.services.kamea_service import KameaService
from tq.viewmodels.kamea_quadset import KameaQuadsetCalculator


class KameaViewModel:
    """View model for the Kamea of Maut panel."""

    def __init__(self, kamea_service: Optional[KameaService] = None):
        """Initialize the view model.

        Args:
            kamea_service: The Kamea service to use (creates a new one if None)
        """
        self.kamea_service = kamea_service or KameaService()

        # Create the quadset calculator
        self.quadset_calculator = KameaQuadsetCalculator(self.kamea_service)

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

    def _convert_cartesian_to_grid_coords(
        self, cartesian_coords: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Convert Cartesian coordinates to grid coordinates.

        Args:
            cartesian_coords: List of (x, y) Cartesian coordinates

        Returns:
            List of (row, col) grid coordinates that are within the grid bounds
        """
        grid_coords = []
        for x, y in cartesian_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(x, y)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                grid_coords.append((grid_row, grid_col))
        return grid_coords

    def calculate_primary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the primary quadset grid coordinates.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (row, col) tuples for the primary quadset
        """
        # Calculate primary quadset (using the service)
        quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
        primary_grid_coords = self._convert_cartesian_to_grid_coords(quadset_coords)

        # Removed debug logging

        return primary_grid_coords

    def calculate_secondary_quadset(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Calculate the secondary quadset grid coordinates.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (row, col) tuples for the secondary quadset
        """
        # Skip for origin and axis cells
        if x == 0 or y == 0:
            return []

        # Get the primary quadset to ensure no overlap
        primary_grid_coords = self.calculate_primary_quadset(x, y)

        # For regular cells, calculate only the specific cells for the secondary quadset
        # These are the cells that should be colored in pastel green
        # The direct diagonal consists of specific cells that are not in the primary quadset
        secondary_coords = [
            (-y, -x),  # Opposite conrune cell
            (y, -x),  # Additional cell 1
            (-y, x),  # Additional cell 2
            (y, x),  # Conrune cell
        ]

        # Removed debug logging

        # Convert to grid coordinates
        secondary_grid_coords = self._convert_cartesian_to_grid_coords(secondary_coords)

        # Remove any cells that are also in the primary quadset
        secondary_grid_coords = [
            cell for cell in secondary_grid_coords if cell not in primary_grid_coords
        ]

        # Removed debug logging

        return secondary_grid_coords

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

        # Calculate primary and secondary quadsets
        # The secondary quadset calculation already ensures no overlap
        primary_grid_coords = self.calculate_primary_quadset(x, y)
        secondary_grid_coords = self.calculate_secondary_quadset(x, y)

        # Removed debug logging

        # Update highlighted cells
        # Removed debug logging

        self.highlighted_cells = primary_grid_coords
        self.secondary_highlighted_cells = secondary_grid_coords

        # Verify the cells were set correctly
        # Removed debug logging

        # Calculate sums
        quad_sum = self.calculate_quadset_sum(primary_grid_coords)
        secondary_sum = self.calculate_quadset_sum(secondary_grid_coords)

        # Return quadset information
        return {
            "primary_grid_coords": primary_grid_coords,
            "secondary_grid_coords": secondary_grid_coords,
            "quad_sum": quad_sum,
            "secondary_sum": secondary_sum,
            "octa_sum": quad_sum + secondary_sum,
        }

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
        """Show vectors for a quadset, without altering persistent highlights."""
        # Get the quadset coordinates
        quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
        # Convert to grid positions (for return value only)
        quadset_grid_positions = []
        for qx, qy in quadset_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(qx, qy)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                quadset_grid_positions.append((grid_row, grid_col))
        # Do NOT set self.highlighted_cells or self.secondary_highlighted_cells here!
        # Calculate vectors
        vectors = self.kamea_service.get_quadset_vectors(x, y)
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
        self.highlighted_cells = []
        self.secondary_highlighted_cells = []

    def clear_vectors(self) -> None:
        """Clear the vector field."""
        self.vectors = []
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

    def show_conrune_transition(self, row: int, col: int):
        """Return the conrune pair and their positions for a selected cell.

        Args:
            row: The selected row
            col: The selected column
        Returns:
            Dict with keys: 'original', 'conrune', 'original_pos', 'conrune_pos'
        """
        ternary_value = self.kamea_service.get_kamea_value(row, col, False)
        if ternary_value is None:
            return None
        ternary_value = str(ternary_value).zfill(6)
        conrune_value = self.kamea_service.get_conrune_pair(ternary_value)
        if conrune_value is None:
            return None
        conrune_position = self.kamea_service.find_cell_position(conrune_value)
        if conrune_position is None:
            return None
        return {
            "original": ternary_value,
            "conrune": conrune_value,
            "original_pos": (row, col),
            "conrune_pos": conrune_position,
        }

    def show_quadset_difference_vectors(self, x: int, y: int):
        """Return difference vectors and related info for a quadset at (x, y)."""
        quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
        quadset_grid_positions = []
        quadset_values = []
        for qx, qy in quadset_coords:
            grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(qx, qy)
            if (
                0 <= grid_row < self.kamea_service.grid_size
                and 0 <= grid_col < self.kamea_service.grid_size
            ):
                quadset_grid_positions.append((grid_row, grid_col))
                value = self.kamea_service.get_kamea_value(grid_row, grid_col, True)
                if value is not None:
                    quadset_values.append(value)
        result = {
            "quadset_grid_positions": quadset_grid_positions,
            "quadset_values": quadset_values,
            "base_conrune_diff": None,
            "reversal_conrune_diff": None,
            "differential_transformation": None,
            "differential_cell_pos": None,
        }
        if len(quadset_values) == 4:
            try:
                base_conrune_diff = int(abs(quadset_values[0] - quadset_values[1]))
                reversal_conrune_diff = int(abs(quadset_values[2] - quadset_values[3]))
                result["base_conrune_diff"] = base_conrune_diff
                result["reversal_conrune_diff"] = reversal_conrune_diff
                from tq.utils.ternary_converter import (
                    decimal_to_ternary,
                    ternary_to_decimal,
                )
                from tq.utils.ternary_transition import TernaryTransition

                transition = TernaryTransition()
                first_ternary = decimal_to_ternary(base_conrune_diff)
                second_ternary = decimal_to_ternary(reversal_conrune_diff)
                max_length = max(len(first_ternary), len(second_ternary))
                first_ternary_padded = first_ternary.zfill(max_length)
                second_ternary_padded = second_ternary.zfill(max_length)
                transition_ternary = transition.apply_transition(
                    first_ternary_padded, second_ternary_padded
                )
                transition_decimal = ternary_to_decimal(transition_ternary)
                result["differential_transformation"] = transition_decimal
                transition_ternary_padded = decimal_to_ternary(
                    transition_decimal
                ).zfill(6)
                diff_trans_position = self.kamea_service.find_cell_position(
                    transition_ternary_padded
                )
                result["differential_cell_pos"] = diff_trans_position
            except Exception as e:
                from loguru import logger

                logger.error(f"Error calculating differential transformation: {e}")
        return result

    def find_patterns(self, pattern_type: str) -> Dict[str, List[Tuple[int, int]]]:
        """Find patterns in the Kamea grid.

        Args:
            pattern_type: 'difference', 'sum', or 'product'
        Returns:
            Dict mapping pattern value (as str) to list of (row, col) cell positions
        """
        results = {}
        if pattern_type == "difference":
            for row in range(self.kamea_service.grid_size):
                for col in range(self.kamea_service.grid_size):
                    ternary_value = self.kamea_service.get_kamea_value(row, col, False)
                    if ternary_value is None:
                        continue
                    ternary_value = str(ternary_value).zfill(6)
                    try:
                        conrune_value = self.kamea_service.get_conrune_pair(
                            ternary_value
                        )
                        if conrune_value is None:
                            continue
                    except Exception:
                        continue
                    conrune_position = self.kamea_service.find_cell_position(
                        conrune_value
                    )
                    if conrune_position is None:
                        continue
                    original_decimal = self.kamea_service.get_kamea_value(
                        row, col, True
                    )
                    conrune_row, conrune_col = conrune_position
                    conrune_decimal = self.kamea_service.get_kamea_value(
                        conrune_row, conrune_col, True
                    )
                    if original_decimal is None or conrune_decimal is None:
                        continue
                    difference = abs(original_decimal - conrune_decimal)
                    key = str(difference)
                    if key not in results:
                        results[key] = []
                    results[key].append((row, col))
        elif pattern_type == "sum":
            for row in range(self.kamea_service.grid_size):
                for col in range(self.kamea_service.grid_size):
                    x, y = self.kamea_service.convert_grid_to_cartesian(row, col)
                    if x == 0 or y == 0:
                        continue
                    quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
                    quadset_grid_positions = []
                    for qx, qy in quadset_coords:
                        (
                            grid_row,
                            grid_col,
                        ) = self.kamea_service.convert_cartesian_to_grid(qx, qy)
                        if (
                            0 <= grid_row < self.kamea_service.grid_size
                            and 0 <= grid_col < self.kamea_service.grid_size
                        ):
                            quadset_grid_positions.append((grid_row, grid_col))
                    quad_sum = 0
                    for grid_row, grid_col in quadset_grid_positions:
                        value = self.kamea_service.get_kamea_value(
                            grid_row, grid_col, True
                        )
                        if value is not None:
                            quad_sum += value
                    key = str(quad_sum)
                    if key not in results:
                        results[key] = []
                    if (row, col) not in results[key]:
                        results[key].append((row, col))
        elif pattern_type == "product":
            for row in range(self.kamea_service.grid_size):
                for col in range(self.kamea_service.grid_size):
                    x, y = self.kamea_service.convert_grid_to_cartesian(row, col)
                    if x == 0 or y == 0:
                        continue
                    quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
                    quadset_grid_positions = []
                    for qx, qy in quadset_coords:
                        (
                            grid_row,
                            grid_col,
                        ) = self.kamea_service.convert_cartesian_to_grid(qx, qy)
                        if (
                            0 <= grid_row < self.kamea_service.grid_size
                            and 0 <= grid_col < self.kamea_service.grid_size
                        ):
                            quadset_grid_positions.append((grid_row, grid_col))
                    quad_product = 1
                    for grid_row, grid_col in quadset_grid_positions:
                        value = self.kamea_service.get_kamea_value(
                            grid_row, grid_col, True
                        )
                        if value is not None:
                            quad_product *= value
                    key = str(quad_product)
                    if key not in results:
                        results[key] = []
                    if (row, col) not in results[key]:
                        results[key].append((row, col))
        return results

    def get_cells_for_pattern(
        self, pattern_type: str, value: int
    ) -> List[Tuple[int, int]]:
        """Return all cells matching a given pattern value for the specified pattern type."""
        key = str(value)
        patterns = self.find_patterns(pattern_type)
        return patterns.get(key, [])

    def locator_to_cell(
        self, region: int, area: int, cell: int
    ) -> Optional[Tuple[int, int]]:
        """Convert locator (region, area, cell) to a cell position (row, col)."""
        # Convert to base 3 and pad to 2 digits
        bigram3 = "".join(str((region // 3) % 3) + str(region % 3))
        bigram2 = "".join(str((area // 3) % 3) + str(area % 3))
        bigram1 = "".join(str((cell // 3) % 3) + str(cell % 3))
        ternary_value = (
            bigram1[0] + bigram2[0] + bigram3[0] + bigram3[1] + bigram2[1] + bigram1[1]
        )
        return self.kamea_service.find_cell_position(ternary_value)

    def show_vectors_for_highlighted_cells(
        self, highlighted_cells: List[Tuple[int, int]]
    ) -> Dict[str, Union[List[Tuple[int, int, int, int, int]], int]]:
        """Show all vectors from each highlighted cell to its Conrune pair (using canonical transformation)."""
        vectors = []
        for row, col in highlighted_cells:
            ternary_value = self.kamea_service.get_kamea_value(row, col, False)
            if ternary_value is None:
                continue
            ternary_value = str(ternary_value).zfill(6)
            conrune_ternary = self.kamea_service.get_conrune_pair(ternary_value)
            if conrune_ternary is None:
                continue
            conrune_position = self.kamea_service.find_cell_position(conrune_ternary)
            if conrune_position is None:
                continue
            conrune_row, conrune_col = conrune_position
            # Only draw if the conrune cell is within bounds
            if (
                0 <= conrune_row < self.kamea_service.grid_size
                and 0 <= conrune_col < self.kamea_service.grid_size
            ):
                cell_value = self.kamea_service.get_kamea_value(row, col, True)
                conrune_value = self.kamea_service.get_kamea_value(
                    conrune_row, conrune_col, True
                )
                dx = conrune_col - col
                dy = conrune_row - row
                difference = (
                    abs(cell_value - conrune_value)
                    if cell_value is not None and conrune_value is not None
                    else 0
                )
                vectors.append((row, col, dx, dy, difference))
        self.vectors = vectors
        self.show_vectors = True
        if vectors:
            self.min_vector_diff = min(v[4] for v in vectors)
            self.max_vector_diff = max(v[4] for v in vectors)
        else:
            self.min_vector_diff = 0
            self.max_vector_diff = 1
        return {
            "vectors": vectors,
            "count": len(vectors),
            "min_diff": self.min_vector_diff,
            "max_diff": self.max_vector_diff,
        }
