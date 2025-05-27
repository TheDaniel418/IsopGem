#!/usr/bin/env python3
"""
Test script for debugging tag display in search panel.

This script tests the tag display functionality to see why tags show as "..." instead of names.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication

from gematria.services.calculation_database_service import CalculationDatabaseService


def test_tag_display():
    """Test the tag display functionality."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Tag Display Functionality")
    print("=" * 50)
    
    # Initialize services
    db_service = CalculationDatabaseService()
    
    # Get some calculations with tags
    print("🔍 Looking for calculations with tags...")
    all_calculations = db_service.get_all_calculations()
    
    calculations_with_tags = [calc for calc in all_calculations if calc.tags]
    
    print(f"📊 Found {len(calculations_with_tags)} calculations with tags out of {len(all_calculations)} total")
    
    if not calculations_with_tags:
        print("⚠️ No calculations with tags found. Creating a test calculation with tags...")
        
        # Get available tags
        all_tags = db_service.get_all_tags()
        if not all_tags:
            print("📝 Creating test tags...")
            tag1 = db_service.create_tag("test-tag-1", "#ff0000", "Test tag 1")
            tag2 = db_service.create_tag("test-tag-2", "#00ff00", "Test tag 2")
            all_tags = [tag1, tag2]
        
        # Create a test calculation (this would normally be done through the gematria service)
        from gematria.models.calculation_result import CalculationResult
        from gematria.models.calculation_type import CalculationType
        from datetime import datetime
        
        test_calc = CalculationResult(
            input_text="test word",
            result_value=123,
            calculation_type=CalculationType.HEBREW_STANDARD_VALUE,
            timestamp=datetime.now(),
            tags=[all_tags[0].id] if all_tags else []
        )
        
        if db_service.save_calculation(test_calc):
            print(f"✅ Created test calculation with tag: {all_tags[0].name if all_tags else 'none'}")
            calculations_with_tags = [test_calc]
        else:
            print("❌ Failed to create test calculation")
            return
    
    # Test tag retrieval for the first calculation with tags
    test_calc = calculations_with_tags[0]
    print(f"\n🔬 Testing tag retrieval for calculation: '{test_calc.input_text}'")
    print(f"📋 Calculation has tag IDs: {test_calc.tags}")
    
    # Test getting each tag
    for tag_id in test_calc.tags:
        print(f"\n🏷️ Testing tag ID: {tag_id}")
        tag = db_service.get_tag(tag_id)
        
        if tag:
            print(f"✅ Successfully retrieved tag:")
            print(f"   - Name: {tag.name}")
            print(f"   - Color: {tag.color}")
            print(f"   - ID: {tag.id}")
            print(f"   - Description: {tag.description}")
        else:
            print(f"❌ Failed to retrieve tag with ID: {tag_id}")
    
    # Test the tag display logic from search panel
    print(f"\n🎨 Testing tag display logic...")
    tag_display_list = []
    
    try:
        for tag_id in test_calc.tags:
            tag = db_service.get_tag(tag_id)
            if tag:
                tag_display_list.append({
                    "name": tag.name,
                    "color": tag.color,
                    "id": tag.id
                })
        
        print(f"📝 Tag display list: {tag_display_list}")
        
        if tag_display_list:
            tag_names = [tag["name"] for tag in tag_display_list]
            plain_text = ", ".join(tag_names)
            print(f"📄 Plain text representation: '{plain_text}'")
        else:
            print("⚠️ No tags in display list")
            
    except Exception as e:
        print(f"❌ Error in tag display logic: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        test_tag_display()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 