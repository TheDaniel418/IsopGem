#!/usr/bin/env python3
"""
Test script for the Number Dictionary window.

This script tests the Number Dictionary functionality including:
- Window creation and display
- Note taking and saving
- Number properties display
- Quadset analysis
- Navigation between numbers
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow


def test_number_dictionary():
    """Test the Number Dictionary window."""
    print("🧪 Testing Number Dictionary Window...")
    
    app = QApplication(sys.argv)
    
    # Test with different numbers
    test_numbers = [1, 7, 42, 100, 666]
    
    for i, number in enumerate(test_numbers):
        print(f"📖 Creating Number Dictionary window for number {number}")
        
        window = NumberDictionaryWindow(number)
        window.setWindowTitle(f"Number Dictionary Test {i+1} - {number}")
        window.show()
        
        # Position windows so they don't overlap
        window.move(50 + i * 50, 50 + i * 50)
    
    print("✅ Number Dictionary windows created successfully!")
    print("💡 You can now:")
    print("   - Take notes in the Notes tab")
    print("   - View number properties in the Properties tab")
    print("   - Explore quadset analysis in the Quadset Analysis tab")
    print("   - Navigate between numbers using the navigation buttons")
    print("   - Link numbers together in the notes")
    print("   - Save and load notes")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_number_dictionary()) 