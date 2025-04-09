#!/usr/bin/env python3
"""
Runs mypy type checking on core files only (excluding UI components).

This script identifies Python files that are not in UI-related directories
and runs mypy only on those files, reducing the noise from UI-related type errors.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Directories to exclude from type checking
EXCLUDED_DIRS = [
    "venv",
    "ui",
    "widgets",
    "panels",
    "dialogs",
    "tabs",
    "tests",
    "__pycache__",
]

# File patterns to exclude
EXCLUDED_PATTERNS = [
    "test_",
]


def should_check_file(file_path: str) -> bool:
    """Determine if a file should be type-checked."""
    # Skip files in excluded directories
    parts = Path(file_path).parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            return False

    # Skip files with excluded patterns
    filename = os.path.basename(file_path)
    for pattern in EXCLUDED_PATTERNS:
        if pattern in filename:
            return False

    # Only check Python files
    return file_path.endswith(".py")


def find_core_files() -> List[str]:
    """Find all core Python files to check."""
    core_files: List[str] = []

    for root, _, files in os.walk("."):
        for file in files:
            file_path = os.path.join(root, file)
            if should_check_file(file_path):
                core_files.append(file_path)

    return core_files


def run_mypy(files: List[str], output_file: Optional[str] = None) -> Tuple[int, str]:
    """Run mypy on the specified files.

    Args:
        files: List of files to check
        output_file: Optional path to save results to

    Returns:
        Tuple of (exit_code, output)
    """
    cmd = ["python", "-m", "mypy"] + files

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    output = result.stdout

    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(output)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)

    return result.returncode, output


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run mypy on core files only")
    parser.add_argument("--output", "-o", help="Save output to file instead of console")
    return parser.parse_args()


def main() -> int:
    """Run mypy on core files."""
    args = parse_args()
    core_files = find_core_files()

    if not core_files:
        print("No core files found to check!")
        return 0

    print(f"Found {len(core_files)} core files to check.")

    try:
        exit_code, output = run_mypy(core_files, args.output)

        if not args.output:
            print(output)

        error_count = output.count("error:")
        print(f"\nMyPy completed with exit code: {exit_code}")
        print(f"Total errors found: {error_count}")

        return exit_code
    except Exception as e:
        print(f"Error running mypy: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
