#!/usr/bin/env python3
"""Run script for the Sacred Geometry Explorer.

This script creates and shows the Sacred Geometry Explorer window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from shared.ui.window_management import WindowManager
from geometry.ui.sacred_geometry.explorer import SacredGeometryExplorer

def main():
    """Run the Sacred Geometry Explorer."""
    # Create application
    app = QApplication(sys.argv)

    # Create explorer first (it will be the main window)
    explorer = SacredGeometryExplorer(None)

    # Create window manager with explorer as main window
    window_manager = WindowManager(explorer)

    # Set window manager in explorer
    explorer.window_manager = window_manager

    # Show explorer
    explorer.show()

    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
