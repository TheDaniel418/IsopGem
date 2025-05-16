"""
Defines the TimeState class for the Stonehenge Eclipse Predictor simulation.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: None
"""

class TimeState:
    """
    Manages the time state of the Stonehenge simulation.

    Attributes:
        current_day (int): The current day of the simulation (overall).
        current_year (int): The current year of the simulation.
        day_within_13_day_cycle (int): Tracks the day within the 13-day cycle 
                                       for Sun marker movement (0-12).
        day_within_year_cycle (int): Tracks the day within the ~364-day year cycle
                                       for Node marker movement (0-363).
        DAYS_IN_HOYLE_YEAR (int): Constant for the number of days in Hoyle's
                                  approximated year for this model (364).
    """
    DAYS_IN_HOYLE_YEAR: int = 364 # 56 holes * 6.5 days/hole for Sun movement approximation

    def __init__(self, start_day: int = 1, start_year: int = 1):
        """
        Initializes a new TimeState.

        Args:
            start_day (int): The overall starting day of the simulation. Defaults to 1.
            start_year (int): The starting year of the simulation. Defaults to 1.
        """
        self.current_day: int = start_day
        self.current_year: int = start_year
        self.day_within_13_day_cycle: int = 0 # Starts at 0, moves to 1 on first advance
        self.day_within_year_cycle: int = 0 # Starts at 0, moves to 1 on first advance

    def __repr__(self) -> str:
        """
        Returns a string representation of the TimeState.

        Returns:
            str: A string like "TimeState(Year: 1, Day: 1, 13-Day Cycle: 0/13, Year Cycle: 0/364)".
        """
        return (
            f"TimeState(Year: {self.current_year}, Day: {self.current_day}, "
            f"13-Day Cycle: {self.day_within_13_day_cycle}/13, "
            f"Year Cycle: {self.day_within_year_cycle}/{self.DAYS_IN_HOYLE_YEAR})"
        )

    def to_dict(self) -> dict:
        """
        Serializes the TimeState to a dictionary.

        Returns:
            dict: A dictionary representation of the TimeState.
        """
        return {
            "current_day": self.current_day,
            "current_year": self.current_year,
            "day_within_13_day_cycle": self.day_within_13_day_cycle,
            "day_within_year_cycle": self.day_within_year_cycle
        }

    def advance_day(self) -> tuple[bool, bool]:
        """
        Advances the simulation time by one day.

        Updates all relevant day and cycle counters. 
        Resets year cycle and increments year if a full Hoyle year has passed.

        Returns:
            tuple[bool, bool]: A tuple (sun_cycle_completed, year_cycle_completed).
                               `sun_cycle_completed` is True if a 13-day cycle just ended.
                               `year_cycle_completed` is True if a Hoyle year just ended.
        """
        self.current_day += 1
        
        sun_cycle_just_completed = False
        year_cycle_just_completed = False

        self.day_within_13_day_cycle = (self.day_within_13_day_cycle + 1) % 13
        if self.day_within_13_day_cycle == 0: # Just completed the 13th day
            sun_cycle_just_completed = True

        self.day_within_year_cycle += 1
        if self.day_within_year_cycle >= self.DAYS_IN_HOYLE_YEAR:
            self.current_year += 1
            self.day_within_year_cycle = 0 # Reset for the new year
            year_cycle_just_completed = True
            
        return sun_cycle_just_completed, year_cycle_just_completed

# Example Usage (can be removed or moved to a test file):
if __name__ == '__main__':
    time_state = TimeState()
    print(time_state)

    print("\nAdvancing time for 15 days:")
    for i in range(15):
        sun_done, year_done = time_state.advance_day()
        print(f"Day {i+1}: {time_state} -> Sun Cycle End: {sun_done}, Year Cycle End: {year_done}")

    print("\nAdvancing time for a full Hoyle year (364 days from current state):")
    # Current state is Day 16, 13-day cycle: 2, year cycle: 15
    # So we need to advance 364 - 15 = 349 more days to complete the current year cycle.
    for i in range(TimeState.DAYS_IN_HOYLE_YEAR - 15):
        time_state.advance_day()
    
    # Next day should complete the year
    sun_done, year_done = time_state.advance_day()
    print(f"End of Year Test: {time_state} -> Sun Cycle End: {sun_done}, Year Cycle End: {year_done}")
    print(time_state) # Should show Year 2, Day 1 of new year cycle 