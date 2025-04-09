"""
Unit tests for ternary conversion utility functions.

Tests the decimal to ternary and ternary to decimal conversion functions,
along with formatting and utility functions for ternary numbers.
"""

import unittest
from tq.utils.ternary_converter import (
    decimal_to_ternary,
    ternary_to_decimal,
    format_ternary,
    split_ternary_digits,
    get_ternary_digit_positions
)


class TestTernaryConverter(unittest.TestCase):
    """Test case for the ternary conversion utilities."""
    
    def test_decimal_to_ternary(self):
        """Test conversion from decimal to ternary."""
        test_cases = [
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '10'),
            (4, '11'),
            (5, '12'),
            (6, '20'),
            (7, '21'),
            (8, '22'),
            (9, '100'),
            (10, '101'),
            (13, '111'),
            (27, '1000'),
            (42, '1120'),
            (-1, '-1'),
            (-10, '-101')
        ]
        
        for decimal, expected_ternary in test_cases:
            with self.subTest(decimal=decimal):
                self.assertEqual(decimal_to_ternary(decimal), expected_ternary)
    
    def test_ternary_to_decimal(self):
        """Test conversion from ternary to decimal."""
        test_cases = [
            ('0', 0),
            ('1', 1),
            ('2', 2),
            ('10', 3),
            ('11', 4),
            ('12', 5),
            ('20', 6),
            ('21', 7),
            ('22', 8),
            ('100', 9),
            ('101', 10),
            ('111', 13),
            ('1000', 27),
            ('1120', 42),
            ('-1', -1),
            ('-101', -10)
        ]
        
        for ternary, expected_decimal in test_cases:
            with self.subTest(ternary=ternary):
                self.assertEqual(ternary_to_decimal(ternary), expected_decimal)
    
    def test_invalid_ternary_input(self):
        """Test error handling for invalid ternary input."""
        invalid_inputs = ['3', '123', 'abc', '1a2', '13', '1-2']
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                with self.assertRaises(ValueError):
                    ternary_to_decimal(invalid_input)
    
    def test_roundtrip_conversion(self):
        """Test that converting decimal to ternary and back maintains the original value."""
        test_values = [0, 1, 5, 10, 27, 42, 100, 999, -5, -42]
        
        for value in test_values:
            with self.subTest(value=value):
                ternary = decimal_to_ternary(value)
                result = ternary_to_decimal(ternary)
                self.assertEqual(result, value)
    
    def test_format_ternary_padding(self):
        """Test ternary formatting with padding."""
        test_cases = [
            ('1', 0, 0, ' ', '1'),        # No padding
            ('1', 3, 0, ' ', '001'),      # Pad to length 3
            ('101', 5, 0, ' ', '00101'),  # Pad to length 5
            ('-1', 3, 0, ' ', '-001')     # Negative number with padding
        ]
        
        for ternary, pad_length, group_size, separator, expected in test_cases:
            with self.subTest(ternary=ternary, pad_length=pad_length):
                result = format_ternary(ternary, pad_length, group_size, separator)
                self.assertEqual(result, expected)
    
    def test_format_ternary_grouping(self):
        """Test ternary formatting with grouping."""
        test_cases = [
            ('12345', 0, 0, ' ', '12345'),       # No grouping
            ('12345', 0, 3, ' ', '12 345'),      # Group by 3
            ('12345', 0, 2, ' ', '1 23 45'),     # Group by 2
            ('12345', 0, 3, '.', '12.345'),      # Custom separator
            ('12345', 7, 3, ' ', '0 012 345'),   # Padding + grouping - fixed expected value
            ('-12345', 0, 3, ' ', '-12 345')     # Negative number with grouping
        ]
        
        for ternary, pad_length, group_size, separator, expected in test_cases:
            with self.subTest(ternary=ternary, group_size=group_size):
                result = format_ternary(ternary, pad_length, group_size, separator)
                self.assertEqual(result, expected)
    
    def test_split_ternary_digits(self):
        """Test splitting ternary string into digit list."""
        test_cases = [
            ('0', [0]),
            ('1', [1]),
            ('2', [2]),
            ('102', [1, 0, 2]),
            ('1120', [1, 1, 2, 0])
        ]
        
        for ternary, expected_digits in test_cases:
            with self.subTest(ternary=ternary):
                self.assertEqual(split_ternary_digits(ternary), expected_digits)
    
    def test_get_ternary_digit_positions(self):
        """Test getting positions and values of ternary digits."""
        # Test regular cases
        self.assertEqual(get_ternary_digit_positions(13), [(2, 1), (1, 1), (0, 1)])  # 13 = 1*3² + 1*3¹ + 1*3⁰
        self.assertEqual(get_ternary_digit_positions(8), [(1, 2), (0, 2)])          # 8 = 2*3¹ + 2*3⁰
        
        # Test with minimum length
        self.assertEqual(get_ternary_digit_positions(1, min_length=3), [(2, 0), (1, 0), (0, 1)])
        self.assertEqual(get_ternary_digit_positions(0, min_length=2), [(1, 0), (0, 0)])


if __name__ == '__main__':
    unittest.main() 