#!/usr/bin/env python3
"""
Test script for enhanced import functionality with tag validation and creation.

This script tests the new tag validation workflow in the import dialog.
"""

import sys
import tempfile
import csv
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.models.calculation_type import Language


def create_test_csv_with_tags():
    """Create a test CSV file with some existing and some missing tags."""
    # Create a temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    
    # Write test data with mixed existing/missing tags
    writer = csv.writer(temp_file)
    writer.writerow(['Word', 'Notes', 'Tags'])  # Header
    writer.writerow(['hello', 'greeting word', 'greetings;common'])  # Assume 'greetings' exists, 'common' doesn't
    writer.writerow(['world', 'planet earth', 'places;geography'])  # Assume both don't exist
    writer.writerow(['test', 'testing word', 'testing'])  # Assume doesn't exist
    writer.writerow(['example', 'sample word', ''])  # No tags
    
    temp_file.close()
    return temp_file.name


def setup_test_tags():
    """Set up some existing tags for testing."""
    db_service = CalculationDatabaseService()
    
    # Create a few test tags
    existing_tags = ['greetings', 'sample', 'basic']
    
    for tag_name in existing_tags:
        try:
            tag = db_service.create_tag(name=tag_name, description=f"Test tag: {tag_name}")
            if tag:
                print(f"✅ Created test tag: {tag_name}")
            else:
                print(f"⚠️ Tag {tag_name} might already exist")
        except Exception as e:
            print(f"⚠️ Could not create tag {tag_name}: {e}")


def test_import_dialog():
    """Test the import dialog with tag validation."""
    app = QApplication(sys.argv)
    
    print("🔧 Setting up test environment...")
    
    # Set up some existing tags
    setup_test_tags()
    
    # Create test CSV file
    csv_file = create_test_csv_with_tags()
    print(f"📄 Created test CSV file: {csv_file}")
    
    print("\n🚀 Opening import dialog...")
    print("📋 Instructions:")
    print("1. Select 'From File' option")
    print("2. Browse and select the test CSV file")
    print("3. You should see a 'Missing Tags Detected' dialog")
    print("4. Test the different options:")
    print("   - 'Create All Missing Tags' - creates all missing tags automatically")
    print("   - 'Create Tags Selectively' - lets you choose which tags to create")
    print("   - 'Continue Without Tags' - proceeds without creating missing tags")
    print("   - 'Cancel Import' - cancels the entire import")
    print("\n🏷️ Expected missing tags: common, places, geography, testing")
    print("🏷️ Expected existing tags: greetings")
    
    # Create and show the dialog
    dialog = ImportWordListDialog()
    
    def on_import_complete(items, language, count):
        print(f"\n✅ Import completed!")
        print(f"📊 Items: {count}")
        print(f"🌐 Language: {language.value}")
        print("📝 Sample items:")
        for i, item in enumerate(items[:3]):  # Show first 3 items
            print(f"  {i+1}. Word: '{item['word']}', Notes: '{item.get('notes', 'None')}', Tags: {item.get('tags', [])}")
    
    dialog.import_complete.connect(on_import_complete)
    
    # Show the dialog
    dialog.show()
    dialog.raise_()
    
    # Set the file path for convenience (user can still browse)
    dialog._file_path_label.setText(csv_file)
    
    print(f"\n📁 Test file path set to: {csv_file}")
    print("🔄 Click 'Load from Source' to load the test data")
    
    # Run the application
    result = app.exec()
    
    # Clean up
    try:
        Path(csv_file).unlink()
        print(f"🧹 Cleaned up test file: {csv_file}")
    except Exception as e:
        print(f"⚠️ Could not clean up test file: {e}")
    
    return result


if __name__ == "__main__":
    print("🧪 Testing Enhanced Import Functionality")
    print("=" * 50)
    
    try:
        test_import_dialog()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 