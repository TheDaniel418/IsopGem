"""
Unit tests for the StonehengeSimulationService class.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: pytest, astrology.services.stonehenge_simulation_service.StonehengeSimulationService, 
              astrology.models.stonehenge_marker.Marker, astrology.models.stonehenge_time_state.TimeState,
              astrology.models.stonehenge_circle_config.NUM_HOLES
"""

import pytest
from astrology.services.stonehenge_simulation_service import StonehengeSimulationService
from astrology.models.stonehenge_marker import Marker # For type hinting if needed, or direct use
from astrology.models.stonehenge_time_state import TimeState
from astrology.models.stonehenge_circle_config import NUM_HOLES

@pytest.fixture
def service() -> StonehengeSimulationService:
    """Provides a default StonehengeSimulationService instance for tests."""
    return StonehengeSimulationService(proximity_threshold=0)

@pytest.fixture
def service_prox_1() -> StonehengeSimulationService:
    """Provides a StonehengeSimulationService instance with proximity_threshold=1."""
    return StonehengeSimulationService(proximity_threshold=1)

class TestStonehengeSimulationService:
    """Test suite for the StonehengeSimulationService class."""

    def test_initialization(self, service: StonehengeSimulationService):
        """Test correct initialization of the service and default marker positions."""
        assert isinstance(service.time_state, TimeState)
        assert service.sun_marker.name == "S" and service.sun_marker.current_position == NUM_HOLES // 2
        assert service.moon_marker.name == "M" and service.moon_marker.current_position == 0
        assert service.node_n_marker.name == "N" and service.node_n_marker.current_position == 0
        assert service.node_n_prime_marker.name == "N'" and service.node_n_prime_marker.current_position == NUM_HOLES // 2
        assert service.proximity_threshold == 0

    def test_initialization_with_proximity(self):
        """Test initialization with a non-default proximity threshold."""
        service_custom_prox = StonehengeSimulationService(proximity_threshold=2)
        assert service_custom_prox.proximity_threshold == 2

    def test_get_current_marker_positions(self, service: StonehengeSimulationService):
        """Test retrieving current marker positions."""
        positions = service.get_current_marker_positions()
        expected_positions = {
            "S": NUM_HOLES // 2,
            "M": 0,
            "N": 0,
            "N'": NUM_HOLES // 2
        }
        assert positions == expected_positions

    def test_moon_marker_movement(self, service: StonehengeSimulationService):
        """Test Moon marker moves 2 positions anticlockwise daily."""
        initial_pos = service.moon_marker.current_position
        service.advance_simulation_step() # Day 1
        assert service.moon_marker.current_position == (initial_pos + 2) % NUM_HOLES
        service.advance_simulation_step() # Day 2
        assert service.moon_marker.current_position == (initial_pos + 4) % NUM_HOLES

    def test_sun_marker_movement(self, service: StonehengeSimulationService):
        """Test Sun marker moves 2 positions anticlockwise every 13 days."""
        initial_pos = service.sun_marker.current_position
        for _ in range(12):
            service.advance_simulation_step()
        assert service.sun_marker.current_position == initial_pos # No move yet
        
        service.advance_simulation_step() # 13th day
        assert service.sun_marker.current_position == (initial_pos + 2) % NUM_HOLES
        
        # After another 12 days, still at the new position
        for _ in range(12):
            service.advance_simulation_step()
        assert service.sun_marker.current_position == (initial_pos + 2) % NUM_HOLES
        service.advance_simulation_step() # 26th day
        assert service.sun_marker.current_position == (initial_pos + 4) % NUM_HOLES

    def test_node_marker_movement(self, service: StonehengeSimulationService):
        """Test Node markers move 3 positions clockwise yearly, N' opposite N."""
        initial_n_pos = service.node_n_marker.current_position
        initial_n_prime_pos = service.node_n_prime_marker.current_position
        
        days_in_hoyle_year = TimeState.DAYS_IN_HOYLE_YEAR
        for _ in range(days_in_hoyle_year -1):
            service.advance_simulation_step()
        
        assert service.node_n_marker.current_position == initial_n_pos
        assert service.node_n_prime_marker.current_position == initial_n_prime_pos

        service.advance_simulation_step() # Completes the year
        expected_n_pos = (initial_n_pos - 3 + NUM_HOLES) % NUM_HOLES
        assert service.node_n_marker.current_position == expected_n_pos
        assert service.node_n_prime_marker.current_position == (expected_n_pos + NUM_HOLES // 2) % NUM_HOLES

    def test_no_eclipse_on_initialization(self, service: StonehengeSimulationService):
        """Test no eclipse is detected on initialization (default positions)."""
        # Need to advance one step to trigger _check_for_eclipses via _move_markers
        # However, let's check the state before the first true step of movement if possible.
        # The _check_for_eclipses is called after movement in advance_simulation_step.
        # Initial state itself is M=0, S=28, N=0, N'=28. Full Moon, M aligned with N. So Lunar Eclipse.
        # Let's test advance_simulation_step output directly.
        
        # After 1 day:
        # M = 2, S = 28, N = 0, N' = 28
        # Not new moon, not full moon. No Node alignment for M.
        result = service.advance_simulation_step()
        assert not result["eclipses_detected"]

    def test_solar_eclipse_detection_exact(self, service: StonehengeSimulationService):
        """Test solar eclipse detection with exact alignment (prox=0)."""
        # Manually set up a known solar eclipse condition
        # New Moon: M == S
        # Moon aligned with Node: M == N (or M == N')
        service.sun_marker.current_position = 10
        service.moon_marker.current_position = 10
        service.node_n_marker.current_position = 10
        service.node_n_prime_marker.current_position = (10 + NUM_HOLES // 2) % NUM_HOLES
        # _check_for_eclipses is internal, so we test through advance_simulation_step
        # To avoid marker movement messing up our setup, we can check internal method if we make it public
        # or carefully control the step. Here, we assume this is a state *after* movement for one step.
        eclipses = service._check_for_eclipses() # Test internal logic directly for setup simplicity
        assert "Solar Eclipse" in eclipses
        assert "Lunar Eclipse" not in eclipses

    def test_lunar_eclipse_detection_exact(self, service: StonehengeSimulationService):
        """Test lunar eclipse detection with exact alignment (prox=0)."""
        # Full Moon: M is opposite S
        # Moon aligned with Node: M == N (or M == N')
        service.sun_marker.current_position = 0
        service.moon_marker.current_position = NUM_HOLES // 2 # M at 28
        service.node_n_marker.current_position = NUM_HOLES // 2 # N at 28
        service.node_n_prime_marker.current_position = 0 # N' at 0
        eclipses = service._check_for_eclipses()
        assert "Lunar Eclipse" in eclipses
        assert "Solar Eclipse" not in eclipses

    def test_solar_eclipse_detection_prox_1(self, service_prox_1: StonehengeSimulationService):
        """Test solar eclipse detection with proximity_threshold = 1."""
        service = service_prox_1
        # New Moon (M near S): S=10, M=11
        # Moon near Node (M near N): M=11, N=12
        service.sun_marker.current_position = 10
        service.moon_marker.current_position = 11 
        service.node_n_marker.current_position = 12
        service.node_n_prime_marker.current_position = (12 + NUM_HOLES // 2) % NUM_HOLES
        eclipses = service._check_for_eclipses()
        assert "Solar Eclipse" in eclipses

        # Test wrap around for S-M proximity
        service.sun_marker.current_position = NUM_HOLES -1 # S at 55
        service.moon_marker.current_position = 0          # M at 0
        service.node_n_marker.current_position = 0          # N at 0
        eclipses = service._check_for_eclipses()
        assert "Solar Eclipse" in eclipses

    def test_lunar_eclipse_detection_prox_1(self, service_prox_1: StonehengeSimulationService):
        """Test lunar eclipse detection with proximity_threshold = 1."""
        service = service_prox_1
        # Full Moon (M near S_opposite): S=0 (S_opp=28), M=27
        # Moon near Node (M near N): M=27, N=28
        service.sun_marker.current_position = 0
        service.moon_marker.current_position = 27
        service.node_n_marker.current_position = 28
        service.node_n_prime_marker.current_position = 0
        eclipses = service._check_for_eclipses()
        assert "Lunar Eclipse" in eclipses

        # Test wrap around for M-N proximity
        service.sun_marker.current_position = 0 # S_opp=28
        service.moon_marker.current_position = 28 # M=28
        service.node_n_marker.current_position = NUM_HOLES -1 # N=55, M is 28. abs(28-55)=27. 56-1=55. Fails. Wait.
                                                # M=28, N=0. aligned(28,0,1) -> diff=28. No. This is not wrap for M-N.
                                                # M-N proximity means M and N are close. Wrap is if M=0, N=55.
        service.node_n_marker.current_position = 0 # M=28, N=0. Not proximate for lunar.
        # Let M=0, N=55. Sun must be at 28 for Full Moon. 
        service.moon_marker.current_position = 0
        service.sun_marker.current_position = NUM_HOLES // 2 # S=28, M is opposite (Full Moon)
        service.node_n_marker.current_position = NUM_HOLES -1 # N=55. M=0. is_aligned(0,55,1) -> yes.
        eclipses = service._check_for_eclipses()
        assert "Lunar Eclipse" in eclipses, f"M={service.moon_marker.current_position}, S={service.sun_marker.current_position}, N={service.node_n_marker.current_position}"


    def test_advance_simulation_step_return_value(self, service: StonehengeSimulationService):
        """Test the return dictionary of advance_simulation_step."""
        result = service.advance_simulation_step()
        assert "day" in result
        assert "year" in result
        assert "eclipses_detected" in result
        assert "marker_positions" in result
        assert isinstance(result["eclipses_detected"], list)
        assert isinstance(result["marker_positions"], dict)
        assert result["day"] == service.time_state.current_day
        assert result["year"] == service.time_state.current_year

    def test_reset_simulation(self, service: StonehengeSimulationService):
        """Test resetting the simulation."""
        # Advance a bit
        for _ in range(50):
            service.advance_simulation_step()
        service.proximity_threshold = 5 # Change threshold
        
        service.reset_simulation(start_day=10, start_year=2, proximity_threshold=1)
        
        assert service.time_state.current_day == 10
        assert service.time_state.current_year == 2
        assert service.time_state.day_within_13_day_cycle == 0
        assert service.time_state.day_within_year_cycle == 0
        assert service.moon_marker.current_position == 0
        assert service.sun_marker.current_position == NUM_HOLES // 2
        assert service.node_n_marker.current_position == 0
        assert service.node_n_prime_marker.current_position == NUM_HOLES // 2
        assert service.proximity_threshold == 1

    def test_simulation_run_finds_eclipses(self, service: StonehengeSimulationService):
        """A basic run to see if any eclipses are found over a period."""
        # This is more of an integration smoke test for the simulation logic.
        # Predicting exact eclipse dates with Hoyle's simple model is complex, 
        # but we expect *some* events over a long enough period.
        eclipse_found = False
        for _ in range(TimeState.DAYS_IN_HOYLE_YEAR * 20): # Simulate 20 Hoyle years
            result = service.advance_simulation_step()
            if result["eclipses_detected"]:
                eclipse_found = True
                print(f"Found: {result['eclipses_detected']} in Year {result['year']}, Day {result['day']}")
                break
        assert eclipse_found, "Expected at least one eclipse event in a 20-year simulation."

# To run these tests, navigate to the project root in the terminal and run: pytest 