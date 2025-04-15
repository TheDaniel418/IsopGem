"""
Purpose: Provides a panel for displaying TQ Grid with base numbers and their transformations

This file is part of the tq pillar and serves as a UI component.
It is responsible for visualizing decimal numbers, their ternary representations,
and transformations including conrune and ternary digit reversal.

Key components:
- TQGridPanel: Main panel for the TQ Grid visualization
- TQNumberDisplay: Widget for displaying a number in different formats

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary
- tq.utils.ternary_transition: For applying transformations like conrune
- tq.ui.widgets.ternary_visualizer: For visualizing ternary digits
- tq.ui.panels.number_properties_panel: For displaying detailed number properties
- shared.services.number_properties_service: For analyzing number properties
- tq.services.tq_grid_service: For managing TQ Grid display numbers

Related files:
- tq/ui/tq_tab.py: Main tab that hosts this panel
- tq/ui/widgets/ternary_visualizer.py: Widget for visualizing ternary numbers
- tq/ui/panels/number_properties_panel.py: Panel for displaying number properties
"""


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from shared.services.number_properties_service import NumberPropertiesService
from tq.services.tq_grid_service import TQGridService
from tq.ui.panels.advanced_properties_panel import AdvancedPropertiesPanel
from tq.ui.panels.number_properties_panel import NumberPropertiesPanel
from tq.ui.panels.quadset_analysis_panel import QuadsetAnalysisPanel
from tq.ui.styles.tq_colors import TQColors, apply_tq_styles
from tq.ui.widgets.ternary_visualizer import TernaryDigitVisualizer
from tq.utils.ternary_converter import (
    decimal_to_ternary,
    format_ternary,
    ternary_to_decimal,
)
from tq.utils.ternary_transition import TernaryTransition


