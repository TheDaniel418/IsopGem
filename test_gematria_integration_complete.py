#!/usr/bin/env python3
"""
Comprehensive test for the complete Number Dictionary integration.

This script tests:
1. Number Dictionary window functionality
2. Search window functionality  
3. Integration with the main Gematria tab
4. Signal connections between components
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from shared.ui.window_management import WindowManager, TabManager
from gematria.ui.gematria_tab import GematriaTab


class TestMainWindow(QMainWindow):
    """Test main window to simulate the full application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IsopGem - Number Dictionary Integration Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create window and tab managers
        self.window_manager = WindowManager(self)
        self.tab_manager = TabManager()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create and add the Gematria tab
        self.gematria_tab = GematriaTab(self.tab_manager, self.window_manager)
        layout.addWidget(self.gematria_tab)
        
        print("✅ Test main window created with Gematria tab")


def test_complete_integration():
    """Test the complete Number Dictionary integration."""
    print("🧪 Testing Complete Number Dictionary Integration...")
    
    app = QApplication(sys.argv)
    
    # Create the test main window
    main_window = TestMainWindow()
    main_window.show()
    
    print("✅ Main window with Gematria tab created successfully!")
    print()
    print("🎯 Integration Test Features Available:")
    print("   📖 Number Dictionary Button - Opens individual number exploration windows")
    print("   🔍 Search Notes Button - Opens search interface for all notes")
    print("   🔗 Cross-linking - Numbers in notes link to other dictionary entries")
    print("   📝 Rich Text Editing - Full RTF support with formatting")
    print("   📊 Properties Display - Mathematical properties with enhanced formatting")
    print("   🎲 Quadset Analysis - Related number navigation")
    print()
    print("💡 Test Instructions:")
    print("   1. Click 'Number Dictionary' to open a number exploration window")
    print("   2. Click 'Search Notes' to open the search interface")
    print("   3. Try entering different numbers in the dictionary")
    print("   4. Create notes and test the search functionality")
    print("   5. Test number linking between notes")
    print("   6. Verify properties display formatting (Yes/No, abundance, prime ordinals)")
    print("   7. Test quadset navigation between related numbers")
    
    # Set up a timer to demonstrate functionality
    def demonstrate_features():
        print("\n🚀 Auto-demonstrating features...")
        
        # Open a Number Dictionary window with number 42
        print("📖 Opening Number Dictionary for number 42...")
        main_window.gematria_tab.open_number_dictionary_with_number(42)
        
        # Schedule opening the search window
        QTimer.singleShot(2000, lambda: demonstrate_search())
    
    def demonstrate_search():
        print("🔍 Opening Number Dictionary search window...")
        main_window.gematria_tab._open_number_dictionary_search()
        
        print("✨ Both windows should now be open!")
        print("   - Number Dictionary window showing number 42")
        print("   - Search window for browsing all notes")
    
    # Start the demonstration after a short delay
    QTimer.singleShot(1000, demonstrate_features)
    
    return app.exec()


if __name__ == "__main__":
    test_complete_integration() 