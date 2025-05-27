"""
Unit tests for the Marker class in the Stonehenge Eclipse Predictor simulation.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: pytest, astrology.models.stonehenge_marker.Marker
"""

import pytest
from astrology.models.stonehenge_marker import Marker
from astrology.models.stonehenge_circle_config import NUM_HOLES # Assuming default NUM_HOLES = 56

class TestMarker:
    """Test suite for the Marker class."""

    def test_marker_initialization_valid(self):
        """Test valid initialization of a Marker."""
        marker = Marker(name="S", initial_position=0)
        assert marker.name == "S"
        assert marker.current_position == 0

        marker_at_end = Marker(name="M", initial_position=NUM_HOLES - 1)
        assert marker_at_end.name == "M"
        assert marker_at_end.current_position == NUM_HOLES - 1

    def test_marker_initialization_invalid_position(self):
        """Test initialization with invalid positions raises ValueError."""
        with pytest.raises(ValueError, match="Initial position must be between 0 and 55."):
            Marker(name="Err", initial_position=-1)
        
        with pytest.raises(ValueError, match="Initial position must be between 0 and 55."):
            Marker(name="Err", initial_position=NUM_HOLES)
        
        with pytest.raises(ValueError, match="Initial position must be between 0 and 55."):
            Marker(name="Err", initial_position=100)

    def test_marker_repr(self):
        """Test the __repr__ method of the Marker."""
        marker = Marker(name="N", initial_position=10)
        assert repr(marker) == "Marker(Name: N, Position: 10)"

    @pytest.mark.parametrize(
        "initial_pos, steps, expected_pos",
        [
            (0, 2, 2),          # Simple anticlockwise
            (54, 1, 55),        # Anticlockwise to end
            (55, 1, 0),         # Anticlockwise wrap-around from end
            (0, NUM_HOLES, 0),  # Full anticlockwise circle
            (10, 50, (10 + 50) % NUM_HOLES), # Large anticlockwise move (4)
        ]
    )
    def test_marker_move_anticlockwise(self, initial_pos, steps, expected_pos):
        """Test anticlockwise movement of the marker, including wrap-around."""
        marker = Marker(name="Test", initial_position=initial_pos)
        marker.move(steps=steps, num_holes=NUM_HOLES, clockwise=False)
        assert marker.current_position == expected_pos

    @pytest.mark.parametrize(
        "initial_pos, steps, expected_pos",
        [
            (2, 2, 0),          # Simple clockwise
            (1, 1, 0),          # Clockwise to start
            (0, 1, 55),         # Clockwise wrap-around from start
            (0, NUM_HOLES, 0),  # Full clockwise circle
            (10, 12, (10 - 12 + NUM_HOLES) % NUM_HOLES), # Large clockwise move (54)
        ]
    )
    def test_marker_move_clockwise(self, initial_pos, steps, expected_pos):
        """Test clockwise movement of the marker, including wrap-around."""
        marker = Marker(name="Test", initial_position=initial_pos)
        marker.move(steps=steps, num_holes=NUM_HOLES, clockwise=True)
        assert marker.current_position == expected_pos

    def test_marker_move_zero_steps(self):
        """Test moving zero steps does not change position."""
        marker = Marker(name="Zero", initial_position=25)
        marker.move(steps=0, clockwise=False)
        assert marker.current_position == 25
        marker.move(steps=0, clockwise=True)
        assert marker.current_position == 25

# To run these tests, navigate to the project root in the terminal and run: pytest 