class TQNumberDisplay(QFrame):
    """Widget for displaying a number in decimal, ternary, and visualization formats."""

    def __init__(self, label_text: str, color: str = TQColors.PRIMARY, parent=None):
        """Initialize the number display widget.

        Args:
            label_text: The label text for this display
            color: The color to use for the header
            parent: The parent widget
        """
        super().__init__(parent)

        # Set up the layout - minimize margins to maximize visualizer space
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)  # Reduce margins significantly
        self.layout.setSpacing(4)  # Reduce spacing to give more room to visualizer

        # Add label with color - more compact
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))  # Smaller font
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 3px; padding: 3px;"
        )  # Less padding
        self.layout.addWidget(self.label)

        # Info layout for decimal and ternary representation - use horizontal layout to save vertical space
        self.info_layout = QHBoxLayout()
        self.info_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.info_layout.setSpacing(2)  # Minimal spacing

        # Create a more compact info container
        info_container = QFrame()
        info_container.setFrameStyle(QFrame.Shape.NoFrame)  # Remove frame
        info_container.setStyleSheet(
            "background-color: transparent;"
        )  # Make transparent

        info_grid = QGridLayout(info_container)
        info_grid.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        info_grid.setSpacing(2)  # Minimal spacing

        # Decimal display - more compact
        decimal_label = QLabel("Dec:")
        decimal_label.setStyleSheet(
            "font-weight: bold; color: #333; font-size: 10px;"
        )  # Smaller font
        info_grid.addWidget(decimal_label, 0, 0)

        self.decimal_label = QLabel("0")
        self.decimal_label.setFont(QFont("Courier New", 10))  # Smaller font
        self.decimal_label.setStyleSheet(
            "background-color: white; padding: 2px; border-radius: 2px; border: 1px solid #DDD;"
        )  # Less padding
        info_grid.addWidget(self.decimal_label, 0, 1)

        # Ternary display - more compact
        ternary_label = QLabel("Ter:")
        ternary_label.setStyleSheet(
            "font-weight: bold; color: #333; font-size: 10px;"
        )  # Smaller font
        info_grid.addWidget(ternary_label, 1, 0)

        self.ternary_label = QLabel("0")
        self.ternary_label.setFont(QFont("Courier New", 10))  # Smaller font
        self.ternary_label.setStyleSheet(
            "background-color: white; padding: 2px; border-radius: 2px; border: 1px solid #DDD;"
        )  # Less padding
        info_grid.addWidget(self.ternary_label, 1, 1)

        self.info_layout.addWidget(info_container)
        self.layout.addLayout(self.info_layout)

        # Create a scroll area for the visualizer to handle large numbers
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Add ternary visualizer
        self.visualizer = TernaryDigitVisualizer()
        self.visualizer.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )

        # Set minimum height for the visualizer based on typical digit count
        self.visualizer.setMinimumHeight(
            600
        )  # Significantly increase height for visualizations

        # Set the visualizer as the widget in the scroll area
        self.scroll_area.setWidget(self.visualizer)
        self.layout.addWidget(
            self.scroll_area, 1
        )  # Give it a stretch factor of 1 to expand

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

    def _center_scroll_area(self) -> None:
        """Center the scroll area on the visualizer.

        This ensures the ternary digits are visible in the middle of the scroll area.
        """
        # Wait for the visualizer to update its layout
        from PyQt6.QtCore import QTimer

        def do_center():
            # Get the total height of the visualizer
            total_height = self.visualizer.height()
            # Get the visible height of the scroll area
            visible_height = self.scroll_area.viewport().height()

            # Calculate the center position
            center_pos = max(0, (total_height - visible_height) // 2)

            # Set the scroll position to center the content
            self.scroll_area.verticalScrollBar().setValue(center_pos)

        # Use a timer to ensure the layout is updated before centering
        QTimer.singleShot(100, do_center)

    def set_number(self, decimal_value: int, pad_length: int = 6) -> None:
        """Set the number to display.

        Args:
            decimal_value: The decimal value to display
            pad_length: Minimum length to pad the ternary representation
        """
        # Update decimal display
        self.decimal_label.setText(str(decimal_value))

        # Convert to ternary and update display
        ternary_str = decimal_to_ternary(decimal_value)

        # Pad ternary string to at least pad_length
        padded_ternary = format_ternary(ternary_str, pad_length=pad_length)

        # Update ternary display
        self.ternary_label.setText(padded_ternary)

        # Update visualizer
        self.visualizer.set_ternary(padded_ternary)

        # Center the scroll area on the visualizer
        self._center_scroll_area()


class TQGridPanel(QFrame):
    """Panel for displaying the TQ Grid with transformations."""

    def __init__(self, parent=None, standalone=False):
        """Initialize the TQ Grid panel.

        Args:
            parent: The parent widget
            standalone: Whether this panel is running standalone (not in main app)
        """
        super().__init__(parent)

        # Store standalone flag
        self.standalone = standalone

        # Initialize the number properties service
        if NumberPropertiesService._instance is None:
            NumberPropertiesService.get_instance()

        # Apply TQ styling
        apply_tq_styles(self)

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Create title
        title_label = QLabel("TQ Grid Explorer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setProperty("isTitle", "true")
        self.layout.addWidget(title_label)

        # Create input section with styled container
        input_container = QFrame()
        input_container.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        input_container.setStyleSheet(
            f"background-color: {TQColors.PRIMARY_LIGHT}; color: white; border-radius: 6px;"
        )

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 10, 15, 10)

        # Number input with label
        input_label = QLabel("Enter decimal number:")
        input_label.setStyleSheet("color: white; font-weight: bold;")
        input_layout.addWidget(input_label)

        self.number_input = QLineEdit()
        self.number_input.setValidator(
            QIntValidator(0, 999999999)
        )  # Limit to positive integers
        self.number_input.setText("0")
        self.number_input.setMaximumWidth(150)
        self.number_input.setStyleSheet(
            "background-color: white; color: #333; border: none; border-radius: 4px; padding: 8px;"
        )
        input_layout.addWidget(self.number_input)

        # Process button
        self.process_button = QPushButton("Explore")
        self.process_button.clicked.connect(self._process_number)
        self.process_button.setStyleSheet(
            f"background-color: {TQColors.SECONDARY}; color: white; font-weight: bold; "
            f"border: none; border-radius: 4px; padding: 8px 16px;"
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
        self.visualizers_layout.setContentsMargins(
            2, 2, 2, 2
        )  # Minimal margins to maximize visualizer space

        # Create scrollable content area for visualizers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create content widget - minimize margins
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(
            5, 5, 5, 5
        )  # Reduce margins to maximize visualizer space
        self.content_layout.setSpacing(5)  # Reduce spacing

        # Create grid layout for the displays - minimize margins
        self.displays_layout = QGridLayout()
        self.displays_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        self.displays_layout.setHorizontalSpacing(10)  # Reduce horizontal spacing
        self.displays_layout.setVerticalSpacing(10)  # Reduce vertical spacing

        # Create the displays with distinct colors
        self.base_display = TQNumberDisplay("Base Number", TQColors.BASE_NUMBER)
        self.displays_layout.addWidget(self.base_display, 0, 0)

        self.conrune_display = TQNumberDisplay("Conrune", TQColors.CONRUNE)
        self.displays_layout.addWidget(self.conrune_display, 0, 1)

        self.reverse_display = TQNumberDisplay("Ternary Reversal", TQColors.REVERSAL)
        self.displays_layout.addWidget(self.reverse_display, 1, 0)

        self.reverse_conrune_display = TQNumberDisplay(
            "Ternary Reversal Conrune", TQColors.REVERSAL_CONRUNE
        )
        self.displays_layout.addWidget(self.reverse_conrune_display, 1, 1)

        self.content_layout.addLayout(self.displays_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        self.visualizers_layout.addWidget(scroll_area)

        # Create properties panel (second tab)
        self.properties_panel = NumberPropertiesPanel()

        # Create analysis panel (third tab)
        self.analysis_panel = QuadsetAnalysisPanel()

        # Create advanced properties panel (fourth tab)
        self.advanced_panel = AdvancedPropertiesPanel()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.visualizers_container, "Ternary Visualizer")
        self.tab_widget.addTab(self.properties_panel, "Number Properties")
        self.tab_widget.addTab(self.analysis_panel, "Quadset Analysis")
        self.tab_widget.addTab(self.advanced_panel, "Advanced Properties")

        # Add the tab widget to the main layout
        self.layout.addWidget(self.tab_widget, 1)  # Give it stretch

        # Create transition utility
        self.transition = TernaryTransition()

        # Set initial values
        self._process_number()

        # Set frame style - main panel styling is handled by apply_tq_styles
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

    def set_number(self, value: int) -> None:
        """Set the number for analysis.

        Args:
            value: The number to analyze
        """
        self.number_input.setText(str(value))
        self._process_number()

    def _process_number(self) -> None:
        """Process the input number and update all displays."""
        try:
            # Get the decimal value
            try:
                decimal_value = int(self.number_input.text() or "0")
            except ValueError:
                decimal_value = 0

            # Get the ternary representation
            ternary_str = decimal_to_ternary(decimal_value)

            # Auto-determine padding length based on ternary length
            # Always use at least 6 digits padding for consistency
            pad_length = max(6, len(ternary_str))

            # Pad the ternary string
            padded_ternary = format_ternary(ternary_str, pad_length=pad_length)

            # Update base number display
            self.base_display.set_number(decimal_value, pad_length)

            # Calculate and update conrune display
            conrune_ternary = self.transition.apply_conrune(padded_ternary)
            conrune_decimal = ternary_to_decimal(conrune_ternary)
            self.conrune_display.decimal_label.setText(str(conrune_decimal))
            self.conrune_display.ternary_label.setText(conrune_ternary)
            self.conrune_display.visualizer.set_ternary(conrune_ternary)

            # Calculate and update reversed ternary display
            reversed_ternary = padded_ternary[::-1]  # Reverse the string
            reversed_decimal = ternary_to_decimal(reversed_ternary)
            self.reverse_display.decimal_label.setText(str(reversed_decimal))
            self.reverse_display.ternary_label.setText(reversed_ternary)
            self.reverse_display.visualizer.set_ternary(reversed_ternary)

            # Calculate and update reversed conrune display
            reversed_conrune = self.transition.apply_conrune(reversed_ternary)
            reversed_conrune_decimal = ternary_to_decimal(reversed_conrune)
            self.reverse_conrune_display.decimal_label.setText(
                str(reversed_conrune_decimal)
            )
            self.reverse_conrune_display.ternary_label.setText(reversed_conrune)
            self.reverse_conrune_display.visualizer.set_ternary(reversed_conrune)

            # Update the TQGridService with current display values
            grid_service = TQGridService.get_instance()
            grid_service.update_grid_display(
                base=decimal_value,
                conrune=conrune_decimal,
                reversal=reversed_decimal,
                reversal_conrune=reversed_conrune_decimal,
            )

            # Update the number properties panel
            self.properties_panel.set_number(decimal_value)

            # The quadset analysis panel will be updated automatically via the callback

            # Dynamically adjust visualizer minimum heights based on digit count
            digit_height = 80  # Significantly increase height per digit
            min_visualizer_height = max(
                600, pad_length * digit_height
            )  # Ensure minimum height of 600px

            self.base_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.conrune_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.reverse_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.reverse_conrune_display.visualizer.setMinimumHeight(
                min_visualizer_height
            )

            # Center all scroll areas
            self.base_display._center_scroll_area()
            self.conrune_display._center_scroll_area()
            self.reverse_display._center_scroll_area()
            self.reverse_conrune_display._center_scroll_area()

            # Adjust window size if this is a standalone window
            if self.standalone or self.parent() is None:
                # Base height plus space for visualizers - prioritize visualizer space
                header_height = 80  # Space for title, input fields (reduced)
                tab_height = 30  # Space for tab bar (reduced)
                total_height = (
                    header_height + tab_height + (min_visualizer_height * 2) + 50
                )  # Minimal spacing between rows

                # Make sure we have enough width for the visualizers
                min_width = 900  # Minimum width to display the visualizers properly
                current_size = self.size()
                self.resize(max(current_size.width(), min_width), total_height)

                # Switch to the visualizer tab to show the results
                self.tab_widget.setCurrentIndex(0)

        except KeyError as e:
            # Handle transition map errors
            import logging

            logging.error(f"Transition error: {e}")

            # Update displays with error message
            error_message = f"Error: {e}"
            self.conrune_display.decimal_label.setText("Error")
            self.conrune_display.ternary_label.setText(error_message)
            self.reverse_conrune_display.decimal_label.setText("Error")
            self.reverse_conrune_display.ternary_label.setText(error_message)

            # Update service with error values
            grid_service = TQGridService.get_instance()
            grid_service.update_grid_display(
                base=decimal_value, conrune=0, reversal=0, reversal_conrune=0
            )


if __name__ == "__main__":
    """Simple demonstration of the TQ Grid panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = TQGridPanel(standalone=True)
    panel.resize(
        1000, 1400
    )  # Significantly increased height for much taller visualizers
    panel.show()
    sys.exit(app.exec())
