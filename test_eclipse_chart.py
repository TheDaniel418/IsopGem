#!/usr/bin/env python3
"""
Test script to diagnose Kerykeion's calculation of solar eclipse positions.

This script creates multiple charts for the August 2, 2027 solar eclipse at Luxor, Egypt
using different timezone handling approaches to identify the cause of discrepancies
with online chart services.
"""

from datetime import datetime, timezone
import pytz
from kerykeion import AstrologicalSubject
from loguru import logger

# Eclipse data for August 2, 2027 at Luxor
eclipse_year = 2027
eclipse_month = 8
eclipse_day = 2
eclipse_hour = 10  # Example time from CSV file (could be different)
eclipse_minute = 4
eclipse_latitude = 25.6872  # Luxor, Egypt latitude
eclipse_longitude = 32.6396  # Luxor, Egypt longitude

print(f"\n=== SOLAR ECLIPSE TEST - {eclipse_month}/{eclipse_day}/{eclipse_year} ===")
print(f"Creating charts for Luxor, Egypt: Lat {eclipse_latitude}, Lng {eclipse_longitude}")

# Method 1: Create chart with explicit UTC timezone and let Kerykeion handle it
print("\n=== METHOD 1: UTC TIMEZONE ===")
try:
    # Create chart with UTC timezone explicitly
    utc_chart = AstrologicalSubject(
        name="Solar Eclipse UTC",
        year=eclipse_year,
        month=eclipse_month,
        day=eclipse_day,
        hour=eclipse_hour,
        minute=eclipse_minute,
        city="Luxor",
        nation="EG",
        lat=eclipse_latitude,
        lng=eclipse_longitude,
        tz_str="UTC",  # Explicitly pass UTC timezone
        online=False,
    )
    
    print(f"UTC Birth Time: {utc_chart.year}-{utc_chart.month:02d}-{utc_chart.day:02d} {utc_chart.hour:02d}:{utc_chart.minute:02d}")
    print(f"Julian Day: {utc_chart.julian_day}")
    print(f"Sun Position: {utc_chart.sun.sign} {utc_chart.sun.position}° (Absolute: {utc_chart.sun.abs_pos}°)")
    print(f"Moon Position: {utc_chart.moon.sign} {utc_chart.moon.position}° (Absolute: {utc_chart.moon.abs_pos}°)")
except Exception as e:
    print(f"Error with UTC chart: {e}")

# Method 2: Create chart with Cairo timezone
print("\n=== METHOD 2: LOCAL TIMEZONE (Africa/Cairo) ===")
try:
    # Create chart with Cairo timezone
    cairo_chart = AstrologicalSubject(
        name="Solar Eclipse Cairo",
        year=eclipse_year,
        month=eclipse_month,
        day=eclipse_day,
        hour=eclipse_hour,
        minute=eclipse_minute,
        city="Luxor",
        nation="EG",
        lat=eclipse_latitude,
        lng=eclipse_longitude,
        tz_str="Africa/Cairo",  # Use Cairo timezone
        online=False,
    )
    
    print(f"Cairo Birth Time: {cairo_chart.year}-{cairo_chart.month:02d}-{cairo_chart.day:02d} {cairo_chart.hour:02d}:{cairo_chart.minute:02d}")
    print(f"Julian Day: {cairo_chart.julian_day}")
    print(f"Sun Position: {cairo_chart.sun.sign} {cairo_chart.sun.position}° (Absolute: {cairo_chart.sun.abs_pos}°)")
    print(f"Moon Position: {cairo_chart.moon.sign} {cairo_chart.moon.position}° (Absolute: {cairo_chart.moon.abs_pos}°)")
except Exception as e:
    print(f"Error with Cairo chart: {e}")

