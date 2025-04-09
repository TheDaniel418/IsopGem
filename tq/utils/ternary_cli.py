"""
Purpose: Command-line interface for ternary number conversions

This file is part of the tq pillar and serves as a utility component.
It provides a simple CLI for converting between decimal and ternary numbers,
formatting ternary strings, and exploring ternary digit patterns.

Key components:
- main: Entry point function that parses arguments and runs the appropriate conversion
- display_ternary_info: Displays detailed information about a ternary number

Dependencies:
- tq.utils.ternary_converter: For core ternary conversion functions
- argparse: For command-line argument parsing

Related files:
- tq/utils/ternary_converter.py: Core conversion functionality
"""

import argparse
import sys
from typing import List, Optional

from tq.utils.ternary_converter import (
    decimal_to_ternary,
    ternary_to_decimal,
    format_ternary,
    split_ternary_digits,
    get_ternary_digit_positions
)


def display_ternary_info(ternary_str: str) -> None:
    """Display detailed information about a ternary number.
    
    Args:
        ternary_str: The ternary string to analyze
    """
    decimal_value = ternary_to_decimal(ternary_str)
    ternary_digits = split_ternary_digits(ternary_str)
    digit_positions = get_ternary_digit_positions(decimal_value)
    
    print(f"Ternary number: {ternary_str}")
    print(f"Decimal value: {decimal_value}")
    print(f"Formatted (grouped): {format_ternary(ternary_str, group_size=3)}")
    
    print("\nDigit breakdown:")
    for i, digit in enumerate(ternary_digits):
        position = len(ternary_digits) - i - 1
        power_value = 3 ** position
        contribution = digit * power_value
        print(f"  Position {position} (3^{position} = {power_value}): "
              f"{digit} × {power_value} = {contribution}")
    
    print(f"\nTotal: {decimal_value}")


def display_decimal_info(decimal_num: int) -> None:
    """Display detailed information about a decimal number in ternary.
    
    Args:
        decimal_num: The decimal number to analyze
    """
    ternary_str = decimal_to_ternary(decimal_num)
    digit_positions = get_ternary_digit_positions(decimal_num)
    
    print(f"Decimal number: {decimal_num}")
    print(f"Ternary representation: {ternary_str}")
    print(f"Formatted (grouped): {format_ternary(ternary_str, group_size=3)}")
    
    print("\nTernary digit breakdown:")
    total = 0
    for position, digit in digit_positions:
        power_value = 3 ** position
        contribution = digit * power_value
        total += contribution
        print(f"  Position {position} (3^{position} = {power_value}): "
              f"{digit} × {power_value} = {contribution}")
    
    print(f"\nTotal: {total}")


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:] if None)
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Convert between decimal and ternary number systems."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Decimal to ternary conversion
    d2t_parser = subparsers.add_parser("d2t", help="Convert decimal to ternary")
    d2t_parser.add_argument("number", type=int, help="Decimal number to convert")
    d2t_parser.add_argument("--pad", type=int, default=0,
                           help="Pad output to specified length")
    d2t_parser.add_argument("--group", type=int, default=0,
                           help="Group digits by specified size")
    d2t_parser.add_argument("--info", action="store_true",
                           help="Display detailed information")
    
    # Ternary to decimal conversion
    t2d_parser = subparsers.add_parser("t2d", help="Convert ternary to decimal")
    t2d_parser.add_argument("number", type=str, help="Ternary number to convert")
    t2d_parser.add_argument("--info", action="store_true",
                           help="Display detailed information")
    
    # Format ternary number
    fmt_parser = subparsers.add_parser("format", help="Format ternary number")
    fmt_parser.add_argument("number", type=str, help="Ternary number to format")
    fmt_parser.add_argument("--pad", type=int, default=0,
                           help="Pad to specified length")
    fmt_parser.add_argument("--group", type=int, default=3,
                           help="Group digits by specified size")
    fmt_parser.add_argument("--separator", type=str, default=" ",
                           help="Separator between groups")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the ternary converter CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:] if None)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)
    
    if not parsed_args.command:
        print("Error: No command specified. Use --help for usage information.")
        return 1
    
    try:
        if parsed_args.command == "d2t":
            if parsed_args.info:
                display_decimal_info(parsed_args.number)
            else:
                result = decimal_to_ternary(parsed_args.number)
                if parsed_args.pad > 0 or parsed_args.group > 0:
                    result = format_ternary(
                        result, 
                        pad_length=parsed_args.pad,
                        group_size=parsed_args.group
                    )
                print(result)
                
        elif parsed_args.command == "t2d":
            if parsed_args.info:
                display_ternary_info(parsed_args.number)
            else:
                result = ternary_to_decimal(parsed_args.number)
                print(result)
                
        elif parsed_args.command == "format":
            result = format_ternary(
                parsed_args.number,
                pad_length=parsed_args.pad,
                group_size=parsed_args.group,
                group_separator=parsed_args.separator
            )
            print(result)
            
    except ValueError as e:
        print(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main()) 