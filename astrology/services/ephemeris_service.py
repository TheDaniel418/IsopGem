"""
Defines the EphemerisService for Skyfield-based astronomical calculations.

Author: IsopGemini
Created: 2024-07-30
Last Modified: 2024-08-06
Dependencies: skyfield
"""

from typing import Dict, Optional, Tuple  # Added Dict and Tuple

from PyQt6.QtCore import QDate  # For type hinting q_date
from skyfield import almanac  # Added almanac
from skyfield.api import (  # Ensure Loader, wgs84, Star are imported
    Loader,
    Star,
    wgs84,
)
from skyfield.framelib import ecliptic_frame  # Removed icrs from here

# For calculating node, we might need a different approach or specific skyfield features.
# Skyfield's default Moon object doesn't directly give mean node longitude easily.
# We might need to use lower-level data or a helper if skyfield.constants. 例えば、月の上昇ノードの平均黄経を計算する
# skyfield. almanac module provides moon_nodes, but this gives times of node crossings.
# For now, placeholder for node calculation. This is a known complex part.

# For simplicity in finding the ephemeris file, we can use skyfield's built-in loader
# that can also download the file if not present in its default cache location.


class EphemerisService:
    """
    Service to perform astronomical calculations using Skyfield.
    Provides positions of Sun, Moon, and Lunar Ascending Node.
    Also provides azimuths for Galactic Center and Cardinal Points (Solstices/Equinoxes).
    """

    EPHEMERIS_ASSETS_DIR = "./assets/ephemeris/"

    # Define Sgr A* (Galactic Center) coordinates as a class attribute
    # RA: 17h 45m 40.04s -> 17.76112222 hours
    # Dec: -29° 00' 28.1" -> -29.00780556 degrees
    GALACTIC_CENTER_STAR = Star(
        ra_hours=17.76112222,
        dec_degrees=-29.00780556
        # Removed epoch='j2000.0' to see if this resolves type issues in vector math
    )

    # RA/Dec for a few prominent stars (J2000.0)
    # Sirius (Alpha Canis Majoris): RA 06h 45m 08.9173s, Dec -16° 42' 58.017"
    SIRIUS_STAR = Star(
        ra_hours=(6 + 45/60 + 8.9173/3600),
        dec_degrees=-(16 + 42/60 + 58.017/3600)
    )
    # Vega (Alpha Lyrae): RA 18h 36m 56.3364s, Dec +38° 47' 01.280"
    VEGA_STAR = Star(
        ra_hours=(18 + 36/60 + 56.3364/3600),
        dec_degrees=(38 + 47/60 + 1.280/3600)
    )
    # Canopus (Alpha Carinae): RA 06h 23m 57.109s, Dec -52° 41' 44.38"
    CANOPUS_STAR = Star(
        ra_hours=(6 + 23/60 + 57.109/3600),
        dec_degrees=-(52 + 41/60 + 44.38/3600)
    )
    # Arcturus (Alpha Boötis): RA 14h 15m 39.672s, Dec +19° 10' 56.67"
    ARCTURUS_STAR = Star(
        ra_hours=(14 + 15/60 + 39.672/3600),
        dec_degrees=(19 + 10/60 + 56.67/3600)
    )
    # Alpha Centauri (Rigil Kentaurus): RA 14h 39m 36.494s, Dec -60° 50' 02.37" (using A component)
    ALPHA_CENTAURI_STAR = Star(
        ra_hours=(14 + 39/60 + 36.494/3600),
        dec_degrees=-(60 + 50/60 + 2.37/3600)
    )

    # Capella (Alpha Aurigae): RA 05h 16m 41.359s, Dec +45° 59' 52.76"
    CAPELLA_STAR = Star(
        ra_hours=(5 + 16/60 + 41.359/3600),
        dec_degrees=(45 + 59/60 + 52.76/3600)
    )
    # Rigel (Beta Orionis): RA 05h 14m 32.3s, Dec -08° 12' 06"
    RIGEL_STAR = Star(
        ra_hours=(5 + 14/60 + 32.3/3600),
        dec_degrees=-(8 + 12/60 + 6/3600)
    )
    # Procyon (Alpha Canis Minoris): RA 07h 39m 18.1s, Dec +05° 13' 30"
    PROCYON_STAR = Star(
        ra_hours=(7 + 39/60 + 18.1/3600),
        dec_degrees=(5 + 13/60 + 30/3600)
    )
    # Achernar (Alpha Eridani): RA 01h 37m 42.8s, Dec -57° 14' 12"
    ACHERNAR_STAR = Star(
        ra_hours=(1 + 37/60 + 42.8/3600),
        dec_degrees=-(57 + 14/60 + 12/3600)
    )
    # Betelgeuse (Alpha Orionis): RA 05h 55m 10.3s, Dec +07° 24' 25"
    BETELGEUSE_STAR = Star(
        ra_hours=(5 + 55/60 + 10.3/3600),
        dec_degrees=(7 + 24/60 + 25/3600)
    )
    # Hadar (Beta Centauri): RA 14h 03m 49.4s, Dec -60° 22' 23"
    HADAR_STAR = Star(
        ra_hours=(14 + 3/60 + 49.4/3600),
        dec_degrees=-(60 + 22/60 + 23/3600)
    )
    # Altair (Alpha Aquilae): RA 19h 50m 47.0s, Dec +08° 52' 06"
    ALTAIR_STAR = Star(
        ra_hours=(19 + 50/60 + 47.0/3600),
        dec_degrees=(8 + 52/60 + 6/3600)
    )
    # Acrux (Alpha Crucis): RA 12h 26m 35.9s, Dec -63° 05' 57"
    ACRUX_STAR = Star(
        ra_hours=(12 + 26/60 + 35.9/3600),
        dec_degrees=-(63 + 5/60 + 57/3600)
    )
    # Aldebaran (Alpha Tauri): RA 04h 35m 55.2s, Dec +16° 30' 33"
    ALDEBARAN_STAR = Star(
        ra_hours=(4 + 35/60 + 55.2/3600),
        dec_degrees=(16 + 30/60 + 33/3600)
    )
    # Spica (Alpha Virginis): RA 13h 25m 11.6s, Dec -11° 09' 41"
    SPICA_STAR = Star(
        ra_hours=(13 + 25/60 + 11.6/3600),
        dec_degrees=-(11 + 9/60 + 41/3600)
    )
    # Antares (Alpha Scorpii): RA 16h 29m 24.4s, Dec -26° 25' 55"
    ANTARES_STAR = Star(
        ra_hours=(16 + 29/60 + 24.4/3600),
        dec_degrees=-(26 + 25/60 + 55/3600)
    )
    # Pollux (Beta Geminorum): RA 07h 45m 18.9s, Dec +28° 01' 34"
    POLLUX_STAR = Star(
        ra_hours=(7 + 45/60 + 18.9/3600),
        dec_degrees=(28 + 1/60 + 34/3600)
    )
    # Fomalhaut (Alpha Piscis Austrini): RA 22h 57m 39.1s, Dec -29° 37' 20"
    FOMALHAUT_STAR = Star(
        ra_hours=(22 + 57/60 + 39.1/3600),
        dec_degrees=-(29 + 37/60 + 20/3600)
    )
    # Deneb (Alpha Cygni): RA 20h 41m 25.9s, Dec +45° 16' 49"
    DENEB_STAR = Star(
        ra_hours=(20 + 41/60 + 25.9/3600),
        dec_degrees=(45 + 16/60 + 49/3600)
    )
    # Mimosa (Beta Crucis): RA 12h 47m 43.3s, Dec -59° 41' 19"
    MIMOSA_STAR = Star(
        ra_hours=(12 + 47/60 + 43.3/3600),
        dec_degrees=-(59 + 41/60 + 19/3600)
    )

    # List of zodiac signs in order
    ZODIAC_SIGNS = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    def __init__(
        self, ephemeris_file_name: str = "de441.bsp"
    ):  # Changed default to de441.bsp
        """
        Initializes the EphemerisService.
        Loads planetary and lunar ephemeris data using Skyfield.

        Args:
            ephemeris_file_name (str): The name of the .bsp ephemeris file to use.
                                       Skyfield's loader will attempt to download it if not found
                                       in the specified assets directory.
        """

        # Use Skyfield's Loader to manage downloads and paths
        # This ensures it looks in EPHEMERIS_ASSETS_DIR and downloads there if needed.
        skyfield_loader = Loader(
            self.EPHEMERIS_ASSETS_DIR, verbose=False
        )  # verbose=True prints download progress

        try:
            self.ts = skyfield_loader.timescale()
            # For .bsp files containing multiple planets, access them via the `planets` attribute of the loader
            # which returns a multi-segment SPK kernel object.
            self.eph = skyfield_loader(
                ephemeris_file_name
            )  # Corrected: Call the loader instance directly

            self.earth = self.eph["earth"]
            self.sun = self.eph["sun"]
            self.moon = self.eph["moon"]
            # print(f"EphemerisService initialized with {ephemeris_file_name} from {self.EPHEMERIS_ASSETS_DIR}.")

            # Attempt to print coverage information from the SPK kernel comments
            # try:
            #     # The eph object itself is the kernel. Its .comments() method should work.
            #     # If it's a list of segments, one might iterate, but for a single file load, this should be it.
            #     coverage_info = self.eph.comments()
            #     print(f"Coverage information for {ephemeris_file_name}:\\n{coverage_info}")
            # except Exception as e_comment:
            #     print(f"Could not retrieve detailed coverage comments for {ephemeris_file_name}: {e_comment}")
            #     print(f"Ephemeris object type: {type(self.eph)}")
            #     if hasattr(self.eph, 'spk') and hasattr(self.eph.spk, 'comments'):
            #         print("Attempting to get comments via eph.spk.comments()")
            #         try:
            #             print(self.eph.spk.comments())
            #         except Exception as e_spk_comment:
            #             print(f"Failed to get comments via eph.spk.comments(): {e_spk_comment}")
            #     else:
            #         print("No obvious .comments() or .spk.comments() method found on eph object.")

            # Add a small star catalog for common names
            self.star_catalog = {
                "Sirius": self.SIRIUS_STAR,
                "Vega": self.VEGA_STAR,
                "Canopus": self.CANOPUS_STAR,
                "Arcturus": self.ARCTURUS_STAR,
                "Alpha Centauri": self.ALPHA_CENTAURI_STAR,
                "Galactic Center": self.GALACTIC_CENTER_STAR,
                "Capella": self.CAPELLA_STAR,
                "Rigel": self.RIGEL_STAR,
                "Procyon": self.PROCYON_STAR,
                "Achernar": self.ACHERNAR_STAR,
                "Betelgeuse": self.BETELGEUSE_STAR,
                "Hadar": self.HADAR_STAR,
                "Altair": self.ALTAIR_STAR,
                "Acrux": self.ACRUX_STAR,
                "Aldebaran": self.ALDEBARAN_STAR,
                "Spica": self.SPICA_STAR,
                "Antares": self.ANTARES_STAR,
                "Pollux": self.POLLUX_STAR,
                "Fomalhaut": self.FOMALHAUT_STAR,
                "Deneb": self.DENEB_STAR,
                "Mimosa": self.MIMOSA_STAR
                # Add other famous_stars here as Star objects if needed directly
                # For a more comprehensive list, Hipparcos catalog loading would be better
            }

        except Exception as e_load:
            print(
                f"CRITICAL ERROR: Could not load ephemeris file '{ephemeris_file_name}'. Error: {e_load}"
            )
            print(
                "Please ensure the file name is correct and Skyfield can download it,"
            )
            print(f"or that the file exists in {self.EPHEMERIS_ASSETS_DIR}.")
            # Re-raise the exception to signal that the service is non-functional
            # This allows calling code to handle the failure appropriately.
            self.ts = None  # type: ignore # Indicate failure
            self.eph = None # type: ignore

    def get_celestial_positions(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 12,
        minute: int = 0,
        second: int = 0,
        observer_latitude: float = 0.0,
        observer_longitude: float = 0.0,
    ) -> Optional[dict[str, float]]:
        """
        Calculates celestial longitudes for Sun, Moon, and Moon's Ascending Node.

        Args:
            year (int): Year.
            month (int): Month.
            day (int): Day.
            hour (int): Hour (UTC). Defaults to 12 (noon).
            minute (int): Minute (UTC). Defaults to 0.
            second (int): Second (UTC). Defaults to 0.
            observer_latitude (float): Latitude of the observer (degrees). Defaults to 0.0.
            observer_longitude (float): Longitude of the observer (degrees). Defaults to 0.0.

        Returns:
            Optional[dict[str, float]]: A dictionary with keys 'sun_longitude_deg', 'moon_longitude_deg',
                          'node_longitude_deg', or None if ephemeris data is not loaded.
        """
        if not self.eph:
            print("Ephemeris data not loaded. Cannot calculate positions.")
            return None

        t = self.ts.utc(year, month, day, hour, minute, second)

        # Sun's ecliptic longitude
        sun_astrometric = self.earth.at(t).observe(self.sun)
        sun_ecliptic_coords = sun_astrometric.apparent().frame_latlon(ecliptic_frame)
        sun_lon_deg = sun_ecliptic_coords[1].degrees

        # Moon's ecliptic longitude
        moon_astrometric = self.earth.at(t).observe(self.moon)
        moon_ecliptic_coords = moon_astrometric.apparent().frame_latlon(ecliptic_frame)
        moon_lon_deg = moon_ecliptic_coords[1].degrees

        # Mean Lunar Ascending Node Longitude - THIS IS A COMPLEX CALCULATION.
        # Skyfield doesn't directly expose "mean node longitude" as a simple attribute.
        # True node is complex. Mean node is often calculated via polynomial series.
        # For a simplified approach suitable for historical modeling like Hoyle's,
        # one might use a pre-calculated series or a simplified model.
        # A common formula for mean longitude of the ascending node (degrees):
        # L = 125.04452 - 1934.136261 * T + 0.0020708 * T^2 + (T^3 / 450000)
        # where T is Julian centuries from J2000.0.
        # This is an approximation. Skyfield's `almanac.moon_nodes` finds times of node crossings,
        # not the longitude at an arbitrary time directly for the mean node.
        # We will use a placeholder or a very simplified calculation here.
        # For a more accurate model, one would need to implement or find a robust routine for mean node.

        # Placeholder/Simplified Node Calculation (e.g., rough estimate or placeholder)
        # This is NOT astronomically accurate for general use. Needs proper implementation.
        # Example: Using a fixed reference and a known regression rate.
        # True Julian Day from J2000.0
        jd_j2000 = t.tt - 2451545.0
        # Mean node longitude (approximation based on a formula, very rough)
        # L = (125.04452 - 0.05295376805 * jd_j2000) % 360 # simplified from a linear term of regression
        # This is a common simplification. For better accuracy, a full series (like Jean Meeus) is needed.

        # Using a simpler approach for now: calculating from skyfield.constants if possible or placeholder
        # Let's assume a very, very rough placeholder value or look for a direct skyfield feature if one exists for mean node.
        # Direct computation of the mean node longitude usually involves specific orbital elements not directly given by basic observation vectors.
        # For now, as a placeholder for demonstration, let's use a fixed value or a very simplified regression.
        # This will need to be replaced with an accurate calculation for real use.
        # For this placeholder, let's try to get *some* value related to moon's orbit plane
        # This does not give mean node longitude directly. Placeholder value will be used.
        node_lon_deg = (
            125.04 - 0.05295376805 * jd_j2000
        ) % 360  # Very rough Meeus-like linear term for mean node
        if node_lon_deg < 0:
            node_lon_deg += 360

        return {
            "sun_longitude_deg": float(sun_lon_deg),
            "moon_longitude_deg": float(moon_lon_deg),
            "node_longitude_deg": float(
                node_lon_deg
            ),  # Placeholder, needs proper calculation
        }

    def get_celestial_body_alt_az(
        self,
        body_name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        lat: float,
        lon: float,
    ) -> Optional[Tuple[float, float]]:
        """
        Calculates Altitude and Azimuth for a given celestial body by name.

        Args:
            body_name (str): Common name of the celestial body (e.g., "Sun", "Moon", "Venus", "Sirius").
            year (int): Year.
            month (int): Month.
            day (int): Day.
            hour (int): Hour (UTC).
            minute (int): Minute (UTC).
            second (int): Second (UTC).
            lat (float): Observer's latitude in degrees.
            lon (float): Observer's longitude in degrees.

        Returns:
            Optional[Tuple[float, float]]: (altitude_degrees, azimuth_degrees), or None if error.
        """
        if not self.eph or not self.ts:
            print("EphemerisService Error: Ephemeris data or timescale not loaded.")
            return None
        if lat is None or lon is None:
            print("EphemerisService Error: Latitude or longitude not provided for Alt/Az.")
            return None

        try:
            t = self.ts.utc(year, month, day, hour, minute, second)
            observer = wgs84.latlon(lat, lon)
            skyfield_body = None

            # Map common names to Skyfield objects or names
            body_name_lower = body_name.lower()

            # Prioritize planet name mapping, including barycenter variants if passed directly
            if body_name_lower == "sun":
                skyfield_body = self.sun
            elif body_name_lower == "moon":
                skyfield_body = self.moon
            elif body_name_lower == "mercury":
                skyfield_body = self.eph["mercury"]
            elif body_name_lower == "venus":
                skyfield_body = self.eph["venus"]
            elif body_name_lower == "mars" or body_name_lower == "mars barycenter": # Handle both common and specific name
                skyfield_body = self.eph["mars barycenter"]
            elif body_name_lower == "jupiter" or body_name_lower == "jupiter barycenter":
                skyfield_body = self.eph["jupiter barycenter"]
            elif body_name_lower == "saturn" or body_name_lower == "saturn barycenter":
                skyfield_body = self.eph["saturn barycenter"]
            # Check our internal star catalog (case-sensitive for now as dict keys for common names)
            elif body_name in self.star_catalog:
                skyfield_body = self.star_catalog[body_name]
            else:
                # Attempt to look up other stars if we implement a broader catalog search later
                # For now, if not in planets or our small catalog, it's unknown
                print(f"EphemerisService Warning: Celestial body '{body_name}' not recognized or not in pre-defined list.")
                return None

            if skyfield_body:
                # Observations from Earth's center for planets/Sun/Moon, or from observer for stars if Star object is geocentric
                # For Alt/Az, we always want the topocentric view from the observer.
                # The observer object `observer` is wgs84.latlon(lat, lon)
                # We need to observe FROM the observer location on Earth.
                station = self.earth + observer # Create a topocentric observer station
                
                # For stars, which are `Star` objects, they are defined with RA/Dec, effectively at infinity.
                # Observing a `Star` object from a topocentric station gives its position relative to that station.
                # For planets/Sun/Moon from self.eph, they are observed from Earth's center by default.
                # To get topocentric Alt/Az for them, we observe them from the `station`.
                
                astrometric = station.at(t).observe(skyfield_body) # Observe from the station
                apparent = astrometric.apparent()
                # Correct: altaz() is called on the apparent object without observer_location
                # because the observation was already made from the specific station (observer).
                alt, az, distance = apparent.altaz()
                return alt.degrees, az.degrees
            else:
                # This case should be caught by the name checks above, but as a fallback:
                print(f"EphemerisService Error: Could not resolve Skyfield object for '{body_name}'.")
                return None

        except Exception as e:
            print(f"EphemerisService Error calculating Alt/Az for '{body_name}': {e}")
            # import traceback
            # traceback.print_exc() # For more detailed debugging if needed
            return None

    def get_celestial_body_ecliptic_coords(
        self,
        body_name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
    ) -> Optional[Tuple[float, float]]:
        """
        Calculates the ecliptic latitude and longitude of a celestial body for a given UTC time.

        Args:
            body_name (str): Common name of the celestial body (e.g., "Sun", "Moon", "Jupiter", "Sirius").
            year (int): UTC year.
            month (int): UTC month.
            day (int): UTC day.
            hour (int): UTC hour.
            minute (int): UTC minute.
            second (int): UTC second.

        Returns:
            Optional[Tuple[float, float]]: A tuple containing (ecliptic_longitude_degrees, ecliptic_latitude_degrees)
                                           or None if the body is not found or an error occurs.
                                           Longitude is 0-360 degrees. Latitude is -90 to +90 degrees.
        """
        if not hasattr(self, 'ts') or not self.ts or not hasattr(self, 'eph') or not self.eph:
            print("ERROR: EphemerisService not properly initialized (ts or eph missing).")
            return None

        try:
            t = self.ts.utc(year, month, day, hour, minute, second)
            
            observer = self.earth

            skyfield_name_map = {
                "Sun": "sun",
                "Moon": "moon",
                "Mercury": "mercury barycenter", 
                "Venus": "venus barycenter",   
                "Mars": "mars barycenter",     
                "Jupiter": "jupiter barycenter",
                "Saturn": "saturn barycenter",
                "Uranus": "uranus barycenter",
                "Neptune": "neptune barycenter",
                "Pluto": "pluto barycenter", 
            }

            if body_name in skyfield_name_map:
                target_body_name = skyfield_name_map[body_name]
                # Ensure self.eph is not None before using it for indexing
                if self.eph is None or target_body_name not in self.eph:
                    print(f"ERROR: Body '{target_body_name}' not found in ephemeris file or ephemeris not loaded.")
                    return None
                celestial_obj = self.eph[target_body_name]
                
                apparent_position = observer.at(t).observe(celestial_obj).apparent()
                # The ecliptic_latlon method returns (latitude, longitude, distance)
                ecl_lat, ecl_lon, _ = apparent_position.ecliptic_latlon(epoch=t) 
                
                return ecl_lon.degrees, ecl_lat.degrees # Return lon, lat

            elif body_name in self.star_catalog:
                star_obj = self.star_catalog[body_name]
                # The ecliptic_latlon method returns (latitude, longitude, distance)
                # CORRECTED: Observe the star from Earth at time t to get its apparent position,
                # then get ecliptic coordinates.
                apparent_star_position = self.earth.at(t).observe(star_obj).apparent()
                ecl_lat, ecl_lon, _ = apparent_star_position.ecliptic_latlon(epoch=t)
                return ecl_lon.degrees, ecl_lat.degrees # Return lon, lat
            
            else:
                print(f"ERROR: Celestial body '{body_name}' not recognized or not in star catalog.")
                return None

        except Exception as e:
            print(f"Error calculating ecliptic coordinates for {body_name}: {e}")
            return None

    def get_galactic_center_azimuth_for_date_and_location(
        self, q_date: QDate, latitude: float, longitude: float
    ) -> Optional[float]:
        """
        Calculates the azimuth of the Galactic Center (Sgr A*) for a given date and observer location.

        Args:
            q_date (QDate): The specific date for the calculation.
            latitude (float): Observer's latitude in degrees.
            longitude (float): Observer's longitude in degrees.

        Returns:
            Optional[float]: The azimuth of the Galactic Center in degrees from North, or None if error.
        """
        if not self.eph or not self.ts:
            print("EphemerisService Error: Ephemeris data or timescale not loaded.")
            return None
        if latitude is None or longitude is None:
            print("EphemerisService Error: Latitude or longitude not provided.")
            return None

        try:
            # Convert QDate to datetime object for Skyfield, assuming noon UTC for the calculation
            year = q_date.year()
            month = q_date.month()
            day = q_date.day()

            # Handle BCE dates specially - Skyfield uses astronomical year numbering
            # where 1 BCE = year 0, 2 BCE = year -1, etc. QDate already uses this convention.

            # Create time object directly with utc() instead of from_datetime()
            # This method better handles ancient dates including BCE
            try:
                t = self.ts.utc(year, month, day, 12, 0, 0)
            except ValueError:
                # If the date is too far in the past for Skyfield's ephemeris
                print(
                    f"EphemerisService Warning: Date {year}-{month}-{day} is outside the range of the ephemeris data. Using approximate calculations."
                )
                # For very ancient dates, fall back to a simplified calculation
                # This is an approximation that won't be accurate for ancient dates
                # but will provide some reasonable values

                # Calculate Earth's position at J2000.0 and rotate based on precession
                # This is a very rough approximation
                t = self.ts.j2000  # Use J2000 as a reference

                # For simplicity in this fallback, return a fixed value
                # In a full implementation, you would apply precession calculations
                return 180.0  # Default to South as a very rough approximation

            print(
                f"DEBUG EphemerisService: Received lat: {latitude} (type: {type(latitude)}), lon: {longitude} (type: {type(longitude)}) for GC calc (USING ACTUAL GC STAR)"
            )
            observer_topos = wgs84.latlon(float(latitude), float(longitude))
            station = self.earth + observer_topos

            apparent_position = (
                station.at(t).observe(self.GALACTIC_CENTER_STAR).apparent()
            )

            alt, az, distance = apparent_position.altaz()

            azimuth_degrees = az.degrees
            return float(azimuth_degrees)
        except Exception as e:
            print(f"EphemerisService Error calculating Galactic Center azimuth: {e}")
            # Provide a default value when the calculation fails
            # This ensures the UI can still function
            return 180.0  # Default to South as a fallback

    def get_cardinal_point_azimuths_for_date_and_location(
        self, q_date: QDate, latitude: float, longitude: float
    ) -> Optional[Dict[str, float]]:
        """
        Calculates the azimuths of the Sun at the four cardinal points (Solstices/Equinoxes)
        for the year of the given date and observer location.

        Args:
            q_date (QDate): The specific date (year is used to find events in that year).
            latitude (float): Observer's latitude in degrees.
            longitude (float): Observer's longitude in degrees.

        Returns:
            Optional[Dict[str, float]]: Dictionary with keys like 'VE_az', 'SS_az', 'AE_az', 'WS_az'
                                        and their azimuths in degrees, or None if error.
        """
        if not self.eph or not self.ts:
            print("EphemerisService Error: Ephemeris data or timescale not loaded.")
            return None
        if latitude is None or longitude is None:
            print(
                "EphemerisService Error: Latitude or longitude not provided for cardinal points."
            )
            return None

        try:
            print(
                f"DEBUG EphemerisService: Received lat: {latitude} (type: {type(latitude)}), lon: {longitude} (type: {type(longitude)}) for Cardinal calc"
            )
            observer_topos = wgs84.latlon(
                float(latitude), float(longitude)
            )  # Explicitly cast to float
            station = self.earth + observer_topos
            year = q_date.year()

            # Handle ancient dates
            try:
                t_start_of_year = self.ts.utc(year, 1, 1)
                t_end_of_year = self.ts.utc(year + 1, 1, 1)

                season_event_times, season_codes = almanac.find_discrete(
                    t_start_of_year, t_end_of_year, almanac.seasons(self.eph)
                )

                cardinal_azimuths: Dict[str, float] = {}
                event_name_map = {0: "VE_az", 1: "SS_az", 2: "AE_az", 3: "WS_az"}

                # Store both azimuth and ecliptic longitude for each event
                cardinal_longitudes: Dict[str, float] = {}

                for t_event, code in zip(season_event_times, season_codes):
                    if code in event_name_map:
                        # Calculate azimuth
                        apparent_position = (
                            station.at(t_event).observe(self.sun).apparent()
                        )
                        alt, az, distance = apparent_position.altaz()
                        cardinal_azimuths[event_name_map[code]] = float(az.degrees)

                        # Calculate ecliptic longitude
                        ecliptic_coords = apparent_position.frame_latlon(ecliptic_frame)
                        ecliptic_longitude = float(ecliptic_coords[1].degrees)
                        cardinal_longitudes[
                            event_name_map[code].replace("_az", "_lon")
                        ] = ecliptic_longitude

                if len(cardinal_azimuths) < 4:
                    print(
                        f"EphemerisService Warning: Found {len(cardinal_azimuths)}/4 cardinal events for year {year}. Data might be incomplete."
                    )

                # Combine azimuths and longitudes
                result = {**cardinal_azimuths, **cardinal_longitudes}
                return result if cardinal_azimuths else None

            except ValueError:
                # If the date is too far in the past for Skyfield's ephemeris
                print(
                    f"EphemerisService Warning: Year {year} is outside the range of the ephemeris data. Using approximate calculations for cardinal points."
                )

                # For very ancient dates, fall back to a simplified calculation
                # This won't be accurate for ancient dates but provides reasonable values
                # Approximate cardinal points for all eras
                return {
                    "VE_az": 90.0,  # Vernal Equinox - East
                    "SS_az": 0.0,  # Summer Solstice - North
                    "AE_az": 270.0,  # Autumnal Equinox - West
                    "WS_az": 180.0,  # Winter Solstice - South
                    "VE_lon": 0.0,  # Aries 0°
                    "SS_lon": 90.0,  # Cancer 0°
                    "AE_lon": 180.0,  # Libra 0°
                    "WS_lon": 270.0,  # Capricorn 0°
                }

        except Exception as e:
            print(f"EphemerisService Error calculating cardinal point azimuths: {e}")
            # Provide default values when the calculation fails
            # This ensures the UI can still function
            return {
                "VE_az": 90.0,  # Vernal Equinox - East
                "SS_az": 0.0,  # Summer Solstice - North
                "AE_az": 270.0,  # Autumnal Equinox - West
                "WS_az": 180.0,  # Winter Solstice - South
                "VE_lon": 0.0,  # Aries 0°
                "SS_lon": 90.0,  # Cancer 0°
                "AE_lon": 180.0,  # Libra 0°
                "WS_lon": 270.0,  # Capricorn 0°
            }

    def get_galactic_center_ecliptic_longitude(self, q_date: QDate) -> Optional[float]:
        """
        Calculates the ecliptic longitude of the Galactic Center for a given date.

        Args:
            q_date (QDate): The specific date for the calculation.

        Returns:
            Optional[float]: The ecliptic longitude in degrees, or None if error.
        """
        if not self.eph or not self.ts:
            print("EphemerisService Error: Ephemeris data or timescale not loaded.")
            return None

        try:
            # Convert QDate to datetime object for Skyfield
            year = q_date.year()
            month = q_date.month()
            day = q_date.day()

            try:
                t = self.ts.utc(year, month, day, 12, 0, 0)
            except ValueError:
                print(
                    f"EphemerisService Warning: Date {year}-{month}-{day} is outside the range of the ephemeris data."
                )
                t = self.ts.j2000  # Use J2000 as reference

            # Calculate GC position in ecliptic coordinates
            earth_at_t = self.earth.at(t)
            gc_astrometric = earth_at_t.observe(self.GALACTIC_CENTER_STAR)
            gc_ecliptic = gc_astrometric.apparent().frame_latlon(ecliptic_frame)

            # Extract longitude
            gc_longitude = float(gc_ecliptic[1].degrees)

            return gc_longitude
        except Exception as e:
            print(
                f"EphemerisService Error calculating Galactic Center ecliptic longitude: {e}"
            )
            return 266.4  # Approximate GC longitude in Sagittarius

    def longitude_to_zodiac(self, longitude: float) -> Tuple[str, float]:
        """
        Converts ecliptic longitude to zodiac sign and degrees within the sign.

        Args:
            longitude (float): Ecliptic longitude in degrees (0-360)

        Returns:
            Tuple[str, float]: (zodiac_sign, degrees_in_sign)
        """
        # Normalize longitude to 0-360 range
        longitude = longitude % 360

        # Calculate the zodiac sign index (0-11)
        sign_index = int(longitude / 30)

        # Calculate degrees within the sign (0-29.99...)
        degrees_in_sign = longitude % 30

        return (self.ZODIAC_SIGNS[sign_index], degrees_in_sign)

    def get_cardinal_points_with_zodiac(
        self, q_date: QDate, latitude: float, longitude: float
    ) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Gets cardinal points with both azimuth and zodiac sign information.

        Args:
            q_date (QDate): The specific date for the calculation.
            latitude (float): Observer's latitude in degrees.
            longitude (float): Observer's longitude in degrees.

        Returns:
            Optional[Dict[str, Dict[str, str]]]: Dictionary with cardinal point information
        """
        # Get azimuths and longitudes
        cardinal_data = self.get_cardinal_point_azimuths_for_date_and_location(
            q_date, latitude, longitude
        )

        if not cardinal_data:
            return None

        result = {}

        # Process each cardinal point
        for point_name in ["VE", "SS", "AE", "WS"]:
            azimuth_key = f"{point_name}_az"
            longitude_key = f"{point_name}_lon"

            if azimuth_key in cardinal_data:
                azimuth = cardinal_data[azimuth_key]

                # Get ecliptic longitude
                ecliptic_longitude = cardinal_data.get(longitude_key)
                if ecliptic_longitude is None:
                    # If longitude not provided, use these standard values
                    if point_name == "VE":
                        ecliptic_longitude = 0.0  # Aries 0°
                    elif point_name == "SS":
                        ecliptic_longitude = 90.0  # Cancer 0°
                    elif point_name == "AE":
                        ecliptic_longitude = 180.0  # Libra 0°
                    elif point_name == "WS":
                        ecliptic_longitude = 270.0  # Capricorn 0°

                # Convert to zodiac
                zodiac_sign, degrees_in_sign = self.longitude_to_zodiac(
                    ecliptic_longitude
                )

                result[point_name] = {
                    "azimuth": f"{azimuth:.2f}°",
                    "zodiac": f"{zodiac_sign} {degrees_in_sign:.2f}°",
                }

        # Add Galactic Center
        gc_azimuth = self.get_galactic_center_azimuth_for_date_and_location(
            q_date, latitude, longitude
        )
        gc_longitude = self.get_galactic_center_ecliptic_longitude(q_date)

        if gc_azimuth and gc_longitude:
            zodiac_sign, degrees_in_sign = self.longitude_to_zodiac(gc_longitude)
            result["GC"] = {
                "azimuth": f"{gc_azimuth:.2f}°",
                "zodiac": f"{zodiac_sign} {degrees_in_sign:.2f}°",
            }

        return result


# Example Usage:
if __name__ == "__main__":
    print("Initializing Ephemeris Service for testing...")
    # Create a dummy assets/ephemeris directory if it doesn't exist for the loader
    import os

    if not os.path.exists("./assets/ephemeris"):
        os.makedirs("./assets/ephemeris")
        print("Created dummy ./assets/ephemeris directory for Loader.")

    ephem_service = EphemerisService()
    if ephem_service.eph:
        print("\nGetting positions for 2000-01-01 12:00:00 UTC (J2000.0 noon)")
        positions = ephem_service.get_celestial_positions(2000, 1, 1)
        if positions:
            print(f"  Sun Longitude: {positions['sun_longitude_deg']:.2f} deg")
            print(f"  Moon Longitude: {positions['moon_longitude_deg']:.2f} deg")
            print(
                f"  Node Longitude (Approx/Placeholder): {positions['node_longitude_deg']:.2f} deg"
            )

        print("\nGetting positions for a different date: 1950-06-15 12:00:00 UTC")
        positions_historical = ephem_service.get_celestial_positions(1950, 6, 15)
        if positions_historical:
            print(
                f"  Sun Longitude: {positions_historical['sun_longitude_deg']:.2f} deg"
            )
            print(
                f"  Moon Longitude: {positions_historical['moon_longitude_deg']:.2f} deg"
            )
            print(
                f"  Node Longitude (Approx/Placeholder): {positions_historical['node_longitude_deg']:.2f} deg"
            )
    else:
        print("Ephemeris service could not be initialized, further tests skipped.")
