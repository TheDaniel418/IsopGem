"""Polygon service module.

This module provides services for interacting with polygon calculators.
"""

from typing import Dict, List


class PolygonService:
    """Service for interacting with polygon calculators."""

    _instance = None

    def __new__(cls):
        """Create a singleton instance of the service."""
        if cls._instance is None:
            cls._instance = super(PolygonService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the service."""
        # Dictionary to store registered panels
        # Key: panel_id, Value: (panel_instance, available_fields)
        self.registered_panels: Dict[str, tuple] = {}

    def register_panel(
        self, panel_id: str, panel_instance: object, available_fields: List[str]
    ) -> None:
        """Register a panel with the service.

        Args:
            panel_id: Unique identifier for the panel
            panel_instance: Instance of the panel
            available_fields: List of field names that can receive values
        """
        self.registered_panels[panel_id] = (panel_instance, available_fields)

    def unregister_panel(self, panel_id: str) -> None:
        """Unregister a panel from the service.

        Args:
            panel_id: Unique identifier for the panel
        """
        if panel_id in self.registered_panels:
            del self.registered_panels[panel_id]

    def get_available_panels(self) -> List[str]:
        """Get a list of available panel IDs.

        Returns:
            List of panel IDs
        """
        return list(self.registered_panels.keys())

    def get_available_fields(self, panel_id: str) -> List[str]:
        """Get a list of available fields for a panel.

        Args:
            panel_id: Unique identifier for the panel

        Returns:
            List of field names
        """
        if panel_id in self.registered_panels:
            return self.registered_panels[panel_id][1]
        return []

    def send_value_to_panel(self, panel_id: str, field_name: str, value: float) -> bool:
        """Send a value to a specific field in a panel.

        Args:
            panel_id: Unique identifier for the panel
            field_name: Name of the field to receive the value
            value: Value to send

        Returns:
            True if the value was sent successfully, False otherwise
        """
        print(
            f"Attempting to send value {value} to field {field_name} in panel {panel_id}"
        )
        print(f"Available panels: {self.get_available_panels()}")

        if panel_id in self.registered_panels:
            panel_instance, available_fields = self.registered_panels[panel_id]
            print(f"Panel found. Available fields: {available_fields}")

            if field_name in available_fields:
                print(f"Field {field_name} found in available fields")
                # Call the receive_value method on the panel instance
                if hasattr(panel_instance, "receive_value"):
                    print("Panel has receive_value method, calling it")
                    panel_instance.receive_value(field_name, value)
                    return True
                else:
                    print("Panel does not have receive_value method")
            else:
                print(f"Field {field_name} not found in available fields")
        else:
            print(f"Panel {panel_id} not found in registered panels")

        return False
