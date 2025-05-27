#!/usr/bin/env python3
"""
Test script for multiple tag display in search panel.

This script tests how calculations with multiple tags are displayed.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication

from gematria.services.calculation_database_service import CalculationDatabaseService


def test_multiple_tags():
    """Test calculations with multiple tags."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Multiple Tag Display")
    print("=" * 50)
    
    # Initialize services
    db_service = CalculationDatabaseService()
    
    # Get all calculations with tags
    print("🔍 Looking for calculations with multiple tags...")
    
    # Search for calculations with tags
    criteria = {"has_tags": True}
    calculations = db_service.search_calculations(criteria)
    
    print(f"📊 Found {len(calculations)} calculations with tags")
    
    # Look for calculations with multiple tags
    multi_tag_calcs = []
    for calc in calculations:
        if len(calc.tags) > 1:
            multi_tag_calcs.append(calc)
    
    print(f"🏷️ Found {len(multi_tag_calcs)} calculations with multiple tags")
    
    if multi_tag_calcs:
        print("\n📋 Calculations with multiple tags:")
        for i, calc in enumerate(multi_tag_calcs[:5]):  # Show first 5
            print(f"\n  Calculation {i+1}:")
            print(f"    Text: {calc.input_text[:50]}...")
            print(f"    Value: {calc.result_value}")
            print(f"    Tag IDs: {calc.tags}")
            
            # Get tag details
            tag_details = []
            for tag_id in calc.tags:
                tag = db_service.get_tag(tag_id)
                if tag:
                    tag_details.append(f"{tag.name} ({tag.color})")
                else:
                    tag_details.append(f"Unknown tag ({tag_id})")
            
            print(f"    Tag details: {', '.join(tag_details)}")
            
            # Test how this would be displayed in the delegate
            tag_data = []
            for tag_id in calc.tags:
                tag = db_service.get_tag(tag_id)
                if tag:
                    tag_data.append({
                        'id': tag.id,
                        'name': tag.name,
                        'color': tag.color
                    })
            
            print(f"    Delegate data: {tag_data}")
            
            # Simulate what the delegate would display
            if len(tag_data) == 1:
                display_text = tag_data[0]['name']
            elif len(tag_data) > 1:
                # This might be where the "..." comes from
                display_text = f"{tag_data[0]['name']}..."  # Truncated display
            else:
                display_text = ""
            
            print(f"    Simulated display: '{display_text}'")
    else:
        print("⚠️ No calculations with multiple tags found.")
        
        # Let's create a test calculation with multiple tags
        print("\n🔧 Creating test calculation with multiple tags...")
        
        # Get available tags
        all_tags = db_service.get_all_tags()
        if len(all_tags) >= 2:
            # Create a test calculation
            from gematria.models.calculation import Calculation
            from gematria.models.calculation_type import Language
            
            test_calc = Calculation(
                input_text="Test Multiple Tags",
                result_value=999,
                calculation_type=("English Tq Standard Value", "Test", Language.ENGLISH),
                tags=[all_tags[0].id, all_tags[1].id]  # Use first two tags
            )
            
            # Save it
            saved_calc = db_service.save_calculation(test_calc)
            print(f"✅ Created test calculation with tags: {[tag.name for tag in all_tags[:2]]}")
            
            # Test the display
            tag_data = []
            for tag_id in saved_calc.tags:
                tag = db_service.get_tag(tag_id)
                if tag:
                    tag_data.append({
                        'id': tag.id,
                        'name': tag.name,
                        'color': tag.color
                    })
            
            print(f"    Tag data: {tag_data}")
            
            # Clean up - delete the test calculation
            db_service.delete_calculation(saved_calc.id)
            print("🧹 Cleaned up test calculation")
        else:
            print("⚠️ Not enough tags available to create test")


if __name__ == "__main__":
    try:
        test_multiple_tags()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 