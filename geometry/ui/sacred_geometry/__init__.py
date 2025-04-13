"""Sacred Geometry Explorer module.

This module contains the Sacred Geometry Explorer, a GeoGebra-like environment
for exploring and creating sacred geometry constructions.
"""

from geometry.ui.sacred_geometry.explorer import SacredGeometryExplorer

__all__ = ["SacredGeometryExplorer"]

# Allow running the module directly
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from shared.ui.window_management import WindowManager

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
