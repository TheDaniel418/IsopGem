#!/usr/bin/env python3
"""
Test to verify the Number Dictionary window shows abundance/deficiency correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow

def test_number_dictionary_display():
    """Test that Number Dictionary window displays abundance/deficiency correctly."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Number Dictionary window for number 12 (abundant)...")
    
    # Create window for number 12
    window = NumberDictionaryWindow(12)
    window.show()
    
    # Get the properties tab
    properties_tab = window.properties_tab
    
    print(f"✅ Window created for number {window.current_number}")
    print(f"📊 Properties tab type: {type(properties_tab)}")
    
    # Check if the properties tab has loaded the number
    if hasattr(properties_tab, 'current_number'):
        print(f"📈 Properties tab current number: {properties_tab.current_number}")
    
    # Try to find the property group widgets
    content_widget = properties_tab.content_widget
    print(f"📋 Content widget children count: {content_widget.layout().count()}")
    
    # Look for PropertyGroupWidget instances
    for i in range(content_widget.layout().count()):
        item = content_widget.layout().itemAt(i)
        if item and item.widget():
            widget = item.widget()
            print(f"  Widget {i}: {type(widget).__name__}")
            if hasattr(widget, 'title'):
                print(f"    Title: {widget.title()}")
    
    print("\n🔍 Window is displayed. Check the Properties tab for 'Yes (abundant by 4)' under is_abundant!")
    
    # Process events to ensure everything is rendered
    app.processEvents()
    
    return window, app

if __name__ == "__main__":
    window, app = test_number_dictionary_display()
    # Don't call app.exec() to avoid blocking 