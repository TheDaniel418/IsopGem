"""
@file skyfield_service.py
@description Service class to encapsulate Skyfield astronomical calculations.
@author IsopGemini
@created 2024-08-13
@lastModified 2024-08-13
@dependencies skyfield
"""

from skyfield.api import load, Topos, Loader
import os

# Define the path to the ephemeris directory relative to this file or a known root
# Assuming this service file is in astrology/services/
# and assets are at the project root.
# Adjust if your project structure is different.
DEFAULT_EPHEMERIS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "ephemeris")
DEFAULT_EPHEMERIS_FILE = "de421.bsp"

class SkyfieldService:
    """
    Provides astronomical calculations using the Skyfield library.
    Manages ephemeris data and observer location.
    """

    def __init__(self, ephemeris_path: str = None):
        """
        Initializes the SkyfieldService.

        Args:
            ephemeris_path (str, optional): Full path to the ephemeris file (e.g., de421.bsp).
                                            If None, uses default path and filename.
        """
        self.timescale = load.timescale()
        self.eph = None
        self.observer = None # Will be a Skyfield Topos object

        if ephemeris_path:
            # If a specific path is provided, try to load directly from it
            try:
                self.eph = load(ephemeris_path)
                print(f"INFO: SkyfieldService: Successfully loaded ephemeris from {ephemeris_path}.")
            except Exception as e:
                print(f"ERROR: SkyfieldService: Failed to load ephemeris from {ephemeris_path}: {e}")
                self.eph = None
        else:
            # Use Skyfield Loader to manage downloads if file not present in default location
            sky_loader = Loader(DEFAULT_EPHEMERIS_DIR, verbose=True) # verbose for download msgs
            default_full_path = os.path.join(DEFAULT_EPHEMERIS_DIR, DEFAULT_EPHEMERIS_FILE)

            # Try to load from the default path first (if it exists)
            if os.path.exists(default_full_path):
                try:
                    self.eph = load(default_full_path)
                    print(f"INFO: SkyfieldService: Successfully loaded ephemeris from {default_full_path}.")
                except Exception as e:
                    print(f"ERROR: SkyfieldService: Failed to load ephemeris from {default_full_path}: {e}")
                    # If loading fails, proceed to attempt download via loader
                    self.eph = None 
            
            # If not loaded from existing file (either didn't exist or failed to load), try loader
            if not self.eph:
                print(f"INFO: SkyfieldService: Ephemeris file {DEFAULT_EPHEMERIS_FILE} not loaded from local path. Attempting to use Skyfield Loader...")
                try:
                    self.eph = sky_loader(DEFAULT_EPHEMERIS_FILE) # Loader will download if not found in its dir
                    print(f"INFO: SkyfieldService: Successfully obtained/verified {DEFAULT_EPHEMERIS_FILE} via Skyfield Loader.")
                except Exception as e:
                    print(f"ERROR: SkyfieldService: Skyfield Loader failed for {DEFAULT_EPHEMERIS_FILE}. Please ensure it's manually placed or network is available: {e}")
                    self.eph = None # Ensure eph is None if download fails

        if self.eph:
            self.sun = self.eph['sun']
            self.moon = self.eph['moon']
            self.earth = self.eph['earth']
        else:
            print("WARNING: SkyfieldService: Ephemeris not loaded. Astronomical calculations will not be available.")
            self.sun = None
            self.moon = None
            self.earth = None

    def set_observer_location(self, latitude_deg: float, longitude_deg: float, elevation_m: float):
        """
        Sets the observer's geographical location.

        Args:
            latitude_deg (float): Observer's latitude in degrees.
            longitude_deg (float): Observer's longitude in degrees.
            elevation_m (float): Observer's elevation in meters above sea level.
        """
        if self.earth: # Ensure Earth object is available from ephemeris
            self.observer = self.earth + Topos(
                latitude_degrees=latitude_deg,
                longitude_degrees=longitude_deg,
                elevation_m=elevation_m
            )
            print(f"INFO: SkyfieldService: Observer location set to Lat: {latitude_deg:.4f}, Lon: {longitude_deg:.4f}, Elev: {elevation_m}m")
        else:
            print("WARNING: SkyfieldService: Earth object not available from ephemeris. Observer location cannot be set.")

    def get_current_time(self):
        """
        Returns the current time as a Skyfield Time object.
        """
        return self.timescale.now()

    # Placeholder for future methods:
    # def get_altaz(self, skyfield_time, target_body):
    #     if not self.observer or not self.eph or not target_body:
    #         print("WARNING: Observer, ephemeris, or target body not set. Cannot calculate Alt/Az.")
    #         return None, None # Or raise error
    #     
    #     astrometric = self.observer.at(skyfield_time).observe(target_body)
    #     alt, az, _ = astrometric.apparent().altaz() # Altitude, Azimuth, distance
    #     return alt, az

    # Example: Get Sun's Alt/Az
    # def get_sun_altaz(self, skyfield_time=None):
    #     if skyfield_time is None:
    #         skyfield_time = self.get_current_time()
    #     if not self.sun:
    #         return None, None
    #     return self.get_altaz(skyfield_time, self.sun)

# Example usage (for testing this file directly)
if __name__ == "__main__":
    service = SkyfieldService()
    if service.eph:
        print("SkyfieldService initialized successfully with ephemeris.")
        
        service.set_observer_location(latitude_deg=ADYTON_LATITUDE_DEG, longitude_deg=ADYTON_LONGITUDE_DEG, elevation_m=ADYTON_ELEVATION_M)
        
        if service.observer:
            print(f"Observer set for Adyton: {service.observer.latitude.degrees:.4f}N, {service.observer.longitude.degrees:.4f}E")
            
            t = service.get_current_time()
            print(f"Current Skyfield Time (UTC): {t.utc_iso()}")
            
            if service.sun:
                astrometric = service.observer.at(t).observe(service.sun)
                alt, az, _ = astrometric.apparent().altaz()
                print(f"Current Sun Alt: {alt.degrees:.2f} deg, Az: {az.degrees:.2f} deg")
        else:
            print("Observer not set.")
    else:
        print("SkyfieldService initialization failed (ephemeris not loaded).")

"""
# Future development:
# - Add methods to get positions of planets, stars (from a catalog).
# - Star catalogs might need to be loaded (e.g., Hipparcos). Skyfield has `load_file` for this.
# - Handle time conversions and specific date inputs.
# - Error handling and logging improvements.
""" 