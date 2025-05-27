#!/usr/bin/env python3
"""
Test to verify Properties tab displays abundance/deficiency amounts correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow

def test_properties_display():
    """Test that the Properties tab displays abundance/deficiency correctly."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Properties tab display...")
    
    # Test abundant number (12)
    print("\n📊 Testing Number Dictionary window for number 12 (abundant)...")
    window12 = NumberDictionaryWindow(12)
    
    # Get the properties tab
    properties_tab = window12.properties_tab
    
    # Load the number to populate the properties
    properties_tab.load_number(12)
    
    # Check if the properties are displayed correctly
    print("✅ Number 12 window created and properties loaded")
    print("   Check the Properties tab for 'Yes (abundant by 4)' in the is_abundant field")
    
    # Test deficient number (8)
    print("\n📊 Testing Number Dictionary window for number 8 (deficient)...")
    window8 = NumberDictionaryWindow(8)
    
    # Get the properties tab
    properties_tab8 = window8.properties_tab
    
    # Load the number to populate the properties
    properties_tab8.load_number(8)
    
    print("✅ Number 8 window created and properties loaded")
    print("   Check the Properties tab for 'Yes (deficient by 1)' in the is_deficient field")
    
    # Test perfect number (6)
    print("\n📊 Testing Number Dictionary window for number 6 (perfect)...")
    window6 = NumberDictionaryWindow(6)
    
    # Get the properties tab
    properties_tab6 = window6.properties_tab
    
    # Load the number to populate the properties
    properties_tab6.load_number(6)
    
    print("✅ Number 6 window created and properties loaded")
    print("   Check the Properties tab for 'No' in both is_abundant and is_deficient fields")
    print("   Should show 'Yes' for is_perfect field")
    
    # Show all windows
    window12.show()
    window8.show()
    window6.show()
    
    print("\n🎯 All windows are now open!")
    print("📝 Please check the Properties tab in each window to verify:")
    print("   - Number 12: is_abundant should show 'Yes (abundant by 4)'")
    print("   - Number 8: is_deficient should show 'Yes (deficient by 1)'")
    print("   - Number 6: both should show 'No', is_perfect should show 'Yes'")
    
    # Keep the application running
    app.exec()

if __name__ == "__main__":
    test_properties_display() 