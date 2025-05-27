#!/usr/bin/env python3
"""
Test to verify enhanced tag display with abundance/deficiency amounts.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gematria.ui.widgets.properties_tab_widget import PropertyGroupWidget
from shared.services.number_properties_service import NumberPropertiesService

def test_enhanced_display():
    """Test that abundance/deficiency amounts are displayed correctly."""
    app = QApplication(sys.argv)
    
    service = NumberPropertiesService.get_instance()
    
    print("🧪 Testing enhanced abundance/deficiency display...")
    
    # Test abundant number (12)
    print("\n📊 Testing number 12 (abundant):")
    props12 = service.get_number_properties(12)
    print(f"  Raw properties: {props12}")
    
    # Create Basic Properties group with the required keys
    basic_props = {
        "number": props12.get("number"),
        "is_abundant": props12.get("is_abundant"),
        "is_deficient": props12.get("is_deficient"),
        "aliquot_sum": props12.get("aliquot_sum")
    }
    
    print(f"  Basic properties for group: {basic_props}")
    
    # Create PropertyGroupWidget
    group_widget = PropertyGroupWidget("Basic Properties", basic_props)
    
    # Test the formatting directly
    formatted_abundant = group_widget._format_value("is_abundant", True, basic_props)
    formatted_deficient = group_widget._format_value("is_deficient", False, basic_props)
    
    print(f"  Formatted results:")
    print(f"    is_abundant: '{formatted_abundant}'")
    print(f"    is_deficient: '{formatted_deficient}'")
    
    # Test deficient number (8)
    print("\n📊 Testing number 8 (deficient):")
    props8 = service.get_number_properties(8)
    print(f"  Raw properties: {props8}")
    
    basic_props8 = {
        "number": props8.get("number"),
        "is_abundant": props8.get("is_abundant"),
        "is_deficient": props8.get("is_deficient"),
        "aliquot_sum": props8.get("aliquot_sum")
    }
    
    group_widget8 = PropertyGroupWidget("Basic Properties", basic_props8)
    formatted_abundant8 = group_widget8._format_value("is_abundant", False, basic_props8)
    formatted_deficient8 = group_widget8._format_value("is_deficient", True, basic_props8)
    
    print(f"  Formatted results:")
    print(f"    is_abundant: '{formatted_abundant8}'")
    print(f"    is_deficient: '{formatted_deficient8}'")
    
    # Show the widgets
    group_widget.show()
    group_widget8.show()
    
    print("\n✅ Enhanced display test completed!")
    print("🔍 Check the widgets to see the abundance/deficiency amounts!")
    
    app.processEvents()
    
    return group_widget, group_widget8, app

if __name__ == "__main__":
    widget1, widget2, app = test_enhanced_display()
    # Don't call app.exec() to avoid blocking 