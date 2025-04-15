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
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tq.utils.ternary_converter import decimal_to_ternary, ternary_to_decimal
from tq.utils.ternary_transition import TernaryTransition


class TernaryDigitVisualizer(QWidget):
    """
    Widget for visualizing a ternary number using PNG images.

    Displays the ternary digits with the least significant digit at the bottom
    and the most significant digit at the top.
    """

    def __init__(self, parent=None, color_scheme="standard"):
        """
        Initialize the visualizer widget.

        Args:
            parent: Parent widget
            color_scheme: Color scheme for digit images ("standard", "blue", "green", "purple")
        """
        super().__init__(parent)

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(5)

        # Available color schemes with RGB tint values
        self.color_schemes = {
            "standard": None,  # No tint for standard
            "blue": (80, 120, 240),  # Blue tint
            "green": (80, 200, 120),  # Green tint
            "purple": (180, 100, 220),  # Purple tint
            "custom": None,  # Will be set when user selects a custom color
        }

        # Current color scheme
        self.current_color_scheme = (
            color_scheme if color_scheme in self.color_schemes else "standard"
        )

        # Original digit images (without tint)
        self.original_digit_images = {}
        # Tinted digit images for display
        self.digit_images = {}

        # Load the original digit images
        self._load_original_images()

        # Apply the initial color scheme
        self._apply_color_scheme()

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

    def _load_original_images(self):
        """Load the original digit images without any tint."""
        self.original_digit_images.clear()

        for digit in ["0", "1", "2"]:
            path = os.path.join("assets", "ternary_digit", f"{digit}_optimized.png")
            if os.path.exists(path):
                pixmap = QPixmap(path)
                self.original_digit_images[digit] = pixmap
            else:
                print(f"Warning: Original digit image not found: {path}")

    def _apply_color_scheme(self):
        """Apply the current color scheme to the original images."""
        self.digit_images.clear()

        # Get the tint color for the current scheme
        tint = self.color_schemes[self.current_color_scheme]

        for digit, original_pixmap in self.original_digit_images.items():
            if tint is None:
                # For standard scheme, use original images
                self.digit_images[digit] = original_pixmap
            else:
                # For colored schemes, apply tint to a copy of the original image
                image = original_pixmap.toImage()

                # Create a new image with the same format
                tinted_image = QImage(image.size(), QImage.Format.Format_ARGB32)

                # Apply tint to each pixel
                for y in range(image.height()):
                    for x in range(image.width()):
                        pixel = image.pixel(x, y)

                        # Get alpha value (transparency)
                        alpha = (pixel >> 24) & 0xFF

                        if alpha > 0:  # Only process non-transparent pixels
                            # Get original RGB values
                            orig_r = (pixel >> 16) & 0xFF
                            orig_g = (pixel >> 8) & 0xFF
                            orig_b = pixel & 0xFF

                            # Calculate grayscale value to determine if pixel is part of the foreground
                            # Using luminance formula: 0.299*R + 0.587*G + 0.114*B
                            grayscale = 0.299 * orig_r + 0.587 * orig_g + 0.114 * orig_b

                            # Check if pixel is background (white or very light)
                            # Threshold of 240 (out of 255) identifies very light pixels as background
                            is_background = grayscale > 240

                            if is_background:
                                # Keep background pixels unchanged
                                tinted_image.setPixel(x, y, pixel)
                            else:
                                # Apply tint to foreground pixels
                                tint_r, tint_g, tint_b = tint

                                # Adaptive blend factor based on darkness
                                # Darker pixels get more tint, preserving details in mid-tones
                                darkness = 1.0 - (grayscale / 255.0)
                                blend_factor = min(0.8, 0.4 + (darkness * 0.5))

                                # Calculate blended RGB values
                                r = int(
                                    orig_r * (1 - blend_factor) + tint_r * blend_factor
                                )
                                g = int(
                                    orig_g * (1 - blend_factor) + tint_g * blend_factor
                                )
                                b = int(
                                    orig_b * (1 - blend_factor) + tint_b * blend_factor
                                )

                                # Ensure values are in valid range
                                r = max(0, min(255, r))
                                g = max(0, min(255, g))
                                b = max(0, min(255, b))

                                # Create tinted pixel (preserve alpha)
                                tinted_pixel = (alpha << 24) | (r << 16) | (g << 8) | b
                                tinted_image.setPixel(x, y, tinted_pixel)
                        else:
                            # Keep transparent pixels transparent
                            tinted_image.setPixel(x, y, pixel)

                # Convert back to pixmap
                self.digit_images[digit] = QPixmap.fromImage(tinted_image)

    def set_color_scheme(self, color_scheme):
        """
        Change the color scheme for digit images.

        Args:
            color_scheme: Name of the color scheme ("standard", "blue", "green", "purple")
        """
        if (
            color_scheme in self.color_schemes
            and color_scheme != self.current_color_scheme
        ):
            self.current_color_scheme = color_scheme

            # Apply the new color scheme
            self._apply_color_scheme()

            # Get the current ternary number from the visualization
            current_ternary = ""
            for label in reversed(
                self.digit_labels
            ):  # Collect current ternary from bottom to top
                for digit in ["0", "1", "2"]:
                    # We can't compare pixmaps directly anymore since they're dynamically generated
                    # Instead, we'll check the label's text property which we'll set when creating labels
                    if hasattr(label, "digit_value") and label.digit_value == digit:
                        current_ternary = digit + current_ternary
                        break

            # Only update if we successfully reconstructed the ternary number
            if current_ternary and all(d in "012" for d in current_ternary):
                self.set_ternary(current_ternary)

    def set_ternary(self, ternary_str: str) -> None:
        """
        Set the ternary number to display.

        Args:
            ternary_str: A valid ternary string
        """
        # Validate input
        if not all(digit in "012" for digit in ternary_str):
            raise ValueError(f"Invalid ternary string: {ternary_str}")

        # Clear existing digit labels
        self._clear_digits()

        # Create labels for each digit, from least significant (bottom) to most significant (top)
        for digit in ternary_str:
            label = QLabel()
            label.setPixmap(self.digit_images[digit])
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                "QLabel { border: none; background: transparent; }"
            )  # Remove any borders
            label.setFrameStyle(0)  # Remove frame
            label.setMargin(0)  # Remove margin

            # Store the digit value in the label for later reference
            label.digit_value = digit

            self.layout.addWidget(label)
            self.digit_labels.append(label)

        # Force layout update and repaint
        self.layout.update()
        self.update()

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

        # Ensure the layout updates properly
        self.layout.update()

    def create_image(self) -> QImage:
        """
        Create an image of the current visualization with transparency.

        Returns:
            QImage: The created image
        """
        # Create a transparent image
        total_height = sum(label.height() for label in self.digit_labels)
        max_width = (
            max(label.width() for label in self.digit_labels)
            if self.digit_labels
            else 100
        )

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

        return image

    def copy_to_clipboard(self) -> bool:
        """
        Copy the current visualization to the system clipboard.

        Returns:
            bool: True if copy was successful, False otherwise
        """
        try:
            # Create the image
            image = self.create_image()

            # Get the system clipboard
            clipboard = QApplication.clipboard()

            # Copy the image to clipboard
            clipboard.setImage(image)

            return True

        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False

    def export_to_png(self, filepath: str) -> bool:
        """
        Export the current visualization to a PNG file with transparency.

        Args:
            filepath: Path where to save the PNG file

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Create the image
            image = self.create_image()

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

        # Set minimum width for better horizontal space
        self.setMinimumWidth(600)

        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Create title
        title_label = QLabel("Ternary Digit Visualizer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-bottom: 10px;"
        )
        main_layout.addWidget(title_label)

        # Create a grid layout for the control panel
        control_panel = QGridLayout()
        control_panel.setColumnStretch(0, 1)  # First column takes more space
        control_panel.setColumnStretch(1, 1)  # Second column takes more space
        control_panel.setHorizontalSpacing(20)
        control_panel.setVerticalSpacing(10)

        # === Input Section (Left Column) ===
        input_group = QGroupBox("Number Input")
        input_layout = QVBoxLayout(input_group)

        # Input type selection
        input_type_layout = QHBoxLayout()
        self.input_type_group = QButtonGroup(self)
        self.ternary_radio = QRadioButton("Ternary")
        self.decimal_radio = QRadioButton("Decimal")
        self.input_type_group.addButton(self.ternary_radio)
        self.input_type_group.addButton(self.decimal_radio)
        self.ternary_radio.setChecked(True)  # Default selection

        input_type_layout.addWidget(self.ternary_radio)
        input_type_layout.addWidget(self.decimal_radio)
        input_layout.addLayout(input_type_layout)

        # Number input field
        number_layout = QHBoxLayout()
        number_layout.addWidget(QLabel("Number:"))
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter number")
        self.number_input.textChanged.connect(self._validate_input)
        number_layout.addWidget(self.number_input)
        input_layout.addLayout(number_layout)

        # Display button
        self.display_button = QPushButton("Display")
        self.display_button.setMinimumHeight(30)
        self.display_button.clicked.connect(self._update_visualization)
        input_layout.addWidget(self.display_button)

        # Add input group to the left column
        control_panel.addWidget(input_group, 0, 0)

        # === Actions Section (Right Column) ===
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Transformation buttons
        transform_layout = QHBoxLayout()
        self.conrune_button = QPushButton("Apply Conrune")
        self.conrune_button.clicked.connect(self._apply_conrune)
        self.reversal_button = QPushButton("Apply Reversal")
        self.reversal_button.clicked.connect(self._apply_reversal)
        transform_layout.addWidget(self.conrune_button)
        transform_layout.addWidget(self.reversal_button)
        actions_layout.addLayout(transform_layout)

        # Export and Copy buttons
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Export PNG")
        self.export_button.clicked.connect(self._export_visualization)
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.copy_button)
        actions_layout.addLayout(export_layout)

        # Add actions group to the right column
        control_panel.addWidget(actions_group, 0, 1)

        # === Appearance Section (Full Width) ===
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QHBoxLayout(appearance_group)

        # Color scheme selection
        appearance_layout.addWidget(QLabel("Color Scheme:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Standard", "Blue", "Green", "Purple", "Custom..."])
        self.color_combo.currentTextChanged.connect(self._change_color_scheme)
        appearance_layout.addWidget(self.color_combo)

        # Color indicator
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(24, 24)
        self.color_indicator.setStyleSheet(
            "background-color: transparent; border: 1px solid gray;"
        )
        appearance_layout.addWidget(self.color_indicator)

        # Color picker button
        self.color_picker_button = QPushButton("Pick Color")
        self.color_picker_button.clicked.connect(self._open_color_picker)
        self.color_picker_button.setVisible(False)  # Initially hidden
        appearance_layout.addWidget(self.color_picker_button)

        # Add appearance group spanning both columns
        control_panel.addWidget(appearance_group, 1, 0, 1, 2)

        # Add the control panel to the main layout
        main_layout.addLayout(control_panel)

        # Create a container for the visualizer with a border
        visualizer_container = QGroupBox("Visualization")
        visualizer_layout = QVBoxLayout(visualizer_container)

        # Create scroll area for the visualizer
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: white;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
            }
        """
        )

        # Create the visualizer widget
        self.visualizer = TernaryDigitVisualizer()
        scroll_area.setWidget(self.visualizer)

        # Add scroll area to the visualizer container
        visualizer_layout.addWidget(scroll_area)

        # Add the visualizer container to the main layout with stretch factor
        main_layout.addWidget(visualizer_container, 1)

        # Create the ternary transition utility
        self.transition = TernaryTransition()

        # Initialize toggle state variables
        self._original_ternary = None
        self._original_input = None
        self._is_conruned = False
        self._is_reversed = False
        self._original_ternary_for_reversal = None
        self._original_input_for_reversal = None

        # Set frame style for the entire panel
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """
        )

        # Set initial value
        self.number_input.setText("210")

    def _validate_input(self) -> None:
        """Validate the input based on selected input type."""
        text = self.number_input.text()
        valid = False

        if self.ternary_radio.isChecked():
            valid = all(digit in "012" for digit in text) if text else True
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
            # Reset transformation toggle states when a new number is entered
            self._original_ternary = None
            self._original_input = None
            self._is_conruned = False
            self._original_ternary_for_reversal = None
            self._original_input_for_reversal = None
            self._is_reversed = False
            self.conrune_button.setText("Apply Conrune")
            self.reversal_button.setText("Apply Reversal")

            if self.ternary_radio.isChecked():
                if all(digit in "012" for digit in text):
                    self.visualizer.set_ternary(text)
            else:  # Decimal mode
                decimal_value = int(text)
                self.visualizer.set_decimal(decimal_value)
        except (ValueError, Exception) as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")

    def _export_visualization(self) -> None:
        """Export the current visualization as a PNG file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Visualization", str(Path.home()), "PNG Images (*.png)"
        )

        if filepath:
            if not filepath.lower().endswith(".png"):
                filepath += ".png"

            if self.visualizer.export_to_png(filepath):
                QMessageBox.information(
                    self, "Success", f"Visualization exported to {filepath}"
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to export visualization")

    def _copy_to_clipboard(self) -> None:
        """Copy the current visualization to the system clipboard."""
        if self.visualizer.copy_to_clipboard():
            QMessageBox.information(
                self, "Success", "Visualization copied to clipboard"
            )
        else:
            QMessageBox.warning(
                self, "Error", "Failed to copy visualization to clipboard"
            )

    def _apply_conrune(self) -> None:
        """Apply the Conrune transformation to the current number."""
        text = self.number_input.text()
        if not text:
            return

        try:
            # Get ternary representation based on input mode
            is_decimal_mode = self.decimal_radio.isChecked()
            if not is_decimal_mode:  # Ternary mode
                if not all(digit in "012" for digit in text):
                    raise ValueError("Invalid ternary number")
                ternary_str = text
                original_input = text  # Store original input format
            else:  # Decimal mode
                decimal_value = int(text)
                ternary_str = decimal_to_ternary(decimal_value)
                original_input = text  # Store original decimal input

            # Store the original value if this is the first transformation
            if not hasattr(self, "_original_ternary") or self._original_ternary is None:
                self._original_ternary = ternary_str
                self._original_input = original_input
                # Apply conrune transformation
                transformed_ternary = self.transition.apply_conrune(ternary_str)
                self._is_conruned = True
                # Update button text to indicate toggle behavior
                self.conrune_button.setText("Revert Conrune")
            else:
                # Toggle between original and transformed
                if self._is_conruned:
                    # Go back to original
                    transformed_ternary = self._original_ternary
                    self._is_conruned = False
                    self.conrune_button.setText("Apply Conrune")
                    # Restore original input format
                    if is_decimal_mode:
                        self.number_input.setText(self._original_input)
                        self.visualizer.set_ternary(transformed_ternary)
                        return
                    # Clear the original values when reverting
                    self._original_ternary = None
                    self._original_input = None
                else:
                    # Apply conrune again
                    self._original_ternary = ternary_str
                    self._original_input = original_input
                    transformed_ternary = self.transition.apply_conrune(ternary_str)
                    self._is_conruned = True
                    self.conrune_button.setText("Revert Conrune")

            # Update display with transformed value based on input mode
            if is_decimal_mode:
                # Convert transformed ternary back to decimal for display
                transformed_decimal = str(ternary_to_decimal(transformed_ternary))
                self.number_input.setText(transformed_decimal)
                self.visualizer.set_ternary(
                    transformed_ternary
                )  # Visualizer always uses ternary
            else:
                # In ternary mode, just display the transformed ternary
                self.number_input.setText(transformed_ternary)
                self.visualizer.set_ternary(transformed_ternary)

        except (ValueError, Exception) as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")

    def _apply_reversal(self) -> None:
        """Apply the digit reversal transformation to the current number."""
        text = self.number_input.text()
        if not text:
            return

        try:
            # Get ternary representation based on input mode
            is_decimal_mode = self.decimal_radio.isChecked()
            if not is_decimal_mode:  # Ternary mode
                if not all(digit in "012" for digit in text):
                    raise ValueError("Invalid ternary number")
                ternary_str = text
                original_input = text  # Store original input format
            else:  # Decimal mode
                decimal_value = int(text)
                ternary_str = decimal_to_ternary(decimal_value)
                original_input = text  # Store original decimal input

            # Store the original value if this is the first transformation
            if (
                not hasattr(self, "_original_ternary_for_reversal")
                or self._original_ternary_for_reversal is None
            ):
                self._original_ternary_for_reversal = ternary_str
                self._original_input_for_reversal = original_input
                # Apply reversal transformation
                transformed_ternary = ternary_str[::-1]  # Reverse the string
                self._is_reversed = True
                # Update button text to indicate toggle behavior
                self.reversal_button.setText("Revert Reversal")
            else:
                # Toggle between original and transformed
                if self._is_reversed:
                    # Go back to original
                    transformed_ternary = self._original_ternary_for_reversal
                    self._is_reversed = False
                    self.reversal_button.setText("Apply Reversal")
                    # Restore original input format
                    if is_decimal_mode:
                        self.number_input.setText(self._original_input_for_reversal)
                        self.visualizer.set_ternary(transformed_ternary)
                        return
                    # Clear the original values when reverting
                    self._original_ternary_for_reversal = None
                    self._original_input_for_reversal = None
                else:
                    # Apply reversal again
                    self._original_ternary_for_reversal = ternary_str
                    self._original_input_for_reversal = original_input
                    transformed_ternary = ternary_str[::-1]  # Reverse the string
                    self._is_reversed = True
                    self.reversal_button.setText("Revert Reversal")

            # Update display with transformed value based on input mode
            if is_decimal_mode:
                # Convert transformed ternary back to decimal for display
                transformed_decimal = str(ternary_to_decimal(transformed_ternary))
                self.number_input.setText(transformed_decimal)
                self.visualizer.set_ternary(
                    transformed_ternary
                )  # Visualizer always uses ternary
            else:
                # In ternary mode, just display the transformed ternary
                self.number_input.setText(transformed_ternary)
                self.visualizer.set_ternary(transformed_ternary)

        except (ValueError, Exception) as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")

    def _change_color_scheme(self, color_text):
        """
        Change the color scheme of the ternary digit visualizer.

        Args:
            color_text: The selected color scheme text from the combo box
        """
        # Handle custom color option
        if color_text == "Custom...":
            self.color_picker_button.setVisible(True)
            # If we already have a custom color, use it
            if self.visualizer.color_schemes["custom"] is not None:
                self.visualizer.set_color_scheme("custom")
                # Update color indicator
                custom_color = self.visualizer.color_schemes["custom"]
                self._update_color_indicator(custom_color)
            else:
                # Otherwise, open the color picker
                self._open_color_picker()
        else:
            # For standard color schemes
            self.color_picker_button.setVisible(False)
            color_scheme = color_text.lower()
            self.visualizer.set_color_scheme(color_scheme)

            # Update color indicator
            tint = self.visualizer.color_schemes[color_scheme]
            self._update_color_indicator(tint)

    def _open_color_picker(self):
        """Open a color picker dialog and apply the selected color."""
        # Get initial color (use current custom color if available)
        initial_color = QColor(Qt.GlobalColor.white)
        if self.visualizer.color_schemes["custom"] is not None:
            r, g, b = self.visualizer.color_schemes["custom"]
            initial_color = QColor(r, g, b)

        # Open color dialog
        color = QColorDialog.getColor(
            initial_color,
            self,
            "Select Custom Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )

        # If a valid color was selected
        if color.isValid():
            # Extract RGB components
            r, g, b = color.red(), color.green(), color.blue()

            # Update custom color in visualizer
            self.visualizer.color_schemes["custom"] = (r, g, b)
            self.visualizer.set_color_scheme("custom")

            # Update color indicator
            self._update_color_indicator((r, g, b))

            # Make sure "Custom..." is selected in the combo box
            index = self.color_combo.findText("Custom...")
            if index >= 0:
                self.color_combo.setCurrentIndex(index)

    def _update_color_indicator(self, tint):
        """Update the color indicator with the current tint color."""
        if tint is None:
            # For standard (no tint), show transparent
            self.color_indicator.setStyleSheet(
                "background-color: transparent; border: 1px solid gray;"
            )
        else:
            # For colored schemes, show the tint color
            r, g, b = tint
            self.color_indicator.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); border: 1px solid gray;"
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
