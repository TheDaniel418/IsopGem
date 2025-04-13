"""
Purpose: Provides geocoding and location search functionality.

This file is part of the astrology pillar and serves as a service component.
It provides functionality to search for locations, convert between location names
and coordinates, and manage favorite locations.

Key components:
- LocationService: Service for geocoding and location search

Dependencies:
- Python typing: For type hint annotations
- requests: For API calls
- pydantic: For data validation
"""

import json
import os
import time
import urllib.parse
from typing import Any, List, Optional

import requests
from loguru import logger

from shared.models.location import Location


class LocationService:
    """Service for geocoding and location search."""

    # Singleton instance
    _instance = None

    # Cache expiration time in seconds (24 hours)
    CACHE_EXPIRATION = 24 * 60 * 60

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
        """Initialize the location service."""
        # Initialize cache
        self._cache = {}
        self._cache_timestamp = {}

        # Initialize favorites
        self._favorites = []

        # Load cache and favorites
        self._load_cache()
        self._load_favorites()

        logger.debug("LocationService initialized")

    def search_locations(self, query: str, limit: int = 10) -> List[Location]:
        """Search for locations by name.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching locations
        """
        # Check cache first
        cache_key = f"search:{query}:{limit}"
        if self._check_cache(cache_key):
            return self._get_from_cache(cache_key)

        # Prepare request
        encoded_query = urllib.parse.quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit={limit}"

        try:
            # Make request
            headers = {"User-Agent": "IsopGem/1.0", "Accept-Language": "en-US,en;q=0.9"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Convert to Location objects
            locations = []
            for item in data:
                try:
                    location = Location(
                        name=item.get("name", ""),
                        display_name=item.get("display_name", ""),
                        latitude=float(item.get("lat", 0)),
                        longitude=float(item.get("lon", 0)),
                        country=item.get("address", {}).get("country", ""),
                        country_code=item.get("address", {}).get("country_code", ""),
                        state=item.get("address", {}).get("state", ""),
                        city=item.get("address", {}).get("city", ""),
                        type=item.get("type", ""),
                        importance=item.get("importance", 0),
                    )
                    locations.append(location)
                except Exception as e:
                    logger.error(f"Error parsing location: {e}")

            # Cache results
            self._add_to_cache(cache_key, locations)

            return locations

        except Exception as e:
            logger.error(f"Error searching for locations: {e}")
            return []

    def geocode(self, address: str) -> Optional[Location]:
        """Convert an address to coordinates.

        Args:
            address: Address to geocode

        Returns:
            Location object or None if geocoding failed
        """
        # Search for the address
        results = self.search_locations(address, limit=1)

        # Return the first result if any
        if results:
            return results[0]

        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        """Convert coordinates to an address.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Location object or None if reverse geocoding failed
        """
        # Check cache first
        cache_key = f"reverse:{latitude},{longitude}"
        if self._check_cache(cache_key):
            return self._get_from_cache(cache_key)

        # Prepare request
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"

        try:
            # Make request
            headers = {"User-Agent": "IsopGem/1.0", "Accept-Language": "en-US,en;q=0.9"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Convert to Location object
            try:
                location = Location(
                    name=data.get("name", ""),
                    display_name=data.get("display_name", ""),
                    latitude=float(data.get("lat", 0)),
                    longitude=float(data.get("lon", 0)),
                    country=data.get("address", {}).get("country", ""),
                    country_code=data.get("address", {}).get("country_code", ""),
                    state=data.get("address", {}).get("state", ""),
                    city=data.get("address", {}).get("city", ""),
                    type=data.get("type", ""),
                    importance=data.get("importance", 0),
                )

                # Cache result
                self._add_to_cache(cache_key, location)

                return location

            except Exception as e:
                logger.error(f"Error parsing location: {e}")
                return None

        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
            return None

    def add_favorite(self, location: Location) -> None:
        """Add a location to favorites.

        Args:
            location: Location to add
        """
        # Check if already in favorites
        for fav in self._favorites:
            if (
                fav.name == location.name
                and fav.latitude == location.latitude
                and fav.longitude == location.longitude
            ):
                return

        # Add to favorites
        self._favorites.append(location)

        # Save favorites
        self._save_favorites()

        logger.debug(f"Added location to favorites: {location.display_name}")

    def remove_favorite(self, location: Location) -> None:
        """Remove a location from favorites.

        Args:
            location: Location to remove
        """
        # Remove from favorites
        self._favorites = [
            fav
            for fav in self._favorites
            if not (
                fav.name == location.name
                and fav.latitude == location.latitude
                and fav.longitude == location.longitude
            )
        ]

        # Save favorites
        self._save_favorites()

        logger.debug(f"Removed location from favorites: {location.display_name}")

    def get_favorites(self) -> List[Location]:
        """Get all favorite locations.

        Returns:
            List of favorite locations
        """
        return self._favorites

    def _check_cache(self, key: str) -> bool:
        """Check if a key is in the cache and not expired.

        Args:
            key: Cache key

        Returns:
            True if the key is in the cache and not expired
        """
        if key not in self._cache:
            return False

        # Check if expired
        timestamp = self._cache_timestamp.get(key, 0)
        if time.time() - timestamp > self.CACHE_EXPIRATION:
            # Remove expired entry
            self._cache.pop(key, None)
            self._cache_timestamp.pop(key, None)
            return False

        return True

    def _get_from_cache(self, key: str) -> Any:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value
        """
        return self._cache.get(key)

    def _add_to_cache(self, key: str, value: Any) -> None:
        """Add a value to the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._cache_timestamp[key] = time.time()

        # Save cache
        self._save_cache()

    def _load_cache(self) -> None:
        """Load the cache from disk."""
        try:
            # Get cache file path
            cache_dir = os.path.expanduser("~/.isopgem/cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "location_cache.json")

            # Check if file exists
            if not os.path.exists(cache_file):
                return

            # Load cache
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Parse cache
            self._cache = {}
            self._cache_timestamp = {}

            for key, entry in data.items():
                value = entry.get("value")
                timestamp = entry.get("timestamp", 0)

                # Skip expired entries
                if time.time() - timestamp > self.CACHE_EXPIRATION:
                    continue

                # Convert to Location objects if needed
                if key.startswith("search:"):
                    value = [Location(**item) for item in value]
                elif key.startswith("reverse:"):
                    value = Location(**value)

                self._cache[key] = value
                self._cache_timestamp[key] = timestamp

            logger.debug(f"Loaded {len(self._cache)} entries from location cache")

        except Exception as e:
            logger.error(f"Error loading location cache: {e}")

    def _save_cache(self) -> None:
        """Save the cache to disk."""
        try:
            # Get cache file path
            cache_dir = os.path.expanduser("~/.isopgem/cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "location_cache.json")

            # Prepare data
            data = {}

            for key, value in self._cache.items():
                # Convert Location objects to dictionaries
                if isinstance(value, list) and value and isinstance(value[0], Location):
                    value = [item.dict() for item in value]
                elif isinstance(value, Location):
                    value = value.dict()

                data[key] = {
                    "value": value,
                    "timestamp": self._cache_timestamp.get(key, time.time()),
                }

            # Save cache
            with open(cache_file, "w") as f:
                json.dump(data, f)

            logger.debug(f"Saved {len(self._cache)} entries to location cache")

        except Exception as e:
            logger.error(f"Error saving location cache: {e}")

    def _load_favorites(self) -> None:
        """Load favorites from disk."""
        try:
            # Get favorites file path
            data_dir = os.path.expanduser("~/.isopgem/data")
            os.makedirs(data_dir, exist_ok=True)
            favorites_file = os.path.join(data_dir, "location_favorites.json")

            # Check if file exists
            if not os.path.exists(favorites_file):
                return

            # Load favorites
            with open(favorites_file, "r") as f:
                data = json.load(f)

            # Parse favorites
            self._favorites = [Location(**item) for item in data]

            logger.debug(f"Loaded {len(self._favorites)} favorite locations")

        except Exception as e:
            logger.error(f"Error loading favorite locations: {e}")

    def _save_favorites(self) -> None:
        """Save favorites to disk."""
        try:
            # Get favorites file path
            data_dir = os.path.expanduser("~/.isopgem/data")
            os.makedirs(data_dir, exist_ok=True)
            favorites_file = os.path.join(data_dir, "location_favorites.json")

            # Prepare data
            data = [item.dict() for item in self._favorites]

            # Save favorites
            with open(favorites_file, "w") as f:
                json.dump(data, f)

            logger.debug(f"Saved {len(self._favorites)} favorite locations")

        except Exception as e:
            logger.error(f"Error saving favorite locations: {e}")
