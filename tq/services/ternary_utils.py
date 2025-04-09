"""
Ternary Utilities Service.

This module provides utility functions for working with ternary numbers,
including conversion between decimal and ternary representations,
ternary arithmetic operations, and pattern analysis.
"""


def decimal_to_ternary(decimal_num: int) -> list[int]:
    """
    Convert a decimal number to its ternary representation.

    Args:
        decimal_num: The decimal number to convert

    Returns:
        A list of integers (0, 1, 2) representing the ternary digits
    """
    if decimal_num == 0:
        return [0]

    digits = []
    n = abs(decimal_num)

    while n > 0:
        remainder = n % 3
        digits.insert(0, remainder)
        n //= 3

    return digits


def ternary_to_decimal(ternary_digits: list[int]) -> int:
    """
    Convert a ternary representation to its decimal value.

    Args:
        ternary_digits: List of ternary digits (0, 1, 2)

    Returns:
        The decimal value as an integer
    """
    decimal = 0
    power = 1

    for digit in reversed(ternary_digits):
        decimal += digit * power
        power *= 3

    return decimal


def find_ternary_patterns(ternary_digits: list[int]) -> dict:
    """
    Analyze ternary digits for patterns.

    Args:
        ternary_digits: List of ternary digits (0, 1, 2)

    Returns:
        Dictionary with pattern analysis results
    """
    result = {
        "digit_counts": {0: 0, 1: 0, 2: 0},
        "sequences": [],
        "dominant_digit": None,
        "balance_score": 0,  # Positive = expansive, Negative = contractive, 0 = balanced
    }

    # Count digits
    for digit in ternary_digits:
        result["digit_counts"][digit] += 1

    # Find the dominant digit
    max_count = max(result["digit_counts"].values())
    dominant_digits = [
        d for d, count in result["digit_counts"].items() if count == max_count
    ]
    result["dominant_digit"] = dominant_digits[0] if len(dominant_digits) == 1 else None

    # Calculate balance score
    result["balance_score"] = result["digit_counts"][1] - result["digit_counts"][2]

    # Find sequences
    current_sequence = []
    current_digit = None

    for digit in ternary_digits:
        if digit == current_digit:
            current_sequence.append(digit)
        else:
            if len(current_sequence) >= 3:
                result["sequences"].append(
                    {"digit": current_digit, "length": len(current_sequence)}
                )
            current_digit = digit
            current_sequence = [digit]

    # Check last sequence
    if len(current_sequence) >= 3:
        result["sequences"].append(
            {"digit": current_digit, "length": len(current_sequence)}
        )

    return result
