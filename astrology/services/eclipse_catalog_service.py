"""
/**
 * @file astrology/services/eclipse_catalog_service.py
 * @description Service for loading and querying solar eclipse data from a CSV file.
 * @author Gemini AI Assistant
 * @created YYYY-MM-DD
 * @lastModified YYYY-MM-DD
 * @dependencies pandas, pydantic, astrology.models.eclipse_data
 */
"""
from typing import List, Optional

import pandas as pd

from astrology.models.eclipse_data import EclipseData

# Define which eclipse types from the CSV are considered solar eclipses
SOLAR_ECLIPSE_TYPES = ["A", "T", "P", "H"]  # Annular, Total, Partial, Hybrid

# Define the exact column names from the CSV that we need
REQUIRED_CSV_COLUMNS = [
    "year",
    "month",
    "day",
    "eclipse_type",
    "cat_no",
    "magnitude",
    "lat_dd_ge",
    "lng_dd_ge",
    "central_duration",
    "path_width",
    "td_ge",
]


class EclipseCatalogService:
    """
    Service to load and query solar eclipse data from a CSV file.
    Handles parsing of the NASA eclipse catalog data.
    """

    def __init__(
        self,
        csv_file_path: str = "assets/ephemeris/eclipse_besselian_from_mysqldump2.csv",
    ):
        """
        Initializes the service and loads the eclipse data.

        Args:
            csv_file_path (str): Path to the eclipse catalog CSV file,
                                 relative to the project root.
        """
        self.csv_file_path = csv_file_path
        self._eclipse_df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self) -> None:
        """
        Loads eclipse data from the CSV file into a pandas DataFrame.
        It selects only the required columns to optimize memory and processing.
        Error handling is included for file not found or parsing issues.
        """
        try:
            print(f"Attempting to load eclipse data from: {self.csv_file_path}")
            self._eclipse_df = pd.read_csv(
                self.csv_file_path,
                usecols=lambda column_name: column_name
                in REQUIRED_CSV_COLUMNS,  # More robust usecols
                low_memory=False,  # Recommended for large files with potentially mixed types
            )
            # Basic cleaning: strip whitespace from string columns that Pydantic will handle as strings
            string_columns_to_clean = [
                "eclipse_type",
                "cat_no",
                "central_duration",
                "path_width",
            ]
            for col in string_columns_to_clean:
                if col in self._eclipse_df.columns:
                    # Ensure column is treated as string before attempting string operations
                    self._eclipse_df[col] = (
                        self._eclipse_df[col].astype(str).str.strip()
                    )
            print(
                f"Successfully loaded and initially processed {len(self._eclipse_df)} records."
            )
        except FileNotFoundError:
            print(
                f"🚨 Error: Eclipse catalog CSV file not found at '{self.csv_file_path}'."
            )
            self._eclipse_df = pd.DataFrame(
                columns=REQUIRED_CSV_COLUMNS
            )  # Ensure empty df has columns
        except ValueError as ve:
            # This can happen if a required column for usecols is missing in the CSV
            print(
                f"🚨 ValueError during CSV loading (e.g., a required column might be missing): {ve}"
            )
            print(
                f"Please ensure the CSV file at '{self.csv_file_path}' contains all columns: {REQUIRED_CSV_COLUMNS}"
            )
            self._eclipse_df = pd.DataFrame(columns=REQUIRED_CSV_COLUMNS)
        except Exception as e:
            print(f"🚨 Unexpected error loading eclipse catalog CSV: {e}")
            self._eclipse_df = pd.DataFrame(columns=REQUIRED_CSV_COLUMNS)

    def _to_float_or_none(self, value) -> Optional[float]:
        """Helper to convert a value to float, returning None if conversion fails or value is NaN/empty."""
        if pd.isna(value) or str(value).strip() == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _to_str_or_none(self, value) -> Optional[str]:
        """Helper to convert a value to string, returning None if value is NaN/empty."""
        if pd.isna(value):
            return None
        val_str = str(value).strip()
        return val_str if val_str else None

    def get_solar_eclipses(
        self, start_year: Optional[int] = None, end_year: Optional[int] = None
    ) -> List[EclipseData]:
        """
        Retrieves a list of solar eclipse events, optionally filtered by a year range.

        Args:
            start_year (Optional[int]): The starting year for filtering (inclusive).
            end_year (Optional[int]): The ending year for filtering (inclusive).

        Returns:
            List[EclipseData]: A list of solar eclipse data objects.
        """
        if self._eclipse_df is None or self._eclipse_df.empty:
            print("Eclipse data not loaded or is empty. Cannot fetch solar eclipses.")
            return []

        # Ensure 'eclipse_type' and 'year' columns exist before filtering
        if (
            "eclipse_type" not in self._eclipse_df.columns
            or "year" not in self._eclipse_df.columns
        ):
            print("Critical columns 'eclipse_type' or 'year' not found in DataFrame.")
            return []

        # Make a copy for filtering to avoid SettingWithCopyWarning
        df_filtered = self._eclipse_df.copy()

        # Filter for solar eclipses
        # Ensure 'eclipse_type' is string type for isin comparison
        df_filtered["eclipse_type"] = df_filtered["eclipse_type"].astype(str)
        df_filtered = df_filtered[df_filtered["eclipse_type"].isin(SOLAR_ECLIPSE_TYPES)]

        # Filter by year range (ensure 'year' is numeric)
        try:
            df_filtered["year"] = pd.to_numeric(df_filtered["year"], errors="coerce")
            df_filtered.dropna(
                subset=["year"], inplace=True
            )  # Remove rows where year could not be coerced
            df_filtered["year"] = df_filtered["year"].astype(int)
        except Exception as e:
            print(
                f"Error converting 'year' column to numeric: {e}. Year filtering may be affected."
            )
            # Proceed without year filtering if conversion fails, or return empty list

        if start_year is not None:
            df_filtered = df_filtered[df_filtered["year"] >= start_year]
        if end_year is not None:
            df_filtered = df_filtered[df_filtered["year"] <= end_year]

        eclipse_events: List[EclipseData] = []
        for _, row in df_filtered.iterrows():
            try:
                event_data = {
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "day": int(row["day"]),
                    "eclipse_type": str(row["eclipse_type"]),
                    "cat_no": str(row["cat_no"]),
                    "magnitude": self._to_float_or_none(row.get("magnitude")),
                    "lat_dd_ge": self._to_float_or_none(row.get("lat_dd_ge")),
                    "lng_dd_ge": self._to_float_or_none(row.get("lng_dd_ge")),
                    "central_duration": self._to_str_or_none(
                        row.get("central_duration")
                    ),
                    "path_width": self._to_str_or_none(row.get("path_width")),
                    "td_ge": self._to_str_or_none(row.get("td_ge")),
                }
                eclipse_events.append(EclipseData(**event_data))
            except Exception as e:
                print(
                    f"⚠️ Skipping row due to data conversion or validation error: {row.to_dict() if hasattr(row, 'to_dict') else 'N/A'}. Error: {e}"
                )

        return eclipse_events


