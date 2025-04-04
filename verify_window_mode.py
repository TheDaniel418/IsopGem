#!/usr/bin/env python
"""Tool to verify window handling mode.

This script verifies that we're properly using free-floating windows
instead of dockable panels for primary content.

For correct application behavior, we should see only AuxiliaryWindow
instances, not PanelWidget instances.
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import WindowManager


def create_content_widget(title: str) -> QWidget:
    """Create a content widget for testing.

    Args:
        title: Title for the content

    Returns:
        Content widget
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Add a label
    label = QLabel(f"Content: {title}")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)

    return widget


def check_window_types(window_manager: WindowManager) -> None:
    """Check the types of windows in the manager.

    Args:
        window_manager: Window manager to check
    """
    print("Checking window types...")

    # Check auxiliary windows
    auxiliary_count = len(window_manager._auxiliary_windows)
    panel_count = len(window_manager._panels)

    print(f"Found {auxiliary_count} auxiliary windows and {panel_count} panels")

    if panel_count > 0:
        print("WARNING: Using panels instead of windows!")
    else:
        print("SUCCESS: Only using free-floating windows")


def main() -> None:
    """Run the tool."""
    # Create application
    app = QApplication(sys.argv)

    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Window Mode Verification")
    main_window.resize(640, 480)

    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Create window manager
    window_manager = WindowManager(main_window)

    # Create a function to create the test window
    def create_test_window() -> None:
        """Create a test window without returning it."""
        window_manager.open_window(
            "test_window", create_content_widget("Free-Floating Window"), "Test Window"
        )

    # Add buttons to test window creation
    window_btn = QPushButton("Create Free-Floating Window")
    window_btn.clicked.connect(create_test_window)
    layout.addWidget(window_btn)

    # Button to check window types
    check_btn = QPushButton("Verify Window Implementation")
    check_btn.clicked.connect(lambda: check_window_types(window_manager))
    layout.addWidget(check_btn)

    # Add instructions
    instructions = QLabel(
        "1. Click 'Create Free-Floating Window' to create a window\n"
        "2. Click 'Verify Window Implementation' to check that we're using\n"
        "   only free-floating windows (no panels)"
    )
    layout.addWidget(instructions)

    # Show main window
    main_window.show()

    # Auto-create a window and verify on startup
    window_manager.open_window(
        "auto_test_window",
        create_content_widget("Auto-Created Window"),
        "Auto-Created Window",
    )
    check_window_types(window_manager)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
