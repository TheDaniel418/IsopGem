"""
Purpose: Provides visualization widgets for ternary numbers in the TQ system

This file is part of the tq pillar and serves as a UI component.
It is responsible for rendering ternary numbers as visual representations
using digit images with the least significant digit at the bottom.

Key components:
- TernaryDigitVisualizer: Widget for displaying ternary numbers using PNG images
- TernaryVisualizerPanel: Container for the visualizer with input controls

Dependencies:
- tq.utils.ternary_converter: For validating and manipulating ternary numbers
- tq.utils.ternary_transition: For applying transformations to ternary numbers

Related files:
- tq/ui/tq_tab.py: Main tab that hosts these visualization widgets
- tq/utils/ternary_converter.py: Utilities for working with ternary numbers
- tq/utils/ternary_transition.py: Transformation utilities for ternary numbers
"""

import os
from typing import List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QScrollArea, QSizePolicy, QFrame, QFileDialog,
    QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt6.QtCore import Qt, QSize

from tq.utils.ternary_converter import decimal_to_ternary
from tq.utils.ternary_transition import TernaryTransition


class TernaryDigitVisualizer(QWidget):
    """
    Widget for visualizing a ternary number using PNG images.
    
    Displays the ternary digits with the least significant digit at the bottom
    and the most significant digit at the top.
    """
    
    def __init__(self, parent=None):
        """Initialize the visualizer widget."""
        super().__init__(parent)
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(5)
        
        # Load digit images directly without inversion
        self.digit_images = {}
        for digit in ['0', '1', '2']:
            pixmap = QPixmap(os.path.join('assets', 'ternary_digit', f'{digit}_optimized.png'))
            self.digit_images[digit] = pixmap
        
        # Container for digit labels
        self.digit_labels: List[QLabel] = []
        
        # Set initial ternary value
        self.set_ternary("0")
        
        # Set widget background to white
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    def set_ternary(self, ternary_str: str) -> None:
        """
        Set the ternary number to display.
        
        Args:
            ternary_str: A valid ternary string
        """
        # Validate input
        if not all(digit in '012' for digit in ternary_str):
            raise ValueError(f"Invalid ternary string: {ternary_str}")
        
        # Clear existing digit labels
        self._clear_digits()
        
        # Create labels for each digit, from least significant (bottom) to most significant (top)
        for digit in ternary_str:
            label = QLabel()
            label.setPixmap(self.digit_images[digit])
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("QLabel { border: none; background: transparent; }")  # Remove any borders
            label.setFrameStyle(0)  # Remove frame
            label.setMargin(0)  # Remove margin
            self.layout.addWidget(label)
            self.digit_labels.append(label)
    
    def set_decimal(self, decimal_value: int) -> None:
        """
        Set the ternary display from a decimal number.
        
        Args:
            decimal_value: Decimal integer to convert and display
        """
        ternary_str = decimal_to_ternary(decimal_value)
        self.set_ternary(ternary_str)
    
    def _clear_digits(self) -> None:
        """Remove all digit labels from the layout."""
        for label in self.digit_labels:
            self.layout.removeWidget(label)
            label.deleteLater()
        self.digit_labels.clear()
    
    def export_to_png(self, filepath: str) -> bool:
        """
        Export the current visualization to a PNG file with transparency.
        
        Args:
            filepath: Path where to save the PNG file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Create a transparent image
            total_height = sum(label.height() for label in self.digit_labels)
            max_width = max(label.width() for label in self.digit_labels)
            
            image = QImage(max_width, total_height, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            
            # Create painter
            painter = QPainter(image)
            
            # Draw each digit
            y_offset = 0
            for label in reversed(self.digit_labels):  # Reverse to draw from top to bottom
                pixmap = label.pixmap()
                x = (max_width - pixmap.width()) // 2  # Center horizontally
                painter.drawPixmap(x, y_offset, pixmap)
                y_offset += pixmap.height()
            
            painter.end()
            
            # Save the image
            return image.save(filepath, "PNG")
            
        except Exception as e:
            print(f"Error exporting PNG: {e}")
            return False


class TernaryVisualizerPanel(QFrame):
    """
    Panel for visualizing and transforming ternary numbers.
    
    Includes inputs for ternary number entry and buttons for transformations.
    """
    
    def __init__(self, parent=None):
        """Initialize the visualizer panel."""
        super().__init__(parent)
        
        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create title
        title_label = QLabel("Ternary Digit Visualizer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Create input type selection
        input_type_layout = QHBoxLayout()
        self.input_type_group = QButtonGroup(self)
        
        self.ternary_radio = QRadioButton("Ternary")
        self.decimal_radio = QRadioButton("Decimal")
        self.input_type_group.addButton(self.ternary_radio)
        self.input_type_group.addButton(self.decimal_radio)
        
        input_type_layout.addWidget(self.ternary_radio)
        input_type_layout.addWidget(self.decimal_radio)
        main_layout.addLayout(input_type_layout)
        
        # Set default selection
        self.ternary_radio.setChecked(True)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        # Number input
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter number")
        self.number_input.textChanged.connect(self._validate_input)
        
        # Display button
        self.display_button = QPushButton("Display")
        self.display_button.clicked.connect(self._update_visualization)
        
        # Export button
        self.export_button = QPushButton("Export PNG")
        self.export_button.clicked.connect(self._export_visualization)
        
        input_layout.addWidget(QLabel("Number:"))
        input_layout.addWidget(self.number_input)
        input_layout.addWidget(self.display_button)
        input_layout.addWidget(self.export_button)
        
        main_layout.addLayout(input_layout)
        
        # Add transformation buttons
        transform_layout = QHBoxLayout()
        
        self.conrune_button = QPushButton("Apply Conrune")
        self.conrune_button.clicked.connect(self._apply_conrune)
        
        transform_layout.addWidget(self.conrune_button)
        main_layout.addLayout(transform_layout)
        
        # Create scroll area for the visualizer
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                background-color: white;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
            }
        """)
        
        # Create the visualizer widget
        self.visualizer = TernaryDigitVisualizer()
        scroll_area.setWidget(self.visualizer)
        
        main_layout.addWidget(scroll_area)
        
        # Create the ternary transition utility
        self.transition = TernaryTransition()
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border-radius: 5px;
            }
        """)
        
        # Set initial value
        self.number_input.setText("210")
    
    def _validate_input(self) -> None:
        """Validate the input based on selected input type."""
        text = self.number_input.text()
        valid = False
        
        if self.ternary_radio.isChecked():
            valid = all(digit in '012' for digit in text) if text else True
        else:  # Decimal mode
            try:
                if text:
                    int(text)
                valid = True
            except ValueError:
                valid = False
        
        if valid:
            self.number_input.setStyleSheet("")
            self.display_button.setEnabled(True)
        else:
            self.number_input.setStyleSheet("background-color: #ffdddd;")
            self.display_button.setEnabled(False)
    
    def _update_visualization(self) -> None:
        """Update the visualizer with the current input value."""
        text = self.number_input.text()
        if not text:
            return
            
        try:
            if self.ternary_radio.isChecked():
                if all(digit in '012' for digit in text):
                    self.visualizer.set_ternary(text)
            else:  # Decimal mode
                decimal_value = int(text)
                self.visualizer.set_decimal(decimal_value)
        except (ValueError, Exception) as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")
    
    def _export_visualization(self) -> None:
        """Export the current visualization as a PNG file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Visualization",
            str(Path.home()),
            "PNG Images (*.png)"
        )
        
        if filepath:
            if not filepath.lower().endswith('.png'):
                filepath += '.png'
            
            if self.visualizer.export_to_png(filepath):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Visualization exported to {filepath}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to export visualization"
                )
    
    def _apply_conrune(self) -> None:
        """Apply the Conrune transformation to the current number."""
        text = self.number_input.text()
        if not text:
            return
            
        try:
            # Get ternary representation based on input mode
            if self.ternary_radio.isChecked():
                if not all(digit in '012' for digit in text):
                    raise ValueError("Invalid ternary number")
                ternary_str = text
            else:  # Decimal mode
                decimal_value = int(text)
                ternary_str = decimal_to_ternary(decimal_value)
            
            # Apply conrune transformation
            transformed = self.transition.apply_conrune(ternary_str)
            
            # Update display with transformed value
            self.number_input.setText(transformed)
            self.visualizer.set_ternary(transformed)
            
        except (ValueError, Exception) as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Invalid input: {str(e)}"
            )


if __name__ == "__main__":
    """Simple demonstration of the ternary digit visualizer."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = TernaryVisualizerPanel()
    panel.resize(400, 600)
    panel.show()
    sys.exit(app.exec()) 