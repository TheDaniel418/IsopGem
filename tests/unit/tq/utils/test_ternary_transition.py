"""
Unit tests for the Ternary Transition System.

Tests the TernaryTransition class functionality, including transition operations,
custom maps, cycle detection, and error handling.
"""

import unittest
from tq.utils.ternary_transition import TernaryTransition, TransitionMap


class TestTernaryTransition(unittest.TestCase):
    """Test case for the TernaryTransition class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transition = TernaryTransition()
        
        # Custom map for testing
        self.custom_map = {
            (0, 0): 1, (0, 1): 1, (0, 2): 1,
            (1, 0): 0, (1, 1): 0, (1, 2): 0,
            (2, 0): 2, (2, 1): 2, (2, 2): 2
        }
        self.custom_transition = TernaryTransition(self.custom_map)
    
    def test_default_map(self):
        """Test the default transition map follows the defined patterns."""
        # The default map should follow Taoist principles
        # Checking a few key transitions
        self.assertEqual(self.transition.transition_map[(0, 0)], 0)  # Equilibrium with equilibrium
        self.assertEqual(self.transition.transition_map[(1, 2)], 0)  # Opposites meeting return to source
        self.assertEqual(self.transition.transition_map[(2, 1)], 0)  # Opposites meeting return to source
        self.assertEqual(self.transition.transition_map[(1, 1)], 1)  # Same active principle stays active
        self.assertEqual(self.transition.transition_map[(2, 2)], 2)  # Same receptive principle stays receptive
    
    def test_custom_map(self):
        """Test creating a transition with a custom map."""
        # Our custom map should produce different results than the default
        self.assertEqual(self.custom_transition.transition_map[(0, 0)], 1)
        self.assertEqual(self.custom_transition.transition_map[(1, 2)], 0)
        
        # Test basic transitions with custom map
        result = self.custom_transition.apply_transition("012", "012")
        self.assertEqual(result, "102")
    
    def test_from_rule_string(self):
        """Test creating a transition from a rule string."""
        rule_string = "00:0,01:2,02:1,10:2,11:1,12:0,20:1,21:0,22:2"
        from_string = TernaryTransition.from_rule_string(rule_string)
        
        # The map should match the default map
        self.assertEqual(from_string.transition_map, self.transition.transition_map)
        
        # Test with a custom rule string
        custom_rule = "00:1,01:1,02:1,10:0,11:0,12:0,20:2,21:2,22:2"
        custom_from_string = TernaryTransition.from_rule_string(custom_rule)
        self.assertEqual(custom_from_string.transition_map, self.custom_map)
    
    def test_invalid_rule_string(self):
        """Test error handling for invalid rule strings."""
        invalid_rules = [
            "00:3,01:2",  # Invalid value (3)
            "03:1,01:2",  # Invalid digit (3)
            "00-1,01:2",  # Invalid format
            "00:1:1,01:2"  # Too many parts
        ]
        
        for rule in invalid_rules:
            with self.subTest(rule=rule):
                with self.assertRaises(ValueError):
                    TernaryTransition.from_rule_string(rule)
    
    def test_apply_transition(self):
        """Test applying a transition between two ternary strings."""
        test_cases = [
            # From the documentation example
            ("220", "111", "002"),
            
            # Other test cases
            ("0", "0", "0"),
            ("1", "2", "0"),
            ("2", "1", "0"),
            ("12", "21", "00"),
            ("1212", "2121", "0000"),
            ("222", "111", "000"),
            ("102", "210", "021")
        ]
        
        for first, second, expected in test_cases:
            with self.subTest(first=first, second=second):
                result = self.transition.apply_transition(first, second)
                self.assertEqual(result, expected)
    
    def test_padding_unequal_lengths(self):
        """Test that strings of unequal length are padded correctly."""
        test_cases = [
            ("1", "22", "10"),    # 1 padded to 01, (0,2)→1, (1,2)→0
            ("22", "1", "10"),    # 1 padded to 01, (2,0)→1, (2,1)→0
            ("100", "2", "201"),  # 2 padded to 002, (1,0)→2, (0,0)→0, (0,2)→1
        ]
        
        for first, second, expected in test_cases:
            with self.subTest(first=first, second=second):
                result = self.transition.apply_transition(first, second)
                self.assertEqual(result, expected)
    
    def test_apply_multiple(self):
        """Test applying multiple transitions."""
        first = "220"
        second = "111"
        expected_sequence = [
            ("220", "111", "002"),  # First transition
            ("002", "220", "111"),  # Second transition
            ("111", "002", "220")   # Third transition (cycle completes)
        ]
        
        result = self.transition.apply_multiple(first, second, 3)
        self.assertEqual(result, expected_sequence)
    
    def test_find_cycle(self):
        """Test finding a cycle in the transition sequence."""
        # Example from documentation with a 3-cycle
        cycle = self.transition.find_cycle("220", "111")
        self.assertEqual(len(cycle), 3)
        
        # Verify the cycle
        # Verify the first step
        self.assertEqual(cycle[0][0], "220")  # First number
        self.assertEqual(cycle[0][1], "111")  # Second number
        self.assertEqual(cycle[0][2], "002")  # Result
        
        # After applying these three steps, we should be back at the start state
        self.assertEqual(cycle[2][2], "220")  # Result of third step is 220, back to the start
    
    def test_validation(self):
        """Test input validation for ternary strings."""
        invalid_inputs = [
            "3",     # Invalid digit
            "123",   # Contains invalid digit
            "abc",   # Non-numeric
            "1-2",   # Contains invalid character
            "1.2"    # Contains invalid character
        ]
        
        for invalid in invalid_inputs:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.transition.apply_transition(invalid, "012")
                
                with self.assertRaises(ValueError):
                    self.transition.apply_transition("012", invalid)
    
    def test_validate_transition_map(self):
        """Test validation of transition maps."""
        # Map with missing pair
        incomplete_map = {
            (0, 0): 0, (0, 1): 2, (0, 2): 1,
            (1, 0): 2, (1, 1): 1, (1, 2): 0,
            (2, 0): 1, (2, 1): 0  # Missing (2,2)
        }
        
        with self.assertRaises(ValueError):
            TernaryTransition(incomplete_map)
        
        # Map with invalid value
        invalid_value_map = {
            (0, 0): 0, (0, 1): 2, (0, 2): 1,
            (1, 0): 2, (1, 1): 1, (1, 2): 0,
            (2, 0): 1, (2, 1): 0, (2, 2): 3  # Invalid value 3
        }
        
        with self.assertRaises(ValueError):
            TernaryTransition(invalid_value_map)
    
    def test_apply_conrune(self):
        """Test the Conrune transformation that swaps 1s and 2s."""
        test_cases = [
            ("11220", "22110"),  # Example from requirement
            ("0", "0"),          # 0 stays the same
            ("1", "2"),          # 1 becomes 2
            ("2", "1"),          # 2 becomes 1
            ("12", "21"),        # Mixed digits
            ("222", "111"),      # All 2s become 1s
            ("111", "222"),      # All 1s become 2s
            ("0102", "0201"),    # Mixed with 0s
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                result = self.transition.apply_conrune(input_str)
                self.assertEqual(result, expected)
    
    def test_conrune_validation(self):
        """Test that apply_conrune validates inputs."""
        invalid_inputs = [
            "3",    # Invalid digit
            "abc",  # Non-numeric
            "12a"   # Contains invalid character
        ]
        
        for invalid in invalid_inputs:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.transition.apply_conrune(invalid)


if __name__ == '__main__':
    unittest.main() 