"""
Purpose: Provides utility functions for converting between decimal, standard ternary, and balanced ternary number systems

This file is part of the tq pillar and serves as a utility component.
It is responsible for handling conversions between base-10 and base-3 number systems,
including both standard and balanced ternary representations, which are fundamental
operations for TQ (Ternary Qabala) analysis.

Key components:
- decimal_to_ternary: Converts decimal integers to standard ternary strings (0,1,2)
- ternary_to_decimal: Converts standard ternary strings to decimal integers
- decimal_to_balanced_ternary: Converts decimal integers to balanced ternary strings (T,0,1)
- balanced_ternary_to_decimal: Converts balanced ternary strings to decimal integers
- balanced_to_original: Converts balanced ternary (T,0,1) to standard ternary (0,1,2)
- format_ternary: Formats ternary strings with padding and grouping options
- Type guards and aliases for type safety in ternary operations

Dependencies:
- None (uses only standard Python libraries)

Related files:
- tq/models/tq_grid.py: Uses ternary conversion for TQ grid positions
- tq/services/tq_analysis_service.py: Uses conversions for element analysis
- tq/ui/widgets/ternary_visualizer.py: Displays ternary numbers in various formats

Implementation Notes:
- Standard ternary uses digits {0,1,2}
- Balanced ternary uses digits {T,0,1} where T represents -1
- All functions include type validation and clear error handling
- Negative numbers are supported in standard ternary format
"""

from typing import List, Literal, NewType, Tuple, TypeGuard, Union, overload

# Type aliases and NewTypes for stronger type safety
TernaryDigit = Literal[0, 1, 2]
BalancedTernaryDigit = Union[Literal[-1], Literal[0], Literal[1]]
TernaryString = NewType(
    "TernaryString", str
)  # A string containing only '0', '1', '2' characters
BalancedTernaryString = NewType(
    "BalancedTernaryString", str
)  # A string containing only 'T', '0', '1' characters


def is_valid_ternary_string(s: str) -> TypeGuard[TernaryString]:
    """Type guard to validate ternary strings.

    Args:
        s: String to validate

    Returns:
        True if string contains only valid ternary digits
    """
    if not s:
        return False
    if s.startswith("-"):
        s = s[1:]
    return all(digit in "012" for digit in s)


def is_valid_balanced_ternary(s: str) -> TypeGuard[BalancedTernaryString]:
    """Type guard to validate balanced ternary strings.

    Args:
        s: String to validate

    Returns:
        True if string contains only valid balanced ternary digits
    """
    return bool(s) and all(digit in "T01" for digit in s)


@overload
def decimal_to_ternary(decimal_num: int, *, pad_length: int = 0) -> TernaryString:
    ...


@overload
def decimal_to_ternary(decimal_num: int, *, group_size: int = 0) -> TernaryString:
    ...


def decimal_to_ternary(
    decimal_num: int, *, pad_length: int = 0, group_size: int = 0
) -> TernaryString:
    """Convert a decimal number to its ternary representation.

    Args:
        decimal_num: The decimal integer to convert
        pad_length: Length to pad the result to with leading zeros
        group_size: Size of digit groups (0 for no grouping)

    Returns:
        The ternary string representation

    Raises:
        TypeError: If input is not an integer
    """
    if not isinstance(decimal_num, int):
        raise TypeError("Input must be an integer")

    if decimal_num == 0:
        result = "0"
        if pad_length > 0:
            result = result.zfill(pad_length)
        return TernaryString(result)

    is_negative = decimal_num < 0
    decimal_num = abs(decimal_num)

    digits = []
    while decimal_num:
        digits.append(str(decimal_num % 3))
        decimal_num //= 3

    result = "".join(reversed(digits))
    if pad_length > 0:
        result = result.zfill(pad_length)
    if group_size > 0:
        groups = []
        for i in range(0, len(result), group_size):
            groups.append(result[i : i + group_size])
        result = " ".join(groups)

    final = f"-{result}" if is_negative else result
    return TernaryString(final)


@overload
def ternary_to_decimal(ternary_str: TernaryString) -> int:
    ...


@overload
def ternary_to_decimal(ternary_str: str) -> int:
    ...


def ternary_to_decimal(ternary_str: Union[TernaryString, str]) -> int:
    """Convert a ternary string to its decimal representation.

    Args:
        ternary_str: The ternary string to convert

    Returns:
        The decimal integer value

    Raises:
        ValueError: If input contains invalid ternary digits
        TypeError: If input is not a string
    """
    if not isinstance(ternary_str, str):
        raise TypeError("Input must be a string")

    if not is_valid_ternary_string(ternary_str):
        raise ValueError("Input must contain only valid ternary digits (0,1,2)")

    is_negative = ternary_str.startswith("-")
    if is_negative:
        ternary_str = ternary_str[1:]

    decimal = 0
    for digit in ternary_str:
        decimal = decimal * 3 + int(digit)

    return -decimal if is_negative else decimal


@overload
def format_ternary(ternary_str: TernaryString, *, pad_length: int = 0) -> TernaryString:
    ...


@overload
def format_ternary(
    ternary_str: TernaryString, *, group_size: int = 0, group_separator: str = " "
) -> TernaryString:
    ...


@overload
def format_ternary(
    ternary_str: TernaryString,
    *,
    pad_length: int = 0,
    group_size: int = 0,
    group_separator: str = " ",
) -> TernaryString:
    ...


