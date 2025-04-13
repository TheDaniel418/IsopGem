#!/usr/bin/env python3
"""
Purpose: View astrological aspects stored in the database.

This script provides a simple interface to view pre-calculated aspects from the database,
allowing filtering by date range and planets.
"""

import argparse
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(description="View astrological aspects stored in the database")
    
    # Date filtering
    parser.add_argument("--date", type=str, 
                       help="View aspects for a specific date (YYYY-MM-DD)")
    parser.add_argument("--start-date", type=str,
                       help="Start date for aspect range (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date for aspect range (YYYY-MM-DD)")
    parser.add_argument("--month", type=str,
                       help="View aspects for a specific month (YYYY-MM)")
    parser.add_argument("--year", type=int,
                       help="View aspects for a specific year (YYYY)")
    
    # Planet filtering
    parser.add_argument("--planet1", type=str,
                       help="Filter by first planet")
    parser.add_argument("--planet2", type=str,
                       help="Filter by second planet")
    
    # Aspect type filtering
    parser.add_argument("--aspect-type", type=str,
                       help="Filter by aspect type (e.g., 'conjunction', 'opposition')")
    parser.add_argument("--major-only", action="store_true",
                       help="Show only major aspects")
    
    # Output options
    parser.add_argument("--count", action="store_true",
                       help="Show only the count of matching aspects")
    parser.add_argument("--limit", type=int, default=100,
                       help="Limit the number of aspects displayed (default: 100)")
    parser.add_argument("--database", type=str, default=None,
                       help="Path to database file (default: ~/.isopgem/isopgem.db)")
    
    args = parser.parse_args()
    
    # Validate and process date arguments
    if args.date:
        try:
            args.date = datetime.strptime(args.date, "%Y-%m-%d")
            args.start_date = args.date
            args.end_date = args.date + timedelta(days=1)
        except ValueError:
            parser.error("Invalid date format. Use YYYY-MM-DD")
    
    elif args.month:
        try:
            month_date = datetime.strptime(args.month, "%Y-%m")
            args.start_date = month_date
            # Get last day of the month
            if month_date.month == 12:
                args.end_date = datetime(month_date.year + 1, 1, 1)
            else:
                args.end_date = datetime(month_date.year, month_date.month + 1, 1)
        except ValueError:
            parser.error("Invalid month format. Use YYYY-MM")
    
    elif args.year:
        args.start_date = datetime(args.year, 1, 1)
        args.end_date = datetime(args.year + 1, 1, 1)
    
    elif args.start_date:
        try:
            args.start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            parser.error("Invalid start date format. Use YYYY-MM-DD")
            
        if args.end_date:
            try:
                args.end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
                # Add one day to include the end date
                args.end_date += timedelta(days=1)
            except ValueError:
                parser.error("Invalid end date format. Use YYYY-MM-DD")
        else:
            # Default to 30 days if no end date is specified
            args.end_date = args.start_date + timedelta(days=30)
    
    # If no date filters provided, show aspects for the current month
    if not (args.date or args.month or args.year or args.start_date):
        now = datetime.now()
        args.start_date = datetime(now.year, now.month, 1)
        if now.month == 12:
            args.end_date = datetime(now.year + 1, 1, 1)
        else:
            args.end_date = datetime(now.year, now.month + 1, 1)
    
    return args


def get_db_path(custom_path=None):
    """Get the path to the database file.
    
    Args:
        custom_path: Optional custom path to database file
        
    Returns:
        Path to database file
    """
    if custom_path:
        return Path(custom_path)
    
    # Default path: ~/.isopgem/isopgem.db
    home_dir = Path.home()
    db_dir = home_dir / ".isopgem"
    db_path = db_dir / "isopgem.db"
    
    return db_path


