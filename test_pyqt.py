#!/usr/bin/env python3
"""Simple PyQt6 test script to verify that PyQt6 is working correctly."""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create a window
    window = QWidget()
    window.setWindowTitle("PyQt6 Test")
    window.resize(400, 200)
    
    # Create a layout
    layout = QVBoxLayout(window)
    
    # Add a label
    label = QLabel("PyQt6 is working correctly!")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    
    # Show the window
    window.show()
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 