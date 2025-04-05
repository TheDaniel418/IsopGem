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

from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import List, Optional, Union, Dict, Any

from gematria.models.calculation_type import CalculationType

@dataclass
class CalculationResult:
    """Represents a gematria calculation result with metadata."""
    
    input_text: str
    calculation_type: Union[CalculationType, str]
    result_value: int
    notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: List[str] = field(default_factory=list)
    favorite: bool = False
    custom_method_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage.
        
        Returns:
            Dictionary representation of the calculation result
        """
        # Handle calculation type (could be enum or string)
        if isinstance(self.calculation_type, CalculationType):
            calc_type_str = str(self.calculation_type.value)
        else:
            calc_type_str = str(self.calculation_type)
            
        # Ensure result_value is an integer
        result_value = 0
        try:
            result_value = int(self.result_value)
        except (ValueError, TypeError):
            # If conversion fails, use 0 as default
            pass
                
        return {
            "id": self.id,
            "input_text": self.input_text,
            "calculation_type": calc_type_str,
            "result_value": result_value,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "favorite": self.favorite,
            "custom_method_name": self.custom_method_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculationResult':
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
            
        # Handle calculation type (convert to enum if possible)
        calc_type_str = data.get("calculation_type", "MISPAR_HECHRACHI")
        try:
            calculation_type = CalculationType(calc_type_str)
        except ValueError:
            # If not a valid enum value, it must be a custom method name
            calculation_type = calc_type_str
            
        # Ensure result_value is an integer
        result_value = data.get("result_value", 0)
        if not isinstance(result_value, int):
            try:
                result_value = int(result_value)
            except (ValueError, TypeError):
                result_value = 0
            
        # Create instance
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            input_text=data.get("input_text", ""),
            calculation_type=calculation_type,
            result_value=result_value,
            notes=data.get("notes"),
            timestamp=timestamp,
            tags=data.get("tags", []),
            favorite=data.get("favorite", False),
            custom_method_name=data.get("custom_method_name")
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
            "Favorite": "★" if self.favorite else ""
        } 