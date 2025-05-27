#!/usr/bin/env python3
"""
Simple test for abundance/deficiency formatting logic.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.services.number_properties_service import NumberPropertiesService

def format_value_test(key: str, value, all_properties: dict) -> str:
    """Test version of the _format_value method."""
    # Handle boolean values
    if isinstance(value, bool):
        if value:
            # For True values, check if we need to add additional info
            if key == "is_prime" and "prime_ordinal" in all_properties:
                prime_ordinal = all_properties["prime_ordinal"]
                if prime_ordinal is not None:
                    return f"Yes (#{prime_ordinal})"
            
            # Handle abundant/deficient numbers - use 'number' key instead of 'value'
            if key == "is_abundant" and "aliquot_sum" in all_properties and "number" in all_properties:
                aliquot_sum = all_properties["aliquot_sum"]
                number_value = all_properties["number"]
                if aliquot_sum is not None and number_value is not None:
                    abundance = aliquot_sum - number_value
                    return f"Yes (abundant by {abundance})"
            
            if key == "is_deficient" and "aliquot_sum" in all_properties and "number" in all_properties:
                aliquot_sum = all_properties["aliquot_sum"]
                number_value = all_properties["number"]
                if aliquot_sum is not None and number_value is not None:
                    deficiency = number_value - aliquot_sum
                    return f"Yes (deficient by {deficiency})"
            
            return "Yes"
        else:
            return "No"
    
    # Default string conversion
    return str(value)

def test_formatting():
    """Test the formatting of abundance/deficiency values."""
    service = NumberPropertiesService.get_instance()
    
    # Test abundant number (12)
    print("🧪 Testing abundant number 12:")
    props12 = service.get_number_properties(12)
    print(f"  Raw properties: {props12}")
    
    # Test the formatting directly
    formatted_abundant = format_value_test("is_abundant", True, props12)
    formatted_deficient = format_value_test("is_deficient", False, props12)
    
    print(f"  Formatted is_abundant: '{formatted_abundant}'")
    print(f"  Formatted is_deficient: '{formatted_deficient}'")
    
    # Test deficient number (8)
    print("\n🧪 Testing deficient number 8:")
    props8 = service.get_number_properties(8)
    print(f"  Raw properties: {props8}")
    
    formatted_abundant8 = format_value_test("is_abundant", False, props8)
    formatted_deficient8 = format_value_test("is_deficient", True, props8)
    
    print(f"  Formatted is_abundant: '{formatted_abundant8}'")
    print(f"  Formatted is_deficient: '{formatted_deficient8}'")
    
    # Test perfect number (6)
    print("\n🧪 Testing perfect number 6:")
    props6 = service.get_number_properties(6)
    print(f"  Raw properties: {props6}")
    
    formatted_abundant6 = format_value_test("is_abundant", False, props6)
    formatted_deficient6 = format_value_test("is_deficient", False, props6)
    formatted_perfect6 = format_value_test("is_perfect", True, props6)
    
    print(f"  Formatted is_abundant: '{formatted_abundant6}'")
    print(f"  Formatted is_deficient: '{formatted_deficient6}'")
    print(f"  Formatted is_perfect: '{formatted_perfect6}'")
    
    # Verify expected results
    print("\n✅ Expected results:")
    print("  Number 12 should show: 'Yes (abundant by 4)'")
    print("  Number 8 should show: 'Yes (deficient by 7)'")
    print("  Number 6 should show: 'No' for both abundant and deficient")
    
    # Check if results match expectations
    print("\n🎯 Results verification:")
    if formatted_abundant == "Yes (abundant by 4)":
        print("  ✅ Number 12 abundance formatting: CORRECT")
    else:
        print(f"  ❌ Number 12 abundance formatting: WRONG (got '{formatted_abundant}')")
    
    if formatted_deficient8 == "Yes (deficient by 7)":
        print("  ✅ Number 8 deficiency formatting: CORRECT")
    else:
        print(f"  ❌ Number 8 deficiency formatting: WRONG (got '{formatted_deficient8}')")

if __name__ == "__main__":
    test_formatting() 