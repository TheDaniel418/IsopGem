#!/usr/bin/env python3
"""
Purpose: Populates the astrological events database with pre-calculated aspects.

This script calculates and stores planetary aspects for a specified time range,
allowing for efficient retrieval of aspect data without redundant calculations.
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from astrology.repositories.astrological_events_repository import (
    AstrologicalEventsRepository,
)
from astrology.services.astrology_calculation_service import AstrologyCalculationService
from shared.repositories.database import Database


def setup_logger():
    """Set up the logger with appropriate configuration."""
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/populate_aspects_{time}.log", level="DEBUG", rotation="100 MB")


def parse_arguments():
    """Parse command line arguments.

    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description="Populate the astrological events database with aspects"
    )

    parser.add_argument(
        "--start-year", type=int, required=True, help="Starting year for calculations"
    )
    parser.add_argument(
        "--end-year", type=int, required=True, help="Ending year for calculations"
    )
    parser.add_argument(
        "--include-minor",
        action="store_true",
        default=False,
        help="Include minor aspects (default: False, major aspects only)",
    )
    parser.add_argument(
        "--orb",
        type=float,
        default=1.0,
        help="Maximum orb to consider for aspects in degrees (default: 1.0)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.start_year > args.end_year:
        parser.error("start-year must be less than or equal to end-year")

    if args.orb <= 0 or args.orb > 10:
        parser.error("orb must be greater than 0 and less than or equal to 10 degrees")

    return args


def main():
    """Main entry point for the script."""
    # Set up logger
    setup_logger()

    # Parse arguments
    args = parse_arguments()

    # Adjust log level if verbose
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    logger.info(
        f"Starting aspect database population for years {args.start_year}-{args.end_year}"
    )
    logger.info(
        f"Including {'major and minor' if args.include_minor else 'only major'} aspects with orb {args.orb}°"
    )

    # Confirm with the user
    total_years = args.end_year - args.start_year + 1
    total_days = total_years * 365.25  # Approximate days
    print(
        f"This will calculate aspects for {total_years} years ({int(total_days)} days)."
    )
    print("This operation may take a long time depending on the range.")

    if input("Do you want to continue? (y/n): ").lower() != "y":
        print("Operation cancelled.")
        return

    start_time = time.time()

    try:
        # Set up database and repositories
        db = Database.get_instance()

        # Ensure database schema is initialized
        print("Initializing database schema...")
        repository = AstrologicalEventsRepository(db)

        # Check if celestial_bodies table exists
        result = db.query_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='celestial_bodies'"
        )
        if not result:
            print("Database tables not properly initialized. Initializing now...")
            repository._initialize_tables()
            repository._create_indexes()

            # Add basic planet records
            print("Adding basic planetary bodies records...")
            try:
                with db.transaction() as conn:
                    planets = [
                        ("Sun", "luminary"),
                        ("Moon", "luminary"),
                        ("Mercury", "planet"),
                        ("Venus", "planet"),
                        ("Mars", "planet"),
                        ("Jupiter", "planet"),
                        ("Saturn", "planet"),
                        ("Uranus", "planet"),
                        ("Neptune", "planet"),
                        ("Pluto", "planet"),
                        ("North Node", "point"),
                    ]

                    for i, (name, type_) in enumerate(planets):
                        conn.execute(
                            "INSERT OR IGNORE INTO celestial_bodies (name, type) VALUES (?, ?)",
                            (name, type_),
                        )
                print("Database initialization completed.")
            except Exception as e:
                print(f"Warning: Error initializing database records: {e}")

        # Set up calculation service
        service = AstrologyCalculationService.get_instance()
        service.set_repository(repository)

        # Run calculation and storage process
        print(
            f"Starting aspect calculation for years {args.start_year}-{args.end_year}..."
        )
        stats = service.calculate_and_store_aspects(
            start_year=args.start_year,
            end_year=args.end_year,
            include_major=True,
            include_minor=args.include_minor,
            orb=args.orb,
        )

        # Print summary
        print("\nCalculation completed!")
        print(f"Total processing time: {stats['duration']:.1f} seconds")
        print(f"Years processed: {stats['years_processed']}")
        print(f"Days processed: {stats['days_processed']}")
        print(f"Aspects found: {stats['aspects_found']}")
        print(f"Aspects stored in database: {stats['aspects_stored']}")

        # Get database stats
        calc_status = repository.get_calculation_status()
        print("\nDatabase Status:")
        print(f"Total events in database: {calc_status['total_events']}")
        print(f"Aspects in database: {calc_status['event_counts']['aspects']}")

        years_covered = []
        for calc_range in calc_status["calculated_ranges"]:
            years_covered.append(f"{calc_range['start_year']}-{calc_range['end_year']}")

        print(f"Years covered: {', '.join(years_covered)}")

    except Exception as e:
        logger.error(f"Error during aspect calculation: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1

    logger.info("Aspect database population completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
