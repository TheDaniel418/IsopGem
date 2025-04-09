"""
Purpose: Provides utility functions for converting between decimal and ternary number systems

This file is part of the tq pillar and serves as a utility component.
It is responsible for handling conversions between base-10 and base-3 number systems,
which is a fundamental operation for TQ (Ternary Qabala) analysis.

Key components:
- decimal_to_ternary: Converts decimal integers to ternary strings
- ternary_to_decimal: Converts ternary strings to decimal integers
- decimal_to_balanced_ternary: Converts decimal integers to balanced ternary strings
- balanced_to_original: Converts balanced ternary back to standard ternary
- format_ternary: Formats ternary strings with padding and grouping options

Dependencies:
- None (uses only standard Python libraries)

Related files:
- tq/models/tq_grid.py: Uses ternary conversion for TQ grid positions
- tq/services/tq_analysis_service.py: Uses conversions for element analysis
"""

from typing import List, Tuple, Optional


def decimal_to_ternary(decimal_num: int) -> str:
    """Convert a decimal (base-10) number to ternary (base-3) representation.
    
    Args:
        decimal_num: The decimal integer to convert
        
    Returns:
        A string representing the ternary value
        
    Examples:
        >>> decimal_to_ternary(8)
        '22'
        >>> decimal_to_ternary(13)
        '111'
    """
    if decimal_num == 0:
        return '0'
    
    digits = []
    n = abs(decimal_num)
    
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    
    # Handle negative numbers with a negative sign prefix
    result = ''.join(reversed(digits))
    if decimal_num < 0:
        result = '-' + result
        
    return result


def ternary_to_decimal(ternary_str: str) -> int:
    """Convert a ternary (base-3) string to a decimal (base-10) integer.
    
    Args:
        ternary_str: String representing a ternary number (containing only 0, 1, 2 digits)
        
    Returns:
        The decimal integer value
        
    Raises:
        ValueError: If ternary_str contains characters other than 0, 1, 2, or -
        
    Examples:
        >>> ternary_to_decimal('22')
        8
        >>> ternary_to_decimal('111')
        13
    """
    # Check for negative sign
    is_negative = False
    if ternary_str.startswith('-'):
        is_negative = True
        ternary_str = ternary_str[1:]
    
    # Validate input
    if not all(digit in '012' for digit in ternary_str):
        raise ValueError(f"Invalid ternary string: {ternary_str} (must contain only digits 0, 1, 2)")
    
    # Convert to decimal
    decimal_value = 0
    for digit in ternary_str:
        decimal_value = decimal_value * 3 + int(digit)
    
    return -decimal_value if is_negative else decimal_value


def format_ternary(ternary_str: str, pad_length: int = 0, group_size: int = 0, 
                  group_separator: str = ' ') -> str:
    """Format a ternary string with optional padding and grouping.
    
    Args:
        ternary_str: The ternary string to format
        pad_length: Length to pad the string to (with leading zeros)
        group_size: Size of each group for separation (0 means no grouping)
        group_separator: Character to use between groups
        
    Returns:
        The formatted ternary string
        
    Examples:
        >>> format_ternary('111', pad_length=6)
        '000111'
        >>> format_ternary('111222', group_size=3)
        '111 222'
        >>> format_ternary('12', pad_length=6, group_size=3)
        '000 012'
    """
    # Handle negative sign if present
    is_negative = False
    if ternary_str.startswith('-'):
        is_negative = True
        ternary_str = ternary_str[1:]
    
    # Apply padding
    if pad_length > 0:
        ternary_str = ternary_str.zfill(pad_length)
    
    # Apply grouping
    if group_size > 0:
        # Calculate groups from right to left
        groups = []
        for i in range(len(ternary_str), 0, -group_size):
            start = max(0, i - group_size)
            groups.insert(0, ternary_str[start:i])
        ternary_str = group_separator.join(groups)
    
    # Restore negative sign if needed
    if is_negative:
        ternary_str = '-' + ternary_str
        
    return ternary_str


def split_ternary_digits(ternary_str: str) -> List[int]:
    """Split a ternary string into a list of individual digits.
    
    Args:
        ternary_str: The ternary string to split
        
    Returns:
        A list of integers (0, 1, or 2) representing the ternary digits
        
    Raises:
        ValueError: If ternary_str contains invalid characters
        
    Examples:
        >>> split_ternary_digits('102')
        [1, 0, 2]
    """
    # Handle negative sign if present
    is_negative = False
    if ternary_str.startswith('-'):
        is_negative = True
        ternary_str = ternary_str[1:]
    
    # Validate input
    if not all(digit in '012' for digit in ternary_str):
        raise ValueError(f"Invalid ternary string: {ternary_str} (must contain only digits 0, 1, 2)")
    
    # Convert to list of integers
    digits = [int(digit) for digit in ternary_str]
    
    # Apply negative sign to first digit if needed (for display purposes)
    if is_negative and digits:
        digits[0] = -digits[0]
        
    return digits


