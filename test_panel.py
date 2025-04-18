#!/usr/bin/env python3
"""
Test script for the TernaryDimensionalAnalysisPanel.
"""

import sys
from PyQt6.QtWidgets import QApplication
from tq.ui.panels.ternary_dimension_panel import TernaryDimensionalAnalysisPanel

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TernaryDimensionalAnalysisPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec())
