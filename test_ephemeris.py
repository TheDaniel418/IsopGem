import sys
import swisseph as swe
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestEphemeris")

def get_moon_position(jd):
    """Get Moon position at Julian day."""
    try:
        # Set the calculation flags
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # Get Moon's position
        logger.debug(f"Calculating Moon position for JD {jd}")
        result = swe.calc_ut(jd, swe.MOON, flags)
        logger.debug(f"Moon calculation result: {result}")
        
        # Extract longitude from result
        if isinstance(result, tuple):
            if len(result) >= 2:
                # result may be (return_code, [values...]) or just [values...]
                pos_data = result[0] if isinstance(result[0], (list, tuple)) else result
                longitude = pos_data[0]
                logger.info(f"Moon longitude: {longitude}")
                return longitude
            else:
                logger.error(f"Unexpected result format: {result}")
                return None
        else:
            logger.error(f"Result is not a tuple: {result}")
            return None
    except Exception as e:
        logger.error(f"Error calculating Moon position: {e}", exc_info=True)
        return None

def get_sun_position(jd):
    """Get Sun position at Julian day."""
    try:
        # Set the calculation flags
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # Get Sun's position
        logger.debug(f"Calculating Sun position for JD {jd}")
        result = swe.calc_ut(jd, swe.SUN, flags)
        logger.debug(f"Sun calculation result: {result}")
        
        # Extract longitude from result
        if isinstance(result, tuple):
            if len(result) >= 2:
                # result may be (return_code, [values...]) or just [values...]
                pos_data = result[0] if isinstance(result[0], (list, tuple)) else result
                longitude = pos_data[0]
                logger.info(f"Sun longitude: {longitude}")
                return longitude
            else:
                logger.error(f"Unexpected result format: {result}")
                return None
        else:
            logger.error(f"Result is not a tuple: {result}")
            return None
    except Exception as e:
        logger.error(f"Error calculating Sun position: {e}", exc_info=True)
        return None

def test_ephemeris_setup():
    """Test that the ephemeris is set up correctly."""
    logger.info("Testing Swiss Ephemeris setup")
    
    # Print Swiss Ephemeris version
    version = swe.version
    logger.info(f"Swiss Ephemeris version: {version}")
    
    # Test with a specific date
    dt = datetime(2000, 1, 1, 12, 0, 0)
    jd = swe.julday(dt.year, dt.month, dt.day, 
                   dt.hour + dt.minute/60 + dt.second/3600)
    logger.info(f"Test date: {dt}, Julian Day: {jd}")
    
    # Calculate positions
    sun_pos = get_sun_position(jd)
    moon_pos = get_moon_position(jd)
    
    if sun_pos is not None and moon_pos is not None:
        logger.info("Ephemeris test successful!")
        return True
    else:
        logger.error("Ephemeris test failed!")
        return False

def test_lunar_phases():
    """Test calculating lunar phases for a year."""
    logger.info("Testing lunar phase calculation")
    
    # Test year
    year = 2000
    
    # Set start and end dates
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year, 12, 31, 23, 59, 59)
    
    # Convert to Julian days
    start_jd = swe.julday(start_dt.year, start_dt.month, start_dt.day, 
                         start_dt.hour + start_dt.minute/60 + start_dt.second/3600)
    end_jd = swe.julday(end_dt.year, end_dt.month, end_dt.day, 
                       end_dt.hour + end_dt.minute/60 + end_dt.second/3600)
    
    # Test getting positions at different times
    test_dates = [
        datetime(year, 1, 1),
        datetime(year, 4, 1),
        datetime(year, 7, 1),
        datetime(year, 10, 1)
    ]
    
    for dt in test_dates:
        jd = swe.julday(dt.year, dt.month, dt.day, 
                       dt.hour + dt.minute/60 + dt.second/3600)
        logger.info(f"\nTesting date: {dt}")
        sun_pos = get_sun_position(jd)
        moon_pos = get_moon_position(jd)
        
        if sun_pos is not None and moon_pos is not None:
            angle = (moon_pos - sun_pos) % 360
            logger.info(f"Sun-Moon angle: {angle} degrees")
        else:
            logger.error("Failed to calculate positions")

if __name__ == "__main__":
    logger.info("Starting Swiss Ephemeris tests")
    
    # Initialize ephemeris
    try:
        # Try to set ephemeris path (use built-in data)
        swe.set_ephe_path()
        logger.info("Using built-in ephemeris data")
    except Exception as e:
        logger.error(f"Error setting ephemeris path: {e}", exc_info=True)
        sys.exit(1)
    
    # Run tests
    if test_ephemeris_setup():
        test_lunar_phases()
    else:
        logger.error("Setup test failed, skipping other tests")
    
    logger.info("Tests completed") 