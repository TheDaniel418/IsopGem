#!/usr/bin/env python3
"""
Final test for abundance/deficiency formatting in the Properties tab.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gematria.ui.widgets.properties_tab_widget import PropertyGroupWidget
from shared.services.number_properties_service import NumberPropertiesService

def test_formatting():
    """Test the formatting of abundance/deficiency values."""
    service = NumberPropertiesService.get_instance()
    
    # Test abundant number (12)
    print("🧪 Testing abundant number 12:")
    props12 = service.get_number_properties(12)
    print(f"  Raw properties: {props12}")
    
    # Create a property group widget to test formatting
    basic_props = {
        "is_abundant": props12.get("is_abundant"),
        "is_deficient": props12.get("is_deficient"),
        "aliquot_sum": props12.get("aliquot_sum"),
        "number": props12.get("number")
    }
    
    group = PropertyGroupWidget("Test", basic_props)
    
    # Test the formatting directly
    formatted_abundant = group._format_value("is_abundant", True, props12)
    formatted_deficient = group._format_value("is_deficient", False, props12)
    
    print(f"  Formatted is_abundant: '{formatted_abundant}'")
    print(f"  Formatted is_deficient: '{formatted_deficient}'")
    
    # Test deficient number (8)
    print("\n🧪 Testing deficient number 8:")
    props8 = service.get_number_properties(8)
    print(f"  Raw properties: {props8}")
    
    formatted_abundant8 = group._format_value("is_abundant", False, props8)
    formatted_deficient8 = group._format_value("is_deficient", True, props8)
    
    print(f"  Formatted is_abundant: '{formatted_abundant8}'")
    print(f"  Formatted is_deficient: '{formatted_deficient8}'")
    
    # Test perfect number (6)
    print("\n🧪 Testing perfect number 6:")
    props6 = service.get_number_properties(6)
    print(f"  Raw properties: {props6}")
    
    formatted_abundant6 = group._format_value("is_abundant", False, props6)
    formatted_deficient6 = group._format_value("is_deficient", False, props6)
    formatted_perfect6 = group._format_value("is_perfect", True, props6)
    
    print(f"  Formatted is_abundant: '{formatted_abundant6}'")
    print(f"  Formatted is_deficient: '{formatted_deficient6}'")
    print(f"  Formatted is_perfect: '{formatted_perfect6}'")
    
    # Verify expected results
    print("\n✅ Expected results:")
    print("  Number 12 should show: 'Yes (abundant by 4)'")
    print("  Number 8 should show: 'Yes (deficient by 7)'")
    print("  Number 6 should show: 'No' for both abundant and deficient")

if __name__ == "__main__":
    test_formatting() 