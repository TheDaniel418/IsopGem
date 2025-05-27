#!/usr/bin/env python3
"""
Test script to verify the Number Dictionary works with TQ Grid properties panel.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow

def test_number_dictionary():
    """Test the Number Dictionary with TQ Grid properties panel."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Number Dictionary with TQ Grid Properties Panel...")
    
    # Test numbers with known properties
    test_numbers = [12, 8, 6, 28]  # abundant, deficient, perfect, perfect
    
    windows = []
    
    for number in test_numbers:
        print(f"\n📊 Creating Number Dictionary window for number {number}")
        
        try:
            window = NumberDictionaryWindow(number)
            window.show()
            windows.append(window)
            
            print(f"✅ Successfully created window for number {number}")
            
        except Exception as e:
            print(f"❌ Error creating window for number {number}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Created {len(windows)} Number Dictionary windows")
    print("📝 Check the Properties tab in each window to verify:")
    print("   - Number 12: Should show abundance amount")
    print("   - Number 8: Should show deficiency amount") 
    print("   - Number 6: Should show as perfect")
    print("   - Number 28: Should show as perfect")
    print("\n💡 The TQ Grid properties panel should handle all formatting correctly!")
    
    # Keep windows open
    if windows:
        app.exec()

if __name__ == "__main__":
    test_number_dictionary() 