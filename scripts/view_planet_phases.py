#!/usr/bin/env python
"""
Purpose: Command-line utility for viewing planet phases from the astrological database.

This script allows viewing stored planetary phases for Mercury and Venus,
with filtering options by date, planet, and phase type.

Usage:
    python scripts/view_planet_phases.py --month 2023-06
    python scripts/view_planet_phases.py --year 2023 --planet Mercury
"""

import argparse
import sys
import os
from datetime import datetime
from loguru import logger
from typing import List, Dict, Any, Optional
import sqlite3
from tabulate import tabulate

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.repositories.database import Database
from astrology.services.astrological_event_calculator import PlanetPhaseType


def setup_logger():
    """Configure the logger for this script."""
    logger.remove()  # Remove default handlers
    logger.add(sys.stderr, level="INFO")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="View planet phases from the database."
    )
    
    # Date filtering arguments
    date_group = parser.add_argument_group("Date filtering")
    date_group.add_argument(
        "--date",
        type=str,
        help="Specific date to view (YYYY-MM-DD)"
    )
    
    date_group.add_argument(
        "--month",
        type=str,
        help="Month to view (YYYY-MM)"
    )
    
    date_group.add_argument(
        "--year",
        type=int,
        help="Year to view"
    )
    
    # Content filtering arguments
    filter_group = parser.add_argument_group("Content filtering")
    filter_group.add_argument(
        "--planet",
        type=str,
        choices=["Mercury", "Venus"],
        help="Filter by planet"
    )
    
    filter_group.add_argument(
        "--phase-type",
        type=str,
        choices=[p.value for p in PlanetPhaseType],
        help="Filter by phase type"
    )
    
    # Display options
    display_group = parser.add_argument_group("Display options")
    display_group.add_argument(
        "--format",
        type=str,
        choices=["table", "csv", "json"],
        default="table",
        help="Output format"
    )
    
    return parser.parse_args()


def get_planet_phases(args) -> List[Dict[str, Any]]:
    """Get planet phases from the database based on filter criteria."""
    db = Database.get_instance()
    
    # Build SQL query based on filters
    sql = """
    SELECT 
        p.id, 
        p.timestamp, 
        b.name as body_name, 
        p.phase_type, 
        p.elongation_degree, 
        p.zodiac_sign, 
        p.position_degree
    FROM planet_phases p
    JOIN celestial_bodies b ON p.body_id = b.id
    WHERE 1=1
    """
    
    params = []
    
    # Date filtering
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
            sql += " AND date(p.timestamp) = ?"
            params.append(date.strftime("%Y-%m-%d"))
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")
            return []
    
    elif args.month:
        try:
            month_date = datetime.strptime(args.month, "%Y-%m")
            year, month = month_date.year, month_date.month
            sql += " AND strftime('%Y', p.timestamp) = ? AND strftime('%m', p.timestamp) = ?"
            params.extend([str(year), f"{month:02d}"])
        except ValueError:
            logger.error(f"Invalid month format: {args.month}. Use YYYY-MM.")
            return []
    
    elif args.year:
        sql += " AND strftime('%Y', p.timestamp) = ?"
        params.append(str(args.year))
    
    # Planet filtering
    if args.planet:
        sql += " AND b.name = ?"
        params.append(args.planet)
    
    # Phase type filtering
    if args.phase_type:
        sql += " AND p.phase_type = ?"
        params.append(args.phase_type)
    
    # Order by timestamp
    sql += " ORDER BY p.timestamp"
    
    try:
        with db.connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'body_name': row['body_name'],
                    'phase_type': row['phase_type'],
                    'elongation_degree': row['elongation_degree'],
                    'zodiac_sign': row['zodiac_sign'],
                    'position_degree': row['position_degree']
                })
            
            return results
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        return []


def format_output(phases: List[Dict[str, Any]], format_type: str) -> str:
    """Format the output according to the specified format."""
    if not phases:
        return "No planet phases found matching the criteria."
    
    if format_type == "table":
        # Format data for tabulate
        headers = ["Date", "Planet", "Phase Type", "Position", "Elongation"]
        table_data = []
        
        for phase in phases:
            # Format date
            timestamp = phase['timestamp']
            if isinstance(timestamp, str):
                try:
                    date_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
                except ValueError:
                    date_str = timestamp
            else:
                date_str = timestamp.strftime("%Y-%m-%d")
            
            # Format position
            position = f"{phase['position_degree']:.1f}° {phase['zodiac_sign']}" if phase['position_degree'] else ""
            
            # Format elongation
            elongation = f"{phase['elongation_degree']:.1f}°" if phase['elongation_degree'] else ""
            
            # Format phase type for display
            phase_type = phase['phase_type'].replace('_', ' ').title()
            
            table_data.append([
                date_str,
                phase['body_name'],
                phase_type,
                position,
                elongation
            ])
        
        return tabulate(table_data, headers=headers, tablefmt="grid")
    
    elif format_type == "csv":
        # Simple CSV output
        lines = ["Date,Planet,Phase Type,Position,Elongation"]
        
        for phase in phases:
            # Format date
            timestamp = phase['timestamp']
            if isinstance(timestamp, str):
                try:
                    date_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
                except ValueError:
                    date_str = timestamp
            else:
                date_str = timestamp.strftime("%Y-%m-%d")
            
            # Format position
            position = f"{phase['position_degree']:.1f}° {phase['zodiac_sign']}" if phase['position_degree'] else ""
            
            # Format elongation
            elongation = f"{phase['elongation_degree']:.1f}°" if phase['elongation_degree'] else ""
            
            # Format phase type for display
            phase_type = phase['phase_type'].replace('_', ' ').title()
            
            lines.append(f"{date_str},{phase['body_name']},{phase_type},{position},{elongation}")
        
        return "\n".join(lines)
    
    elif format_type == "json":
        import json
        # Convert datetime objects to strings for JSON serialization
        for phase in phases:
            if isinstance(phase['timestamp'], datetime):
                phase['timestamp'] = phase['timestamp'].isoformat()
        
        return json.dumps(phases, indent=2)
    
    return "Unsupported output format."


def main():
    """Main entry point for the script."""
    setup_logger()
    args = parse_args()
    
    # Get phases from database
    phases = get_planet_phases(args)
    
    # Format and print output
    output = format_output(phases, args.format)
    print(output)
    
    logger.info(f"Found {len(phases)} planet phase events")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 