def format_ternary(
    ternary_str: TernaryString,
    pad_length: int = 0,
    group_size: int = 0,
    group_separator: str = " ",
) -> TernaryString:
    """Format a ternary string with optional padding and grouping.

    Args:
        ternary_str: The ternary string to format
        pad_length: Length to pad the string to (with leading zeros)
        group_size: Size of each group for separation (0 means no grouping)
        group_separator: Character to use between groups

    Returns:
        The formatted ternary string

    Examples:
        >>> format_ternary(TernaryString('111'), pad_length=6)
        '000111'
        >>> format_ternary(TernaryString('111222'), group_size=3)
        '111 222'
        >>> format_ternary(TernaryString('12'), pad_length=6, group_size=3)
        '000 012'
    """
    # Handle negative sign if present
    is_negative = False
    if ternary_str.startswith("-"):
        is_negative = True
        ternary_str = ternary_str[1:]

    # Apply padding
    if pad_length > 0:
        ternary_str = ternary_str.zfill(pad_length)

    # Apply grouping
    if group_size > 0:
        # Calculate groups from right to left
        groups: List[str] = []
        for i in range(len(ternary_str), 0, -group_size):
            start = max(0, i - group_size)
            groups.insert(0, ternary_str[start:i])
        ternary_str = group_separator.join(groups)

    # Restore negative sign if needed
    result_str = "-" + ternary_str if is_negative else ternary_str
    # Cast to TernaryString for type safety
    from typing import cast

    return cast(TernaryString, TernaryString(result_str))


@overload
def split_ternary_digits(ternary_str: TernaryString) -> List[TernaryDigit]:
    ...


@overload
def split_ternary_digits(ternary_str: str) -> List[TernaryDigit]:
    ...


def split_ternary_digits(ternary_str: Union[TernaryString, str]) -> List[TernaryDigit]:
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
    if ternary_str.startswith("-"):
        is_negative = True
        ternary_str = ternary_str[1:]

    # Validate input
    if not all(digit in "012" for digit in ternary_str):
        raise ValueError(
            f"Invalid ternary string: {ternary_str} (must contain only digits 0, 1, 2)"
        )

    # Convert to list of integers and cast to TernaryDigit
    from typing import cast

    digits = [cast(TernaryDigit, int(digit)) for digit in ternary_str]

    # Apply negative sign to first digit if needed (for display purposes)
    if is_negative and digits:
        # This is just for display, the actual value will be handled elsewhere
        # We'll cast back to TernaryDigit after operations
        digits[0] = cast(TernaryDigit, -digits[0])

    return digits


def get_ternary_digit_positions(
    decimal_num: int, min_length: int = 1
) -> List[Tuple[int, TernaryDigit]]:
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
    positions: List[Tuple[int, TernaryDigit]] = []
    for i, digit in enumerate(reversed(digits)):
        positions.append((i, digit))

    # Pad with zeros if needed
    while len(positions) < min_length:
        positions.append((len(positions), 0))

    return list(reversed(positions))


@overload
def decimal_to_balanced_ternary(decimal_num: int) -> BalancedTernaryString:
    ...


@overload
def decimal_to_balanced_ternary(
    decimal_num: int, *, pad_length: int = 0
) -> BalancedTernaryString:
    ...


def decimal_to_balanced_ternary(
    decimal_num: int, *, pad_length: int = 0
) -> BalancedTernaryString:
    """Convert a decimal number to balanced ternary representation.

    Args:
        decimal_num: The decimal integer to convert
        pad_length: Length to pad the result to with leading zeros

    Returns:
        The balanced ternary string representation using T (-1), 0, and 1

    Raises:
        TypeError: If input is not an integer
    """
    if not isinstance(decimal_num, int):
        raise TypeError("Input must be an integer")

    if decimal_num == 0:
        result = "0"
        if pad_length > 0:
            result = result.zfill(pad_length)
        return BalancedTernaryString(result)

    digits = []
    while decimal_num:
        remainder = decimal_num % 3
        if remainder == 2:
            remainder = -1
            decimal_num += 3
        digits.append("T" if remainder == -1 else str(remainder))
        decimal_num //= 3

    result = "".join(reversed(digits))

    # Apply padding if needed
    if pad_length > 0 and len(result) < pad_length:
        result = "0" * (pad_length - len(result)) + result

    return BalancedTernaryString(result)


@overload
def balanced_to_original(balanced_str: BalancedTernaryString) -> TernaryString:
    ...


@overload
def balanced_to_original(balanced_str: str) -> TernaryString:
    ...


def balanced_to_original(
    balanced_str: Union[BalancedTernaryString, str]
) -> TernaryString:
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
        >>> balanced_to_original(BalancedTernaryString('1T1T'))
        '1212'  # Each T becomes 2
        >>> balanced_to_original(BalancedTernaryString('T11'))
        '211'   # Leading T becomes 2
    """
    if not is_valid_balanced_ternary(balanced_str):
        raise ValueError(
            f"Invalid balanced ternary string: {balanced_str} (must contain only T, 0, 1)"
        )

    # Convert T to 2, leave 0 and 1 unchanged
    return TernaryString(balanced_str.replace("T", "2"))


@overload
def balanced_ternary_to_decimal(balanced_str: BalancedTernaryString) -> int:
    ...


@overload
def balanced_ternary_to_decimal(balanced_str: str) -> int:
    ...


def balanced_ternary_to_decimal(balanced_str: Union[BalancedTernaryString, str]) -> int:
    """Convert a balanced ternary string to its decimal representation.

    Args:
        balanced_str: The balanced ternary string to convert

    Returns:
        The decimal integer value

    Raises:
        ValueError: If input contains invalid balanced ternary digits
        TypeError: If input is not a string
    """
    if not isinstance(balanced_str, str):
        raise TypeError("Input must be a string")

    if not is_valid_balanced_ternary(balanced_str):
        raise ValueError(
            "Input must contain only valid balanced ternary digits (T,0,1)"
        )

    decimal = 0
    for digit in balanced_str:
        value = -1 if digit == "T" else int(digit)
        decimal = decimal * 3 + value

    return decimal
