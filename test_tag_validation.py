#!/usr/bin/env python3
"""
Test script for tag validation functionality in import dialog.

This script directly tests the tag validation methods.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication

from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog
from gematria.services.calculation_database_service import CalculationDatabaseService


def test_tag_validation():
    """Test the tag validation functionality."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Tag Validation Functionality")
    print("=" * 50)
    
    # Initialize services
    db_service = CalculationDatabaseService()
    
    # Create some test tags
    print("🔧 Setting up test tags...")
    test_tags = ['existing1', 'existing2', 'existing3']
    
    for tag_name in test_tags:
        try:
            tag = db_service.create_tag(name=tag_name, description=f"Test tag: {tag_name}")
            if tag:
                print(f"✅ Created test tag: {tag_name}")
        except Exception as e:
            print(f"⚠️ Tag {tag_name} might already exist: {e}")
    
    # Get all existing tags
    existing_tags = db_service.get_all_tags()
    print(f"\n📊 Total existing tags in database: {len(existing_tags)}")
    print("🏷️ Existing tag names:")
    for tag in existing_tags[:10]:  # Show first 10
        print(f"  - {tag.name}")
    if len(existing_tags) > 10:
        print(f"  ... and {len(existing_tags) - 10} more")
    
    # Create test import data with mixed existing/missing tags
    test_import_data = [
        {"word": "hello", "notes": "greeting", "tags": ["existing1", "missing1"]},
        {"word": "world", "notes": "planet", "tags": ["missing2", "missing3"]},
        {"word": "test", "notes": "testing", "tags": ["existing2"]},
        {"word": "example", "notes": "sample", "tags": ["missing4", "existing3", "missing5"]},
        {"word": "simple", "notes": "basic", "tags": []},  # No tags
    ]
    
    print(f"\n📝 Test import data:")
    for item in test_import_data:
        print(f"  - '{item['word']}' with tags: {item['tags']}")
    
    # Create dialog and test validation
    dialog = ImportWordListDialog()
    
    print(f"\n🔍 Testing tag validation...")
    
    # Test the validation method
    result = dialog._validate_tags_in_import_data(test_import_data)
    
    print(f"📊 Validation result: {result}")
    print(f"🏷️ Missing tags found: {sorted(list(dialog._missing_tags))}")
    
    # Expected missing tags: missing1, missing2, missing3, missing4, missing5
    expected_missing = {"missing1", "missing2", "missing3", "missing4", "missing5"}
    actual_missing = dialog._missing_tags
    
    if expected_missing == actual_missing:
        print("✅ Tag validation working correctly!")
    else:
        print("❌ Tag validation issue detected:")
        print(f"   Expected missing: {sorted(list(expected_missing))}")
        print(f"   Actual missing: {sorted(list(actual_missing))}")
    
    return result


if __name__ == "__main__":
    try:
        test_tag_validation()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 