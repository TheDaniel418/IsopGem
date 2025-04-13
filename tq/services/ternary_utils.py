"""
Ternary Utilities Service.

This module provides utility functions for working with ternary numbers,
including conversion between decimal and ternary representations,
ternary arithmetic operations, and pattern analysis.
"""
from typing import Dict, List, Optional, Tuple, Union, cast, TypedDict


class TernarySequenceDict(TypedDict):
    digit: Optional[int]
    length: Optional[int]

class TernaryPatternResultDict(TypedDict):
    digit_counts: Dict[int, int]
    sequences: List[Dict[str, int]]
    dominant_digit: int
    balance_score: float

class TernarySequence(dict[str, Optional[int]]):
    digit: Optional[int]
    length: Optional[int]

    def __init__(self, **kwargs: Optional[int]) -> None:
        super().__init__(**kwargs)
        self.digit = kwargs.get('digit')
        self.length = kwargs.get('length')


class TernaryPatternResult(dict[str, Union[Dict[int, int], List[Dict[str, int]], int, float]]):
    digit_counts: Dict[int, int]
    sequences: List[Dict[str, int]]
    dominant_digit: int
    balance_score: float

    def __init__(self, **kwargs: Union[Dict[int, int], List[Dict[str, int]], int, float]) -> None:
        super().__init__(**kwargs)
        self.digit_counts = kwargs.get('digit_counts', {})
        self.sequences = kwargs.get('sequences', [])
        self.dominant_digit = kwargs.get('dominant_digit', 0)
        self.balance_score = kwargs.get('balance_score', 0.0)


class TernaryPatternAnalysis(TypedDict):
    zero_count: int
    one_count: int
    two_count: int
    dominant_digit: int
    balance_score: float
    longest_sequence: int
    sequence_digit: int


TernaryDigit = Union[int, str]
TernaryNumber = List[TernaryDigit]


def decimal_to_ternary(decimal: int) -> TernaryNumber:
    """
    Convert a decimal number to its ternary representation.

    Args:
        decimal: The decimal number to convert

    Returns:
        List of ternary digits (0, 1, or 2)
    """
    if decimal == 0:
        return [0]

    ternary: TernaryNumber = []
    n = abs(decimal)
    
    while n:
        ternary.append(n % 3)
        n //= 3
        
    if decimal < 0:
        # For negative numbers, convert to balanced ternary
        for i in range(len(ternary)):
            if ternary[i] == 2:
                ternary[i] = -1
                if i + 1 >= len(ternary):
                    ternary.append(1)
                else:
                    ternary[i + 1] += 1
    
    return list(reversed(ternary))


def ternary_to_decimal(ternary: TernaryNumber) -> int:
    """
    Convert ternary digits back to decimal.

    Args:
        ternary: List of ternary digits (0, 1, or 2)

    Returns:
        The decimal number
    """
    decimal = 0
    power = 1
    
    for digit in reversed(ternary):
        digit_val = int(digit) if isinstance(digit, str) else digit
        decimal += digit_val * power
        power *= 3
        
    return decimal


def find_ternary_patterns(ternary: TernaryNumber) -> TernaryPatternAnalysis:
    """
    Analyze ternary digits for patterns.

    Examines the ternary representation for:
    - Digit counts (0s, 1s, 2s)
    - Dominant digit
    - Balance score
    - Sequences of same digits

    Args:
        ternary: List of ternary digits to analyze

    Returns:
        Dictionary containing pattern analysis:
        {
            'zero_count': Number of 0s,
            'one_count': Number of 1s,
            'two_count': Number of 2s,
            'dominant_digit': Most frequent digit,
            'balance_score': How evenly distributed the digits are (0-1),
            'longest_sequence': Length of longest sequence of same digit,
            'sequence_digit': The digit in the longest sequence
        }
    """
    # Convert string digits to integers
    ternary_int = [int(d) if isinstance(d, str) else d for d in ternary]
    
    # Count occurrences of each digit
    counts = {
        0: sum(1 for d in ternary_int if d == 0),
        1: sum(1 for d in ternary_int if d == 1),
        2: sum(1 for d in ternary_int if d == 2)
    }
    
    # Find dominant digit
    dominant = max(counts.items(), key=lambda x: x[1])[0]
    
    # Calculate balance score (0 = perfectly balanced, 1 = all same digit)
    total = len(ternary)
    expected = total / 3
    deviations = [abs(c - expected) for c in counts.values()]
    balance = sum(deviations) / (2 * expected)
    
    # Find longest sequence
    current_digit = ternary_int[0]
    current_len = 1
    max_len = 1
    max_digit = current_digit
    
    for digit in ternary_int[1:]:
        if digit == current_digit:
            current_len += 1
            if current_len > max_len:
                max_len = current_len
                max_digit = digit
        else:
            current_digit = digit
            current_len = 1
    
    return {
        'zero_count': counts[0],
        'one_count': counts[1], 
        'two_count': counts[2],
        'dominant_digit': dominant,
        'balance_score': balance,
        'longest_sequence': max_len,
        'sequence_digit': max_digit
    }
