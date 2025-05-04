"""
Minimal test script for the Series Transitions feature.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from tq.ui.widgets.series_transition_widget import SeriesTransitionWidget

def main():
    """Main test function."""
    app = QApplication(sys.argv)
    
    # Create a main window
    window = QMainWindow()
    window.setWindowTitle("Series Transition Test")
    window.resize(800, 600)
    
    # Create the widget
    widget = SeriesTransitionWidget()
    window.setCentralWidget(widget)
    
    # Add some test pairs
    widget.add_number_pair(3, 4)
    widget.add_number_pair(5, 6)
    
    # Show the window
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
