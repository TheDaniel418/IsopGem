"""
Simple test script for the TQ Grid panel with the new Quadset Analysis panel.
"""

import sys
from PyQt6.QtWidgets import QApplication

# Import the TQGridPanel directly
from tq.ui.panels.tq_grid_panel import TQGridPanel

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TQGridPanel(standalone=True)
    panel.resize(1400, 800)  # Larger initial size to accommodate all panels
    panel.show()
    sys.exit(app.exec())
