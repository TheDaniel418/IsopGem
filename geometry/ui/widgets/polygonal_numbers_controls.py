"""
Polygonal Numbers Controls Widget.

This module provides a control panel for the polygonal numbers visualization,
allowing for dot selection, connection management, and mathematical operations.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QRadioButton, QSpinBox, QComboBox,
    QToolButton, QInputDialog, QScrollArea
)


class PolygonalNumbersControls(QWidget):
    """Control panel for the polygonal numbers visualization."""

    # Define signals
    selectionModeChanged = pyqtSignal(bool)
    clearSelectionsRequested = pyqtSignal()
    selectAllRequested = pyqtSignal()  # Added signal for Select All
    connectDotsRequested = pyqtSignal()
    showConnectionsChanged = pyqtSignal(bool)
    selectionGroupChanged = pyqtSignal(str)
    closePolygonRequested = pyqtSignal()
    selectLayerRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize the control panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """Initialize the user interface."""
        # Main layout with scroll area for small screens
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)

        # Use a QVBoxLayout for the scroll area
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll_area)

        # Use a wider layout with more breathing room
        self.setMinimumWidth(550)
        self.setFixedWidth(600)  # FORCE width to exactly match what we set in interactive widget

        # Title
        title_label = QLabel("Selection Controls")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Mode selection in horizontal layout (save vertical space)
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()  # Changed to horizontal layout

        self.pan_mode_radio = QRadioButton("Pan && Zoom")
        self.pan_mode_radio.setChecked(True)
        self.pan_mode_radio.toggled.connect(self._on_mode_changed)

        self.select_mode_radio = QRadioButton("Select Dots")
        self.select_mode_radio.toggled.connect(self._on_mode_changed)

        mode_layout.addWidget(self.pan_mode_radio)
        mode_layout.addWidget(self.select_mode_radio)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Add keyboard shortcut tips below the mode buttons
        shortcut_label = QLabel("Tip: Use Ctrl+S to toggle selection mode")
        shortcut_label.setStyleSheet("color: gray; font-size: 8pt;")
        layout.addWidget(shortcut_label)

        # Selection management
        selection_group = QGroupBox("Selection")
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(5)  # Reduce spacing to save vertical space

        # Info and buttons in horizontal layout
        info_layout = QHBoxLayout()

        # Selection info on left side
        info_sublayout = QVBoxLayout()

        self.selection_info_label = QLabel("No dots selected")
        info_sublayout.addWidget(self.selection_info_label)

        self.sum_label = QLabel("Sum: 0")
        info_sublayout.addWidget(self.sum_label)

        info_layout.addLayout(info_sublayout, 2)  # Give it more space

        # Buttons on right side
        buttons_sublayout = QVBoxLayout()

        buttons_row = QHBoxLayout()

        # Clear selection button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Clear all selections (Esc)")
        self.clear_button.clicked.connect(self.clearSelectionsRequested.emit)
        buttons_row.addWidget(self.clear_button)

        # Select all button
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setToolTip("Select all dots (Ctrl+A)")
        self.select_all_button.clicked.connect(self._select_all_dots)
        buttons_row.addWidget(self.select_all_button)

        buttons_sublayout.addLayout(buttons_row)

        info_layout.addLayout(buttons_sublayout, 1)

        selection_layout.addLayout(info_layout)

        # Selection by layer in compact form
        layer_selection_layout = QHBoxLayout()
        layer_selection_layout.addWidget(QLabel("Select Layer:"))

        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(0, 20)
        self.layer_spin.setValue(1)
        layer_selection_layout.addWidget(self.layer_spin)

        self.select_layer_button = QPushButton("Select")
        self.select_layer_button.clicked.connect(self._select_layer)
        layer_selection_layout.addWidget(self.select_layer_button)

        selection_layout.addLayout(layer_selection_layout)

        # Selection Instruction Label
        selection_help_label = QLabel("Click dots sequentially to select. Use Ctrl+click to toggle selection.")
        selection_help_label.setWordWrap(True)
        selection_help_label.setStyleSheet("color: #666; font-size: 8pt;")
        selection_layout.addWidget(selection_help_label)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Selection groups
        group_group = QGroupBox("Selection Groups")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(5)  # Reduce spacing to save vertical space

        group_label = QLabel("Save and manage selections as named groups:")
        group_label.setWordWrap(True)
        group_layout.addWidget(group_label)

        # Group selection combo - horizontal layout
        groups_layout = QHBoxLayout()
        groups_layout.addWidget(QLabel("Active Group:"))

        self.group_combo = QComboBox()
        self.group_combo.addItem("Default")
        self.group_combo.currentTextChanged.connect(self._on_group_changed)
        groups_layout.addWidget(self.group_combo)

        self.add_group_button = QToolButton()
        self.add_group_button.setText("+")
        self.add_group_button.setToolTip("Create a new group")
        self.add_group_button.clicked.connect(self._add_selection_group)
        groups_layout.addWidget(self.add_group_button)

        group_layout.addLayout(groups_layout)

        # Group action buttons
        group_buttons_layout = QHBoxLayout()

        self.save_to_group_button = QPushButton("Save Selection")
        self.save_to_group_button.setToolTip("Save current selection to the active group")
        self.save_to_group_button.clicked.connect(self._save_to_current_group)
        group_buttons_layout.addWidget(self.save_to_group_button)

        self.delete_group_button = QPushButton("Delete Group")
        self.delete_group_button.setToolTip("Delete the active group")
        self.delete_group_button.clicked.connect(self._delete_current_group)
        group_buttons_layout.addWidget(self.delete_group_button)

        group_layout.addLayout(group_buttons_layout)

        # Group operations
        group_op_label = QLabel("Group Operations:")
        group_layout.addWidget(group_op_label)

        group_op_layout = QHBoxLayout()

        group_op_layout.addWidget(QLabel("Operation:"))
        self.group_op_combo = QComboBox()
        self.group_op_combo.addItems([
            "Union (A∪B)",
            "Intersection (A∩B)",
            "Difference (A-B)",
            "Symmetric Diff (A⊕B)"
        ])
        group_op_layout.addWidget(self.group_op_combo)

        group_layout.addLayout(group_op_layout)

        # First group selection
        group_a_layout = QHBoxLayout()
        group_a_layout.addWidget(QLabel("Group A:"))
        self.group_a_combo = QComboBox()
        self.group_a_combo.addItem("Default")
        group_a_layout.addWidget(self.group_a_combo)

        group_layout.addLayout(group_a_layout)

        # Second group selection
        group_b_layout = QHBoxLayout()
        group_b_layout.addWidget(QLabel("Group B:"))
        self.group_b_combo = QComboBox()
        self.group_b_combo.addItem("Default")
        group_b_layout.addWidget(self.group_b_combo)

        group_layout.addLayout(group_b_layout)

        # Result group
        result_group_layout = QHBoxLayout()
        result_group_layout.addWidget(QLabel("Result:"))
        self.result_group_combo = QComboBox()
        self.result_group_combo.addItem("Default")
        self.result_group_combo.setEditable(True)
        result_group_layout.addWidget(self.result_group_combo)

        group_layout.addLayout(result_group_layout)

        # Perform operation button
        self.perform_op_button = QPushButton("Perform Operation")
        self.perform_op_button.clicked.connect(self._perform_group_operation)
        group_layout.addWidget(self.perform_op_button)

        # Group color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Group Color:"))

        self.color_button = QPushButton()
        self.color_button.setMinimumWidth(80)
        self.color_button.setMaximumWidth(80)
        self._update_color_button()  # Initialize the color button
        self.color_button.clicked.connect(self._change_group_color)
        color_layout.addWidget(self.color_button)

        group_layout.addLayout(color_layout)

        group_group.setLayout(group_layout)
        layout.addWidget(group_group)

        # Results label for group operations
        self.result_label = QLabel("No results")
        self.result_label.setWordWrap(True)
        # Give the results label a fixed height to prevent UI jumping
        self.result_label.setMinimumHeight(60)
        layout.addWidget(self.result_label)

        # Connection info label (hidden but needed for updates)
        self.connection_info_label = QLabel("No connections")
        self.connection_info_label.setVisible(False)
        layout.addWidget(self.connection_info_label)

        # Add stretch to push everything to the top
        layout.addStretch(1)

    def _on_mode_changed(self, checked):
        """Handle mode selection change.

        Args:
            checked: Whether the radio button is checked
        """
        if checked:
            # Only emit for the selected radio button
            if self.sender() == self.select_mode_radio:
                self.selectionModeChanged.emit(True)
            elif self.sender() == self.pan_mode_radio:
                self.selectionModeChanged.emit(False)

    def _select_all_dots(self):
        """Select all available dots by emitting the selectAllRequested signal."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("_select_all_dots called, emitting selectAllRequested signal")

        # Emit the signal to let the panel handle the selection
        self.selectAllRequested.emit()

    def _select_layer(self):
        """Select all dots in the specified layer."""
        layer = self.layer_spin.value()
        self.selectLayerRequested.emit(layer)

    def _on_group_changed(self, group_name):
        """Handle selection group change.

        Args:
            group_name: Name of the selected group
        """
        if group_name:
            self.selectionGroupChanged.emit(group_name)
            self._update_color_button()

    def _add_selection_group(self):
        """Add a new selection group."""
        group_name, ok = QInputDialog.getText(
            self, "New Selection Group", "Enter group name:")

        if ok and group_name:
            # Check if the group already exists
            if self.group_combo.findText(group_name) == -1:
                self.group_combo.addItem(group_name)
                self.group_a_combo.addItem(group_name)
                self.group_b_combo.addItem(group_name)
                self.result_group_combo.addItem(group_name)
                self.group_combo.setCurrentText(group_name)

                # Update color button
                self._update_color_button()

    def _save_to_current_group(self):
        """Save the current selection to the active group."""
        # Access visualization and save current selection to the active group
        if hasattr(self.parent(), 'visualization'):
            viz = self.parent().visualization
            group_name = self.group_combo.currentText()

            if not group_name:
                return

            # Get current selection
            selected_dots = viz.get_selected_dots()

            if not selected_dots:
                # Show a message that there's nothing to save
                self.result_label.setText("No dots selected to save to group")
                return

            # Save to group
            viz.selection_groups[group_name] = selected_dots.copy()
            viz._debug_print(f"Saved {len(selected_dots)} dots to group '{group_name}'")

            # Confirm in UI
            self.result_label.setText(f"Saved {len(selected_dots)} dots to group '{group_name}'")

    def _delete_current_group(self):
        """Delete the currently selected group."""
        group_name = self.group_combo.currentText()

        if group_name == "Default":
            # Can't delete the default group
            self.result_label.setText("Cannot delete the Default group")
            return

        # Access visualization and delete the group
        if hasattr(self.parent(), 'visualization') and group_name:
            viz = self.parent().visualization

            if group_name in viz.selection_groups:
                # If current selection is from this group, clear it
                if viz.current_group == group_name:
                    viz.selected_dots = []
                    viz.current_group = "Default"

                # Remove the group
                del viz.selection_groups[group_name]

                # Update the combo box
                index = self.group_combo.findText(group_name)
                if index >= 0:
                    self.group_combo.removeItem(index)

                # Select the Default group
                self.group_combo.setCurrentText("Default")

                # Confirm in UI
                self.result_label.setText(f"Deleted group '{group_name}'")
                viz.update()



    def update_selection_info(self, selected_count, selected_sum):
        """Update the selection information display.

        Args:
            selected_count: Number of selected dots
            selected_sum: Sum of selected dot values
        """
        if selected_count == 0:
            self.selection_info_label.setText("No dots selected")
        elif selected_count == 1:
            self.selection_info_label.setText(f"1 dot selected")
        else:
            self.selection_info_label.setText(f"{selected_count} dots selected")

        self.sum_label.setText(f"Sum: {selected_sum}")

    def update_connection_info(self, connection_count):
        """Update the connection information display.

        Args:
            connection_count: Number of connections
        """
        if connection_count == 0:
            self.connection_info_label.setText("No connections")
        elif connection_count == 1:
            self.connection_info_label.setText(f"1 connection")
        else:
            self.connection_info_label.setText(f"{connection_count} connections")







    def _update_color_button(self) -> None:
        """Update the color button to show the current group color."""
        if not hasattr(self.parent(), 'visualization'):
            return

        viz = self.parent().visualization
        current_group = self.group_combo.currentText()

        if current_group and hasattr(viz, 'get_group_color'):
            color = viz.get_group_color(current_group)

            # Set the button background to the group color
            self.color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"color: {'black' if color.lightness() > 128 else 'white'};"
            )
            self.color_button.setText("Change")

    def _change_group_color(self) -> None:
        """Change the color of the current group."""
        if not hasattr(self.parent(), 'visualization'):
            return

        viz = self.parent().visualization
        current_group = self.group_combo.currentText()

        if not current_group:
            return

        from PyQt6.QtWidgets import QColorDialog

        # Get the current color
        current_color = viz.get_group_color(current_group)

        # Open color dialog
        color = QColorDialog.getColor(current_color, self, f"Select Color for '{current_group}'")

        # If a valid color was chosen
        if color.isValid():
            # Set the color for the group
            viz.set_group_color(current_group, color)

            # Update the color button
            self._update_color_button()

            # Update the visualization
            viz.update()

    def _perform_group_operation(self) -> None:
        """Perform the selected group operation."""
        if not hasattr(self.parent(), 'visualization'):
            return

        viz = self.parent().visualization

        # Get operation type
        op_text = self.group_op_combo.currentText()
        operation = ""

        if "Union" in op_text:
            operation = "union"
        elif "Intersection" in op_text:
            operation = "intersection"
        elif "Symmetric" in op_text:
            operation = "symmetric_difference"
        elif "Difference" in op_text:
            operation = "difference"

        # Get groups
        group_a = self.group_a_combo.currentText()
        group_b = self.group_b_combo.currentText()
        result_group = self.result_group_combo.currentText()

        # Validate
        if not group_a or not group_b or not result_group:
            self.result_label.setText("Please select valid groups for the operation")
            return

        # Perform the operation
        viz.perform_group_operation(operation, group_a, group_b, result_group)

        # Ensure the result group is in the combo boxes
        if self.group_combo.findText(result_group) == -1:
            self.group_combo.addItem(result_group)
            self.group_a_combo.addItem(result_group)
            self.group_b_combo.addItem(result_group)
            self.result_group_combo.addItem(result_group)

        # Show result
        self.result_label.setText(
            f"Performed {operation} between '{group_a}' and '{group_b}', "
            f"result in '{result_group}'"
        )

        # Switch to the result group
        self.group_combo.setCurrentText(result_group)

    def _add_selection_to_group(self) -> None:
        """Add current selection to the selected group."""
        if not hasattr(self.parent(), 'visualization'):
            self.result_label.setText("Cannot access visualization widget")
            return

        viz = self.parent().visualization
        group_name = self.group_combo.currentText()

        if not group_name:
            self.result_label.setText("No group selected")
            return

        # Get current selection from visualization
        selected_dots = viz.selected_dots.copy()

        if not selected_dots:
            self.result_label.setText("No dots selected")
            return

        # Add to or create group
        if group_name not in viz.selection_groups:
            viz.selection_groups[group_name] = []

            # Add to all group comboboxes if not already present
            self._sync_group_comboboxes()

        # Add dots to the group, avoiding duplicates
        for dot in selected_dots:
            if dot not in viz.selection_groups[group_name]:
                viz.selection_groups[group_name].append(dot)

        # Sort for consistency
        viz.selection_groups[group_name].sort()

        # Update the UI
        self.result_label.setText(f"Added {len(selected_dots)} dots to group '{group_name}'")

        # Update group status if we have a label for it
        if hasattr(self, 'group_status_label'):
            self.group_status_label.setText(f"Group '{group_name}': {len(viz.selection_groups[group_name])} dots")

    def _sync_group_comboboxes(self) -> None:
        """Ensure all group comboboxes have the same entries."""
        if not hasattr(self.parent(), 'visualization'):
            return

        viz = self.parent().visualization

        # Get all available groups
        groups = list(viz.selection_groups.keys())

        # Get current selections from each combobox to restore after update
        current_group = self.group_combo.currentText() if self.group_combo.count() > 0 else ""
        current_group_a = self.group_a_combo.currentText() if hasattr(self, 'group_a_combo') and self.group_a_combo.count() > 0 else ""
        current_group_b = self.group_b_combo.currentText() if hasattr(self, 'group_b_combo') and self.group_b_combo.count() > 0 else ""
        current_result = self.result_group_combo.currentText() if hasattr(self, 'result_group_combo') and self.result_group_combo.count() > 0 else ""

        # Update all comboboxes
        for group in groups:
            if self.group_combo.findText(group) == -1:
                self.group_combo.addItem(group)
            if hasattr(self, 'group_a_combo') and self.group_a_combo.findText(group) == -1:
                self.group_a_combo.addItem(group)
            if hasattr(self, 'group_b_combo') and self.group_b_combo.findText(group) == -1:
                self.group_b_combo.addItem(group)
            if hasattr(self, 'result_group_combo') and self.result_group_combo.findText(group) == -1:
                self.result_group_combo.addItem(group)

        # Restore previously selected items
        if current_group and self.group_combo.findText(current_group) != -1:
            self.group_combo.setCurrentText(current_group)
        if current_group_a and hasattr(self, 'group_a_combo') and self.group_a_combo.findText(current_group_a) != -1:
            self.group_a_combo.setCurrentText(current_group_a)
        if current_group_b and hasattr(self, 'group_b_combo') and self.group_b_combo.findText(current_group_b) != -1:
            self.group_b_combo.setCurrentText(current_group_b)
        if current_result and hasattr(self, 'result_group_combo') and self.result_group_combo.findText(current_result) != -1:
            self.result_group_combo.setCurrentText(current_result)