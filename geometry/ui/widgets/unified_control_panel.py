"""
Unified Control Panel for Polygonal Numbers Visualization.

This module provides a unified control panel that combines all controls
for the polygonal numbers visualization in a single, organized interface.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geometry.models.saved_visualization import SavedVisualization, VisualizationManager


class UnifiedControlPanel(QWidget):
    """Unified control panel for polygonal numbers visualization."""

    # Define signals for polygonal number configuration
    typeChanged = pyqtSignal(bool)  # True for centered, False for regular
    sidesChanged = pyqtSignal(int)  # Number of sides
    indexChanged = pyqtSignal(int)  # Index value

    # Define signals for visualization options
    gridToggled = pyqtSignal(bool)
    labelsToggled = pyqtSignal(bool)
    layersToggled = pyqtSignal(bool)
    dotNumbersToggled = pyqtSignal(bool)
    dotSizeChanged = pyqtSignal(float)
    zoomChanged = pyqtSignal(float)
    resetViewRequested = pyqtSignal()
    colorSchemeChanged = pyqtSignal(str)

    # Define signals for animation
    animationToggled = pyqtSignal(bool)
    animationReset = pyqtSignal()

    # Define signals for selection and interaction
    selectionModeChanged = pyqtSignal(bool)  # True for selection, False for pan
    clearSelectionsRequested = pyqtSignal()
    selectAllRequested = pyqtSignal()
    connectDotsRequested = pyqtSignal()
    showConnectionsChanged = pyqtSignal(bool)
    closePolygonRequested = pyqtSignal()
    selectLayerRequested = pyqtSignal(int)

    # Define signals for group operations
    selectionGroupChanged = pyqtSignal(str)
    groupOperationRequested = pyqtSignal(
        str, str, str, str
    )  # operation, group1, group2, result

    def __init__(self, parent=None):
        """Initialize the unified control panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Store reference to parent panel
        self.panel = parent

        # Set size policy to allow proper resizing
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Initialize UI
        self._init_ui()

    def showEvent(self, event):
        """Handle show events.

        Args:
            event: Show event
        """
        super().showEvent(event)

        # Refresh the groups when the panel is shown
        print("Panel shown, refreshing groups")
        self._populate_group_comboboxes()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create tab widget for different control categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Connect tab change signal to refresh groups when the groups tab is shown
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Create tabs for different control categories
        self.tab_widget.addTab(self._create_configuration_tab(), "Configuration")
        self.tab_widget.addTab(self._create_visualization_tab(), "Visualization")
        self.tab_widget.addTab(self._create_selection_tab(), "Selection")
        self.tab_widget.addTab(self._create_groups_tab(), "Groups")
        self.tab_widget.addTab(self._create_analysis_tab(), "Analysis")
        self.tab_widget.addTab(self._create_visualizations_tab(), "Visualizations")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Add status bar at the bottom
        self._create_status_bar()
        main_layout.addWidget(self.status_bar)

        # Populate group combo boxes with saved groups
        self._populate_group_comboboxes()

    def _create_configuration_tab(self):
        """Create the configuration tab with polygonal number settings.

        Returns:
            The configuration tab widget
        """
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(10)

        # Type selection group
        type_group = QGroupBox("Polygonal Number Type")
        type_layout = QVBoxLayout(type_group)

        # Radio buttons for regular vs centered
        self.regular_radio = QRadioButton("Regular Polygonal Numbers")
        self.regular_radio.setChecked(True)
        self.regular_radio.toggled.connect(self._on_type_changed)
        self.regular_radio.setToolTip(
            "Regular polygonal numbers form shapes with dots on the perimeter"
        )

        self.centered_radio = QRadioButton("Centered Polygonal Numbers")
        self.centered_radio.toggled.connect(self._on_type_changed)
        self.centered_radio.setToolTip(
            "Centered polygonal numbers have a central dot with layers around it"
        )

        type_layout.addWidget(self.regular_radio)
        type_layout.addWidget(self.centered_radio)

        # Polygon sides selection
        sides_layout = QFormLayout()

        # Replace combobox with a combination of combobox and spinbox
        sides_container = QWidget()
        sides_container_layout = QHBoxLayout(sides_container)
        sides_container_layout.setContentsMargins(0, 0, 0, 0)
        sides_container_layout.setSpacing(5)

        self.sides_combo = QComboBox()

        # Add common polygon options
        polygon_options = {
            3: "Triangular",
            4: "Square",
            5: "Pentagonal",
            6: "Hexagonal",
            7: "Heptagonal",
            8: "Octagonal",
            9: "Nonagonal",
            10: "Decagonal",
            11: "Hendecagonal",
            12: "Dodecagonal",
            15: "Pentadecagonal",
            20: "Icosagonal",
        }

        for sides, name in polygon_options.items():
            self.sides_combo.addItem(name, sides)

        # Add a "Custom" option at the end
        self.sides_combo.addItem("Custom...", -1)

        self.sides_combo.setToolTip("Select the type of polygon to visualize")
        self.sides_combo.currentIndexChanged.connect(self._on_sides_combo_changed)
        sides_container_layout.addWidget(self.sides_combo, 2)

        # Add a spinbox for custom sides
        self.sides_spin = QSpinBox()
        self.sides_spin.setRange(3, 1000)  # Allow up to 1000 sides
        self.sides_spin.setValue(3)
        self.sides_spin.setToolTip("Set a custom number of sides")
        self.sides_spin.valueChanged.connect(self._on_sides_spin_changed)
        self.sides_spin.setVisible(False)  # Hide initially
        sides_container_layout.addWidget(self.sides_spin, 1)

        sides_layout.addRow("Shape:", sides_container)
        type_layout.addLayout(sides_layout)

        # Add type group to config layout
        config_layout.addWidget(type_group)

        # Index control group
        index_group = QGroupBox("Number Index")
        index_layout = QVBoxLayout(index_group)

        # Index spinner
        index_form = QFormLayout()
        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 100)
        self.index_spin.setValue(5)
        self.index_spin.valueChanged.connect(self._on_index_changed)
        self.index_spin.setToolTip("Set the index of the polygonal number")
        index_form.addRow("Index:", self.index_spin)

        # Value display
        self.value_label = QLabel("Value: 5")
        self.value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        index_form.addRow("", self.value_label)

        index_layout.addLayout(index_form)

        # Index slider
        self.index_slider = QSlider(Qt.Orientation.Horizontal)
        self.index_slider.setRange(1, 100)
        self.index_slider.setValue(5)
        self.index_slider.valueChanged.connect(self._on_slider_changed)
        self.index_slider.setToolTip("Adjust the index of the polygonal number")
        index_layout.addWidget(self.index_slider)

        # Animation controls
        animation_layout = QHBoxLayout()

        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self._on_animation_toggled)
        self.play_button.setToolTip("Play/pause animation of the sequence")
        animation_layout.addWidget(self.play_button)

        self.reset_button = QPushButton("⟲ Reset")
        self.reset_button.clicked.connect(self.animationReset.emit)
        self.reset_button.setToolTip("Reset animation to the beginning")
        animation_layout.addWidget(self.reset_button)

        index_layout.addLayout(animation_layout)

        # Add index group to config layout
        config_layout.addWidget(index_group)

        # Add spacer to push everything to the top
        config_layout.addStretch()

        # Return the tab widget
        return config_tab

    def _create_visualization_tab(self):
        """Create the visualization tab with display options."""
        viz_tab = QWidget()
        viz_layout = QVBoxLayout(viz_tab)
        viz_layout.setContentsMargins(10, 10, 10, 10)
        viz_layout.setSpacing(10)

        # Display options group
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)

        # Grid toggle
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(False)
        self.grid_check.toggled.connect(self.gridToggled.emit)
        self.grid_check.setToolTip("Show/hide the coordinate grid")
        display_layout.addWidget(self.grid_check)

        # Labels toggle
        self.labels_check = QCheckBox("Show Labels")
        self.labels_check.setChecked(True)
        self.labels_check.toggled.connect(self.labelsToggled.emit)
        self.labels_check.setToolTip("Show/hide labels with formula and information")
        display_layout.addWidget(self.labels_check)

        # Layers toggle
        self.layers_check = QCheckBox("Show Colored Layers")
        self.layers_check.setChecked(True)
        self.layers_check.toggled.connect(self.layersToggled.emit)
        self.layers_check.setToolTip("Show/hide layer coloring")
        display_layout.addWidget(self.layers_check)

        # Dot numbers toggle
        self.dot_numbers_check = QCheckBox("Show Dot Numbers")
        self.dot_numbers_check.setChecked(False)
        self.dot_numbers_check.toggled.connect(self.dotNumbersToggled.emit)
        self.dot_numbers_check.setToolTip("Show/hide number labels on dots")
        display_layout.addWidget(self.dot_numbers_check)

        # Color scheme selection
        color_scheme_layout = QFormLayout()
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(["Rainbow", "Pastel", "Monochrome", "Custom"])
        self.color_scheme_combo.setToolTip("Select a color scheme for layers/gnomons")
        self.color_scheme_combo.currentTextChanged.connect(
            self._on_color_scheme_changed
        )
        color_scheme_layout.addRow("Layer Colors:", self.color_scheme_combo)
        display_layout.addLayout(color_scheme_layout)

        # Add display group to viz layout
        viz_layout.addWidget(display_group)

        # Size and zoom group
        size_group = QGroupBox("Size and Zoom")
        size_layout = QVBoxLayout(size_group)

        # Dot size control
        dot_size_layout = QFormLayout()
        self.dot_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.dot_size_slider.setRange(2, 20)
        self.dot_size_slider.setValue(10)
        self.dot_size_slider.valueChanged.connect(
            lambda value: self.dotSizeChanged.emit(float(value))
        )
        self.dot_size_slider.setToolTip("Adjust the size of dots")
        dot_size_layout.addRow("Dot Size:", self.dot_size_slider)
        size_layout.addLayout(dot_size_layout)

        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(lambda: self.zoomChanged.emit(1.2))
        self.zoom_in_button.setToolTip("Zoom in")
        zoom_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.clicked.connect(lambda: self.zoomChanged.emit(0.8))
        self.zoom_out_button.setToolTip("Zoom out")
        zoom_layout.addWidget(self.zoom_out_button)

        self.reset_view_button = QPushButton("Reset View")
        self.reset_view_button.clicked.connect(self.resetViewRequested.emit)
        self.reset_view_button.setToolTip("Reset pan and zoom to default")
        zoom_layout.addWidget(self.reset_view_button)

        size_layout.addLayout(zoom_layout)

        # Add size group to viz layout
        viz_layout.addWidget(size_group)

        # Add keyboard shortcuts info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        shortcuts_text = QLabel(
            "Arrow keys: Pan\n"
            "+/-: Zoom in/out\n"
            "Space: Reset view\n"
            "Esc: Clear selection\n"
            "Ctrl+A: Select all dots\n"
            "Ctrl+Z: Undo selection\n"
            "Ctrl+C: Close polygon\n"
            "Ctrl+S: Toggle selection mode"
        )
        shortcuts_text.setWordWrap(True)
        shortcuts_layout.addWidget(shortcuts_text)

        # Add shortcuts group to viz layout
        viz_layout.addWidget(shortcuts_group)

        # Add spacer to push everything to the top
        viz_layout.addStretch()

        # Return the tab widget
        return viz_tab

    def _create_selection_tab(self):
        """Create the selection tab with interaction controls."""
        selection_tab = QWidget()
        selection_layout = QVBoxLayout(selection_tab)
        selection_layout.setContentsMargins(10, 10, 10, 10)
        selection_layout.setSpacing(10)

        # Mode selection group
        mode_group = QGroupBox("Interaction Mode")
        mode_layout = QHBoxLayout(mode_group)

        self.pan_mode_radio = QRadioButton("Pan && Zoom")
        self.pan_mode_radio.setChecked(True)
        self.pan_mode_radio.toggled.connect(self._on_mode_changed)
        self.pan_mode_radio.setToolTip(
            "Navigate the visualization by panning and zooming"
        )

        self.select_mode_radio = QRadioButton("Select Dots")
        self.select_mode_radio.toggled.connect(self._on_mode_changed)
        self.select_mode_radio.setToolTip("Select dots to analyze or connect")

        mode_layout.addWidget(self.pan_mode_radio)
        mode_layout.addWidget(self.select_mode_radio)

        # Add mode group to selection layout
        selection_layout.addWidget(mode_group)

        # Selection tools group
        tools_group = QGroupBox("Selection Tools")
        tools_layout = QVBoxLayout(tools_group)

        # Selection info
        self.selection_info_label = QLabel("No dots selected")
        self.sum_label = QLabel("Sum: 0")
        self.sum_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.selection_info_label)
        info_layout.addWidget(self.sum_label)
        tools_layout.addLayout(info_layout)

        # Selection buttons
        buttons_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Clear all selections (Esc)")
        self.clear_button.clicked.connect(self.clearSelectionsRequested.emit)
        buttons_layout.addWidget(self.clear_button)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setToolTip("Select all dots (Ctrl+A)")
        self.select_all_button.clicked.connect(self.selectAllRequested.emit)
        buttons_layout.addWidget(self.select_all_button)

        tools_layout.addLayout(buttons_layout)

        # Layer selection
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Layer:"))

        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(1, 20)
        self.layer_spin.setValue(1)
        self.layer_spin.setToolTip("Select a specific layer to highlight")
        layer_layout.addWidget(self.layer_spin)

        self.select_layer_button = QPushButton("Select Layer")
        self.select_layer_button.setToolTip("Select all dots in the specified layer")
        self.select_layer_button.clicked.connect(
            lambda: self.selectLayerRequested.emit(self.layer_spin.value())
        )
        layer_layout.addWidget(self.select_layer_button)

        tools_layout.addLayout(layer_layout)

        # Add tools group to selection layout
        selection_layout.addWidget(tools_group)

        # Connection group
        connection_group = QGroupBox("Connections")
        connection_layout = QVBoxLayout(connection_group)

        # Connection controls
        conn_header_layout = QHBoxLayout()

        self.show_connections_checkbox = QCheckBox("Show Connections")
        self.show_connections_checkbox.setChecked(False)  # Default to off
        self.show_connections_checkbox.toggled.connect(self.showConnectionsChanged.emit)
        self.show_connections_checkbox.setToolTip(
            "Show/hide connections between selected dots"
        )
        conn_header_layout.addWidget(self.show_connections_checkbox)

        self.connection_info_label = QLabel("No connections")
        conn_header_layout.addWidget(self.connection_info_label)

        connection_layout.addLayout(conn_header_layout)

        # Connection buttons
        connection_buttons_layout = QHBoxLayout()

        self.connect_button = QPushButton("Connect")
        self.connect_button.setToolTip("Connect selected dots in order")
        self.connect_button.clicked.connect(self.connectDotsRequested.emit)
        connection_buttons_layout.addWidget(self.connect_button)

        self.close_polygon_button = QPushButton("Close Polygon")
        self.close_polygon_button.setToolTip(
            "Connect the last dot to the first (Ctrl+C)"
        )
        self.close_polygon_button.clicked.connect(self.closePolygonRequested.emit)
        connection_buttons_layout.addWidget(self.close_polygon_button)

        connection_layout.addLayout(connection_buttons_layout)

        # Add connection group to selection layout
        selection_layout.addWidget(connection_group)

        # Add spacer to push everything to the top
        selection_layout.addStretch()

        # Return the tab widget
        return selection_tab

    def _create_groups_tab(self):
        """Create the groups tab with selection group management."""
        groups_tab = QWidget()
        groups_layout = QVBoxLayout(groups_tab)
        groups_layout.setContentsMargins(10, 10, 10, 10)
        groups_layout.setSpacing(10)

        # Create a scroll area to contain all content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Create a widget to hold all the content in the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)

        # ===== STEP 1: INTRODUCTION =====
        # Add a header with step number
        step1_header = QLabel("<b>STEP 1: SELECT DOTS</b>")
        step1_header.setStyleSheet(
            "font-size: 12pt; color: #2c3e50; background-color: #ecf0f1; padding: 5px;"
        )
        scroll_layout.addWidget(step1_header)

        # Introduction with workflow explanation
        intro_box = QGroupBox("How Groups Work")
        intro_layout = QVBoxLayout(intro_box)

        workflow_label = QLabel(
            "<b>Working with Groups:</b><br>"
            "1. <b>Select dots</b> in the visualization (switch to Selection tab if needed)<br>"
            "2. <b>Save or add</b> your selection to a group<br>"
            "3. <b>Switch between groups</b> to view different selections<br>"
            "4. <b>Perform operations</b> between groups to create new patterns"
        )
        workflow_label.setWordWrap(True)
        workflow_label.setTextFormat(Qt.TextFormat.RichText)
        intro_layout.addWidget(workflow_label)

        scroll_layout.addWidget(intro_box)

        # ===== STEP 2: GROUP MANAGEMENT =====
        step2_header = QLabel("<b>STEP 2: MANAGE GROUPS</b>")
        step2_header.setStyleSheet(
            "font-size: 12pt; color: #2c3e50; background-color: #ecf0f1; padding: 5px;"
        )
        scroll_layout.addWidget(step2_header)

        # Current group management
        current_group = QGroupBox("Active Group")
        current_layout = QVBoxLayout(current_group)

        # Group selection with color indicator
        group_selector_layout = QHBoxLayout()

        # Active group label with color box
        group_selector_layout.addWidget(QLabel("Active Group:"))

        # Group combo with color indicators
        self.group_combo = QComboBox()
        self.group_combo.addItem("Default")
        self.group_combo.setToolTip("Select a group to work with")
        self.group_combo.currentTextChanged.connect(self._on_group_changed)
        self.group_combo.setMinimumWidth(200)
        group_selector_layout.addWidget(self.group_combo, 1)  # Give it stretch

        # Add group button
        self.add_group_button = QPushButton("+")
        self.add_group_button.setToolTip("Create a new group")
        self.add_group_button.setMaximumWidth(30)
        self.add_group_button.clicked.connect(self._add_selection_group)
        group_selector_layout.addWidget(self.add_group_button)

        current_layout.addLayout(group_selector_layout)

        # Group status with dot count
        self.group_status_label = QLabel("Group 'Default': 0 dots")
        self.group_status_label.setStyleSheet(
            "font-size: 11pt; font-weight: bold; margin-top: 5px;"
        )
        current_layout.addWidget(self.group_status_label)

        # Show only active group checkbox
        self.show_only_active_group_checkbox = QCheckBox("Show Only Active Group")
        self.show_only_active_group_checkbox.setToolTip(
            "When checked, only dots in the active group will be highlighted"
        )
        self.show_only_active_group_checkbox.toggled.connect(
            self._toggle_show_only_active_group
        )
        current_layout.addWidget(self.show_only_active_group_checkbox)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        current_layout.addWidget(divider)

        # Group action explanation
        action_explanation = QLabel(
            "<b>Save Selection:</b> Open a dialog to save or add your selection to a group<br>"
            "You can create new groups or modify existing ones"
        )
        action_explanation.setWordWrap(True)
        action_explanation.setStyleSheet(
            "color: #555; font-size: 9pt; margin-bottom: 5px;"
        )
        current_layout.addWidget(action_explanation)

        # Group action buttons
        group_buttons_layout = QHBoxLayout()

        self.save_to_group_button = QPushButton("Save Selection...")
        self.save_to_group_button.setToolTip("Save or add current selection to a group")
        self.save_to_group_button.setIcon(QIcon.fromTheme("document-save"))
        # Connect using lambda to ensure the connection works
        self.save_to_group_button.clicked.connect(lambda: self._save_selection_dialog())
        group_buttons_layout.addWidget(self.save_to_group_button)

        current_layout.addLayout(group_buttons_layout)

        # Delete button in a separate row
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()

        self.delete_group_button = QPushButton("Delete Group")
        self.delete_group_button.setToolTip("Delete the active group")
        self.delete_group_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_group_button.clicked.connect(self._delete_current_group)
        self.delete_group_button.setStyleSheet("color: #c0392b;")
        delete_layout.addWidget(self.delete_group_button)

        delete_layout.addStretch()
        current_layout.addLayout(delete_layout)

        scroll_layout.addWidget(current_group)

        # ===== STEP 3: GROUP OPERATIONS =====
        step3_header = QLabel("<b>STEP 3: COMBINE GROUPS (OPTIONAL)</b>")
        step3_header.setStyleSheet(
            "font-size: 12pt; color: #2c3e50; background-color: #ecf0f1; padding: 5px;"
        )
        scroll_layout.addWidget(step3_header)

        # Group operations
        operations_group = QGroupBox("Group Operations")
        operations_layout = QVBoxLayout(operations_group)

        # Visual explanation of operations
        operations_visual = QLabel()
        operations_visual.setPixmap(self._create_operations_diagram())
        operations_visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        operations_layout.addWidget(operations_visual)

        # Operation selection with visual indicators
        op_layout = QFormLayout()

        self.group_op_combo = QComboBox()
        self.group_op_combo.addItems(
            [
                "Union (∪) - All dots from any group",
                "Intersection (∩) - Only dots in all groups",
                "Difference (-) - Dots in first group but not in others",
                "Symmetric Difference (⊕) - Dots in an odd number of groups",
            ]
        )
        self.group_op_combo.setToolTip("Select the set operation to perform")
        op_layout.addRow("Operation:", self.group_op_combo)

        operations_layout.addLayout(op_layout)

        # Group selection for operations
        groups_selection_layout = QVBoxLayout()

        # Label for group selection
        groups_label = QLabel("Select Groups:")
        groups_label.setStyleSheet("font-weight: bold;")
        groups_selection_layout.addWidget(groups_label)

        # Group selection list
        self.groups_list = QListWidget()
        self.groups_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.groups_list.setMinimumHeight(100)
        self.groups_list.setToolTip(
            "Select multiple groups to operate on (Ctrl+click or Shift+click)"
        )
        groups_selection_layout.addWidget(self.groups_list)

        # Note about operations
        note_label = QLabel(
            "<i>Note: For Difference operation, the first selected group is subtracted by all others.</i>"
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #666; font-size: 8pt;")
        groups_selection_layout.addWidget(note_label)

        # Result group name
        result_layout = QFormLayout()
        self.result_group_edit = QLineEdit()
        self.result_group_edit.setPlaceholderText("Auto-generated if left empty")
        self.result_group_edit.setToolTip(
            "Name for the result group (leave empty for auto-naming)"
        )
        result_layout.addRow("Result Group:", self.result_group_edit)
        groups_selection_layout.addLayout(result_layout)

        operations_layout.addLayout(groups_selection_layout)

        # Operation button
        op_button_layout = QHBoxLayout()
        op_button_layout.addStretch()

        self.perform_op_button = QPushButton("Perform Operation")
        self.perform_op_button.setToolTip("Execute the selected operation")
        self.perform_op_button.setIcon(QIcon.fromTheme("system-run"))
        self.perform_op_button.clicked.connect(self._perform_group_operation)
        op_button_layout.addWidget(self.perform_op_button)

        op_button_layout.addStretch()
        operations_layout.addLayout(op_button_layout)

        # Operation result
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.Shape.StyledPanel)
        result_frame.setFrameShadow(QFrame.Shadow.Sunken)
        result_layout = QVBoxLayout(result_frame)

        result_header = QLabel("Operation Result:")
        result_header.setStyleSheet("font-weight: bold;")
        result_layout.addWidget(result_header)

        self.op_result_label = QLabel("No operations performed yet")
        self.op_result_label.setWordWrap(True)
        self.op_result_label.setStyleSheet("color: #444;")
        result_layout.addWidget(self.op_result_label)

        operations_layout.addWidget(result_frame)

        scroll_layout.addWidget(operations_group)

        # ===== STEP 4: EXAMPLES =====
        step4_header = QLabel("<b>EXAMPLES & TIPS</b>")
        step4_header.setStyleSheet(
            "font-size: 12pt; color: #2c3e50; background-color: #ecf0f1; padding: 5px;"
        )
        scroll_layout.addWidget(step4_header)

        # Examples box
        examples_box = QGroupBox("Common Workflows")
        examples_layout = QVBoxLayout(examples_box)

        examples_text = QLabel(
            "<b>Compare Two Patterns:</b><br>"
            "1. Select dots for pattern A and save to 'Group A'<br>"
            "2. Select dots for pattern B and save to 'Group B'<br>"
            "3. Use Union to see all dots, or Intersection to see overlaps<br><br>"
            "<b>Find Unique Elements:</b><br>"
            "1. Create two groups with different selections<br>"
            "2. Use Difference (A - B) to see what's in A but not in B<br><br>"
            "<b>Build Complex Patterns:</b><br>"
            "1. Create groups for basic patterns<br>"
            "2. Combine them with operations to create complex patterns<br>"
        )
        examples_text.setWordWrap(True)
        examples_text.setTextFormat(Qt.TextFormat.RichText)
        examples_layout.addWidget(examples_text)

        scroll_layout.addWidget(examples_box)

        # Add spacer to push everything to the top
        scroll_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(scroll_content)
        groups_layout.addWidget(scroll_area)

        # Return the tab widget
        return groups_tab

    def _create_operations_diagram(self) -> QPixmap:
        """Create a diagram showing set operations visually."""
        # Create a pixmap for the diagram
        pixmap = QPixmap(400, 100)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define colors
        color_a = QColor(70, 130, 180, 150)  # Steel blue, semi-transparent
        color_b = QColor(220, 20, 60, 150)  # Crimson, semi-transparent
        color_overlap = QColor(128, 0, 128, 200)  # Purple, more opaque

        # Draw the set operation diagrams
        # Union
        painter.setBrush(color_a)
        painter.drawEllipse(20, 20, 60, 60)
        painter.setBrush(color_b)
        painter.drawEllipse(50, 20, 60, 60)
        painter.drawText(40, 90, "Union")

        # Intersection
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(130, 20, 60, 60)
        painter.drawEllipse(160, 20, 60, 60)
        painter.setBrush(color_overlap)
        painter.drawEllipse(145, 20, 30, 60)
        painter.drawText(140, 90, "Intersection")

        # Difference
        painter.setBrush(color_a)
        painter.drawEllipse(240, 20, 60, 60)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(270, 20, 60, 60)
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(270, 20, 30, 60)
        painter.drawText(250, 90, "Difference")

        # Symmetric Difference
        painter.setBrush(color_a)
        painter.drawEllipse(350, 20, 60, 60)
        painter.setBrush(color_b)
        painter.drawEllipse(380, 20, 60, 60)
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(365, 20, 30, 60)
        painter.drawText(340, 90, "Sym. Difference")

        painter.end()
        return pixmap

    def _create_analysis_tab(self):
        """Create the analysis tab with mathematical operations."""
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        analysis_layout.setSpacing(10)

        # Presets group
        presets_group = QGroupBox("Number Pattern Selection")
        presets_layout = QVBoxLayout(presets_group)

        # Add explanation label
        explanation_label = QLabel(
            "Select dots that match specific number patterns or properties. "
            "Use these tools to explore mathematical relationships in the visualization."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("color: #444; font-style: italic;")
        presets_layout.addWidget(explanation_label)

        # Preset selection
        preset_combo_layout = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            [
                "Prime Numbers",
                "Even Numbers",
                "Odd Numbers",
                "Divisible by N",
                "Not Divisible by N",
                "Fibonacci Sequence",
                "Triangle Numbers",
                "Square Numbers",
                "Pentagonal Numbers",
            ]
        )
        self.preset_combo.setToolTip(
            "Select a number pattern to highlight dots with specific properties"
        )
        preset_combo_layout.addRow("Pattern:", self.preset_combo)
        presets_layout.addLayout(preset_combo_layout)

        # Preset parameters
        self.preset_params_widget = QWidget()
        self.preset_params_layout = QFormLayout(self.preset_params_widget)

        # Parameter for divisibility
        self.divisible_by_spin = QSpinBox()
        self.divisible_by_spin.setRange(2, 20)
        self.divisible_by_spin.setValue(2)
        self.divisible_by_spin.setToolTip(
            "Select the divisor for divisibility patterns"
        )
        self.preset_params_layout.addRow("Divisor (N):", self.divisible_by_spin)

        # Parameter description label
        self.param_description_label = QLabel("")
        self.param_description_label.setWordWrap(True)
        self.param_description_label.setStyleSheet("color: #666; font-size: 8pt;")
        self.preset_params_layout.addRow("", self.param_description_label)

        presets_layout.addWidget(self.preset_params_widget)

        # Apply preset button
        preset_button_layout = QHBoxLayout()

        self.create_preset_button = QPushButton("Select Pattern")
        self.create_preset_button.setToolTip(
            "Select dots that match the chosen number pattern"
        )
        preset_button_layout.addWidget(self.create_preset_button)

        self.save_pattern_group_button = QPushButton("Save as Group")
        self.save_pattern_group_button.setToolTip(
            "Save dots matching the pattern as a new group"
        )
        preset_button_layout.addWidget(self.save_pattern_group_button)

        presets_layout.addLayout(preset_button_layout)

        # Result label
        self.preset_result_label = QLabel("")
        self.preset_result_label.setWordWrap(True)
        self.preset_result_label.setStyleSheet("color: #444; font-weight: bold;")
        presets_layout.addWidget(self.preset_result_label)

        # Connect preset combo to update parameters
        self.preset_combo.currentTextChanged.connect(self._update_preset_params)

        # Connect preset buttons
        self.create_preset_button.clicked.connect(lambda: self._apply_preset(False))
        self.save_pattern_group_button.clicked.connect(self._save_pattern_as_group)

        # Add presets group to analysis layout
        analysis_layout.addWidget(presets_group)

        # Add spacer to push everything to the top
        analysis_layout.addStretch()

        # Return the tab widget
        return analysis_tab

    def _create_status_bar(self):
        """Create a status bar at the bottom of the panel."""
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)

        # Status label
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        # Add spacer to push everything to the left
        status_layout.addStretch()

    def _on_type_changed(self, checked):
        """Handle type selection change.

        Args:
            checked: Whether the radio button is checked
        """
        if checked and self.sender() == self.centered_radio:
            self.typeChanged.emit(True)  # Centered
        elif checked and self.sender() == self.regular_radio:
            self.typeChanged.emit(False)  # Regular

    def _on_sides_combo_changed(self, _):
        """Handle sides combo selection change.

        Args:
            _: Index of the selected item (unused)
        """
        sides = self.sides_combo.currentData()

        if sides == -1:  # Custom option selected
            # Show the spinbox and use its value
            self.sides_spin.setVisible(True)
            sides = self.sides_spin.value()
        else:
            # Hide the spinbox
            self.sides_spin.setVisible(False)

        self.sidesChanged.emit(sides)

    def _on_sides_spin_changed(self, value):
        """Handle sides spin value change.

        Args:
            value: New sides value
        """
        # Only emit if the custom option is selected
        if self.sides_combo.currentData() == -1:
            self.sidesChanged.emit(value)

    def _on_color_scheme_changed(self, scheme: str) -> None:
        """Handle color scheme selection change.

        Args:
            scheme: Name of the selected color scheme
        """
        # Convert to lowercase for internal use
        scheme_lower = scheme.lower()
        self.colorSchemeChanged.emit(scheme_lower)

    def _update_preset_params(self) -> None:
        """Update the parameter widgets based on the selected preset."""
        preset_name = self.preset_combo.currentText()

        # Hide all parameter widgets by default
        for i in range(self.preset_params_layout.rowCount()):
            if i == 0:  # Keep the divisor parameter row
                self.preset_params_layout.itemAt(
                    i, QFormLayout.ItemRole.LabelRole
                ).widget().setVisible(False)
                self.preset_params_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                ).widget().setVisible(False)

        # Show appropriate parameters and set description based on preset
        if preset_name == "Prime Numbers":
            self.param_description_label.setText(
                "Selects all prime numbers in the visualization. "
                "Prime numbers are divisible only by 1 and themselves."
            )

        elif preset_name == "Even Numbers":
            self.param_description_label.setText(
                "Selects all even numbers (divisible by 2) in the visualization."
            )

        elif preset_name == "Odd Numbers":
            self.param_description_label.setText(
                "Selects all odd numbers (not divisible by 2) in the visualization."
            )

        elif preset_name == "Divisible by N":
            # Show divisibility parameter
            self.preset_params_layout.itemAt(
                0, QFormLayout.ItemRole.LabelRole
            ).widget().setVisible(True)
            self.preset_params_layout.itemAt(
                0, QFormLayout.ItemRole.FieldRole
            ).widget().setVisible(True)

            self.param_description_label.setText(
                f"Selects all numbers that are divisible by {self.divisible_by_spin.value()}. "
                "Adjust the divisor to explore different patterns."
            )

        elif preset_name == "Not Divisible by N":
            # Show divisibility parameter
            self.preset_params_layout.itemAt(
                0, QFormLayout.ItemRole.LabelRole
            ).widget().setVisible(True)
            self.preset_params_layout.itemAt(
                0, QFormLayout.ItemRole.FieldRole
            ).widget().setVisible(True)

            self.param_description_label.setText(
                f"Selects all numbers that are NOT divisible by {self.divisible_by_spin.value()}. "
                "Adjust the divisor to explore different patterns."
            )

        elif preset_name == "Fibonacci Sequence":
            self.param_description_label.setText(
                "Selects all Fibonacci numbers in the visualization. "
                "The Fibonacci sequence starts with 1, 1 and each number is the sum of the two preceding ones."
            )

        elif preset_name == "Triangle Numbers":
            self.param_description_label.setText(
                "Selects all triangular numbers in the visualization. "
                "Triangular numbers follow the formula n(n+1)/2."
            )

        elif preset_name == "Square Numbers":
            self.param_description_label.setText(
                "Selects all perfect squares in the visualization. "
                "Square numbers follow the formula n²."
            )

        elif preset_name == "Pentagonal Numbers":
            self.param_description_label.setText(
                "Selects all pentagonal numbers in the visualization. "
                "Pentagonal numbers follow the formula n(3n-1)/2."
            )

        # Update the divisor parameter when it changes
        self.divisible_by_spin.valueChanged.connect(self._update_divisor_description)

    def _update_divisor_description(self) -> None:
        """Update the description when the divisor value changes."""
        preset_name = self.preset_combo.currentText()

        if preset_name == "Divisible by N":
            self.param_description_label.setText(
                f"Selects all numbers that are divisible by {self.divisible_by_spin.value()}. "
                "Adjust the divisor to explore different patterns."
            )
        elif preset_name == "Not Divisible by N":
            self.param_description_label.setText(
                f"Selects all numbers that are NOT divisible by {self.divisible_by_spin.value()}. "
                "Adjust the divisor to explore different patterns."
            )

    def _apply_preset(self, add: bool = False) -> None:
        """Apply the selected preset to create a selection.

        Args:
            add: Whether to add to the current selection or replace it
        """
        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            self.preset_result_label.setText("Cannot access visualization")
            return

        # Get the selected preset
        preset_name = self.preset_combo.currentText()

        # Map preset names to internal preset types and prepare parameters
        preset_type = ""
        params = {}

        if preset_name == "Prime Numbers":
            preset_type = "primes"

        elif preset_name == "Even Numbers":
            preset_type = "even"

        elif preset_name == "Odd Numbers":
            preset_type = "odd"

        elif preset_name == "Divisible by N":
            preset_type = "divisible"
            params["n"] = self.divisible_by_spin.value()

        elif preset_name == "Not Divisible by N":
            preset_type = "not_divisible"
            params["n"] = self.divisible_by_spin.value()

        elif preset_name == "Fibonacci Sequence":
            preset_type = "fibonacci"

        elif preset_name == "Triangle Numbers":
            preset_type = "triangular"

        elif preset_name == "Square Numbers":
            preset_type = "square"

        elif preset_name == "Pentagonal Numbers":
            preset_type = "pentagonal"

        # Create the selection
        if preset_type:
            try:
                # Get the dots that match the pattern
                result = viz.create_preset_selection(preset_type, params)

                if result:
                    # Apply the selection to the visualization
                    viz.select_dots_by_indices(
                        result, not add
                    )  # Replace unless 'add' is True

                    # Update the result label
                    action = "Added" if add else "Selected"
                    self.preset_result_label.setText(
                        f"{action} {len(result)} dots matching the '{preset_name}' pattern"
                    )
                else:
                    self.preset_result_label.setText(
                        f"No dots match the '{preset_name}' pattern"
                    )
            except Exception as e:
                import logging

                logging.getLogger(__name__).error(f"Error applying preset: {e}")
                self.preset_result_label.setText(f"Error: {str(e)}")
        else:
            self.preset_result_label.setText(f"Preset '{preset_name}' not implemented")

    def _save_pattern_as_group(self) -> None:
        """Save the current pattern selection as a new group."""
        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            self.preset_result_label.setText("Cannot access visualization")
            return

        # Get the selected preset
        preset_name = self.preset_combo.currentText()

        # Map preset names to internal preset types and prepare parameters
        preset_type = ""
        params = {}

        if preset_name == "Prime Numbers":
            preset_type = "primes"

        elif preset_name == "Even Numbers":
            preset_type = "even"

        elif preset_name == "Odd Numbers":
            preset_type = "odd"

        elif preset_name == "Divisible by N":
            preset_type = "divisible"
            params["n"] = self.divisible_by_spin.value()
            # Update the preset name to include the divisor
            preset_name = f"Divisible by {self.divisible_by_spin.value()}"

        elif preset_name == "Not Divisible by N":
            preset_type = "not_divisible"
            params["n"] = self.divisible_by_spin.value()
            # Update the preset name to include the divisor
            preset_name = f"Not Divisible by {self.divisible_by_spin.value()}"

        elif preset_name == "Fibonacci Sequence":
            preset_type = "fibonacci"

        elif preset_name == "Triangle Numbers":
            preset_type = "triangular"

        elif preset_name == "Square Numbers":
            preset_type = "square"

        elif preset_name == "Pentagonal Numbers":
            preset_type = "pentagonal"

        # Create the selection
        if preset_type:
            try:
                # Get the dots that match the pattern
                result = viz.create_preset_selection(preset_type, params)

                if not result:
                    self.preset_result_label.setText(
                        f"No dots match the '{preset_name}' pattern"
                    )
                    return

                # Generate a unique group name based on the pattern
                base_group_name = f"Pattern: {preset_name}"
                group_name = base_group_name

                # Ensure the name is unique
                counter = 1
                while group_name in viz.selection_groups and counter < 100:
                    group_name = f"{base_group_name} ({counter})"
                    counter += 1

                # Create the group and add the dots
                viz.selection_groups[group_name] = result.copy()

                # Generate a color for the group based on the pattern type
                # Use a hash of the preset_type to get a consistent color for each pattern type
                hue = hash(preset_type) % 360
                color = QColor.fromHsv(hue, 200, 220)
                viz.set_group_color(group_name, color)

                # Update the UI
                self.preset_result_label.setText(
                    f"Saved {len(result)} dots matching '{preset_name}' as group '{group_name}'"
                )

                # Update the group comboboxes
                self._sync_group_comboboxes()

                # Switch to the new group
                self.group_combo.setCurrentText(group_name)
                self._on_group_changed(group_name)

                # Switch to the Groups tab to show the new group
                self.tab_widget.setCurrentIndex(3)  # Index 3 is the Groups tab

            except Exception as e:
                import logging

                logging.getLogger(__name__).error(f"Error saving pattern as group: {e}")
                self.preset_result_label.setText(f"Error: {str(e)}")
        else:
            self.preset_result_label.setText(f"Preset '{preset_name}' not implemented")

    def _on_index_changed(self, value):
        """Handle index spinner change.

        Args:
            value: New index value
        """
        self.index_slider.setValue(value)  # Update slider to match
        self.indexChanged.emit(value)

    def _on_slider_changed(self, value):
        """Handle index slider change.

        Args:
            value: New index value
        """
        self.index_spin.setValue(value)  # Update spinner to match
        self.indexChanged.emit(value)

    def _on_animation_toggled(self):
        """Handle animation toggle."""
        # Toggle animation state
        if self.play_button.text() == "▶ Play":
            self.play_button.setText("⏸ Pause")
            self.animationToggled.emit(True)  # Start animation
        else:
            self.play_button.setText("▶ Play")
            self.animationToggled.emit(False)  # Stop animation

    def _on_mode_changed(self, checked):
        """Handle mode selection change.

        Args:
            checked: Whether the radio button is checked
        """
        if checked:
            # Only emit for the selected radio button
            if self.sender() == self.select_mode_radio:
                self.selectionModeChanged.emit(True)  # Selection mode
            elif self.sender() == self.pan_mode_radio:
                self.selectionModeChanged.emit(False)  # Pan mode

    def update_value_display(self, value):
        """Update the value display.

        Args:
            value: Current polygonal number value
        """
        self.value_label.setText(f"Value: {value}")

    def update_selection_info(self, selected_count, selected_sum):
        """Update the selection information display.

        Args:
            selected_count: Number of selected dots
            selected_sum: Sum of selected dot values
        """
        if selected_count == 0:
            self.selection_info_label.setText("No dots selected")
        elif selected_count == 1:
            self.selection_info_label.setText("1 dot selected")
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
            self.connection_info_label.setText("1 connection")
        else:
            self.connection_info_label.setText(f"{connection_count} connections")

    def _on_group_changed(self, group_name):
        """Handle selection group change.

        Args:
            group_name: Name of the selected group
        """
        if group_name:
            # Get the visualization using our helper method
            viz = self.get_visualization()
            if not viz:
                print("Error: Cannot access visualization in _on_group_changed")
                return

            # Make sure the group exists
            if group_name not in viz.selection_groups:
                viz.selection_groups[group_name] = []

            # Update the current group
            viz.current_group = group_name

            # Update the selection to match the group
            viz.selected_dots = viz.selection_groups[group_name].copy()

            # Debug output
            print(f"Changed to group '{group_name}' with {len(viz.selected_dots)} dots")
            print(f"Group contents: {viz.selection_groups[group_name]}")

            # Update the UI
            self.group_status_label.setText(
                f"Group '{group_name}': {len(viz.selection_groups[group_name])} dots"
            )

            # If "Show Only Active Group" is checked, update the visualization
            # This ensures the correct group is highlighted
            if (
                hasattr(self, "show_only_active_group_checkbox")
                and self.show_only_active_group_checkbox.isChecked()
            ):
                print(
                    f"Updating visualization for 'Show Only Active Group' with active group: {group_name}"
                )
                viz.update()
            else:
                # Update the visualization normally
                viz.update()

            # Emit the signal for other components
            self.selectionGroupChanged.emit(group_name)
            self._update_color_button()

    def _update_color_button(self):
        """Update the color button to reflect the current group's color."""
        # This will be implemented when we connect to the visualization
        pass

    def _add_selection_group(self):
        """Add a new selection group."""
        group_name, ok = QInputDialog.getText(
            self, "New Selection Group", "Enter group name:"
        )

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

    def _save_selection_dialog(self):
        """Open a dialog to save the current selection to a group."""
        print("_save_selection_dialog called!")

        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        # Get current selection
        selected_dots = viz.selected_dots.copy()

        if not selected_dots:
            # Show a message that there's nothing to save
            self.op_result_label.setText("No dots selected to save to group")
            return

        # Get existing groups
        existing_groups = list(viz.selection_groups.keys())
        if "Default" not in existing_groups:
            existing_groups.insert(0, "Default")

        # Create a custom dialog directly here
        dialog = QDialog(self)
        dialog.setWindowTitle("Save Selection")
        dialog.setMinimumWidth(400)
        dialog.setModal(True)

        # Main layout
        layout = QVBoxLayout(dialog)

        # Selection info
        info_label = QLabel(f"<b>{len(selected_dots)} dots selected</b>")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Mode selection
        mode_group = QGroupBox("Save Mode")
        mode_layout = QVBoxLayout(mode_group)

        save_radio = QRadioButton("Replace group contents")
        save_radio.setChecked(True)
        mode_layout.addWidget(save_radio)

        add_radio = QRadioButton("Add to existing group")
        mode_layout.addWidget(add_radio)

        layout.addWidget(mode_group)

        # Group selection
        group_group = QGroupBox("Select Group")
        group_box_layout = QVBoxLayout(group_group)

        # Existing group option
        existing_radio = QRadioButton("Use existing group:")
        existing_radio.setChecked(True)
        group_box_layout.addWidget(existing_radio)

        # Group combo
        group_combo = QComboBox()
        for group in existing_groups:
            group_combo.addItem(group)
        group_box_layout.addWidget(group_combo)

        # New group option
        new_radio = QRadioButton("Create new group:")
        group_box_layout.addWidget(new_radio)

        # New group name
        new_group_edit = QLineEdit()
        new_group_edit.setPlaceholderText("Enter new group name")
        new_group_edit.setEnabled(False)
        group_box_layout.addWidget(new_group_edit)

        # Connect radio buttons to enable/disable fields
        def toggle_group_options(_):  # Ignore the checked parameter
            if existing_radio.isChecked():
                group_combo.setEnabled(True)
                new_group_edit.setEnabled(False)
            else:
                group_combo.setEnabled(False)
                new_group_edit.setEnabled(True)

        existing_radio.toggled.connect(toggle_group_options)
        new_radio.toggled.connect(toggle_group_options)

        layout.addWidget(group_group)

        # Color selection
        color_group = QGroupBox("Group Color")
        color_layout = QHBoxLayout(color_group)

        # Color preview
        color_preview = QFrame()
        color_preview.setFrameShape(QFrame.Shape.Box)
        color_preview.setMinimumSize(30, 30)
        color_preview.setMaximumSize(30, 30)
        color_preview.setStyleSheet("background-color: #3498db;")  # Default blue
        color_layout.addWidget(color_preview)

        # Store the color
        selected_color = QColor(52, 152, 219)  # Default blue

        # Color button
        color_button = QPushButton("Choose Color")

        def choose_color():
            nonlocal selected_color
            color = QColorDialog.getColor(selected_color, dialog, "Choose Group Color")
            if color.isValid():
                selected_color = color
                color_preview.setStyleSheet(f"background-color: {color.name()};")

        color_button.clicked.connect(choose_color)
        color_layout.addWidget(color_button)

        layout.addWidget(color_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show the dialog
        print("Showing dialog...")
        result = dialog.exec()
        print(f"Dialog result: {result}")

        if result:
            # Get the values from the dialog
            if existing_radio.isChecked():
                group_name = group_combo.currentText()
            else:
                group_name = new_group_edit.text()

            is_save_mode = save_radio.isChecked()

            print(
                f"Got result: group={group_name}, mode={'save' if is_save_mode else 'add'}"
            )

            if not group_name:
                return

            # Create the group if it doesn't exist
            if group_name not in viz.selection_groups:
                viz.selection_groups[group_name] = []

            # Save or add to the group based on mode
            if is_save_mode:
                # Replace the group contents
                viz.selection_groups[group_name] = selected_dots.copy()
                action_text = "Saved"
            else:
                # Add to the group, avoiding duplicates
                added_count = 0
                for dot in selected_dots:
                    if dot not in viz.selection_groups[group_name]:
                        viz.selection_groups[group_name].append(dot)
                        added_count += 1

                # Sort for consistency
                viz.selection_groups[group_name].sort()
                action_text = "Added"

            # Set current group
            viz.current_group = group_name

            # Set the group color
            viz.set_group_color(group_name, selected_color)

            # Debug output
            print(f"{action_text} {len(selected_dots)} dots to group '{group_name}'")
            print(f"Group contents: {viz.selection_groups[group_name]}")

            # No need to save groups to disk anymore, they're managed in memory

            # Update the UI
            self.op_result_label.setText(
                f"{action_text} {len(selected_dots)} dots to group '{group_name}'"
            )
            self.group_status_label.setText(
                f"Group '{group_name}': {len(viz.selection_groups[group_name])} dots"
            )

            # Always sync the combo boxes to ensure they're up to date
            self._sync_group_comboboxes()

            # Select the group in the combo box
            self.group_combo.setCurrentText(group_name)

            # Debug output
            print(f"After saving, group_combo has {self.group_combo.count()} items")
            print(f"Current group in combo box: {self.group_combo.currentText()}")

    def _delete_current_group(self):
        """Delete the current selection group."""
        group_name = self.group_combo.currentText()

        if group_name == "Default":
            self.op_result_label.setText("Cannot delete the Default group")
            return

        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        if group_name in viz.selection_groups:
            # If current selection is from this group, clear it
            if viz.current_group == group_name:
                viz.selected_dots = []
                viz.current_group = "Default"

            # Remove the group
            del viz.selection_groups[group_name]

            # Also remove the color if it exists
            if group_name in viz.group_colors:
                del viz.group_colors[group_name]

            # No need to save groups to disk anymore, they're managed in memory

            # Update the combo boxes
            self._sync_group_comboboxes()

            # Select the Default group
            self.group_combo.setCurrentText("Default")

            # Update the UI
            self.op_result_label.setText(f"Deleted group '{group_name}'")
            self.group_status_label.setText("Group 'Default': 0 dots")

    def _populate_group_comboboxes(self):
        """Populate group combo boxes with saved groups from the visualization."""
        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        # No need to load groups from disk anymore, they're managed in memory

        # Get all groups from the visualization
        groups = list(viz.selection_groups.keys())

        # Debug output
        print(f"Found {len(groups)} groups: {groups}")
        for group_name, dots in viz.selection_groups.items():
            print(f"Group '{group_name}' has {len(dots)} dots: {dots}")

        # Make sure Default is always first
        if "Default" in groups:
            groups.remove("Default")
            groups.insert(0, "Default")
        else:
            groups.insert(0, "Default")
            viz.selection_groups["Default"] = []

        # Clear all comboboxes and lists
        self.group_combo.clear()

        # Also clear the groups list if it exists
        if hasattr(self, "groups_list"):
            self.groups_list.clear()

        # Add all groups to the combo box and list
        for group in groups:
            self.group_combo.addItem(group)

            # Add to the groups list if it exists
            if hasattr(self, "groups_list"):
                self.groups_list.addItem(group)

        # Set the current group in the visualization
        if groups and viz.current_group not in groups:
            viz.current_group = groups[0]

    def _sync_group_comboboxes(self):
        """Ensure all group comboboxes have the same entries."""
        # Get the visualization to get the latest groups
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization in _sync_group_comboboxes")
            return

        # Get all groups from the visualization
        groups = list(viz.selection_groups.keys())

        # Debug output
        print(f"Syncing comboboxes with {len(groups)} groups: {groups}")

        # Make sure Default is always first
        if "Default" in groups:
            groups.remove("Default")
            groups.insert(0, "Default")
        else:
            groups.insert(0, "Default")

        # Clear all comboboxes and lists
        self.group_combo.clear()

        # Also clear the groups list if it exists
        if hasattr(self, "groups_list"):
            self.groups_list.clear()

        # Add all groups to the combo box and list
        for group in groups:
            self.group_combo.addItem(group)

            # Add to the groups list if it exists
            if hasattr(self, "groups_list"):
                self.groups_list.addItem(group)

        # Debug output
        print(f"After sync, group_combo has {self.group_combo.count()} items")

    def _change_group_color(self):
        """Change the color of the current group."""
        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return
        current_group = self.group_combo.currentText()

        if not current_group:
            return

        # Get the current color
        current_color = viz.get_group_color(current_group)

        # Open color dialog
        color = QColorDialog.getColor(
            current_color, self, f"Select Color for '{current_group}'"
        )

        # If a valid color was chosen
        if color.isValid():
            # Set the color for the group
            viz.set_group_color(current_group, color)

            # Update the color button
            self._update_color_button()

            # Update the visualization
            viz.update()

    def _perform_group_operation(self):
        """Perform the selected group operation with multiple groups."""
        # Get the visualization using our helper method
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        # Get operation type
        op_text = self.group_op_combo.currentText()
        operation = ""

        if "Union" in op_text:
            operation = "union"
        elif "Intersection" in op_text:
            operation = "intersection"
        elif "Difference" in op_text:
            operation = "difference"
        elif "Symmetric" in op_text:
            operation = "symmetric_difference"

        # Get selected groups
        selected_items = self.groups_list.selectedItems()
        selected_groups = [item.text() for item in selected_items]

        # Get result group name (or leave empty for auto-naming)
        result_group = self.result_group_edit.text().strip()

        # Validate
        if len(selected_groups) < 2:
            self.op_result_label.setText(
                "Please select at least two groups for the operation"
            )
            return

        # For difference operation, warn if more than 2 groups are selected
        if operation == "difference" and len(selected_groups) > 2:
            # Just a note, not an error - we'll proceed with the operation
            print(
                f"Note: Difference operation with {len(selected_groups)} groups: {selected_groups[0]} minus all others"
            )

        # Perform the operation
        viz.perform_group_operation(operation, selected_groups, result_group)

        # Get the actual result group name (might have been auto-generated)
        if not result_group:
            # Find the most recently added group
            all_groups = list(viz.selection_groups.keys())
            # The result group should be the one that's not in our original list
            for group in all_groups:
                if group not in selected_groups and group != "Default":
                    result_group = group
                    break

        # Ensure the result group is in the combo boxes and lists
        self._sync_group_comboboxes()

        # Select the result group in the list
        if result_group:
            for i in range(self.groups_list.count()):
                if self.groups_list.item(i).text() == result_group:
                    self.groups_list.item(i).setSelected(True)
                    break

        # Update the UI
        result_count = len(viz.selection_groups.get(result_group, []))

        # Create a readable description of the operation
        op_symbol = {
            "union": "∪",
            "intersection": "∩",
            "difference": "−",
            "symmetric_difference": "⊕",
        }.get(operation, operation)

        # Format the group list for display
        if len(selected_groups) <= 3:
            groups_text = ", ".join(selected_groups)
        else:
            groups_text = f"{selected_groups[0]}, {selected_groups[1]}, ... ({len(selected_groups)} groups)"

        self.op_result_label.setText(
            f"Operation completed: {op_symbol}({groups_text})\n"
            f"Result saved to '{result_group}' with {result_count} dots"
        )

        # Update group status if result group is the current group
        if result_group == self.group_combo.currentText():
            self.group_status_label.setText(
                f"Group '{result_group}': {result_count} dots"
            )

    def update_status(self, status_text):
        """Update the status bar.

        Args:
            status_text: Status text to display
        """
        self.status_label.setText(status_text)

    def set_animation_state(self, is_playing):
        """Set the animation button state.

        Args:
            is_playing: Whether animation is playing
        """
        self.play_button.setText("⏸ Pause" if is_playing else "▶ Play")

    def set_selection_mode(self, is_selection_mode):
        """Set the selection mode.

        Args:
            is_selection_mode: Whether selection mode is active
        """
        self.select_mode_radio.setChecked(is_selection_mode)
        self.pan_mode_radio.setChecked(not is_selection_mode)

    def _toggle_show_only_active_group(self, checked):
        """Toggle showing only the active group.

        Args:
            checked: Whether to show only the active group
        """
        # Get the visualization
        viz = self.get_visualization()
        if not viz:
            print(
                "Error: Cannot access visualization in _toggle_show_only_active_group"
            )
            return

        # Set the flag in the visualization
        viz.show_only_active_group = checked

        # Update the visualization
        viz.update()

        # Debug output
        print(f"Show only active group: {checked}")

    def _add_selection_group(self):
        """Create a new empty selection group."""
        # Get the visualization
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization in _add_selection_group")
            return

        # Ask for the group name
        group_name, ok = QInputDialog.getText(
            self, "New Group", "Enter name for new group:", text="New Group"
        )

        if not ok or not group_name:
            return

        # Check if the group already exists
        if group_name in viz.selection_groups:
            # Ask if they want to replace it
            from PyQt6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "Group Exists",
                f"Group '{group_name}' already exists. Replace it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                return

        # Create the group
        viz.selection_groups[group_name] = []

        # Set a default color
        viz.set_group_color(group_name, QColor(52, 152, 219))  # Default blue

        # No need to save groups to disk anymore, they're managed in memory

        # Update the UI
        self._sync_group_comboboxes()

        # Select the new group
        self.group_combo.setCurrentText(group_name)

        # Update the status
        self.op_result_label.setText(f"Created empty group '{group_name}'")
        self.group_status_label.setText(f"Group '{group_name}': 0 dots")

        # Debug output
        print(f"Created new group: {group_name}")
        print(f"After adding, group_combo has {self.group_combo.count()} items")
        print(f"Current group in combo box: {self.group_combo.currentText()}")

    def _on_tab_changed(self, index):
        """Handle tab change events.

        Args:
            index: Index of the selected tab
        """
        # Check if the groups tab is selected (index 3)
        if index == 3:  # Groups tab
            print("Groups tab selected, refreshing groups")
            # Refresh the groups
            self._populate_group_comboboxes()
        # Check if the visualizations tab is selected (index 5)
        elif index == 5:  # Visualizations tab
            print("Visualizations tab selected, updating info")
            # Update visualization info
            self._update_visualization_info()
            # Refresh the visualization list
            self._populate_visualization_list()

    def _create_visualizations_tab(self):
        """Create the Visualizations tab for saving and loading visualizations.

        Returns:
            The visualizations tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Current Visualization Info
        info_group = QGroupBox("Current Visualization")
        info_layout = QFormLayout(info_group)

        self.viz_type_label = QLabel("Type: Regular")
        self.viz_sides_label = QLabel("Sides: 3")
        self.viz_index_label = QLabel("Index: 1")

        info_layout.addRow("Type:", self.viz_type_label)
        info_layout.addRow("Sides:", self.viz_sides_label)
        info_layout.addRow("Index:", self.viz_index_label)

        layout.addWidget(info_group)

        # Save Visualization Section
        save_group = QGroupBox("Save Visualization")
        save_layout = QVBoxLayout(save_group)

        save_form = QFormLayout()
        self.viz_name_edit = QLineEdit()
        self.viz_desc_edit = QTextEdit()
        self.viz_desc_edit.setMaximumHeight(60)

        save_form.addRow("Name:", self.viz_name_edit)
        save_form.addRow("Description:", self.viz_desc_edit)

        save_layout.addLayout(save_form)

        save_button = QPushButton("Save Visualization")
        save_button.clicked.connect(self._save_current_visualization)
        save_layout.addWidget(save_button)

        layout.addWidget(save_group)

        # Load Visualization Section
        load_group = QGroupBox("Saved Visualizations")
        load_layout = QVBoxLayout(load_group)

        self.viz_list = QListWidget()
        self.viz_list.itemSelectionChanged.connect(self._on_viz_selection_changed)
        load_layout.addWidget(self.viz_list)

        button_layout = QHBoxLayout()
        load_button = QPushButton("Load")
        load_button.clicked.connect(self._load_selected_visualization)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_selected_visualization)

        button_layout.addWidget(load_button)
        button_layout.addWidget(delete_button)
        load_layout.addLayout(button_layout)

        layout.addWidget(load_group)

        # Add spacer to push everything to the top
        layout.addStretch()

        # Populate the list
        self._populate_visualization_list()

        return tab

    def _save_current_visualization(self):
        """Save the current visualization."""
        # Get the visualization
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        # Get the name and description
        name = self.viz_name_edit.text()
        if not name:
            QMessageBox.warning(
                self, "Save Visualization", "Please enter a name for the visualization"
            )
            return

        description = self.viz_desc_edit.toPlainText()

        # Create a SavedVisualization object
        saved_viz = SavedVisualization(
            name=name,
            description=description,
            viz_type="centered" if viz.calculator.is_centered else "regular",
            sides=viz.calculator.sides,
            index=viz.calculator.index,
        )

        # Copy groups and colors
        saved_viz.groups = viz.selection_groups.copy()
        saved_viz.colors = viz.group_colors.copy()

        # Copy connections
        saved_viz.connections = viz.connections.copy()

        # Save it
        manager = VisualizationManager()
        if manager.save_visualization(saved_viz):
            QMessageBox.information(
                self, "Save Visualization", f"Visualization '{name}' saved successfully"
            )
            self._populate_visualization_list()
        else:
            QMessageBox.warning(
                self, "Save Visualization", "Failed to save visualization"
            )

    def _populate_visualization_list(self):
        """Populate the visualization list."""
        self.viz_list.clear()

        manager = VisualizationManager()
        visualizations = manager.get_all_visualizations()

        for viz_id, viz_info in visualizations.items():
            item = QListWidgetItem(
                f"{viz_info['name']} ({viz_info['type']}, {viz_info['sides']}, {viz_info['index']})"
            )
            item.setData(Qt.ItemDataRole.UserRole, viz_id)
            self.viz_list.addItem(item)

    def _on_viz_selection_changed(self):
        """Handle visualization selection change."""
        # Could add preview functionality here
        pass

    def _load_selected_visualization(self):
        """Load the selected visualization."""
        selected_items = self.viz_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Load Visualization", "Please select a visualization to load"
            )
            return

        viz_id = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # Load the visualization
        manager = VisualizationManager()
        saved_viz = manager.load_visualization(viz_id)

        if not saved_viz:
            QMessageBox.warning(
                self, "Load Visualization", "Failed to load visualization"
            )
            return

        # Get the visualization
        viz = self.get_visualization()
        if not viz:
            print("Error: Cannot access visualization")
            return

        # Update the visualization parameters
        viz.calculator.set_centered(saved_viz.type == "centered")
        viz.calculator.set_sides(saved_viz.sides)
        viz.calculator.set_index(saved_viz.index)

        # Update the groups and colors
        viz.selection_groups = saved_viz.groups.copy()
        viz.group_colors = saved_viz.colors.copy()

        # Load connections
        if hasattr(saved_viz, "connections") and saved_viz.connections:
            # Clear existing connections
            viz.connections = []

            # Import the Connection class
            from geometry.ui.widgets.polygonal_numbers_visualization import Connection

            # Convert saved connection data to Connection objects
            for conn_data in saved_viz.connections:
                # Create a QColor from the color data
                color_data = conn_data.get(
                    "color", {"r": 100, "g": 100, "b": 255, "a": 150}
                )
                color = QColor(
                    color_data.get("r", 100),
                    color_data.get("g", 100),
                    color_data.get("b", 255),
                    color_data.get("a", 150),
                )

                # Get the style as a Qt.PenStyle enum value
                style_int = conn_data.get("style", 1)  # Default to solid line
                # Handle both direct enum values and integer values
                try:
                    style = Qt.PenStyle(style_int)
                except (TypeError, ValueError):
                    # If conversion fails, default to solid line
                    style = Qt.PenStyle.SolidLine

                # Create a new Connection object
                connection = Connection(
                    conn_data["dot1"],
                    conn_data["dot2"],
                    color,
                    conn_data.get("width", 2),
                    style,
                )

                # Add to the visualization's connections
                viz.connections.append(connection)

        # Update the UI
        self._update_visualization_info()
        self._sync_group_comboboxes()

        # Update the visualization
        viz.update()

        QMessageBox.information(
            self,
            "Load Visualization",
            f"Visualization '{saved_viz.name}' loaded successfully",
        )

    def _delete_selected_visualization(self):
        """Delete the selected visualization."""
        selected_items = self.viz_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Delete Visualization", "Please select a visualization to delete"
            )
            return

        viz_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        viz_name = selected_items[0].text()

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Visualization",
            f"Are you sure you want to delete '{viz_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete the visualization
        manager = VisualizationManager()
        if manager.delete_visualization(viz_id):
            QMessageBox.information(
                self,
                "Delete Visualization",
                f"Visualization '{viz_name}' deleted successfully",
            )
            self._populate_visualization_list()
        else:
            QMessageBox.warning(
                self, "Delete Visualization", "Failed to delete visualization"
            )

    def _update_visualization_info(self):
        """Update the visualization info display."""
        viz = self.get_visualization()
        if not viz:
            return

        self.viz_type_label.setText(
            f"Type: {'Centered' if viz.calculator.is_centered else 'Regular'}"
        )
        self.viz_sides_label.setText(f"Sides: {viz.calculator.sides}")
        self.viz_index_label.setText(f"Index: {viz.calculator.index}")

        # Update the visualization info when it's first shown
        if hasattr(self, "viz_name_edit"):
            # Set a default name based on the current configuration
            polygon_name = viz.calculator.get_polygonal_name()
            value = viz.calculator.calculate_value()
            default_name = f"{polygon_name} ({viz.calculator.sides}, {viz.calculator.index}) - {value} dots"

            # Only set the name if it's empty
            if not self.viz_name_edit.text():
                self.viz_name_edit.setText(default_name)

    def get_visualization(self):
        """Get the visualization from the parent panel.

        Returns:
            The visualization widget or None if not found
        """
        if not self.panel:
            print("No parent panel")
            return None

        if hasattr(self.panel, "interactive") and hasattr(
            self.panel.interactive, "visualization"
        ):
            return self.panel.interactive.visualization

        return None
