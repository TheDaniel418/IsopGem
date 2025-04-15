"""
Test script for the TQ Grid panel layout.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

# Import the TQGridPanel directly
from tq.ui.panels.tq_grid_panel import TQGridPanel

class TestWindow(QMainWindow):
    """Test window for the TQ Grid panel."""
    
    def __init__(self):
        """Initialize the test window."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("TQ Grid Layout Test")
        self.setGeometry(100, 100, 1500, 900)
        
        # Create the TQ Grid panel
        self.grid_panel = TQGridPanel(self)
        
        # Set the panel as the central widget
        self.setCentralWidget(self.grid_panel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
