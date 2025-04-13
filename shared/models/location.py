"""
Purpose: Defines the Location model used across the application.

This file is part of the shared models and provides a common Location model
that can be used by multiple pillars for geographic functionality.

Key components:
- Location: Model for representing geographic locations
"""

from typing import Optional, Tuple

from pydantic import BaseModel


class Location(BaseModel):
    """Model representing a geographic location."""

    name: str
    display_name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    country_code: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    type: Optional[str] = None
    importance: Optional[float] = None

    def __str__(self) -> str:
        """Get a string representation of the location.

        Returns:
            String representation
        """
        return self.display_name

    @property
    def coordinates(self) -> Tuple[float, float]:
        """Get the coordinates as a tuple.

        Returns:
            Tuple of (latitude, longitude)
        """
        return (self.latitude, self.longitude) 