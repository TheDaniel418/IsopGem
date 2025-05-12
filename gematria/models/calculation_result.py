"""
Purpose: Defines the data model for gematria calculation results

This file is part of the gematria pillar and serves as a model component.
It is responsible for representing the structure and properties of calculation
results throughout the application, providing a standardized way to store and
retrieve calculation data.

Key components:
- CalculationResult: Data class representing a complete gematria calculation
  with input text, method, result value, timestamp, and metadata like tags and notes

Dependencies:
- dataclasses: For creating a proper data class with minimal boilerplate
- uuid: For generating unique identifiers for calculations
- datetime: For timestamp tracking

Related files:
- gematria/services/gematria_service.py: Creates calculation results
- gematria/repositories/calculation_repository.py: Stores calculation results
- gematria/ui/panels/calculation_history_panel.py: Displays calculation results
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from gematria.models.calculation_type import CalculationType

logger = logging.getLogger(__name__)


@dataclass
class CalculationResult:
    """Represents a gematria calculation result with metadata."""

    input_text: str
    calculation_type: Union[CalculationType, str]
    result_value: Union[int, str]
    notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: List[str] = field(default_factory=list)
    favorite: bool = False
    custom_method_name: Optional[str] = None

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        This is an alias for the timestamp attribute to maintain compatibility
        with code that expects a created_at attribute.

        Returns:
            The timestamp when this calculation was created
        """
        return self.timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage.

        Returns:
            Dictionary representation of the calculation result
        """
        # Handle calculation type
        if isinstance(self.calculation_type, CalculationType):
            calc_type_str = (
                self.calculation_type.name
            )  # Store the enum's programmatic name
        else:
            # This handles cases where calculation_type is already a string (e.g., "CUSTOM_CIPHER")
            calc_type_str = str(self.calculation_type)

        return {
            "id": self.id,
            "input_text": self.input_text,
            "calculation_type": calc_type_str,
            "result_value": str(self.result_value),
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "favorite": self.favorite,
            "custom_method_name": self.custom_method_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalculationResult":
        """Create from dictionary representation.

        Args:
            data: Dictionary data from storage

        Returns:
            CalculationResult instance
        """
        # Handle timestamp (convert from ISO format)
        if isinstance(data.get("timestamp"), str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = datetime.now()

        # Handle calculation type
        calc_type_data = data.get("calculation_type")
        calculation_type_to_assign: Union[CalculationType, str]

        if isinstance(calc_type_data, str):
            try:
                # Attempt to convert from enum member name string (e.g., "HEBREW_STANDARD_VALUE")
                calculation_type_to_assign = CalculationType[calc_type_data]
            except KeyError:
                # Not a direct enum name. Check for old stringified tuple format.
                if calc_type_data.startswith("(") and calc_type_data.endswith(")"):
                    try:
                        # Attempt to parse the first element of the stringified tuple,
                        # which should be the display name.
                        # Example: "('Hebrew Standard Value', 'Description', <Language.HEBREW: 'Hebrew'>)"
                        # We want "Hebrew Standard Value"

                        # Find the first quoted string within the parentheses
                        first_quote_start = calc_type_data.find("'")
                        if first_quote_start != -1:
                            first_quote_end = calc_type_data.find(
                                "'", first_quote_start + 1
                            )
                            if first_quote_end != -1:
                                potential_display_name = calc_type_data[
                                    first_quote_start + 1 : first_quote_end
                                ]

                                found_enum_member = None
                                for member in CalculationType:
                                    if member.value[0] == potential_display_name:
                                        found_enum_member = member
                                        break

                                if found_enum_member:
                                    calculation_type_to_assign = found_enum_member
                                    logger.info(
                                        f"Successfully converted old string tuple format '{calc_type_data}' to enum member {found_enum_member.name}"
                                    )
                                else:
                                    logger.warning(
                                        f"Could not find CalculationType member for display name '{potential_display_name}' "
                                        f"extracted from string tuple '{calc_type_data}'. Treating as literal string."
                                    )
                                    calculation_type_to_assign = (
                                        calc_type_data  # Fallback to original string
                                    )
                            else:  # No closing quote for the first element
                                logger.warning(
                                    f"Malformed string tuple (no closing quote for first element) for calc_type_data: '{calc_type_data}'. Treating as literal string."
                                )
                                calculation_type_to_assign = calc_type_data
                        else:  # No opening quote found
                            logger.warning(
                                f"Malformed string tuple (no opening quote for first element) for calc_type_data: '{calc_type_data}'. Treating as literal string."
                            )
                            calculation_type_to_assign = calc_type_data
                    except Exception as e:  # Broad exception for parsing issues
                        logger.error(
                            f"Error parsing string tuple format for calc_type_data: '{calc_type_data}'. Error: {e}. Treating as literal string."
                        )
                        calculation_type_to_assign = calc_type_data
                elif (
                    calc_type_data == "CUSTOM_CIPHER"
                ):  # Handle specific string for custom ciphers
                    calculation_type_to_assign = calc_type_data
                else:
                    # Could be an old custom method name string, or an old format (like "33").
                    logger.warning(
                        f"Could not convert string '{calc_type_data}' to a CalculationType enum member by name, "
                        f"and it does not appear to be a recognized old format. Treating as literal string."
                    )
                    calculation_type_to_assign = calc_type_data
        elif isinstance(calc_type_data, CalculationType):
            # This case should ideally not happen if the database stores basic types like strings.
            # But if it does, use it directly.
            logger.debug(
                f"calculation_type from DB is already a CalculationType instance: {calc_type_data}"
            )
            calculation_type_to_assign = calc_type_data
        else:
            # Fallback for None or other unexpected types from DB (e.g., int if old data)
            logger.error(
                f"Unexpected data type for calculation_type from DB: {type(calc_type_data)} with value '{calc_type_data}'. "
                f"Defaulting to HEBREW_STANDARD_VALUE."
            )
            # Default to a known valid enum or a specific string indicating an error/unknown state.
            calculation_type_to_assign = (
                CalculationType.HEBREW_STANDARD_VALUE
            )  # Or perhaps a dedicated "UNKNOWN_DB_TYPE" string

        # result_value will now be stored as TEXT, so it will come as a string from DB
        result_value_from_db = data.get("result_value")
        if result_value_from_db is None:
            logger.warning("result_value is None from DB, defaulting to '0'")
            result_value_to_assign = "0"
        else:
            result_value_to_assign = str(
                result_value_from_db
            )  # Ensure it is a string for the model

        # Create instance
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            input_text=data.get("input_text", ""),
            calculation_type=calculation_type_to_assign,
            result_value=result_value_to_assign,  # Assign the string value
            notes=data.get("notes"),
            timestamp=timestamp,
            tags=data.get("tags", []),
            favorite=data.get("favorite", False),
            custom_method_name=data.get("custom_method_name"),
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Convert the calculation result to a display-friendly dictionary.

        Returns:
            Dictionary with string keys and values for display in UI
        """
        # Use custom method name if available, otherwise format the calculation type
        if self.custom_method_name:
            method_display = self.custom_method_name
        elif isinstance(self.calculation_type, CalculationType):
            method_display = self.calculation_type.name.replace("_", " ").title()
        else:
            method_display = "Unknown Method"

        return {
            "Input": self.input_text,
            "Method": method_display,
            "Result": str(self.result_value),
            "Time": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Notes": self.notes or "",
            "Tags": ", ".join(self.tags) if self.tags else "",
            "Favorite": "★" if self.favorite else "",
        }
