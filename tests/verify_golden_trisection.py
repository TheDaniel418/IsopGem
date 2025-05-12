#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify the Golden Trisection implementation by running the panel directly.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from geometry.ui.panels.golden_trisection_panel import GoldenTrisectionPanel


class TestWindow(QMainWindow):
    """Test window for the Golden Trisection panel."""
    
    def __init__(self):
        """Initialize the test window."""
        super().__init__()
        self.setWindowTitle("Golden Trisection Verification")
        self.resize(900, 700)
        
        # Create and set the central widget
        self.panel = GoldenTrisectionPanel()
        self.setCentralWidget(self.panel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
