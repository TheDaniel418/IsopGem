"""
Defines the StonehengeSimulationService for running the eclipse prediction simulation.

This service manages the simulation state, marker movements, and eclipse detection
based on Fred Hoyle's model.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: 
    astrology.models.stonehenge_marker.Marker
    astrology.models.stonehenge_time_state.TimeState
    astrology.models.stonehenge_circle_config.NUM_HOLES
    astrology.services.ephemeris_service.EphemerisService
    astrology.utils.astronomical_calculations.longitude_to_aubrey_hole, ASTRO_LONGITUDE_FOR_HOLE_0
    PyQt6.QtCore.QDate
"""

from PyQt6.QtCore import QDate

from astrology.models.stonehenge_marker import Marker
from astrology.models.stonehenge_time_state import TimeState
from astrology.models.stonehenge_circle_config import NUM_HOLES
from astrology.services.ephemeris_service import EphemerisService
from astrology.utils.astronomical_calculations import longitude_to_aubrey_hole, ASTRO_LONGITUDE_FOR_HOLE_0

class StonehengeSimulationService:
    """
    Manages the Stonehenge eclipse prediction simulation.

    Attributes:
        time_state (TimeState): The current time state of the simulation.
        sun_marker (Marker): The Sun marker.
        moon_marker (Marker): The Moon marker.
        node_n_marker (Marker): The Ascending Node (N) marker.
        node_n_prime_marker (Marker): The Descending Node (N') marker.
        proximity_threshold (int): The number of holes within which markers are 
                                   considered "aligned" for eclipse detection.
                                   0 means exact alignment.
    """

    def __init__(self, proximity_threshold: int = 0):
        """
        Initializes the StonehengeSimulationService.

        Sets up the initial positions of the Sun, Moon, and Node markers
        based on Hoyle's suggested lunar eclipse start:
        - Moon (M) at hole 0.
        - Sun (S) directly opposite M (hole 28).
        - Ascending Node (N) at the same position as M (hole 0).
        - Descending Node (N') at the same position as S (hole 28).

        Args:
            proximity_threshold (int): The threshold for eclipse detection. 
                                       Defaults to 0 (exact alignment).
        """
        self.time_state = TimeState()
        
        # Initial positions based on Hoyle's lunar eclipse start
        self.moon_marker = Marker(name="M", initial_position=0)
        self.sun_marker = Marker(name="S", initial_position=NUM_HOLES // 2) # Opposite Moon
        self.node_n_marker = Marker(name="N", initial_position=0) # Same as Moon
        self.node_n_prime_marker = Marker(name="N'", initial_position=NUM_HOLES // 2) # Opposite N
        
        self.proximity_threshold: int = proximity_threshold
        # Define solstice alignment holes (assuming Hole 0 is North)
        # Summer Solstice (approx NE, e.g., Heel Stone direction) -> Hole 7
        # Winter Solstice (opposite Summer Solstice) -> Hole 35
        self._summer_solstice_alignment_hole = 7 
        self._winter_solstice_alignment_hole = 35
        self._last_correction_log = {"lunar": "", "solar": ""} # To avoid spamming log
        self._ephemeris_seeded_initial_positions: dict[str, int] | None = None
        self._ephemeris_seed_gregorian_date: QDate | None = None # Updated type hint
        self.nodal_influence_width_one_sided: int = 3 # NEW: For wider nodal influence zones

    def _advance_hoyle_day_for_temp_simulation(
        self,
        temp_sun_marker: Marker,
        temp_moon_marker: Marker,
        temp_node_n_marker: Marker,
        temp_node_n_prime_marker: Marker,
        temp_time_state: TimeState, # For day_within_year_cycle
        sun_cycle_completed: bool,
        year_cycle_completed: bool
    ):
        """
        Advances markers for one day in a temporary simulation, including auto-recalibrations.
        This method mirrors the logic of _move_markers but operates on provided temporary objects
        and does not produce log messages.
        """
        # Moon Marker (M): Moves 2 positions anticlockwise daily.
        temp_moon_marker.move(steps=2, num_holes=NUM_HOLES, clockwise=False)

        # Sun Marker (S): Moves 2 positions anticlockwise every 13 days.
        if sun_cycle_completed:
            temp_sun_marker.move(steps=2, num_holes=NUM_HOLES, clockwise=False)

        # Node Markers (N, N_prime): Move 3 positions clockwise yearly.
        if year_cycle_completed:
            temp_node_n_marker.move(steps=3, num_holes=NUM_HOLES, clockwise=True)
            temp_node_n_prime_marker.current_position = (temp_node_n_marker.current_position + NUM_HOLES // 2) % NUM_HOLES
            
            # Solar Auto-Recalibration (at start/mid of Hoyle Year)
            current_hoyle_day_in_year = temp_time_state.day_within_year_cycle # Use temp_time_state
            
            if current_hoyle_day_in_year == 1: # Start of Hoyle Year
                if temp_sun_marker.current_position != self._summer_solstice_alignment_hole:
                    temp_sun_marker.current_position = self._summer_solstice_alignment_hole
            elif current_hoyle_day_in_year == (TimeState.DAYS_IN_HOYLE_YEAR // 2) + 1: # Mid Hoyle Year
                 if temp_sun_marker.current_position != self._winter_solstice_alignment_hole:
                    temp_sun_marker.current_position = self._winter_solstice_alignment_hole
        
        # Lunar Auto-Recalibration (at Full Moon)
        sun_pos = temp_sun_marker.current_position
        moon_pos = temp_moon_marker.current_position
        expected_moon_at_full = (sun_pos + NUM_HOLES // 2) % NUM_HOLES
        
        alignment_check_threshold = max(0, self.proximity_threshold)
        
        diff = abs(moon_pos - expected_moon_at_full)
        is_full_moon_condition_for_correction = diff <= alignment_check_threshold or diff >= (NUM_HOLES - alignment_check_threshold)

        if is_full_moon_condition_for_correction:
            if moon_pos != expected_moon_at_full: # If not already perfectly opposite
                temp_moon_marker.current_position = expected_moon_at_full

    def _move_markers(self, sun_cycle_completed: bool, year_cycle_completed: bool) -> list[str]:
        """
        Moves the markers based on the simulation's current time state and cycle completions.
        Also applies automatic recalibrations.

        Args:
            sun_cycle_completed (bool): True if the 13-day Sun cycle just ended.
            year_cycle_completed (bool): True if the Hoyle year cycle just ended.
        
        Returns:
            list[str]: A list of log messages generated by auto-recalibration events.
        """
        recalibration_logs = []

        # Moon Marker (M): Moves 2 positions anticlockwise daily.
        self.moon_marker.move(steps=2, num_holes=NUM_HOLES, clockwise=False)

        # Sun Marker (S): Moves 2 positions anticlockwise every 13 days.
        if sun_cycle_completed:
            self.sun_marker.move(steps=2, num_holes=NUM_HOLES, clockwise=False)

        # Node Markers (N, N_prime): Move 3 positions clockwise yearly.
        if year_cycle_completed:
            self.node_n_marker.move(steps=3, num_holes=NUM_HOLES, clockwise=True)
            self.node_n_prime_marker.current_position = (self.node_n_marker.current_position + NUM_HOLES // 2) % NUM_HOLES
            
            # Solar Auto-Recalibration (at start of Hoyle Year for Summer Solstice alignment)
            # And at mid-year for Winter Solstice alignment
            current_hoyle_day_in_year = self.time_state.day_within_year_cycle
            
            if current_hoyle_day_in_year == 1: # Start of Hoyle Year (Summer Solstice proxy)
                if self.sun_marker.current_position != self._summer_solstice_alignment_hole:
                    self.sun_marker.current_position = self._summer_solstice_alignment_hole
                    log_msg = "☀️ Sun marker auto-aligned to Summer Solstice point (Hole {}).".format(self._summer_solstice_alignment_hole)
                    if self._last_correction_log["solar"] != log_msg:
                        recalibration_logs.append(log_msg)
                        self._last_correction_log["solar"] = log_msg
            elif current_hoyle_day_in_year == (TimeState.DAYS_IN_HOYLE_YEAR // 2) + 1: # Mid Hoyle Year (Winter Solstice proxy)
                 if self.sun_marker.current_position != self._winter_solstice_alignment_hole:
                    self.sun_marker.current_position = self._winter_solstice_alignment_hole
                    log_msg = "☀️ Sun marker auto-aligned to Winter Solstice point (Hole {}).".format(self._winter_solstice_alignment_hole)
                    if self._last_correction_log["solar"] != log_msg:
                        recalibration_logs.append(log_msg)
                        self._last_correction_log["solar"] = log_msg
        
        # Lunar Auto-Recalibration (at Full Moon)
        # Check for Full Moon: Sun and Moon markers are opposite
        sun_pos = self.sun_marker.current_position
        moon_pos = self.moon_marker.current_position
        expected_moon_at_full = (sun_pos + NUM_HOLES // 2) % NUM_HOLES
        
        # Check if they are opposite (within proximity for detection, but correction is exact)
        # Using a small threshold for *detecting* the full moon condition for correction
        alignment_check_threshold = max(0, self.proximity_threshold) # Use at least 0
        
        diff = abs(moon_pos - expected_moon_at_full)
        is_full_moon_condition_for_correction = diff <= alignment_check_threshold or diff >= (NUM_HOLES - alignment_check_threshold)

        if is_full_moon_condition_for_correction:
            if moon_pos != expected_moon_at_full: # If not already perfectly opposite
                self.moon_marker.current_position = expected_moon_at_full
                log_msg = "🌕 Lunar marker auto-recalibrated for perfect Full Moon alignment (M at {}, S at {}).".format(expected_moon_at_full, sun_pos)
                # Avoid logging the same correction repeatedly if conditions persist for a step
                if self._last_correction_log["lunar"] != log_msg:
                    recalibration_logs.append(log_msg)
                    self._last_correction_log["lunar"] = log_msg
            else: # It's a full moon and already aligned, clear last log to allow future logs
                self._last_correction_log["lunar"] = ""
        else: # Not a full moon, clear last log
            self._last_correction_log["lunar"] = ""

        return recalibration_logs

    def _is_in_nodal_zone(self, position_to_check: int, node_position: int) -> bool:
        """
        Checks if a given position falls within the influence zone of a node.
        The zone is defined by self.nodal_influence_width_one_sided.
        """
        if not (0 <= position_to_check < NUM_HOLES and 0 <= node_position < NUM_HOLES):
            # Invalid input positions, should ideally not happen if markers are constrained
            return False

        width = self.nodal_influence_width_one_sided
        diff = abs(position_to_check - node_position)
        
        # Check direct proximity and proximity across the wrap-around point
        # Example: NUM_HOLES = 56. Node at 1, width = 2. Zone = [55, 0, 1, 2, 3]
        # If position_to_check = 55: diff = abs(55-1) = 54. NUM_HOLES - diff = 2. 2 <= width is True.
        # If position_to_check = 3: diff = abs(3-1) = 2. 2 <= width is True.
        return diff <= width or (NUM_HOLES - diff) <= width

    def _check_for_eclipses(self) -> list[str]:
        """
        Checks for solar and lunar eclipse conditions based on current marker positions.
        Uses self.proximity_threshold for Sun-Moon syzygy.
        Uses self.nodal_influence_width_one_sided for Moon-Node alignment.

        Returns:
            list[str]: A list of strings describing any detected eclipses (e.g., 
                       ["Solar Eclipse", "Lunar Eclipse"]). Empty if no eclipse.
        """
        detected_eclipses = []
        
        s_pos = self.sun_marker.current_position
        m_pos = self.moon_marker.current_position
        n_pos = self.node_n_marker.current_position
        n_prime_pos = self.node_n_prime_marker.current_position

        # Helper to check syzygy alignment (Sun-Moon)
        def is_syzygy_aligned(pos1: int, pos2: int, threshold: int) -> bool:
            diff = abs(pos1 - pos2)
            return diff <= threshold or diff >= (NUM_HOLES - threshold)

        # Solar Eclipse Conditions:
        # 1. New Moon: Moon (M) aligned with Sun (S) using self.proximity_threshold
        is_new_moon = is_syzygy_aligned(m_pos, s_pos, self.proximity_threshold)
        
        # 2. Moon in Nodal Zone: Moon (M) is within the influence zone of N or N'
        moon_in_n_zone = self._is_in_nodal_zone(m_pos, n_pos)
        moon_in_n_prime_zone = self._is_in_nodal_zone(m_pos, n_prime_pos)

        if is_new_moon and (moon_in_n_zone or moon_in_n_prime_zone):
            detected_eclipses.append("Solar Eclipse")

        # Lunar Eclipse Conditions:
        # 1. Full Moon: Moon (M) aligned opposite Sun (S) using self.proximity_threshold
        sun_opposite_pos = (s_pos + NUM_HOLES // 2) % NUM_HOLES
        is_full_moon = is_syzygy_aligned(m_pos, sun_opposite_pos, self.proximity_threshold)
        
        if is_full_moon and (moon_in_n_zone or moon_in_n_prime_zone): # Re-use nodal zone checks
            detected_eclipses.append("Lunar Eclipse")
            
        return detected_eclipses

    def advance_simulation_step(self) -> dict:
        """
        Advances the simulation by one full step (one day).

        This involves: 
        1. Advancing the time state.
        2. Moving the markers according to their rules, including auto-recalibrations.
        3. Checking for eclipse conditions.

        Returns:
            dict: A dictionary containing the results of the step, including:
                  - "day": current_day of the simulation (from TimeState).
                  - "year": current_year of the simulation (from TimeState).
                  - "eclipses_detected": list of strings (e.g., ["Solar Eclipse"] or []).
                  - "marker_positions": dict of current marker positions ({name: pos}).
                  - "recalibration_logs": list of strings from auto-recalibration events.
        """
        sun_cycle_completed, year_cycle_completed = self.time_state.advance_day()
        recalibration_log_messages = self._move_markers(sun_cycle_completed, year_cycle_completed) # Now returns logs
        eclipses = self._check_for_eclipses()
        
        marker_positions = {
            self.sun_marker.name: self.sun_marker.current_position,
            self.moon_marker.name: self.moon_marker.current_position,
            self.node_n_marker.name: self.node_n_marker.current_position,
            self.node_n_prime_marker.name: self.node_n_prime_marker.current_position,
        }
        
        return {
            "day": self.time_state.current_day,
            "year": self.time_state.current_year,
            "eclipses_detected": eclipses,
            "marker_positions": marker_positions,
            "recalibration_logs": recalibration_log_messages # Add this to the return
        }

    def get_current_marker_positions(self) -> dict[str, int]:
        """
        Returns the current positions of all markers.

        Returns:
            dict[str, int]: A dictionary mapping marker names to their current positions.
        """
        return {
            self.sun_marker.name: self.sun_marker.current_position,
            self.moon_marker.name: self.moon_marker.current_position,
            self.node_n_marker.name: self.node_n_marker.current_position,
            self.node_n_prime_marker.name: self.node_n_prime_marker.current_position,
        }

    def reset_simulation(self, start_day: int = 1, start_year: int = 1, proximity_threshold: int = 0) -> dict[str, int]:
        """
        Resets the simulation to its initial state or a specified state.

        Args:
            start_day (int): The overall starting day for TimeState. Defaults to 1.
            start_year (int): The starting year for TimeState. Defaults to 1.
            proximity_threshold (int): The threshold for eclipse detection. Defaults to 0.
        """
        self.time_state = TimeState(start_day=start_day, start_year=start_year)
        # Initial positions based on Hoyle's lunar eclipse start, but solar recalibration will override Sun if day 1 year 1
        self.moon_marker = Marker(name="M", initial_position=0)
        self.sun_marker = Marker(name="S", initial_position=NUM_HOLES // 2) 
        self.node_n_marker = Marker(name="N", initial_position=0)
        self.node_n_prime_marker = Marker(name="N'", initial_position=NUM_HOLES // 2)
        self.proximity_threshold = proximity_threshold
        self._last_correction_log = {"lunar": "", "solar": ""} # Reset log cache
        self._ephemeris_seeded_initial_positions = None # Clear seed info
        self._ephemeris_seed_gregorian_date = None # Clear seed info

        # Apply initial solar alignment if reset is to Day 1, Year 1
        if self.time_state.current_year == 1 and self.time_state.day_within_year_cycle == 1:
             self.sun_marker.current_position = self._summer_solstice_alignment_hole
             print(f"Initial solar alignment on reset: Sun marker set to Hole {self._summer_solstice_alignment_hole} for Summer Solstice.")
        
        print(f"Simulation reset to: Time: Day {self.time_state.current_day}, Year {self.time_state.current_year}, ProxThreshold: {self.proximity_threshold}")
        return self.get_current_marker_positions()

    def reset_simulation_from_ephemeris(self, year: int, month: int, day: int, hour: int = 12, minute: int = 0, second: int = 0) -> dict[str, int] | None:
        """
        Resets the simulation markers based on astronomical positions from ephemeris data
        for a given calendar date and time.

        The Hoyle simulation time (day/year) is reset to its default initial state (Day 1, Year 1),
        as this method only sets the *initial positions* of the markers based on the sky.
        The Hoyle model's internal day/year counting proceeds from these new positions.

        Args:
            year (int): Calendar year (e.g., 2024).
            month (int): Calendar month (1-12).
            day (int): Calendar day (1-31).
            hour (int): Calendar hour (0-23, UTC). Defaults to 12 (noon).
            minute (int): Calendar minute (0-59). Defaults to 0.
            second (int): Calendar second (0-59). Defaults to 0.

        Returns:
            dict[str, int] | None: A dictionary of marker positions ({name: pos}) if successful,
                                   or None if ephemeris data could not be retrieved.
        """
        try:
            ephemeris_service = EphemerisService() # Assumes default ephemeris file
            celestial_data = ephemeris_service.get_celestial_positions(
                year=year, month=month, day=day, hour=hour, minute=minute, second=second
            )

            if celestial_data:
                sun_lon = celestial_data["sun_longitude_deg"]
                moon_lon = celestial_data["moon_longitude_deg"]
                node_lon = celestial_data["node_longitude_deg"] # Mean Node from ephemeris service

                # Convert longitudes to Aubrey Hole numbers
                # Using the standard ASTRO_LONGITUDE_FOR_HOLE_0 from astronomical_calculations
                sun_hole = longitude_to_aubrey_hole(sun_lon, NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                moon_hole = longitude_to_aubrey_hole(moon_lon, NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                node_n_hole = longitude_to_aubrey_hole(node_lon, NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                
                # Reset Hoyle simulation time to default start, as ephemeris sets initial positions
                self.time_state = TimeState(start_day=1, start_year=1)
                self._last_correction_log = {"lunar": "", "solar": ""} # Reset log cache

                # Update marker positions
                self.sun_marker.current_position = sun_hole
                self.moon_marker.current_position = moon_hole
                self.node_n_marker.current_position = node_n_hole
                self.node_n_prime_marker.current_position = (node_n_hole + NUM_HOLES // 2) % NUM_HOLES
                
                # Store these as the ephemeris seeded positions
                self._ephemeris_seeded_initial_positions = {
                    "S": sun_hole, "M": moon_hole, "N": node_n_hole, "N'": self.node_n_prime_marker.current_position
                }
                # Try to import QDate for storing the seed date, handle if not available (e.g. service used headless)
                try:
                    self._ephemeris_seed_gregorian_date = QDate(year, month, day)
                except Exception as e_qdate: # Catch any potential error during QDate creation itself
                    print(f"Warning: Could not create QDate for seed: {e_qdate}")
                    self._ephemeris_seed_gregorian_date = None

                print(f"Simulation reset from ephemeris for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d} UTC.")
                print(f"  Raw Longitudes: Sun={sun_lon:.2f}, Moon={moon_lon:.2f}, Node={node_lon:.2f}")
                print(f"  Converted Holes: Sun(S)={sun_hole}, Moon(M)={moon_hole}, Node(N)={node_n_hole}, Node(N\')={self.node_n_prime_marker.current_position}")
                print(f"  Hoyle Time reset to: Day {self.time_state.current_day}, Year {self.time_state.current_year}")
                
                # Apply solar alignment if the reset effectively puts us at the start of a Hoyle year
                # This is important because ephemeris sets specific positions, but Hoyle's model
                # expects the Sun marker at a solstice point at year start/midpoint.
                # We prioritize the ephemeris position initially but log if a correction would occur.
                # For simplicity, we won't override ephemeris here but will rely on the _move_markers
                # to handle corrections on the *next* relevant Hoyle cycle if this reset isn't exactly Day 1/183.
                # The self.time_state is now (1,1) so next call to _move_markers with year_cycle_completed=True (if day 1)
                # will perform the correction.

                # However, to be more immediate for *this specific function's outcome* on a reset that
                # makes it effectively day 1 of year 1 in Hoyle terms (which it does by design):
                if self.time_state.day_within_year_cycle == 1: # It will be due to TimeState(1,1)
                    if self.sun_marker.current_position != self._summer_solstice_alignment_hole:
                        # Log the difference but prefer ephemeris position for this specific type of reset.
                        # The auto-correction will kick in on the *next* appropriate Hoyle cycle step.
                        # Or, we can choose to override here. Let's choose to log for now,
                        # and the standard auto-correction in _move_markers will handle it.
                        # For now, let's allow the ephemeris value to stand for this reset,
                        # but the *next* time a year cycle completes and it's day 1, it will snap.
                        # This might be less confusing than immediate override here.
                        print(f"  Note: Ephemeris Sun at {sun_hole}. Standard Summer Solstice alignment is Hole {self._summer_solstice_alignment_hole}. Auto-correction will apply on next relevant cycle.")

                return self.get_current_marker_positions()
            else:
                print(f"Error: Could not retrieve ephemeris data for {year}-{month:02d}-{day:02d}.")
                return None
        except Exception as e:
            print(f"Error during ephemeris reset: {e}")
            # Optionally, re-raise or handle more gracefully
            return None

    def get_hoyle_prediction_for_date(self, target_year: int, target_day: int) -> dict:
        """
        Calculates Hoyle's model prediction for a specific target date without 
        altering the service's main simulation state.
        If the simulation is seeded, it also provides actual sky data for the equivalent Gregorian date.

        Args:
            target_year (int): The target year (Hoyle calendar).
            target_day (int): The target day (1-364) within the target year.

        Returns:
            dict: A dictionary containing potentially:
                  - "target_year", "target_day"
                  - "hoyle_predicted_eclipses": list of strings (e.g., ["Solar"] or []).
                  - "hoyle_marker_positions_on_date": dict of marker positions ({name: pos}).
                  - "sky_predicted_eclipses": list of strings, if seeded and successful.
                  - "sky_marker_positions_on_date": dict, if seeded and successful.
                  - "equivalent_gregorian_date_str": string, if seeded.
                  - "error": string, if sky data retrieval failed.
        """

        # Branch 1: Target date IS the main simulation's current Hoyle date
        if (self.time_state.current_year == target_year and
                self.time_state.current_day == target_day):
            
            current_hoyle_marker_positions = self.get_current_marker_positions()
            hoyle_eclipses_on_date = []
            
            # Local helper for alignment checks
            def is_aligned_local(pos1: int, pos2: int, threshold: int) -> bool:
                diff = abs(pos1 - pos2)
                return diff <= threshold or diff >= (NUM_HOLES - threshold)

            s_pos = current_hoyle_marker_positions.get("S", -1)
            m_pos = current_hoyle_marker_positions.get("M", -1)
            n_pos = current_hoyle_marker_positions.get("N", -1)
            n_prime_pos = current_hoyle_marker_positions.get("N'", -1)

            if all(p != -1 for p in [s_pos, m_pos, n_pos, n_prime_pos]):
                # Check Hoyle Solar Eclipse
                if is_aligned_local(m_pos, s_pos, self.proximity_threshold) and \
                   (self._is_in_nodal_zone(m_pos, n_pos) or \
                    self._is_in_nodal_zone(m_pos, n_prime_pos)):
                    hoyle_eclipses_on_date.append("Solar")
                # Check Hoyle Lunar Eclipse
                sun_opposite_pos_local = (s_pos + NUM_HOLES // 2) % NUM_HOLES
                if is_aligned_local(m_pos, sun_opposite_pos_local, self.proximity_threshold) and \
                   (self._is_in_nodal_zone(m_pos, n_pos) or \
                    self._is_in_nodal_zone(m_pos, n_prime_pos)):
                    hoyle_eclipses_on_date.append("Lunar")
            
            results = {
                "hoyle_predicted_eclipses": hoyle_eclipses_on_date,
                "hoyle_marker_positions_on_date": current_hoyle_marker_positions,
                "target_year": target_year,
                "target_day": target_day
            }

            # If seeded, the current markers ARE the sky markers for this specific date (seed date)
            if self._ephemeris_seeded_initial_positions is not None and self._ephemeris_seed_gregorian_date:
                try:
                    if isinstance(self._ephemeris_seed_gregorian_date, QDate):
                        results["sky_marker_positions_on_date"] = current_hoyle_marker_positions # Same as Hoyle's current
                        results["equivalent_gregorian_date_str"] = self._ephemeris_seed_gregorian_date.toString("yyyy-MM-dd")
                        
                        # Re-check eclipse conditions for sky (which are same as Hoyle's current here)
                        sky_eclipses = []
                        if all(p != -1 for p in [s_pos, m_pos, n_pos, n_prime_pos]): # Using already fetched s_pos etc.
                            if is_aligned_local(m_pos, s_pos, self.proximity_threshold) and \
                               (self._is_in_nodal_zone(m_pos, n_pos) or \
                                self._is_in_nodal_zone(m_pos, n_prime_pos)):
                                sky_eclipses.append("Solar")
                            sun_opposite_pos_sky = (s_pos + NUM_HOLES // 2) % NUM_HOLES
                            if is_aligned_local(m_pos, sun_opposite_pos_sky, self.proximity_threshold) and \
                               (self._is_in_nodal_zone(m_pos, n_pos) or \
                                self._is_in_nodal_zone(m_pos, n_prime_pos)):
                                sky_eclipses.append("Lunar")
                        results["sky_predicted_eclipses"] = sky_eclipses
                    else:
                        results["sky_data_error"] = "Seed Gregorian date not in QDate format for Branch 1."
                        results["equivalent_gregorian_date_str"] = "Error"
                except Exception as e_sky_date: # Catch any potential error during sky date processing
                    results["sky_data_error"] = f"Error processing sky date for Branch 1: {e_sky_date}"
                    results["equivalent_gregorian_date_str"] = "Error"
            else: # Not seeded, or seed date info missing
                results["equivalent_gregorian_date_str"] = "N/A (Not Seeded or Seed Date Missing)"

            return results

        # Store current main simulation state to restore later (applies to branches 2 & 3)
        original_time_state_data = self.time_state.to_dict()
        original_sun_pos = self.sun_marker.current_position
        original_moon_pos = self.moon_marker.current_position
        original_node_n_pos = self.node_n_marker.current_position
        original_node_n_prime_pos = self.node_n_prime_marker.current_position
        
        # Temporarily re-initialize simulation state for the check
        temp_time_state = TimeState(start_day=1, start_year=1) # Temp sim time always starts Y1,D1 for counting steps

        DAYS_IN_HOYLE_YEAR = TimeState.DAYS_IN_HOYLE_YEAR # Use class constant
        # Calculate total days to simulate from the *start of the Hoyle calendar* (Y1,D1) 
        # to reach the target_year, target_day.
        # Note: target_day is 1-indexed.
        total_hoyle_days_from_calendar_start_to_target = (target_year - 1) * DAYS_IN_HOYLE_YEAR + (target_day -1)


        hoyle_sim_results = {}
        sky_data_results = {}

        # Branch 2: An ephemeris seed exists, and target is not the exact current main sim state.
        # We will calculate BOTH Hoyle's progression from seed AND sky data for the equivalent Gregorian date.
        if self._ephemeris_seeded_initial_positions is not None:
            # --- Part 1: Hoyle's model progression from initial seed markers ---
            temp_sun_hoyle = Marker(name="S", initial_position=self._ephemeris_seeded_initial_positions["S"])
            temp_moon_hoyle = Marker(name="M", initial_position=self._ephemeris_seeded_initial_positions["M"])
            temp_node_n_hoyle = Marker(name="N", initial_position=self._ephemeris_seeded_initial_positions["N"])
            temp_node_n_prime_hoyle = Marker(name="N'", initial_position=self._ephemeris_seeded_initial_positions["N'"])
            
            # Temp time state for this Hoyle progression simulation
            # This time state starts at Y1,D1 for the purpose of counting days from the seed.
            # The number of steps to take is from the seed date (which is treated as Y1D1 of this temp sim)
            # to the target_year, target_day.
            hoyle_progression_time_state = TimeState(start_day=1, start_year=1) # Corresponds to the seed date
            
            # Days to simulate for Hoyle progression from the seed date.
            # If target_year, target_day is the seed date itself, steps = 0.
            # Seed date is considered Y1,D1. So, if target is Y1,D1, steps is (1-1)*364 + (1-1) = 0.
            # If target is Y1,D2, steps is (1-1)*364 + (2-1) = 1.
            steps_for_hoyle_progression = (target_year - 1) * DAYS_IN_HOYLE_YEAR + (target_day - 1)


            for _ in range(steps_for_hoyle_progression):
                sun_cycle_comp, year_cycle_comp = hoyle_progression_time_state.advance_day()
                self._advance_hoyle_day_for_temp_simulation(
                    temp_sun_hoyle, temp_moon_hoyle, temp_node_n_hoyle, temp_node_n_prime_hoyle,
                    hoyle_progression_time_state,
                    sun_cycle_comp, year_cycle_comp
                )
            
            hoyle_eclipses = []
            # Use a local helper for alignment checks to avoid impacting main simulation's state or methods
            def is_aligned_local(pos1: int, pos2: int, threshold: int) -> bool:
                diff = abs(pos1 - pos2)
                return diff <= threshold or diff >= (NUM_HOLES - threshold)

            s_pos_h = temp_sun_hoyle.current_position
            m_pos_h = temp_moon_hoyle.current_position
            n_pos_h = temp_node_n_hoyle.current_position
            n_prime_pos_h = temp_node_n_prime_hoyle.current_position

            if is_aligned_local(m_pos_h, s_pos_h, self.proximity_threshold) and \
               (self._is_in_nodal_zone(m_pos_h, n_pos_h) or \
                self._is_in_nodal_zone(m_pos_h, n_prime_pos_h)):
                hoyle_eclipses.append("Solar")
            
            sun_opp_h = (s_pos_h + NUM_HOLES // 2) % NUM_HOLES
            if is_aligned_local(m_pos_h, sun_opp_h, self.proximity_threshold) and \
               (self._is_in_nodal_zone(m_pos_h, n_pos_h) or \
                self._is_in_nodal_zone(m_pos_h, n_prime_pos_h)):
                hoyle_eclipses.append("Lunar")

            hoyle_sim_results = {
                "hoyle_predicted_eclipses": hoyle_eclipses,
                "hoyle_marker_positions_on_date": {
                    temp_sun_hoyle.name: s_pos_h, temp_moon_hoyle.name: m_pos_h,
                    temp_node_n_hoyle.name: n_pos_h, temp_node_n_prime_hoyle.name: n_prime_pos_h
                }
            }

            # --- Part 2: Sky data for the equivalent Gregorian date ---
            equivalent_gregorian_date_str = "N/A"
            if self._ephemeris_seed_gregorian_date:
                try:
                    # QDate is needed for date calculations if available
                    if isinstance(self._ephemeris_seed_gregorian_date, QDate):
                        # Calculate days elapsed in Hoyle calendar from seed date (Y1,D1) to target_year,target_day
                        # This is the same as steps_for_hoyle_progression
                        hoyle_days_elapsed_from_seed = steps_for_hoyle_progression
                        
                        target_gregorian_date = self._ephemeris_seed_gregorian_date.addDays(hoyle_days_elapsed_from_seed)
                        equivalent_gregorian_date_str = target_gregorian_date.toString("yyyy-MM-dd")
                        
                        ephem_service = EphemerisService()
                        sky_celestial_data = ephem_service.get_celestial_positions(
                            target_gregorian_date.year(), 
                            target_gregorian_date.month(), 
                            target_gregorian_date.day()
                        )

                        if sky_celestial_data:
                            sky_sun_hole = longitude_to_aubrey_hole(sky_celestial_data["sun_longitude_deg"], NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                            sky_moon_hole = longitude_to_aubrey_hole(sky_celestial_data["moon_longitude_deg"], NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                            sky_node_hole = longitude_to_aubrey_hole(sky_celestial_data["node_longitude_deg"], NUM_HOLES, ASTRO_LONGITUDE_FOR_HOLE_0)
                            sky_node_prime_hole = (sky_node_hole + NUM_HOLES // 2) % NUM_HOLES

                            sky_markers = {"S": sky_sun_hole, "M": sky_moon_hole, "N": sky_node_hole, "N'": sky_node_prime_hole}
                            
                            sky_eclipses = []
                            s_pos_sky = sky_markers["S"]
                            m_pos_sky = sky_markers["M"]
                            n_pos_sky = sky_markers["N"]
                            n_prime_pos_sky = sky_markers["N'"]

                            if is_aligned_local(m_pos_sky, s_pos_sky, self.proximity_threshold) and \
                               (self._is_in_nodal_zone(m_pos_sky, n_pos_sky) or \
                                self._is_in_nodal_zone(m_pos_sky, n_prime_pos_sky)):
                                sky_eclipses.append("Solar")
                            
                            sun_opp_sky = (s_pos_sky + NUM_HOLES // 2) % NUM_HOLES
                            if is_aligned_local(m_pos_sky, sun_opp_sky, self.proximity_threshold) and \
                               (self._is_in_nodal_zone(m_pos_sky, n_pos_sky) or \
                                self._is_in_nodal_zone(m_pos_sky, n_prime_pos_sky)):
                                sky_eclipses.append("Lunar")

                            sky_data_results = {
                                "sky_predicted_eclipses": sky_eclipses,
                                "sky_marker_positions_on_date": sky_markers
                            }
                        else:
                            sky_data_results = {"error": "Failed to retrieve sky ephemeris data."}
                    else: # self._ephemeris_seed_gregorian_date is not a QDate instance
                         sky_data_results = {"error": "Seed Gregorian date not in expected QDate format."}
                except Exception as e: # Broader catch for any other issues during sky data part
                    sky_data_results = {"error": f"Error during sky data calculation: {str(e)}"}
            
            sky_data_results["equivalent_gregorian_date_str"] = equivalent_gregorian_date_str


        # Branch 3: No ephemeris seed (original stateless simulation from NOMINAL Hoyle start)
        # This branch only calculates Hoyle's model prediction.
        else:
            temp_sun_nominal = Marker(name="S", initial_position=NUM_HOLES // 2)
            temp_moon_nominal = Marker(name="M", initial_position=0)
            temp_node_n_nominal = Marker(name="N", initial_position=0)
            temp_node_n_prime_nominal = Marker(name="N'", initial_position=NUM_HOLES // 2)
            
            # Apply initial solar alignment for the nominal start if target is Y1,D1 
            # (i.e., total_hoyle_days_from_calendar_start_to_target is 0)
            if total_hoyle_days_from_calendar_start_to_target == 0:
                 temp_sun_nominal.current_position = self._summer_solstice_alignment_hole

            # Temp time state for this nominal Hoyle simulation
            nominal_sim_time_state = TimeState(start_day=1, start_year=1)

            for _ in range(total_hoyle_days_from_calendar_start_to_target):
                sun_cycle_comp, year_cycle_comp = nominal_sim_time_state.advance_day()
                self._advance_hoyle_day_for_temp_simulation(
                    temp_sun_nominal, temp_moon_nominal, temp_node_n_nominal, temp_node_n_prime_nominal,
                    nominal_sim_time_state,
                    sun_cycle_comp, year_cycle_comp
                )
            
            nominal_eclipses = []
            # Local helper for alignment checks
            def is_aligned_local(pos1: int, pos2: int, threshold: int) -> bool:
                diff = abs(pos1 - pos2)
                return diff <= threshold or diff >= (NUM_HOLES - threshold)

            s_pos_nom = temp_sun_nominal.current_position
            m_pos_nom = temp_moon_nominal.current_position
            n_pos_nom = temp_node_n_nominal.current_position
            n_prime_pos_nom = temp_node_n_prime_nominal.current_position
            
            if is_aligned_local(m_pos_nom, s_pos_nom, self.proximity_threshold) and \
               (self._is_in_nodal_zone(m_pos_nom, n_pos_nom) or \
                self._is_in_nodal_zone(m_pos_nom, n_prime_pos_nom)):
                nominal_eclipses.append("Solar")

            sun_opp_nom = (s_pos_nom + NUM_HOLES // 2) % NUM_HOLES
            if is_aligned_local(m_pos_nom, sun_opp_nom, self.proximity_threshold) and \
               (self._is_in_nodal_zone(m_pos_nom, n_pos_nom) or \
                self._is_in_nodal_zone(m_pos_nom, n_prime_pos_nom)):
                nominal_eclipses.append("Lunar")

            hoyle_sim_results = { # Store nominal results under "hoyle_" keys for consistency
                "hoyle_predicted_eclipses": nominal_eclipses,
                "hoyle_marker_positions_on_date": {
                    temp_sun_nominal.name: s_pos_nom, temp_moon_nominal.name: m_pos_nom,
                    temp_node_n_nominal.name: n_pos_nom, temp_node_n_prime_nominal.name: n_prime_pos_nom
                }
            }
            # No sky data for purely nominal Hoyle check unless explicitly requested by a different mechanism
            sky_data_results = {"equivalent_gregorian_date_str": "N/A (Nominal Hoyle Check)"}


        # Restore original main simulation state (important!)
        self.time_state.current_day = original_time_state_data['current_day']
        self.time_state.current_year = original_time_state_data['current_year']
        self.time_state.day_within_13_day_cycle = original_time_state_data['day_within_13_day_cycle']
        self.time_state.day_within_year_cycle = original_time_state_data['day_within_year_cycle']
        self.sun_marker.current_position = original_sun_pos
        self.moon_marker.current_position = original_moon_pos
        self.node_n_marker.current_position = original_node_n_pos
        self.node_n_prime_marker.current_position = original_node_n_prime_pos

        # Combine results
        final_results = {
            "target_year": target_year,
            "target_day": target_day,
            **hoyle_sim_results,
            **sky_data_results
        }
        return final_results

    def get_current_day(self) -> int:
        """
        Returns the current day of the simulation from the TimeState.
        """
        return self.time_state.current_day

    def get_current_year(self) -> int:
        """
        Returns the current year of the simulation from the TimeState.
        """
        return self.time_state.current_year

# Example Usage (for testing - can be removed or moved to a test file):
if __name__ == '__main__':
    # This block is for testing the service directly.
    # from PyQt6.QtCore import QDate, QTime, QDateTime # QDate already imported, QTime/QDateTime not strictly needed for current test logic
    # For testing ephemeris reset

    # print("Initializing Stonehenge Simulation Service...")

    # print("Initial Time: {simulation_service.time_state}")
    # print("Initial Positions: {simulation_service.get_current_marker_positions()}")

    # Test advance_simulation_step and eclipse detection
    # print("\\n--- Running simulation for 6 Hoyle years (2184 days) ---")
    total_days_to_simulate = 364 * 6 # Approx 6 Hoyle years
    eclipse_events_found = 0
    
    for day_num in range(1, total_days_to_simulate + 1):
        result = simulation_service.advance_simulation_step()
        if result["eclipses_detected"]:
            eclipse_events_found +=1
            # print(f"Year: {result['year']}, Day: {result['day']} (Overall Day: {day_num}) -> *** {result['eclipses_detected']} ***")
            # print(f"    Markers: {result['marker_positions']}")
            pass
    
    # print(f"\\n--- Simulation Complete. Ran for {total_days_to_simulate} days. Found {eclipse_events_found} eclipse events. ---")
    # print(f"Final Time: {simulation_service.time_state}")
    # print(f"Final Positions: {simulation_service.get_current_marker_positions()}")

    # Test reset_simulation
    # print("\\n--- Testing reset --- ")
    simulation_service.reset_simulation()
    # print(f"Post-Reset Time: {simulation_service.time_state}")
    # print(f"Post-Reset Positions: {simulation_service.get_current_marker_positions()}")
    for _ in range(5): # Step a few times after reset
        simulation_service.advance_simulation_step()
    # print(f"After 5 steps post-reset: {simulation_service.get_current_marker_positions()}")

    # Test get_hoyle_prediction_for_date
    # print("\\n--- Testing get_hoyle_prediction_for_date ---")
    # prediction_at_6_16 = simulation_service.get_hoyle_prediction_for_date(target_year=6, target_day=16)
    # print(f"Hoyle prediction for Year 6, Day 16:")
    # print(f"  Predicted eclipses: {prediction_at_6_16.get('predicted_eclipses')}")
    # print(f"  Markers: {prediction_at_6_16.get('marker_positions_on_date')}")

    # print("\\n--- Testing reset_simulation_from_ephemeris ---")
    # Example: Reset to a known eclipse date - e.g. Great American Eclipse 2017-08-21
    # test_qdate = QDateTime(QDate(2017, 8, 21), QTime(18,0,0), Qt. टाइमSpec.UTC) # Approx time of max eclipse
    # print(f"Attempting to reset from ephemeris for: {test_qdate.toString()}")
    # new_positions_from_eph = simulation_service.reset_simulation_from_ephemeris(2017, 8, 21)
    # if new_positions_from_eph:
    #     print(f"Successfully reset from ephemeris. New positions: {new_positions_from_eph}")
    #     print(f"Simulation Hoyle Time is now: Day {simulation_service.time_state.current_day}, Year {simulation_service.time_state.current_year}")
    # else:
    #     print("Failed to reset from ephemeris.")

    # print("\\n--- Testing edge cases for _is_solar_eclipse_hoyle and _is_lunar_eclipse_hoyle ---")
    # Example: Manually set markers to test conditions
    # simulation_service.sun_marker.current_position = 0
    # simulation_service.moon_marker.current_position = 0
    # simulation_service.node_n_marker.current_position = 0
    # simulation_service.node_n_prime_marker.current_position = 28 # Opposite N
    # print(f"Test Solar Eclipse (S=0, M=0, N=0, N'=28): {simulation_service._is_solar_eclipse_hoyle()}") # Expected: True

    # simulation_service.sun_marker.current_position = 0
    # simulation_service.moon_marker.current_position = 28 # Moon opposite Sun
    # simulation_service.node_n_marker.current_position = 0 # Sun at N
    # simulation_service.node_n_prime_marker.current_position = 28 # Moon at N'
    # print(f"Test Lunar Eclipse (S=0 at N, M=28 at N'): {simulation_service._is_lunar_eclipse_hoyle()}") # Expected: True
    
    # simulation_service.sun_marker.current_position = 5 # Sun not at a node
    # simulation_service.moon_marker.current_position = 5 # Moon with Sun
    # simulation_service.node_n_marker.current_position = 0
    # print(f"Test Solar Eclipse Fail (Sun not at node): {simulation_service._is_solar_eclipse_hoyle()}") # Expected: False
    
    pass # Keep the test block, just without prints 