def get_ternary_digit_positions(decimal_num: int, min_length: int = 1) -> List[Tuple[int, int]]:
    """Get the positions and values of ternary digits in a decimal number.
    
    This is useful for TQ grid analysis where you need to know which powers of 3
    contribute to a number and their corresponding digit values.
    
    Args:
        decimal_num: The decimal number to analyze
        min_length: The minimum number of positions to return
        
    Returns:
        A list of (position, value) tuples, where position is the power of 3 (0-indexed)
        and value is the ternary digit (0, 1, or 2)
        
    Examples:
        >>> get_ternary_digit_positions(13)  # 13 in ternary is '111'
        [(2, 1), (1, 1), (0, 1)]
    """
    ternary = decimal_to_ternary(decimal_num)
    digits = split_ternary_digits(ternary)
    
    # Calculate positions (powers of 3)
    # The rightmost digit is 3^0, the next is 3^1, etc.
    positions = []
    for i, digit in enumerate(reversed(digits)):
        positions.append((i, digit))
    
    # Pad with zeros if needed
    while len(positions) < min_length:
        positions.append((len(positions), 0))
    
    return list(reversed(positions))


def decimal_to_balanced_ternary(decimal_num: int) -> str:
    """Convert a decimal number to balanced ternary representation.
    
    In balanced ternary, digits are {-1, 0, 1} instead of {0, 1, 2}.
    We represent -1 as 'T' (for "minus").
    
    Args:
        decimal_num: The decimal integer to convert
        
    Returns:
        A string representing the balanced ternary value using {T,0,1}
        
    Examples:
        >>> decimal_to_balanced_ternary(8)
        '1T1T'  # 1×3³ + (-1)×3² + 1×3¹ + (-1)×3⁰ = 27 - 9 + 3 - 1 = 8
        >>> decimal_to_balanced_ternary(-4)
        'T11'   # (-1)×3² + 1×3¹ + 1×3⁰ = -9 + 3 + 1 = -4
    """
    if decimal_num == 0:
        return '0'
        
    digits = []
    n = abs(decimal_num)
    
    while n > 0:
        remainder = n % 3
        n //= 3
        
        if remainder == 2:
            remainder = -1
            n += 1
            
        digits.append('T' if remainder == -1 else str(remainder))
    
    result = ''.join(reversed(digits))
    if decimal_num < 0:
        # For negative numbers, negate each digit
        result = ''.join('T' if d == '1' else '1' if d == 'T' else '0' for d in result)
        
    return result


def balanced_to_original(balanced_str: str) -> str:
    """Convert a balanced ternary string to standard ternary.
    
    In balanced ternary, digits are {T,0,1} for {-1,0,1}.
    This converts back to standard ternary {0,1,2}.
    
    Args:
        balanced_str: String using {T,0,1} for {-1,0,1}
        
    Returns:
        A string representing standard ternary using {0,1,2}
        
    Raises:
        ValueError: If balanced_str contains invalid characters
        
    Examples:
        >>> balanced_to_original('1T1T')
        '1212'  # Each T becomes 2
        >>> balanced_to_original('T11')
        '211'   # Leading T becomes 2
    """
    if not all(digit in 'T01' for digit in balanced_str):
        raise ValueError(f"Invalid balanced ternary string: {balanced_str} (must contain only T, 0, 1)")
    
    # Convert T to 2, leave 0 and 1 unchanged
    return balanced_str.replace('T', '2')


def balanced_ternary_to_decimal(balanced_str: str) -> int:
    """Convert a balanced ternary string to decimal.
    
    Args:
        balanced_str: String using {T,0,1} for {-1,0,1}
        
    Returns:
        The decimal integer value
        
    Raises:
        ValueError: If balanced_str contains invalid characters
        
    Examples:
        >>> balanced_ternary_to_decimal('1T1T')
        8
        >>> balanced_ternary_to_decimal('T11')
        -4
    """
    if not all(digit in 'T01' for digit in balanced_str):
        raise ValueError(f"Invalid balanced ternary string: {balanced_str} (must contain only T, 0, 1)")
    
    decimal_value = 0
    for digit in balanced_str:
        decimal_value = decimal_value * 3 + (-1 if digit == 'T' else int(digit))
    
    return decimal_value 