# Method 3: Use ISO UTC method (explicit approach)
print("\n=== METHOD 3: FROM ISO UTC TIME ===")
try:
    # Create an ISO format UTC string
    iso_utc_str = f"{eclipse_year}-{eclipse_month:02d}-{eclipse_day:02d}T{eclipse_hour:02d}:{eclipse_minute:02d}:00Z"
    
    # Create chart using Kerykeion's from_iso_utc_time method
    iso_chart = AstrologicalSubject.get_from_iso_utc_time(
        name="Solar Eclipse ISO",
        iso_utc_time=iso_utc_str,
        city="Luxor",
        nation="EG",
        lat=eclipse_latitude,
        lng=eclipse_longitude,
        tz_str="UTC",  # Should be ignored since time is already UTC
        online=False,
    )
    
    print(f"ISO UTC Time: {iso_utc_str}")
    print(f"Julian Day: {iso_chart.julian_day}")
    print(f"Sun Position: {iso_chart.sun.sign} {iso_chart.sun.position}° (Absolute: {iso_chart.sun.abs_pos}°)")
    print(f"Moon Position: {iso_chart.moon.sign} {iso_chart.moon.position}° (Absolute: {iso_chart.moon.abs_pos}°)")
except Exception as e:
    print(f"Error with ISO chart: {e}")

# Method 4: Create chart with UTC, but correct for the 3-hour time difference in Cairo
print("\n=== METHOD 4: TIME OFFSET FOR CAIRO (+3 hours from UTC) ===")
try:
    # Calculate the actual local time in Cairo (UTC+3) when the eclipse happens at UTC time
    cairo_hour = (eclipse_hour + 3) % 24
    
    cairo_offset_chart = AstrologicalSubject(
        name="Solar Eclipse Cairo Offset",
        year=eclipse_year,
        month=eclipse_month,
        day=eclipse_day + (1 if cairo_hour < eclipse_hour else 0),  # Adjust day if needed
        hour=cairo_hour,
        minute=eclipse_minute,
        city="Luxor",
        nation="EG",
        lat=eclipse_latitude,
        lng=eclipse_longitude,
        tz_str="Africa/Cairo",  # Use Cairo timezone
        online=False,
    )
    
    print(f"Cairo Offset Time: {cairo_offset_chart.year}-{cairo_offset_chart.month:02d}-{cairo_offset_chart.day:02d} {cairo_offset_chart.hour:02d}:{cairo_offset_chart.minute:02d}")
    print(f"Julian Day: {cairo_offset_chart.julian_day}")
    print(f"Sun Position: {cairo_offset_chart.sun.sign} {cairo_offset_chart.sun.position}° (Absolute: {cairo_offset_chart.sun.abs_pos}°)")
    print(f"Moon Position: {cairo_offset_chart.moon.sign} {cairo_offset_chart.moon.position}° (Absolute: {cairo_offset_chart.moon.abs_pos}°)")
except Exception as e:
    print(f"Error with Cairo offset chart: {e}")

# Method 5: Debug internal timezone conversions
print("\n=== METHOD 5: DEBUG TIMEZONE CONVERSION ===")
try:
    # Create timezone objects
    utc_tz = pytz.timezone("UTC")
    cairo_tz = pytz.timezone("Africa/Cairo")
    
    # Create naive datetime
    naive_dt = datetime(eclipse_year, eclipse_month, eclipse_day, eclipse_hour, eclipse_minute)
    
    # UTC version
    utc_dt = utc_tz.localize(naive_dt)
    print(f"UTC datetime: {utc_dt.isoformat()}")
    
    # Convert to Cairo time
    cairo_dt = utc_dt.astimezone(cairo_tz)
    print(f"Cairo datetime: {cairo_dt.isoformat()}")
    
    # Convert back to UTC
    back_to_utc = cairo_dt.astimezone(utc_tz)
    print(f"Back to UTC: {back_to_utc.isoformat()}")
    
    # Compare
    print(f"Original UTC and back-converted match: {utc_dt == back_to_utc}")
except Exception as e:
    print(f"Error with timezone debug: {e}")

print("\n=== TEST COMPLETE ===") 