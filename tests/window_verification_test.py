#!/usr/bin/env python
"""Verification test for window management.

This script runs a simple verification test on the window management system
to ensure it's using only free-floating windows as required.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import PyQt components
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer

# Import project components
from shared.ui.window_management import WindowManager, AuxiliaryWindow


def run_verification_test():
    """Run the verification test and output results."""
    # Create a QApplication instance
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Window Verification Test")
    main_window.resize(400, 200)
    
    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Create window manager
    window_manager = WindowManager(main_window)
    
    # Create test content
    test_widget = QWidget()
    test_layout = QVBoxLayout(test_widget)
    test_layout.addWidget(QLabel("Test Window Content"))
    
    # Open a test window
    window = window_manager.open_window(
        "test_window",
        test_widget,
        "Test Window"
    )
    
    # Display verification results
    result_label = QLabel()
    layout.addWidget(result_label)
    
    # Check the results
    panel_count = len(window_manager._panels)
    window_count = len(window_manager._auxiliary_windows)
    
    if panel_count == 0 and window_count > 0:
        result_label.setText("✅ SUCCESS: Using only free-floating windows as required!")
        print("✅ SUCCESS: Using only free-floating windows as required!")
    else:
        result_label.setText("❌ ISSUE: Found panels when we should only be using free-floating windows.")
        print("❌ ISSUE: Found panels when we should only be using free-floating windows.")
    
    # Show details
    details_label = QLabel(f"Panels: {panel_count}\nWindows: {window_count}")
    layout.addWidget(details_label)
    print(f"Panels: {panel_count}")
    print(f"Windows: {window_count}")
    
    # Show main window
    main_window.show()
    
    # Auto-close after 2 seconds if run in non-interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        QTimer.singleShot(2000, app.quit)
    
    # Run the application
    return app.exec(), window_count > 0 and panel_count == 0


if __name__ == "__main__":
    exit_code, success = run_verification_test()
    if not success:
        sys.exit(1)
    sys.exit(exit_code) 