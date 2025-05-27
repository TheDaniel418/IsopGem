"""
/**
 * @file astrology/models/eclipse_data.py
 * @description Pydantic model for storing individual eclipse event data.
 * @author Your Name/AI Assistant
 * @created YYYY-MM-DD
 * @lastModified YYYY-MM-DD
 * @dependencies pydantic
 */
"""
from typing import Optional

from pydantic import BaseModel


class EclipseData(BaseModel):
    """
    Represents the data for a single solar eclipse event, parsed from a catalog.
    """

    year: int
    month: int
    day: int
    eclipse_type: str  # e.g., "T", "A", "P", "H"
    cat_no: str  # Catalog number, e.g., "07901"
    magnitude: Optional[float] = None
    lat_dd_ge: Optional[float] = None  # Latitude of Greatest Eclipse (Decimal Degrees)
    lng_dd_ge: Optional[float] = None  # Longitude of Greatest Eclipse (Decimal Degrees)
    central_duration: Optional[str] = None  # e.g., "02m10.5s"
    path_width: Optional[str] = None  # e.g., "100km"
    td_ge: Optional[str] = None  # Time of Greatest Eclipse, e.g., "03:14:51"

    class Config:
        anystr_strip_whitespace = True
        validate_assignment = True


# Example Usage (for testing or understanding)
if __name__ == "__main__":
    sample_eclipse = EclipseData(
        year=1605,
        month=10,
        day=12,
        eclipse_type="A",
        cat_no="05805",
        magnitude=0.9376,
        lat_dd_ge=1.4,
        lng_dd_ge=23.2,
        central_duration="07m41s",
        path_width="250",
        td_ge="12:34:56",
    )
    print(
        f"Sample Eclipse Event: {sample_eclipse.year}-{sample_eclipse.month:02d}-{sample_eclipse.day:02d}"
    )
    print(f"  Type: {sample_eclipse.eclipse_type}, Catalog: {sample_eclipse.cat_no}")
    print(f"  Magnitude: {sample_eclipse.magnitude}")
    print(
        f"  Greatest Eclipse at: Lat {sample_eclipse.lat_dd_ge}, Lng {sample_eclipse.lng_dd_ge}"
    )
    print(
        f"  Central Duration: {sample_eclipse.central_duration}, Path Width: {sample_eclipse.path_width}km"
    )
    print(f"  Time of Greatest Eclipse: {sample_eclipse.td_ge}")

    try:
        invalid_data = EclipseData(
            year="not_a_year", month=1, day=1, eclipse_type="T", cat_no="test"
        )
    except Exception as e:
        print(f"\nError with invalid data: {e}")
