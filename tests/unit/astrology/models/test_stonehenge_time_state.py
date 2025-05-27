"""
Unit tests for the TimeState class in the Stonehenge Eclipse Predictor simulation.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: pytest, astrology.models.stonehenge_time_state.TimeState
"""

import pytest
from astrology.models.stonehenge_time_state import TimeState

class TestTimeState:
    """Test suite for the TimeState class."""

    def test_timestate_initialization_default(self):
        """Test default initialization of TimeState."""
        ts = TimeState()
        assert ts.current_day == 1
        assert ts.current_year == 1
        assert ts.day_within_13_day_cycle == 0
        assert ts.day_within_year_cycle == 0
        assert ts.DAYS_IN_HOYLE_YEAR == 364

    def test_timestate_initialization_custom(self):
        """Test custom initialization of TimeState."""
        ts = TimeState(start_day=100, start_year=5)
        assert ts.current_day == 100
        assert ts.current_year == 5
        assert ts.day_within_13_day_cycle == 0
        assert ts.day_within_year_cycle == 0

    def test_timestate_repr(self):
        """Test the __repr__ method of TimeState."""
        ts = TimeState()
        expected_repr = "TimeState(Year: 1, Day: 1, 13-Day Cycle: 0/13, Year Cycle: 0/364)"
        assert repr(ts) == expected_repr
        ts.advance_day() # Day 2, 13-day: 1, year: 1
        expected_repr_advanced = "TimeState(Year: 1, Day: 2, 13-Day Cycle: 1/13, Year Cycle: 1/364)"
        assert repr(ts) == expected_repr_advanced

    def test_advance_day_single_step(self):
        """Test a single advancement of a day."""
        ts = TimeState()
        sun_done, year_done = ts.advance_day()
        assert ts.current_day == 2
        assert ts.day_within_13_day_cycle == 1
        assert ts.day_within_year_cycle == 1
        assert not sun_done
        assert not year_done

    def test_advance_day_13_day_cycle_completion(self):
        """Test completion of the 13-day cycle."""
        ts = TimeState()
        sun_done, year_done = False, False
        for i in range(1, 13): # Advance 12 days
            sun_done, year_done = ts.advance_day()
            assert ts.day_within_13_day_cycle == i
            assert not sun_done
            assert not year_done
        
        # 13th advancement, should complete the cycle
        sun_done, year_done = ts.advance_day()
        assert ts.current_day == 14
        assert ts.day_within_13_day_cycle == 0 # Cycle resets to 0
        assert ts.day_within_year_cycle == 13
        assert sun_done
        assert not year_done

        # Next day, cycle starts at 1 again
        sun_done, year_done = ts.advance_day()
        assert ts.day_within_13_day_cycle == 1
        assert not sun_done

    def test_advance_day_year_cycle_completion(self):
        """Test completion of the Hoyle year cycle."""
        ts = TimeState()
        sun_done, year_done = False, False
        # Advance to the day before year completion
        for _ in range(ts.DAYS_IN_HOYLE_YEAR - 1):
            sun_done, year_done = ts.advance_day()
            assert not year_done
        
        assert ts.current_day == ts.DAYS_IN_HOYLE_YEAR
        assert ts.current_year == 1
        assert ts.day_within_year_cycle == ts.DAYS_IN_HOYLE_YEAR -1
        
        # Next advancement should complete the year
        sun_done, year_done = ts.advance_day()
        assert ts.current_day == ts.DAYS_IN_HOYLE_YEAR + 1
        assert ts.current_year == 2 # Year increments
        assert ts.day_within_year_cycle == 0 # Year cycle resets
        assert year_done

        # Check 13-day cycle at year turnover (e.g., 364 % 13)
        # 364 = 13 * 28. So day_within_13_day_cycle should be 0 if year completed on day 364.
        # Since advance_day increments the 13-day cycle first, then checks year, this is correct.
        assert ts.day_within_13_day_cycle == (ts.DAYS_IN_HOYLE_YEAR % 13)
        if (ts.DAYS_IN_HOYLE_YEAR % 13) == 0:
             assert sun_done # If year end coincides with 13-day cycle end

    def test_advance_day_multiple_years(self):
        """Test advancing through multiple year cycles."""
        ts = TimeState()
        days_to_simulate = ts.DAYS_IN_HOYLE_YEAR * 3 + 5 # Simulate 3 full years and 5 extra days
        final_sun_cycle_pos = 0
        final_year_cycle_pos = 0

        for i in range(days_to_simulate):
            sun_done, year_done = ts.advance_day()
            if i == days_to_simulate -1:
                final_sun_cycle_pos = ts.day_within_13_day_cycle
                final_year_cycle_pos = ts.day_within_year_cycle
        
        assert ts.current_year == 4 # Started at 1, 3 full years passed
        assert ts.current_day == days_to_simulate + 1 # +1 because current_day starts at 1
        assert final_year_cycle_pos == 5
        assert final_sun_cycle_pos == (days_to_simulate % 13) # day_within_13_day_cycle is (total days advanced) % 13

# To run these tests, navigate to the project root in the terminal and run: pytest 