"""
@file kamea_service.py
@description Provides services for Kamea of Maut operations and calculations, using canonical grid data from CSVs.
@author Daniel (and AI assistant)
@created 2024-06-11
@lastModified 2024-06-11
@dependencies pandas, tq.utils.ternary_transition

This service is the authoritative implementation for Kamea grid operations in IsopGem.

- The Kamea grid is loaded from:
    - assets/cvs/Decimal Kamea.csv (decimal values)
    - assets/cvs/Ternary Decimal.csv (ternary values)
- These CSVs are the single source of truth for all cell values and mappings.
- All coordinate, conrune, and transformation logic is grounded in these files.
- For mathematical principles, see: docs/kamea_mathematical_principles.md
"""

import os
from typing import List, Optional, Tuple, Union

import pandas as pd
from loguru import logger

from tq.utils.ternary_transition import TernaryTransition


class KameaService:
    """
    Service for Kamea-related operations and calculations.

    This class loads the canonical Kamea grid from CSV files and provides methods
    for value lookup, coordinate conversion, quadset and conrune operations.

    The CSVs in assets/cvs/ are the single source of truth for all grid values.
    See docs/kamea_mathematical_principles.md for mathematical details.
    """

    def __init__(self):
        """
        Initialize the Kamea service and load the canonical grid data from CSVs.
        """
        self.grid_size = 27
        self.transition = TernaryTransition()
        self.decimal_data = None
        self.ternary_data = None
        self._load_kamea_data()

    def _load_kamea_data(self) -> None:
        """
        Load the Kamea grid data from the canonical CSV files.
        If loading fails, initializes with zero-filled arrays.
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            decimal_path = os.path.join(base_dir, "assets", "cvs", "Decimal Kamea.csv")
            ternary_path = os.path.join(
                base_dir, "assets", "cvs", "Ternary Decimal.csv"
            )

            # Load the data as 27x27 arrays
            self.decimal_data = pd.read_csv(decimal_path, header=None).values
            self.ternary_data = pd.read_csv(ternary_path, header=None).values

            logger.debug(
                f"Loaded Kamea data: {self.decimal_data.shape} decimal, {self.ternary_data.shape} ternary"
            )
        except Exception as e:
            logger.error(f"Error loading Kamea data: {e}")
            self.decimal_data = [
                [0 for _ in range(self.grid_size)] for _ in range(self.grid_size)
            ]
            self.ternary_data = [
                [0 for _ in range(self.grid_size)] for _ in range(self.grid_size)
            ]

    def get_kamea_value(
        self, row: int, col: int, decimal: bool = True
    ) -> Optional[Union[int, str]]:
        """
        Get the value at a specific position in the Kamea grid.

        Args:
            row: The row index (0-based)
            col: The column index (0-based)
            decimal: If True, return the decimal value; if False, return the ternary string.

        Returns:
            The value at the specified position, or None if out of bounds.
        """
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if decimal and self.decimal_data is not None:
                return self.decimal_data[row][col]
            elif not decimal and self.ternary_data is not None:
                return self.ternary_data[row][col]
        return None

    def find_cell_position(self, ternary_value: str) -> Optional[Tuple[int, int]]:
        """
        Find the (row, col) position of a cell with the given ternary value.
        Pads the ternary value to 6 digits for comparison.

        Args:
            ternary_value: The ternary value to search for (as string)

        Returns:
            Tuple of (row, col) if found, else None.
        """
        ternary_value = str(ternary_value)
        padded_value = ternary_value.zfill(6)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = self.get_kamea_value(row, col, False)
                if value is None:
                    continue
                padded_cell_value = str(value).zfill(6)
                if padded_cell_value == padded_value:
                    logger.debug(
                        f"Found cell with ternary value {ternary_value} at position ({row}, {col})"
                    )
                    return (row, col)
        logger.debug(
            f"Could not find cell with ternary value {ternary_value} (padded: {padded_value})"
        )
        return None

    def calculate_difference_vectors(
        self, min_diff: int = 0, max_diff: int = 364
    ) -> List[Tuple[int, int, int, int, int]]:
        """Calculate difference vectors for all cells in the Kamea grid.

        Args:
            min_diff: Minimum difference to include
            max_diff: Maximum difference to include

        Returns:
            List of (row, col, dx, dy, difference) tuples
        """
        vectors = []
        total_cells = 0
        found_conrune = 0
        in_range = 0

        # Sample a few cells for debugging
        debug_samples = []

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                total_cells += 1

                # Get the ternary value of the current cell
                ternary_value = self.get_kamea_value(row, col, False)
                if ternary_value is None:
                    continue

                # Ensure ternary_value is a string
                ternary_value = str(ternary_value).zfill(6)

                # Apply conrune transformation
                try:
                    conrune_value = self.transition.apply_conrune(ternary_value)
                except Exception as e:
                    logger.error(f"Error applying conrune to {ternary_value}: {e}")
                    continue

                # Find the position of the conrune cell
                conrune_position = self.find_cell_position(conrune_value)
                if conrune_position is None:
                    logger.debug(
                        f"Could not find position for conrune value {conrune_value}"
                    )
                    continue

                found_conrune += 1

                # Get the conrune cell position
                conrune_row, conrune_col = conrune_position

                # Calculate the vector for reference (dx, dy)
                dx = conrune_col - col
                dy = row - conrune_row  # Invert y for screen coordinates

                # Calculate the difference
                original_decimal = self.get_kamea_value(row, col, True)
                conrune_decimal = self.get_kamea_value(conrune_row, conrune_col, True)

                # Ensure we have valid decimal values
                if original_decimal is None or conrune_decimal is None:
                    logger.debug(
                        f"Missing decimal values: original={original_decimal}, conrune={conrune_decimal}"
                    )
                    continue

                difference = abs(original_decimal - conrune_decimal)

                # Collect some samples for debugging
                if len(debug_samples) < 5:
                    debug_samples.append(
                        {
                            "position": (row, col),
                            "ternary": ternary_value,
                            "conrune": conrune_value,
                            "conrune_position": conrune_position,
                            "original_decimal": original_decimal,
                            "conrune_decimal": conrune_decimal,
                            "difference": difference,
                        }
                    )

                # Filter by difference range
                if min_diff <= difference <= max_diff:
                    in_range += 1
                    vectors.append((row, col, dx, dy, difference))

        # Log debug information
        logger.debug(
            f"Vector calculation stats: Total cells: {total_cells}, Found conrune: {found_conrune}, In range: {in_range}"
        )
        for i, sample in enumerate(debug_samples):
            logger.debug(f"Sample {i+1}: {sample}")

        return vectors

    def get_quadset_coordinates(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get the coordinates for a quadset based on a cell position.

        See: docs/kamea_mathematical_principles.md, section 'Quadsets'.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (x, y) tuples representing the quadset coordinates
        """
        if x == 0 and y == 0:
            # Origin cell - only include itself
            return [(0, 0)]
        elif x == 0:
            # Vertical axis cell - (0, y) and (0, -y)
            return [(0, y), (0, -y)]
        elif y == 0:
            # Horizontal axis cell - (x, 0) and (-x, 0)
            return [(x, 0), (-x, 0)]
        else:
            # Regular cell - all four sign permutations
            return [
                (x, y),
                (-x, -y),
                (-x, y),
                (x, -y),
            ]

    def get_conrune_pair(self, ternary_value: str) -> Optional[str]:
        """
        Get the conrune pair for a ternary value using the canonical transformation.
        The conrune transformation swaps 1s and 2s, keeps 0s the same.
        See docs/kamea_mathematical_principles.md for details.

        Args:
            ternary_value: The ternary value as a string (will be padded to 6 digits)

        Returns:
            The conrune-transformed ternary string, or None on error.
        """
        try:
            ternary_value = str(ternary_value).zfill(6)
            transition = TernaryTransition()
            conrune_value = transition.apply_conrune(ternary_value)
            return conrune_value
        except Exception as e:
            logger.error(f"Error applying conrune to {ternary_value}: {e}")
            return None

    def get_quadset_vectors(
        self, x: int, y: int
    ) -> List[Tuple[int, int, int, int, int]]:
        """Calculate vectors for a quadset based on a cell position.

        Args:
            x: The x coordinate (Cartesian)
            y: The y coordinate (Cartesian)

        Returns:
            List of (row, col, dx, dy, difference) tuples
        """
        # Get the quadset coordinates
        quadset_coords = self.get_quadset_coordinates(x, y)

        # Convert to grid positions
        quadset_grid_positions = []
        for qx, qy in quadset_coords:
            grid_row = self.grid_size // 2 - qy
            grid_col = qx + self.grid_size // 2
            if 0 <= grid_row < self.grid_size and 0 <= grid_col < self.grid_size:
                quadset_grid_positions.append((grid_row, grid_col))

        # Calculate vectors for each cell in the quadset
        vectors = []

        for grid_row, grid_col in quadset_grid_positions:
            # Get the ternary value of the current cell
            ternary_value = self.get_kamea_value(grid_row, grid_col, False)
            if ternary_value is None:
                continue

            # Ensure ternary_value is a string
            ternary_value = str(ternary_value).zfill(6)

            # Apply conrune transformation
            try:
                conrune_value = self.transition.apply_conrune(ternary_value)
            except Exception as e:
                logger.error(f"Error applying conrune to {ternary_value}: {e}")
                continue

            # Find the position of the conrune cell
            conrune_position = self.find_cell_position(conrune_value)
            if conrune_position is None:
                logger.debug(
                    f"Could not find position for conrune value {conrune_value}"
                )
                continue

            # Get the conrune cell position
            conrune_row, conrune_col = conrune_position

            # Calculate the vector for reference (dx, dy)
            dx = conrune_col - grid_col
            dy = grid_row - conrune_row  # Invert y for screen coordinates

            # Calculate the difference
            original_decimal = self.get_kamea_value(grid_row, grid_col, True)
            conrune_decimal = self.get_kamea_value(conrune_row, conrune_col, True)

            # Ensure we have valid decimal values
            if original_decimal is None or conrune_decimal is None:
                continue

            difference = abs(original_decimal - conrune_decimal)

            # Add the vector to our list
            vectors.append((grid_row, grid_col, dx, dy, difference))

        return vectors

    def extract_bigrams(self, ternary_value: str) -> Tuple[str, str, str]:
        """Extract the three bigrams from a ternary value.

        Args:
            ternary_value: The ternary value to analyze

        Returns:
            Tuple of (bigram1, bigram2, bigram3)
        """
        # Ensure it's a string and padded to 6 digits
        ternary_str = str(ternary_value).zfill(6)

        # Extract the three bigrams (pairing from opposite ends)
        # For a 6-digit number, digit positions are 0-5 in the string
        # Digit 6 = position 0 (most significant/leftmost)
        # Digit 1 = position 5 (least significant/rightmost)
        bigram1 = ternary_str[0] + ternary_str[5]  # First bigram (digits 6 and 1)
        bigram2 = ternary_str[1] + ternary_str[4]  # Second bigram (digits 5 and 2)
        bigram3 = ternary_str[2] + ternary_str[3]  # Third bigram (digits 4 and 3)

        return (bigram1, bigram2, bigram3)

    def find_cells_with_bigram(
        self, bigram_index: int, bigram_value: str
    ) -> List[Tuple[int, int]]:
        """Find cells with a matching bigram.

        Args:
            bigram_index: 0 for first bigram, 1 for second, 2 for third
            bigram_value: The bigram value to match

        Returns:
            List of (row, col) tuples for matching cells
        """
        matching_cells = []

        # Search for cells with matching bigram
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                value = self.get_kamea_value(r, c, False)
                if value is not None:
                    cell_ternary = str(value).zfill(6)

                    # Extract the appropriate bigram based on the index
                    if bigram_index == 0:
                        # First bigram (digits 6 and 1)
                        cell_bigram = cell_ternary[0] + cell_ternary[5]
                    elif bigram_index == 1:
                        # Second bigram (digits 5 and 2)
                        cell_bigram = cell_ternary[1] + cell_ternary[4]
                    elif bigram_index == 2:
                        # Third bigram (digits 4 and 3)
                        cell_bigram = cell_ternary[2] + cell_ternary[3]
                    else:
                        continue

                    # Check if this cell matches the criteria
                    if cell_bigram == bigram_value:
                        matching_cells.append((r, c))

        return matching_cells

    def calculate_kamea_locator(self, ternary_value: str) -> str:
        """Calculate the Kamea Locator for a ternary value.

        Args:
            ternary_value: The ternary value to analyze

        Returns:
            The Kamea Locator string in format "region-area-cell"
        """
        # Extract bigrams
        bigram1, bigram2, bigram3 = self.extract_bigrams(ternary_value)

        # Calculate the Kamea Locator (decimal values of the bigrams)
        # Order: 9×9 region (bigram3) - 3×3 area (bigram2) - cell (bigram1)
        locator = f"{int(bigram3, 3)}-{int(bigram2, 3)}-{int(bigram1, 3)}"

        return locator

    def convert_grid_to_cartesian(self, row: int, col: int) -> Tuple[int, int]:
        """Convert grid coordinates to Cartesian coordinates.

        Args:
            row: The row index in the grid
            col: The column index in the grid

        Returns:
            Tuple of (x, y) in Cartesian coordinates
        """
        x = col - self.grid_size // 2
        y = self.grid_size // 2 - row  # Invert Y since grid Y increases downward
        return (x, y)

    def convert_cartesian_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """Convert Cartesian coordinates to grid coordinates.

        Args:
            x: The x coordinate in Cartesian system
            y: The y coordinate in Cartesian system

        Returns:
            Tuple of (row, col) in grid coordinates
        """
        col = x + self.grid_size // 2
        row = self.grid_size // 2 - y  # Invert Y since grid Y increases downward
        return (row, col)