# Example Usage Block
if __name__ == "__main__":
    print("--- Eclipse Catalog Service Test --- ")
    # Check for pandas installation
    try:
        import pandas

        print(f"✅ Pandas version: {pandas.__version__}")
    except ImportError:
        print(
            "❌ Critical Error: Pandas library is not installed. Please install it (e.g., pip install pandas)."
        )
        exit(1)

    print("\n✨ Initializing EclipseCatalogService...")
    # The default path 'assets/ephemeris/eclipse_besselian_from_mysqldump2.csv' will be used.
    # Ensure this file exists at the specified location relative to your project root.
    catalog_service = EclipseCatalogService()

    if (
        catalog_service._eclipse_df is not None
        and not catalog_service._eclipse_df.empty
    ):
        print(f"\n📚 Loaded {len(catalog_service._eclipse_df)} total records from CSV.")

        print("\n☀️ Fetching all solar eclipses (showing first 5 if available)...")
        all_solar_eclipses = catalog_service.get_solar_eclipses()
        if all_solar_eclipses:
            print(f"Found {len(all_solar_eclipses)} solar eclipses in total.")
            for i, eclipse in enumerate(all_solar_eclipses[:5]):
                print(
                    f"  {i+1}. {eclipse.year}-{eclipse.month:02d}-{eclipse.day:02d}: Type={eclipse.eclipse_type}, Cat={eclipse.cat_no}, Mag={eclipse.magnitude:.4f if eclipse.magnitude else 'N/A'}"
                )
        else:
            print("No solar eclipses found or data loading issue persisted.")

        print("\n📅 Fetching solar eclipses for the year 1605...")
        eclipses_1605 = catalog_service.get_solar_eclipses(
            start_year=1605, end_year=1605
        )
        if eclipses_1605:
            print(f"Found {len(eclipses_1605)} solar eclipse(s) in 1605:")
            for eclipse in eclipses_1605:
                print(
                    f"  - {eclipse.year}-{eclipse.month:02d}-{eclipse.day:02d}: Type={eclipse.eclipse_type}, Cat={eclipse.cat_no}, Mag={eclipse.magnitude:.4f if eclipse.magnitude else 'N/A'}, Lat={eclipse.lat_dd_ge}, Dur={eclipse.central_duration}"
                )
        else:
            print("No solar eclipses found for 1605.")

        print(
            "\n🗓️ Fetching solar eclipses from 2000 to 2001 (showing first 5 if available)..."
        )
        eclipses_2000_2001 = catalog_service.get_solar_eclipses(
            start_year=2000, end_year=2001
        )
        if eclipses_2000_2001:
            print(f"Found {len(eclipses_2000_2001)} solar eclipses between 2000-2001.")
            for i, eclipse in enumerate(eclipses_2000_2001[:5]):
                print(
                    f"  {i+1}. {eclipse.year}-{eclipse.month:02d}-{eclipse.day:02d}: Type={eclipse.eclipse_type}, Cat={eclipse.cat_no}"
                )
        else:
            print("No solar eclipses found for 2000-2001.")

        print("\n👻 Fetching solar eclipses for a year with no eclipses (e.g., 1)...")
        eclipses_year_1 = catalog_service.get_solar_eclipses(start_year=1, end_year=1)
        if not eclipses_year_1:
            print(
                "Correctly found no solar eclipses for year 1 (as expected from typical catalog ranges)."
            )
        else:
            print(
                f"Found {len(eclipses_year_1)} solar eclipses for year 1, which might be unexpected."
            )

    else:
        print(
            "❌ Eclipse data DataFrame is None or empty after initialization. Service cannot function."
        )
    print("\n--- Test Complete --- ")
