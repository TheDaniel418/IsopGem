"""
Purpose: Calculates house cusps for astrological charts.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to calculate house cusps for different house systems
based on a given date, time, and location.

Key components:
- HouseSystemService: Service for calculating house cusps

Dependencies:
- Python typing: For type hint annotations
- datetime: For date and time handling
- astrology.models: For astrological data models
"""

import swisseph as swe
from datetime import datetime
from typing import List

from loguru import logger

from astrology.models.zodiac import House, HouseSystem


class HouseSystemService:
    """Service for calculating house cusps."""

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the house system service."""
        logger.debug("HouseSystemService initialized")

    def calculate_houses(
        self,
        date_time: datetime,
        latitude: float,
        longitude: float,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ) -> List[House]:
        """Calculate house cusps for a given date, time, and location.

        Args:
            date_time: Date and time for the calculation
            latitude: Latitude of the location
            longitude: Longitude of the location
            house_system: House system to use

        Returns:
            List of houses with their cusps
        """
        # Using Swiss Ephemeris for accurate astronomical calculations
        houses = []

        # Convert datetime to Julian day
        jd = swe.julday(
            date_time.year,
            date_time.month,
            date_time.day,
            date_time.hour + date_time.minute/60.0 + date_time.second/3600.0
        )

        # Map HouseSystem enum to Swiss Ephemeris house system characters
        house_system_map = {
            HouseSystem.PLACIDUS: b'P',
            HouseSystem.KOCH: b'K',
            HouseSystem.EQUAL: b'E',
            HouseSystem.WHOLE_SIGN: b'W',
            HouseSystem.REGIOMONTANUS: b'R',
            HouseSystem.CAMPANUS: b'C',
            HouseSystem.PORPHYRY: b'O',
            HouseSystem.MORINUS: b'M',
            HouseSystem.TOPOCENTRIC: b'T',
            HouseSystem.ALCABITIUS: b'B',
        }

        # Get the Swiss Ephemeris house system character
        swe_house_system = house_system_map.get(house_system, b'P')  # Default to Placidus
        
        # Debug log for house system
        logger.debug(f"Using house system: {house_system.value}, SwissEph code: {swe_house_system}")

        # Calculate house cusps using Swiss Ephemeris
        try:
            logger.debug(f"Calling swe.houses with jd={jd}, lat={latitude}, lon={longitude}, hsys={swe_house_system}")
            # Try both bytes and string versions for compatibility
            try:
                # Try with bytes version
                result = swe.houses(jd, latitude, longitude, swe_house_system)
            except Exception as bytes_error:
                logger.warning(f"Failed with bytes version: {str(bytes_error)}, trying string version")
                # Try with string version (convert bytes to string)
                swe_house_system_str = swe_house_system.decode('utf-8')
                result = swe.houses(jd, latitude, longitude, swe_house_system_str)
            logger.debug(f"Result type: {type(result)}, length: {len(result) if hasattr(result, '__len__') else 'N/A'}")

            # Extract house cusps and additional points
            cusps = result[0]  # House cusps array (1-indexed)
            ascmc = result[1]  # Additional points: Ascendant, MC, etc.

            logger.debug(f"Cusps type: {type(cusps)}, length: {len(cusps) if hasattr(cusps, '__len__') else 'N/A'}")
            logger.debug(f"Ascmc type: {type(ascmc)}, length: {len(ascmc) if hasattr(ascmc, '__len__') else 'N/A'}")

            # Log the raw cusps array for debugging
            logger.debug(f"Raw cusps array from Swiss Ephemeris: {cusps}")
            logger.debug(f"Raw ascmc array from Swiss Ephemeris: {ascmc}")
        except Exception as e:
            logger.error(f"Error in swe.houses: {str(e)}")
            # Fallback to equal houses
            logger.warning("Falling back to equal houses")
            cusps = [0] * 13  # Create a 1-indexed array (ignore index 0)
            ascmc = [0] * 10  # Create array for ascendant, MC, etc.

            # Set ascendant (arbitrary value for testing)
            ascendant = 0.0
            mc = 90.0

            # Fill cusps array with equal houses
            for i in range(1, 13):
                cusps[i] = (ascendant + (i - 1) * 30) % 360

            # Fill ascmc array
            ascmc[0] = ascendant  # Ascendant
            ascmc[1] = mc         # Midheaven

        # Extract key points
        ascendant = ascmc[0]  # Ascendant (1st house cusp)
        mc = ascmc[1]        # Midheaven (10th house cusp)

        logger.debug(f"Swiss Ephemeris calculated Ascendant: {ascendant:.2f}°, MC: {mc:.2f}°")

        # Log the house cusps for debugging in a clear format
        logger.debug("=== HOUSE CUSP CALCULATION RESULTS ===")
        logger.debug(f"Ascendant: {ascendant:.2f}°, MC: {mc:.2f}°")
        logger.debug(f"House system: {house_system.value}")
        logger.debug("-" * 50)
        logger.debug(f"{'House':<6} {'Cusp Degree':>12} {'Next House':>12} {'Width':>8}")
        logger.debug("-" * 50)

        # Create house objects using the cusps calculated by Swiss Ephemeris
        # Note: Swiss Ephemeris cusps array is 1-indexed, so we need to be careful with indexing
        for i in range(1, 13):
            # For next house cusp, wrap around to house 1 if we're on house 12
            next_i = i + 1 if i < 12 else 1
            
            # Special handling for house 12
            if i == 12:
                # House 12 goes from its cusp to the Ascendant (house 1 cusp)
                cusp = cusps[i] if i < len(cusps) else (ascendant + 330) % 360  # Fallback: 30 degrees before Ascendant
                end = cusps[1]  # End at the Ascendant (house 1 cusp)
            else:
                # Make sure we don't go out of bounds
                if i < len(cusps):
                    cusp = cusps[i]
                    end = cusps[next_i] if next_i < len(cusps) else cusps[1]
                else:
                    # Fallback if the cusps array doesn't have enough elements
                    # This shouldn't happen with a properly working Swiss Ephemeris
                    logger.error(f"Cusps array index out of range: i={i}, next_i={next_i}, len(cusps)={len(cusps)}")
                    cusp = (ascendant + (i - 1) * 30) % 360  # Fallback to equal houses
                    end = (cusp + 30) % 360

            # Calculate width (handle wrap-around at 360 degrees)
            width = (end - cusp) % 360

            # Log house information
            logger.debug(f"{i:<6} {cusp:>12.2f}° {next_i:>12} {width:>8.2f}°")

            # Get the zodiac sign for this house cusp
            sign_name = self._get_sign_for_longitude(cusp)

            # Create the house object
            house = House(
                number=i,
                name=f"House {i}",
                cusp_degree=cusp,
                end_degree=end,
                sign=sign_name,
                keywords=self._get_house_keywords(i)
            )
            houses.append(house)

            # Log detailed house information
            logger.debug(f"House {i:<2}: cusp at {cusp:>6.2f}° ({sign_name:<10}), ends at {end:>6.2f}°, width: {width:>5.2f}°")

        return houses

    # These methods are no longer used with Swiss Ephemeris
    # They are kept as stubs for backward compatibility

    # The _calculate_placidus_cusp method has been removed as it's no longer needed
    # We now use a different approach to calculate house cusps in the calculate_houses method

    def _get_sign_for_longitude(self, longitude: float) -> str:
        """Get the zodiac sign for a given longitude.

        Args:
            longitude: Longitude in degrees (0-360)

        Returns:
            Name of the zodiac sign
        """
        # Normalize longitude to 0-360 range
        normalized_longitude = longitude % 360

        # Each sign is 30 degrees
        sign_index = int(normalized_longitude / 30)

        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        return signs[sign_index]

    def _get_house_keywords(self, house_number: int) -> List[str]:
        """Get keywords for a house.

        Args:
            house_number: House number (1-12)

        Returns:
            List of keywords
        """
        keywords = {
            1: ["self", "identity", "appearance", "beginnings"],
            2: ["possessions", "values", "resources", "self-worth"],
            3: ["communication", "siblings", "local travel", "learning"],
            4: ["home", "family", "roots", "security"],
            5: ["creativity", "pleasure", "children", "romance"],
            6: ["work", "health", "service", "routine"],
            7: ["partnerships", "marriage", "contracts", "open enemies"],
            8: ["transformation", "shared resources", "intimacy", "death"],
            9: ["higher learning", "philosophy", "travel", "expansion"],
            10: ["career", "public image", "authority", "achievement"],
            11: ["friends", "groups", "hopes", "humanitarian pursuits"],
            12: ["unconscious", "spirituality", "isolation", "hidden enemies"]
        }

        return keywords.get(house_number, [])
