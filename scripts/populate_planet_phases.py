#!/usr/bin/env python
"""
Purpose: Command-line utility for populating the astrological database with planet phases.

This script is used to calculate and store planetary phases for Mercury and Venus
over a specified time range. It can calculate:
- Conjunctions with the Sun (superior & inferior)
- Maximum elongations (eastern & western)
- Retrograde/direct stations

Usage:
    python scripts/populate_planet_phases.py --start-year 2023 --end-year 2025
"""

import argparse
import sys
import os
from datetime import datetime
from loguru import logger

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astrology.services.astrological_event_calculator import AstrologicalEventCalculator


def setup_logger():
    """Configure the logger for this script."""
    logger.remove()  # Remove default handlers
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/planet_phases_{time}.log", level="DEBUG", rotation="10 MB")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate and store planet phases for Mercury and Venus."
    )
    
    parser.add_argument(
        "--start-year",
        type=int,
        required=True,
        help="Start year to calculate phases for"
    )
    
    parser.add_argument(
        "--end-year",
        type=int,
        required=False,
        help="End year to calculate phases for (defaults to start-year)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    setup_logger()
    args = parse_args()
    
    start_year = args.start_year
    end_year = args.end_year if args.end_year is not None else start_year
    
    logger.info(f"Starting planet phase calculation for {start_year}-{end_year}")
    
    # Get the calculator instance
    calculator = AstrologicalEventCalculator.get_instance()
    
    # Calculate start time
    start_time = datetime.now()
    logger.info(f"Started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Populate the planet phases
        count = calculator.populate_planet_phases(start_year, end_year)
        
        # Calculate end time and duration
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"Calculated and stored {count} planet phases")
        logger.info(f"Completed in {duration.total_seconds():.1f} seconds")
        
    except Exception as e:
        logger.error(f"Error during planet phase calculation: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 