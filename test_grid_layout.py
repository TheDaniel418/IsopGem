"""
Simplified test script for the TQ Grid panel layout.
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)


class SimpleTQNumberDisplay(QFrame):
    """Simplified version of TQNumberDisplay for testing."""

    def __init__(self, label_text: str, color: str = "#3F51B5", parent=None):
        """Initialize the number display widget."""
        super().__init__(parent)

        # Set up the layout - minimize margins to maximize visualizer space
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        self.layout.setSpacing(4)  # Reduced spacing

        # Add label with color
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 6px;")
        self.layout.addWidget(self.label)

        # Create a scroll area for the visualizer
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Add a placeholder for content - much taller
        content = QLabel("Sample Content")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 4px;")
        content.setMinimumHeight(600)  # Significantly increased height for visualizations

        # Set the content as the widget in the scroll area
        self.scroll_area.setWidget(content)
        self.layout.addWidget(self.scroll_area, 1)  # Give it a stretch factor of 1

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            """
        )


class SimplePropertiesPanel(QFrame):
    """Simplified version of NumberPropertiesPanel for testing."""

    def __init__(self, parent=None):
        """Initialize the properties panel."""
        super().__init__(parent)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Add title
        title = QLabel("Number Properties")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #3F51B5;")
        self.layout.addWidget(title)

        # Add some sample content
        for i in range(5):
            label = QLabel(f"Property {i+1}: Sample Value")
            label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 5px;")
            self.layout.addWidget(label)

        self.layout.addStretch()

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            """
        )


class SimpleAnalysisPanel(QFrame):
    """Simplified version of QuadsetAnalysisPanel for testing."""

    def __init__(self, parent=None):
        """Initialize the analysis panel."""
        super().__init__(parent)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Add title
        title = QLabel("Quadset Analysis")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FF4081;")
        self.layout.addWidget(title)

        # Add some sample content
        for i in range(2):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            frame.setStyleSheet(f"background-color: {'#E8F5E9' if i == 0 else '#FFF8E1'}; border-radius: 6px;")

            frame_layout = QVBoxLayout(frame)

            subtitle = QLabel("Differences" if i == 0 else "Sums")
            subtitle.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(subtitle)

            content = QLabel("Sample Grid Content")
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content.setStyleSheet("background-color: white; padding: 40px; border-radius: 4px;")
            frame_layout.addWidget(content)

            self.layout.addWidget(frame)

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            """
        )


class SimpleTQGridPanel(QFrame):
    """Simplified version of TQGridPanel for testing."""

    def __init__(self, parent=None):
        """Initialize the TQ Grid panel."""
        super().__init__(parent)

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Create title
        title_label = QLabel("TQ Grid Explorer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3F51B5;")
        self.layout.addWidget(title_label)

        # Create input section with styled container
        input_container = QFrame()
        input_container.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        input_container.setStyleSheet("background-color: #7986CB; color: white; border-radius: 6px;")

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 10, 15, 10)

        # Number input with label
        input_label = QLabel("Enter decimal number:")
        input_label.setStyleSheet("color: white; font-weight: bold;")
        input_layout.addWidget(input_label)

        self.number_input = QLineEdit("42")
        self.number_input.setMaximumWidth(150)
        self.number_input.setStyleSheet(
            "background-color: white; color: #333; border: none; border-radius: 4px; padding: 8px;"
        )
        input_layout.addWidget(self.number_input)

        # Process button
        self.process_button = QPushButton("Explore")
        self.process_button.setStyleSheet(
            "background-color: #FF4081; color: white; font-weight: bold; "
            "border: none; border-radius: 4px; padding: 8px 16px;"
        )
        input_layout.addWidget(self.process_button)

        input_layout.addStretch()
        self.layout.addWidget(input_container)

        # Create tab widget for organizing content
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # More modern look
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border: 1px solid #BDBDBD;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #D0D0D0;
            }
            """
        )

        # Create visualizers container (main tab) - minimize margins
        self.visualizers_container = QWidget()
        self.visualizers_layout = QVBoxLayout(self.visualizers_container)
        self.visualizers_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins

        # Create grid layout for the displays - minimize margins
        self.displays_layout = QGridLayout()
        self.displays_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        self.displays_layout.setHorizontalSpacing(10)  # Reduced spacing
        self.displays_layout.setVerticalSpacing(10)  # Reduced spacing

        # Create the displays with distinct colors
        self.base_display = SimpleTQNumberDisplay("Base Number", "#3F51B5")
        self.displays_layout.addWidget(self.base_display, 0, 0)

        self.conrune_display = SimpleTQNumberDisplay("Conrune", "#009688")
        self.displays_layout.addWidget(self.conrune_display, 0, 1)

        self.reverse_display = SimpleTQNumberDisplay("Ternary Reversal", "#FF4081")
        self.displays_layout.addWidget(self.reverse_display, 1, 0)

        self.reverse_conrune_display = SimpleTQNumberDisplay("Ternary Reversal Conrune", "#FF9800")
        self.displays_layout.addWidget(self.reverse_conrune_display, 1, 1)

        self.visualizers_layout.addLayout(self.displays_layout)

        # Create properties panel (second tab)
        self.properties_panel = SimplePropertiesPanel()

        # Create analysis panel (third tab)
        self.analysis_panel = SimpleAnalysisPanel()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.visualizers_container, "Ternary Visualizer")
        self.tab_widget.addTab(self.properties_panel, "Number Properties")
        self.tab_widget.addTab(self.analysis_panel, "Quadset Analysis")

        # Add the tab widget to the main layout
        self.layout.addWidget(self.tab_widget, 1)  # Give it stretch

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            """
        )


class TestWindow(QMainWindow):
    """Test window for the TQ Grid panel."""

    def __init__(self):
        """Initialize the test window."""
        super().__init__()

        # Set window properties
        self.setWindowTitle("TQ Grid Layout Test")
        self.setGeometry(100, 100, 1000, 1400)  # Increased height for taller visualizers

        # Create the TQ Grid panel
        self.grid_panel = SimpleTQGridPanel(self)

        # Set the panel as the central widget
        self.setCentralWidget(self.grid_panel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
