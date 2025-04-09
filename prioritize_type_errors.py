#!/usr/bin/env python3
"""
Prioritizes type errors from mypy output.

This script reads mypy error output from a file, categorizes errors by type
and severity, and outputs a prioritized list of errors to fix.
"""

import argparse
import os
import re
import sys
import tempfile
import subprocess
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set

# Error categories in order of priority (highest first)
ERROR_PRIORITIES = [
    "assignment",           # Type incompatibility in assignments
    "arg-type",             # Argument type incompatibility
    "attr-defined",         # Attribute errors
    "return-value",         # Return type incompatibility
    "no-any-return",        # Returning Any from a typed function
    "valid-type",           # Type validation errors
    "unreachable",          # Unreachable code
    "no-redef",             # Name redefinition
    "var-annotated",        # Missing variable annotations
    "no-untyped-def",       # Missing function annotations
    "import-untyped",       # Untyped imports
    # Add more categories as needed
]

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Prioritize mypy errors")
    parser.add_argument("input_file", nargs='?', help="Input file with mypy error output (optional)")
    parser.add_argument("--mypy-args", help="Arguments to pass to mypy, e.g. 'shared/utils/app.py'")
    parser.add_argument("--output", "-o", help="Output file for prioritized errors")
    parser.add_argument("--summary", "-s", action="store_true", 
                        help="Output only a summary of error types")
    return parser.parse_args()

def run_mypy(mypy_args: Optional[str] = None) -> str:
    """Run mypy and return the output filename."""
    # Create a temporary file for mypy output
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    temp_file.close()
    
    # Determine mypy command
    if mypy_args:
        cmd = f"python -m mypy {mypy_args}"
    else:
        cmd = "python -m mypy ."  # Run on entire project by default
    
    print(f"Running: {cmd}")
    try:
        # Run mypy and capture output
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        with open(temp_file.name, 'w') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
        
        print(f"MyPy completed with exit code {result.returncode}")
        return temp_file.name
    except Exception as e:
        print(f"Error running mypy: {e}")
        os.unlink(temp_file.name)
        sys.exit(1)

def read_error_file(filename: str) -> List[str]:
    """Read the error file and return a list of error lines."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if "error:" in line]

def categorize_errors(errors: List[str]) -> Dict[str, List[str]]:
    """Categorize errors by error type."""
    categorized: Dict[str, List[str]] = defaultdict(list)
    
    for error in errors:
        # Extract error code using regex
        match = re.search(r'\[([^\]]+)\]', error)
        if match:
            error_code = match.group(1)
            categorized[error_code].append(error)
        else:
            categorized["uncategorized"].append(error)
            
    return categorized

def get_files_with_errors(errors: List[str]) -> Dict[str, int]:
    """Count errors per file."""
    file_counts: Dict[str, int] = Counter()
    
    for error in errors:
        # Extract filename using regex
        match = re.search(r'^([^:]+):', error)
        if match:
            filename = match.group(1)
            file_counts[filename] += 1
            
    return file_counts

def output_errors(
    categorized_errors: Dict[str, List[str]], 
    file_counts: Dict[str, int],
    summary_only: bool,
    output_file: Optional[str] = None
) -> None:
    """Output prioritized errors to stdout or a file."""
    lines = []
    
    # Generate a summary of error types
    lines.append("=== Error Type Summary ===")
    for error_type in ERROR_PRIORITIES:
        if error_type in categorized_errors:
            lines.append(f"{error_type}: {len(categorized_errors[error_type])} errors")
    
    # Add any error types not in the priority list
    for error_type, errors in categorized_errors.items():
        if error_type not in ERROR_PRIORITIES:
            lines.append(f"{error_type}: {len(errors)} errors")
    
    lines.append("")
    lines.append("=== Files with Most Errors ===")
    for filename, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        lines.append(f"{filename}: {count} errors")
    
    if not summary_only:
        # Output errors by priority
        lines.append("")
        lines.append("=== Errors by Priority ===")
        for error_type in ERROR_PRIORITIES:
            if error_type in categorized_errors and categorized_errors[error_type]:
                lines.append(f"\n--- {error_type} ({len(categorized_errors[error_type])} errors) ---")
                lines.extend(categorized_errors[error_type][:20])  # Show first 20 of each type
                if len(categorized_errors[error_type]) > 20:
                    lines.append(f"... and {len(categorized_errors[error_type]) - 20} more errors of this type")
        
        # Output any uncategorized errors
        for error_type, errors in categorized_errors.items():
            if error_type not in ERROR_PRIORITIES and errors:
                lines.append(f"\n--- {error_type} ({len(errors)} errors) ---")
                lines.extend(errors[:20])
                if len(errors) > 20:
                    lines.append(f"... and {len(errors) - 20} more errors of this type")
    
    # Output to file or stdout
    output = "\n".join(lines)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Prioritized errors saved to {output_file}")
    else:
        print(output)

def main() -> int:
    """Main function."""
    args = parse_args()
    
    # Default output file name if not specified
    default_output = "type_errors_prioritized.txt"
    
    # If no input file specified, run mypy
    if not args.input_file:
        input_file = run_mypy(args.mypy_args)
        temp_file_created = True
    else:
        input_file = args.input_file
        temp_file_created = False
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.", file=sys.stderr)
            return 1
    
    try:
        # Read and categorize errors
        errors = read_error_file(input_file)
        categorized_errors = categorize_errors(errors)
        file_counts = get_files_with_errors(errors)
        
        # Output results
        output_errors(categorized_errors, file_counts, args.summary, args.output or default_output)
        
        print(f"\nTotal errors: {len(errors)}")
        print(f"Report saved to: {args.output or default_output}")
        
        # Clean up temp file if we created one
        if temp_file_created:
            os.unlink(input_file)
            
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 