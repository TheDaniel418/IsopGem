#!/usr/bin/env python3
"""
Final debug script to test PropertyGroupWidget directly.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

from gematria.ui.widgets.properties_tab_widget import PropertyGroupWidget
from shared.services.number_properties_service import NumberPropertiesService


def test_property_group_widget():
    """Test PropertyGroupWidget directly."""
    app = QApplication(sys.argv)

    service = NumberPropertiesService.get_instance()

    # Test abundant number (12)
    print("🧪 Testing PropertyGroupWidget with number 12 (abundant):")
    props12 = service.get_number_properties(12)
    print(f"  Raw properties: {props12}")

    # Create basic properties for testing
    basic_props = {
        "is_abundant": props12.get("is_abundant"),
        "is_deficient": props12.get("is_deficient"),
        "aliquot_sum": props12.get("aliquot_sum"),
        "number": props12.get("number"),
    }

    print(f"  Basic props for widget: {basic_props}")

    # Create the PropertyGroupWidget
    group_widget = PropertyGroupWidget("Basic Properties", basic_props)

    # Test the _format_value method directly
    formatted_abundant = group_widget._format_value("is_abundant", True, props12)
    formatted_deficient = group_widget._format_value("is_deficient", False, props12)

    print("  Direct _format_value test:")
    print(f"    is_abundant: '{formatted_abundant}'")
    print(f"    is_deficient: '{formatted_deficient}'")

    # Show the widget to see what it actually displays
    group_widget.show()

    print("\n✅ PropertyGroupWidget created and shown!")
    print("📝 Check the widget to see if it shows 'Yes (abundant by 4)' for is_abundant")

    # Keep the application running briefly
    app.processEvents()

    return group_widget, app


if __name__ == "__main__":
    widget, app = test_property_group_widget()
    # Don't call app.exec() to avoid blocking