def get_aspects(db_conn, start_date, end_date, planet1=None, planet2=None, 
               aspect_type=None, is_major=None, limit=None):
    """Get aspects from the database with optional filtering.
    
    Args:
        db_conn: Database connection
        start_date: Start date to filter aspects
        end_date: End date to filter aspects
        planet1: Optional first planet to filter aspects
        planet2: Optional second planet to filter aspects
        aspect_type: Optional aspect type to filter aspects
        is_major: Optional flag to filter major/minor aspects
        limit: Maximum number of aspects to return
        
    Returns:
        List of aspect records with planet names included
    """
    # Build query with dynamic parameters
    query = """
    SELECT 
        a.id, cb1.name as body1_name, cb2.name as body2_name, 
        a.aspect_type, a.is_major, a.year,
        a.applying_timestamp, a.exact_timestamp, a.separation_timestamp,
        a.exact_position1, a.exact_position2
    FROM aspects a
    JOIN celestial_bodies cb1 ON a.body1_id = cb1.id
    JOIN celestial_bodies cb2 ON a.body2_id = cb2.id
    WHERE 1=1
    """
    
    params = []
    
    # Add date filters if provided
    if start_date:
        query += " AND a.exact_timestamp >= ?"
        params.append(start_date.isoformat())
        
    if end_date:
        query += " AND a.exact_timestamp <= ?"
        params.append(end_date.isoformat())
        
    # Add planet filters if provided
    if planet1:
        query += " AND cb1.name = ?"
        params.append(planet1)
        
    if planet2:
        query += " AND cb2.name = ?"
        params.append(planet2)
        
    # Add aspect type filter if provided
    if aspect_type:
        query += " AND a.aspect_type = ?"
        params.append(aspect_type)
        
    # Add major/minor filter if provided
    if is_major is not None:
        query += " AND a.is_major = ?"
        params.append(1 if is_major else 0)
        
    # Add ordering
    query += " ORDER BY a.exact_timestamp"
    
    # Add limit if provided
    if limit:
        query += f" LIMIT {limit}"
    
    # Execute query
    cursor = db_conn.execute(query, params)
    
    # Process results
    aspects = []
    for row in cursor:
        # Convert to dict
        aspect = {
            'id': row[0],
            'body1_name': row[1],
            'body2_name': row[2],
            'aspect_type': row[3],
            'is_major': bool(row[4]),
            'year': row[5],
            'applying_timestamp': row[6],
            'exact_timestamp': row[7],
            'separation_timestamp': row[8],
            'exact_position1': row[9],
            'exact_position2': row[10]
        }
        aspects.append(aspect)
        
    return aspects


def format_aspect_summary(aspect):
    """Format an aspect as a readable summary.
    
    Args:
        aspect: Aspect dictionary from the repository
        
    Returns:
        Formatted aspect summary
    """
    # Parse datetime from ISO string
    exact_time = aspect.get('exact_timestamp')
    if isinstance(exact_time, str):
        exact_time = datetime.fromisoformat(exact_time)
    
    formatted_date = exact_time.strftime('%Y-%m-%d %H:%M')
    
    positions = ""
    if 'exact_position1' in aspect and 'exact_position2' in aspect:
        sign1 = get_zodiac_sign(aspect['exact_position1'])
        sign2 = get_zodiac_sign(aspect['exact_position2'])
        positions = f" ({sign1} {aspect['exact_position1']%30:.1f}° - {sign2} {aspect['exact_position2']%30:.1f}°)"
    
    return f"{formatted_date} | {aspect['body1_name']} {aspect['aspect_type']} {aspect['body2_name']}{positions}"


def get_zodiac_sign(position):
    """Get zodiac sign from a position in degrees.
    
    Args:
        position: Position in degrees (0-360)
        
    Returns:
        Zodiac sign name
    """
    # Normalize position to 0-360 range
    position = position % 360
    
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    # Each sign spans 30 degrees
    sign_index = int(position / 30)
    return signs[sign_index]


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    try:
        # Connect to database
        db_path = get_db_path(args.database)
        print(f"Using database: {db_path}")
        
        if not db_path.exists():
            print(f"Error: Database file not found at {db_path}")
            return 1
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Get aspects based on filters
        aspects = get_aspects(
            db_conn=conn,
            start_date=args.start_date,
            end_date=args.end_date,
            planet1=args.planet1,
            planet2=args.planet2,
            aspect_type=args.aspect_type,
            is_major=True if args.major_only else None,
            limit=args.limit
        )
        
        # Print header with query details
        date_range = f"{args.start_date.strftime('%Y-%m-%d')} to {args.end_date.strftime('%Y-%m-%d')}"
        filters = []
        if args.planet1:
            filters.append(f"Planet 1: {args.planet1}")
        if args.planet2:
            filters.append(f"Planet 2: {args.planet2}")
        if args.aspect_type:
            filters.append(f"Aspect type: {args.aspect_type}")
        if args.major_only:
            filters.append("Major aspects only")
        
        filter_str = ", ".join(filters) if filters else "No filters"
        
        print(f"Astrological Aspects for {date_range}")
        print(f"Filters: {filter_str}")
        print(f"Found {len(aspects)} aspects")
        print("-" * 80)
        
        # If only count is requested, exit
        if args.count:
            return 0
        
        # Print aspects
        for aspect in aspects:
            print(format_aspect_summary(aspect))
        
        # Close connection
        conn.close()
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 