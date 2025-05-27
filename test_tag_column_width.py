#!/usr/bin/env python3
"""
Test script for tag column width and display in search panel.

This script tests the tag column display to see if width is causing the "..." issue.
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


def test_tag_column_width():
    """Test the tag column width and display."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Tag Column Width and Display")
    print("=" * 50)
    
    # Initialize services
    db_service = CalculationDatabaseService()
    cipher_service = CustomCipherService()
    
    # Create search panel
    search_panel = SearchPanel(db_service, cipher_service)
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("Tag Column Width Test")
    window.setCentralWidget(search_panel)
    window.resize(1000, 600)  # Make it wide enough
    
    # Perform a search to get results with tags
    print("🔍 Performing search for calculations with tags...")
    
    # Set up search criteria for calculations with tags
    search_panel.has_tags.setChecked(True)
    search_panel._perform_search()
    
    # Check the results table
    results_table = search_panel.results_table
    row_count = results_table.rowCount()
    
    print(f"📊 Found {row_count} results")
    
    if row_count > 0:
        # Check column widths
        print("\n📏 Column widths:")
        for col in range(results_table.columnCount()):
            width = results_table.columnWidth(col)
            header = results_table.horizontalHeaderItem(col).text()
            print(f"  {header}: {width}px")
        
        # Check tag data in first few rows
        print("\n🏷️ Tag data in first 3 rows:")
        for row in range(min(3, row_count)):
            text_item = results_table.item(row, 0)
            tags_item = results_table.item(row, 3)  # Tags column
            
            if text_item and tags_item:
                text = text_item.text()[:30] + "..." if len(text_item.text()) > 30 else text_item.text()
                
                # Get tag data from UserRole
                tag_data = tags_item.data(Qt.ItemDataRole.UserRole)
                display_text = tags_item.text()
                
                print(f"  Row {row + 1}: '{text}'")
                print(f"    Display text: '{display_text}'")
                print(f"    Tag data: {tag_data}")
                
                if tag_data and isinstance(tag_data, list):
                    print(f"    Tag count: {len(tag_data)}")
                    for i, tag in enumerate(tag_data):
                        if isinstance(tag, dict):
                            print(f"      Tag {i+1}: {tag.get('name', 'No name')} ({tag.get('color', 'No color')})")
        
        # Adjust column widths to see if that helps
        print("\n🔧 Adjusting column widths...")
        results_table.setColumnWidth(3, 200)  # Make tags column wider
        
        print("✅ Tag column width set to 200px")
        print("💡 If you see '...' in the tag column, it might be due to:")
        print("   1. Column width too narrow")
        print("   2. Multiple tags not fitting in the space")
        print("   3. Font size too large for the cell height")
        
        # Show the window for visual inspection
        window.show()
        print("\n👀 Window displayed for visual inspection")
        print("   Check if tags are now visible properly")
        
        # Run for a short time to allow visual inspection
        import time
        app.processEvents()
        time.sleep(2)
        app.processEvents()
        
    else:
        print("⚠️ No results found with tags")
    
    print("\n✅ Test completed")


if __name__ == "__main__":
    try:
        test_tag_column_width()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 