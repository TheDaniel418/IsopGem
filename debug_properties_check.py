#!/usr/bin/env python3
"""
Debug script to check what properties are returned by NumberPropertiesService.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.services.number_properties_service import NumberPropertiesService


def main():
    service = NumberPropertiesService.get_instance()

    # Test with number 12 (abundant)
    print("Properties for 12 (abundant):")
    props = service.get_number_properties(12)
    for key, value in sorted(props.items()):
        print(f"  {key}: {value}")

    print()
    print("Keys that contain 'number' or 'value':")
    relevant_keys = [
        k for k in props.keys() if "number" in k.lower() or "value" in k.lower()
    ]
    for key in relevant_keys:
        print(f"  {key}: {props[key]}")

    print()
    print("Abundance calculation check:")
    if "aliquot_sum" in props and "value" in props:
        aliquot_sum = props["aliquot_sum"]
        number_value = props["value"]
        print(f"  Number: {number_value}")
        print(f"  Aliquot sum: {aliquot_sum}")
        print(f"  Abundance: {aliquot_sum - number_value}")

    print()
    # Test with number 8 (deficient)
    print("Properties for 8 (deficient):")
    props8 = service.get_number_properties(8)
    if "aliquot_sum" in props8 and "value" in props8:
        aliquot_sum = props8["aliquot_sum"]
        number_value = props8["value"]
        print(f"  Number: {number_value}")
        print(f"  Aliquot sum: {aliquot_sum}")
        print(f"  Deficiency: {number_value - aliquot_sum}")


if __name__ == "__main__":
    main()
