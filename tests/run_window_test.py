#!/usr/bin/env python
"""Direct test runner for window implementation.

This is a direct test runner that verifies our window implementation
is using only free-floating windows without depending on pytest.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, project_root)

# Import required modules
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton

# Import the modules we want to test
from shared.ui.window_management import WindowManager, AuxiliaryWindow, PanelWidget


def create_content_widget():
    """Create a simple content widget for testing."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QPushButton("Test Button"))
    return widget


def run_test():
    """Run the test and return success/failure."""
    # Create QApplication
    app = QApplication([])

    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Window Test")

    # Create window manager
    window_manager = WindowManager(main_window)

    # Test 1: Open window creates AuxiliaryWindow
    print("\n🧪 TEST 1: open_window creates AuxiliaryWindow")
    window = window_manager.open_window(
        "test_window", create_content_widget(), "Test Window"
    )

    test1_success = isinstance(window, AuxiliaryWindow)
    test1_panels = len(window_manager._panels) == 0
    test1_windows = "test_window" in window_manager._auxiliary_windows

    # Close the window
    window.close()

    # Clear all windows between tests
    window_manager.close_all_windows()

    # Report test 1 results
    if all([test1_success, test1_panels, test1_windows]):
        print("✅ PASSED: open_window creates AuxiliaryWindow")
    else:
        print("❌ FAILED: open_window creates AuxiliaryWindow")
        print(f"  - Instance type check: {test1_success}")
        print(f"  - No panels created: {test1_panels}")
        print(f"  - Window tracked correctly: {test1_windows}")

    # Test 2: Multiple windows, no panels
    print("\n🧪 TEST 2: Multiple windows create no panels")

    # Make sure we start with no windows
    assert (
        len(window_manager._auxiliary_windows) == 0
    ), "Windows from previous test weren't cleaned up"

    # Create multiple windows
    for i in range(3):
        window_manager.open_window(
            f"test_window_{i}", create_content_widget(), f"Test Window {i}"
        )

    test2_panel_count = len(window_manager._panels)
    test2_window_count = len(window_manager._auxiliary_windows)

    # Close all windows
    window_manager.close_all_windows()

    # Report test 2 results
    if test2_panel_count == 0 and test2_window_count == 3:
        print("✅ PASSED: Multiple windows create no panels")
    else:
        print("❌ FAILED: Multiple windows create no panels")
        print(f"  - Panel count: {test2_panel_count} (expected 0)")
        print(f"  - Window count: {test2_window_count} (expected 3)")

    # Test 3: Overall implementation
    print("\n🧪 TEST 3: Implementation uses only free-floating windows")

    # Make sure we start with no windows
    assert (
        len(window_manager._auxiliary_windows) == 0
    ), "Windows from previous test weren't cleaned up"

    # Open a window again
    window = window_manager.open_window(
        "test_window", create_content_widget(), "Test Window"
    )

    # Check panel count
    test3_panel_count = len(window_manager._panels)
    test3_window_count = len(window_manager._auxiliary_windows)

    # Close all windows
    window_manager.close_all_windows()

    # Report test 3 results
    if test3_panel_count == 0 and test3_window_count == 1:
        print("✅ PASSED: Implementation uses only free-floating windows")
    else:
        print("❌ FAILED: Implementation uses only free-floating windows")
        print(f"  - Panel count: {test3_panel_count} (expected 0)")
        print(f"  - Window count: {test3_window_count} (expected 1)")

    # Final summary
    all_tests_passed = (
        all([test1_success, test1_panels, test1_windows])
        and test2_panel_count == 0
        and test2_window_count == 3
        and test3_panel_count == 0
        and test3_window_count == 1
    )

    print("\n✨ TEST SUMMARY")
    if all_tests_passed:
        print(
            "✅ ALL TESTS PASSED: Application is correctly using only free-floating windows"
        )
    else:
        print(
            "❌ SOME TESTS FAILED: Application may not be correctly configured for free-floating windows only"
        )

    return all_tests_passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
