#!/usr/bin/env python3
"""
Test script for search panel tag display functionality.

This script tests the search panel to see how tags are displayed.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.ui.panels.search_panel import SearchPanel


def test_search_panel_tags():
    """Test the search panel tag display functionality."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Search Panel Tag Display")
    print("=" * 50)
    
    # Initialize services
    db_service = CalculationDatabaseService()
    custom_cipher_service = CustomCipherService()
    
    # Create a test window with the search panel
    window = QMainWindow()
    window.setWindowTitle("Search Panel Tag Test")
    window.resize(1000, 600)
    
    # Create the search panel
    search_panel = SearchPanel(db_service, custom_cipher_service)
    
    # Set up the window
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.addWidget(search_panel)
    window.setCentralWidget(central_widget)
    
    # Perform a search to get some results with tags
    print("🔍 Performing search for calculations with tags...")
    
    # Search for calculations that have tags
    search_panel.has_tags.setChecked(True)
    search_panel._perform_search()
    
    # Check the results table
    results_table = search_panel.results_table
    row_count = results_table.rowCount()
    
    print(f"📊 Found {row_count} results")
    
    if row_count > 0:
        print("\n🏷️ Checking tag display in first few rows:")
        
        for row in range(min(5, row_count)):  # Check first 5 rows
            # Get the tags item
            tags_item = results_table.item(row, 3)  # Column 3 is tags
            
            if tags_item:
                # Get the text displayed
                displayed_text = tags_item.text()
                
                # Get the tag data stored for the delegate
                tag_data = tags_item.data(Qt.ItemDataRole.UserRole)
                
                # Get the calculation data
                calc_item = results_table.item(row, 0)
                calc_data = calc_item.data(Qt.ItemDataRole.UserRole) if calc_item else None
                
                print(f"\n  Row {row}:")
                if calc_data:
                    print(f"    Text: {calc_data.input_text[:50]}...")
                    print(f"    Tag IDs: {calc_data.tags}")
                print(f"    Displayed text: '{displayed_text}'")
                print(f"    Tag data for delegate: {tag_data}")
                
                # Check if delegate data is properly formatted
                if isinstance(tag_data, list) and tag_data:
                    print(f"    Tag names from delegate data: {[tag.get('name', 'NO_NAME') for tag in tag_data]}")
                else:
                    print(f"    ⚠️ Tag data is not a list or is empty")
    else:
        print("⚠️ No results found. Let's try a broader search...")
        
        # Try searching for a specific value that we know has tags
        search_panel._clear_search()
        search_panel.exact_value.setText("719")  # From our previous test
        search_panel._perform_search()
        
        row_count = results_table.rowCount()
        print(f"📊 Found {row_count} results for value 719")
        
        if row_count > 0:
            # Check the first result
            tags_item = results_table.item(0, 3)
            if tags_item:
                displayed_text = tags_item.text()
                tag_data = tags_item.data(Qt.ItemDataRole.UserRole)
                print(f"    Displayed text: '{displayed_text}'")
                print(f"    Tag data: {tag_data}")
    
    # Show the window for visual inspection
    print(f"\n👁️ Showing window for visual inspection...")
    window.show()
    
    # Don't run the event loop, just show what we found
    print(f"\n✅ Test completed. Check the displayed window to see tag rendering.")
    
    return app, window


if __name__ == "__main__":
    try:
        app, window = test_search_panel_tags()
        # Keep the window open for inspection
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 