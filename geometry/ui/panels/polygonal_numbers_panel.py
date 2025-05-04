"""
Polygonal Numbers Panel.

This module provides a UI panel for visualizing and exploring polygonal numbers
and centered polygonal numbers.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.polygonal_numbers_calculator import PolygonalNumbersCalculator
from geometry.services.polygonal_visualization_service import PolygonalVisualizationService
from geometry.ui.widgets.polygonal_numbers_visualization import PolygonalNumbersVisualization
from geometry.ui.widgets.polygonal_numbers_interactive import PolygonalNumbersInteractive
from geometry.ui.widgets.unified_control_panel import UnifiedControlPanel
from shared.services.number_properties_service import NumberPropertiesService


class PolygonalNumbersPanel(QWidget):
    """Panel for visualizing and exploring polygonal numbers."""

    def __init__(self, parent=None):
        """Initialize the panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        # Initialize calculator
        self.calculator = PolygonalNumbersCalculator()

        # Initialize number properties service
        self.number_service = NumberPropertiesService.get_instance()

        # Initialize polygonal visualization service and register callback
        self.viz_service = PolygonalVisualizationService.get_instance()
        self.viz_service.register_callback(self._check_for_visualization_request)

        # Set a minimum size for the panel but allow resizing
        self.setMinimumSize(1200, 700)

        # Initialize UI
        self._init_ui()

        # Update the display
        self._update_display()

        # Force window to be large enough after a brief delay
        QTimer.singleShot(100, self._force_resize)

    def _force_resize(self):
        """Force the window to resize to accommodate all content."""
        if self.parent():
            # If we have a parent window, resize it
            parent_window = self.parent().window()
            parent_window.resize(1200, 700)
        else:
            # Otherwise resize ourselves
            self.resize(1200, 700)

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)  # Add more spacing between components
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for maximum space

        # Set minimum size for the panel but allow resizing
        self.setMinimumSize(1200, 700)

        # Create a splitter for better resizing behavior
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)  # Prevent collapsing sections to zero
        main_splitter.setHandleWidth(8)  # Make the splitter handle wider and more visible

        # Create the tab widget for different views
        tab_widget = QTabWidget()
        tab_widget.setMinimumWidth(600)  # Reduced minimum width
        tab_widget.setMaximumWidth(700)  # Reduced maximum width to prevent overlap

        # Create a container for the interactive tab to ensure proper boundaries
        interactive_container = QFrame()  # Use QFrame instead of QWidget for border
        interactive_container.setFrameShape(QFrame.Shape.StyledPanel)  # Add a visible frame
        interactive_container.setFrameShadow(QFrame.Shadow.Sunken)  # Add shadow for depth
        interactive_container.setLineWidth(2)  # Make the frame more visible
        interactive_layout = QVBoxLayout(interactive_container)
        interactive_layout.setContentsMargins(10, 10, 10, 10)  # Add larger margins for visual separation

        # Create the interactive visualization widget for the first tab
        self.interactive = PolygonalNumbersInteractive(self)

        # Pass our calculator to the interactive widget
        self.interactive.set_calculator(self.calculator)

        # Add the interactive widget to the container
        interactive_layout.addWidget(self.interactive)

        # Add the container to the first tab
        tab_widget.addTab(interactive_container, "Interactive Mode")

        # Create the basic visualization for the second tab
        visualization_container = QFrame()  # Use QFrame instead of QWidget for border
        visualization_container.setFrameShape(QFrame.Shape.StyledPanel)  # Add a visible frame
        visualization_container.setFrameShadow(QFrame.Shadow.Sunken)  # Add shadow for depth
        visualization_container.setLineWidth(2)  # Make the frame more visible
        visualization_layout = QVBoxLayout(visualization_container)
        visualization_layout.setContentsMargins(10, 10, 10, 10)  # Add larger margins for visual separation

        # Create the basic visualization
        self.basic_visualization = PolygonalNumbersVisualization(visualization_container)
        self.basic_visualization.set_calculator(self.calculator)

        # Add the visualization to the layout
        visualization_layout.addWidget(self.basic_visualization)

        # Add the visualization tab
        tab_widget.addTab(visualization_container, "Basic View")

        # Create the unified control panel
        self.control_panel = UnifiedControlPanel(self)
        self.control_panel.setMinimumWidth(500)  # Minimum width for better tab display
        self.control_panel.setMaximumWidth(550)  # Maximum width to prevent excessive expansion

        # Connect control panel signals to handlers
        self._connect_control_panel_signals()

        # Connect the interactive visualization to the control panel
        self.interactive.connect_signals(self.control_panel)

        # Add widgets to the splitter
        main_splitter.addWidget(tab_widget)
        main_splitter.addWidget(self.control_panel)

        # Set initial splitter sizes - give more space to the control panel to prevent overlap
        main_splitter.setSizes([600, 600])

        # Add the info panel to the third tab
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)

        # Create formula display with scroll area
        formula_group = QGroupBox("Formula")
        formula_layout = QVBoxLayout()

        formula_scroll = QScrollArea()
        formula_scroll.setWidgetResizable(True)
        formula_scroll.setFrameShape(QFrame.Shape.NoFrame)

        formula_content = QWidget()
        formula_content_layout = QVBoxLayout(formula_content)

        self.formula_text = QLabel()
        self.formula_text.setWordWrap(True)
        self.formula_text.setTextFormat(Qt.TextFormat.RichText)
        self.formula_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        formula_content_layout.addWidget(self.formula_text)
        formula_content_layout.addStretch()

        formula_scroll.setWidget(formula_content)
        formula_layout.addWidget(formula_scroll)

        formula_group.setLayout(formula_layout)
        info_layout.addWidget(formula_group)

        # Create sequence display with scroll area
        sequence_group = QGroupBox("Sequence")
        sequence_layout = QVBoxLayout()

        sequence_scroll = QScrollArea()
        sequence_scroll.setWidgetResizable(True)
        sequence_scroll.setFrameShape(QFrame.Shape.NoFrame)

        sequence_content = QWidget()
        sequence_content_layout = QVBoxLayout(sequence_content)

        self.sequence_text = QLabel()
        self.sequence_text.setWordWrap(True)
        self.sequence_text.setTextFormat(Qt.TextFormat.RichText)
        self.sequence_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.sequence_text.setOpenExternalLinks(True)  # Enable opening links in browser

        sequence_content_layout.addWidget(self.sequence_text)
        sequence_content_layout.addStretch()

        sequence_scroll.setWidget(sequence_content)
        sequence_layout.addWidget(sequence_scroll)

        sequence_group.setLayout(sequence_layout)
        info_layout.addWidget(sequence_group)

        # Create properties display with scroll area
        properties_group = QGroupBox("Properties")
        properties_layout = QVBoxLayout()

        properties_scroll = QScrollArea()
        properties_scroll.setWidgetResizable(True)
        properties_scroll.setFrameShape(QFrame.Shape.NoFrame)

        properties_content = QWidget()
        properties_content_layout = QVBoxLayout(properties_content)

        self.properties_text = QLabel()
        self.properties_text.setWordWrap(True)
        self.properties_text.setTextFormat(Qt.TextFormat.RichText)
        self.properties_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        properties_content_layout.addWidget(self.properties_text)
        properties_content_layout.addStretch()

        properties_scroll.setWidget(properties_content)
        properties_layout.addWidget(properties_scroll)

        properties_group.setLayout(properties_layout)
        info_layout.addWidget(properties_group)

        # Add the properties tab
        tab_widget.addTab(info_panel, "Information")

        # Add the splitter to the main layout
        main_layout.addWidget(main_splitter, 1)  # Give it a stretch factor of 1

        # Initialize animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animation_step)
        self.animation_active = False

    def _connect_control_panel_signals(self):
        """Connect signals from the unified control panel to handlers."""
        # Connect polygonal number configuration signals
        self.control_panel.typeChanged.connect(self._type_changed)
        self.control_panel.sidesChanged.connect(self._sides_changed)
        self.control_panel.indexChanged.connect(self._index_changed)

        # Connect visualization options signals
        self.control_panel.gridToggled.connect(self._update_grid)
        self.control_panel.labelsToggled.connect(self._update_labels)
        self.control_panel.layersToggled.connect(self._update_layers)
        self.control_panel.dotNumbersToggled.connect(self._update_dot_numbers)
        self.control_panel.dotSizeChanged.connect(self._update_dot_size)
        self.control_panel.zoomChanged.connect(self._update_zoom)
        self.control_panel.resetViewRequested.connect(self._reset_view)
        self.control_panel.colorSchemeChanged.connect(self._update_color_scheme)

        # Connect animation signals
        self.control_panel.animationToggled.connect(self._toggle_animation)
        self.control_panel.animationReset.connect(self._reset_animation)

        # Connect selection and interaction signals
        self.control_panel.selectionModeChanged.connect(self._toggle_selection_mode)
        self.control_panel.clearSelectionsRequested.connect(self._clear_selections)
        self.control_panel.selectAllRequested.connect(self._select_all)
        self.control_panel.connectDotsRequested.connect(self._connect_dots)
        self.control_panel.showConnectionsChanged.connect(self._toggle_connections)
        self.control_panel.closePolygonRequested.connect(self._close_polygon)
        self.control_panel.selectLayerRequested.connect(self._select_layer)

    def _type_changed(self, is_centered: bool) -> None:
        """Handle change between regular and centered polygonal numbers.

        Args:
            is_centered: Whether to use centered polygonal numbers
        """
        self.calculator.set_centered(is_centered)
        self._update_display()

    def _sides_changed(self, sides: int) -> None:
        """Handle change in polygon sides.

        Args:
            sides: Number of sides for the polygon
        """
        self.calculator.set_sides(sides)
        self._update_display()

    def _index_changed(self, index: int) -> None:
        """Handle change in index value.

        Args:
            index: New index value
        """
        self.calculator.set_index(index)
        self._update_display()

    def _update_grid(self, show: bool) -> None:
        """Update grid visibility in visualizations.

        Args:
            show: Whether to show the grid
        """
        self.interactive.visualization.toggle_grid(show)
        self.basic_visualization.toggle_grid(show)

    def _update_labels(self, show: bool) -> None:
        """Update label visibility in visualizations.

        Args:
            show: Whether to show labels
        """
        self.interactive.visualization.toggle_labels(show)
        self.basic_visualization.toggle_labels(show)

    def _update_layers(self, show: bool) -> None:
        """Update layer coloring in visualizations.

        Args:
            show: Whether to show colored layers
        """
        self.interactive.visualization.toggle_layers(show)
        self.basic_visualization.toggle_layers(show)

    def _update_dot_numbers(self, show: bool) -> None:
        """Update dot number visibility in visualizations.

        Args:
            show: Whether to show dot numbers
        """
        self.interactive.visualization.toggle_dot_numbers(show)
        self.basic_visualization.toggle_dot_numbers(show)

    def _update_dot_size(self, size: float) -> None:
        """Update dot size in visualizations.

        Args:
            size: New dot size
        """
        self.interactive.visualization.set_dot_size(size)
        self.basic_visualization.set_dot_size(size)

    def _update_zoom(self, factor: float) -> None:
        """Update zoom level in visualizations.

        Args:
            factor: Zoom factor to apply
        """
        self.interactive.visualization.set_zoom(factor)
        self.basic_visualization.set_zoom(factor)

    def _reset_view(self) -> None:
        """Reset the view to default pan and zoom."""
        # Reset visualization pan and zoom
        self.interactive.visualization.pan_x = 0.0
        self.interactive.visualization.pan_y = 0.0
        self.interactive.visualization.set_zoom(1.0)
        self.interactive.visualization.update()

        # Also reset the basic visualization
        self.basic_visualization.pan_x = 0.0
        self.basic_visualization.pan_y = 0.0
        self.basic_visualization.set_zoom(1.0)
        self.basic_visualization.update()

    def _toggle_animation(self, play: bool) -> None:
        """Toggle animation on/off.

        Args:
            play: Whether to play the animation
        """
        if play:
            self.animation_timer.start(500)  # Animation speed in ms
            self.animation_active = True
            self.control_panel.set_animation_state(True)
        else:
            self.animation_timer.stop()
            self.animation_active = False
            self.control_panel.set_animation_state(False)

    def _reset_animation(self) -> None:
        """Reset animation to index 1."""
        self.control_panel.index_spin.setValue(1)
        self.control_panel.index_slider.setValue(1)
        self.calculator.set_index(1)
        self._update_display()

    def _animation_step(self) -> None:
        """Advance animation by one step."""
        current_index = self.control_panel.index_spin.value()
        if current_index < 100:  # Maximum index
            self.control_panel.index_spin.setValue(current_index + 1)
        else:
            # Stop animation when reaching the end
            self._toggle_animation(False)

    def _toggle_selection_mode(self, enabled: bool) -> None:
        """Toggle selection mode.

        Args:
            enabled: Whether selection mode is enabled
        """
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.set_selection_mode(enabled)

        if hasattr(self.basic_visualization, 'set_selection_mode'):
            self.basic_visualization.set_selection_mode(enabled)

    def _clear_selections(self) -> None:
        """Clear all selections in both visualizations."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("_clear_selections called")

        # Clear selections in the interactive visualization
        if hasattr(self.interactive, 'visualization'):
            logger.debug("Clearing selections in interactive visualization")
            viz = self.interactive.visualization

            # Log current state
            logger.debug(f"Before clearing: {len(viz.selected_dots)} dots selected")

            # Clear selections
            viz.clear_selections()

            # Log new state
            logger.debug(f"After clearing: {len(viz.selected_dots)} dots selected")

            # Force update
            viz.update()
        else:
            logger.debug("Interactive visualization not available")

        # Clear selections in the basic visualization
        if hasattr(self.basic_visualization, 'clear_selections'):
            logger.debug("Clearing selections in basic visualization")

            # Log current state if possible
            if hasattr(self.basic_visualization, 'selected_dots'):
                logger.debug(f"Before clearing: {len(self.basic_visualization.selected_dots)} dots selected")

            # Clear selections
            self.basic_visualization.clear_selections()

            # Log new state if possible
            if hasattr(self.basic_visualization, 'selected_dots'):
                logger.debug(f"After clearing: {len(self.basic_visualization.selected_dots)} dots selected")

            # Force update
            if hasattr(self.basic_visualization, 'update'):
                self.basic_visualization.update()
        else:
            logger.debug("Basic visualization clear_selections method not available")

    def _select_all(self) -> None:
        """Select all dots in both visualizations."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("_select_all called")

        # First, ensure we're in selection mode
        logger.debug("Setting selection mode to True")
        self._toggle_selection_mode(True)

        # Select all dots in the interactive visualization
        if hasattr(self.interactive, 'visualization'):
            logger.debug("Selecting all dots in interactive visualization")
            viz = self.interactive.visualization

            # Log current state
            logger.debug(f"Before selecting: {len(viz.selected_dots)} dots selected")

            # Make sure dot positions are up to date
            viz.update_dot_positions()
            all_dots = list(viz.dot_positions.keys())
            logger.debug(f"Found {len(all_dots)} dots in interactive visualization")

            if all_dots:
                # Select all dots
                viz.select_dots_by_indices(all_dots)

                # Log new state
                logger.debug(f"After selecting: {len(viz.selected_dots)} dots selected")

                # Force update
                viz.update()
            else:
                logger.debug("No dots available in interactive visualization")
        else:
            logger.debug("Interactive visualization not available")

        # Select all dots in the basic visualization
        if hasattr(self.basic_visualization, 'select_dots_by_indices'):
            logger.debug("Selecting all dots in basic visualization")

            # Log current state if possible
            if hasattr(self.basic_visualization, 'selected_dots'):
                logger.debug(f"Before selecting: {len(self.basic_visualization.selected_dots)} dots selected")

            # Make sure dot positions are up to date
            self.basic_visualization.update_dot_positions()
            all_dots = list(self.basic_visualization.dot_positions.keys())
            logger.debug(f"Found {len(all_dots)} dots in basic visualization")

            if all_dots:
                # Select all dots
                self.basic_visualization.select_dots_by_indices(all_dots)

                # Log new state if possible
                if hasattr(self.basic_visualization, 'selected_dots'):
                    logger.debug(f"After selecting: {len(self.basic_visualization.selected_dots)} dots selected")

                # Force update
                if hasattr(self.basic_visualization, 'update'):
                    self.basic_visualization.update()
            else:
                logger.debug("No dots available in basic visualization")
        else:
            logger.debug("Basic visualization select_dots_by_indices method not available")

    def _connect_dots(self) -> None:
        """Connect selected dots."""
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.connect_selected_dots()

    def _toggle_connections(self, show: bool) -> None:
        """Toggle connections visibility.

        Args:
            show: Whether to show connections
        """
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.toggle_connections(show)

    def _close_polygon(self) -> None:
        """Close the polygon by connecting the last dot to the first."""
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.close_polygon()

    def _select_layer(self, layer: int) -> None:
        """Select all dots in a specific layer.

        Args:
            layer: Layer number to select
        """
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.select_dots_by_layer(layer)

    def _update_color_scheme(self, scheme: str) -> None:
        """Update the color scheme for layers.

        Args:
            scheme: Color scheme name ("rainbow", "pastel", "monochrome", "custom")
        """
        if hasattr(self.interactive, 'visualization'):
            self.interactive.visualization.set_color_scheme(scheme)

        if hasattr(self.basic_visualization, 'set_color_scheme'):
            self.basic_visualization.set_color_scheme(scheme)

    def _update_display(self) -> None:
        """Update all display elements."""
        # Update the visualizations
        self.interactive.set_calculator(self.calculator)
        self.basic_visualization.set_calculator(self.calculator)

        # Update the interactive widget info
        self.interactive.update_info()

        # Update the value display in the control panel
        value = self.calculator.calculate_value()
        self.control_panel.update_value_display(value)

        # Update properties
        self._update_properties(value)

        # Update the control panel status
        self.control_panel.update_status(f"Displaying {self.calculator.get_polygonal_name()} Number: {value}")

    def _update_properties(self, value: int) -> None:
        """Update the properties display.

        Args:
            value: Current polygonal number value
        """
        # Update formula
        formula_text = self._get_formula_text()
        self.formula_text.setText(formula_text)

        # Update sequence
        sequence_text = self._get_sequence_text()
        self.sequence_text.setText(sequence_text)

        # Update number properties
        properties_text = self._get_properties_text(value)
        self.properties_text.setText(properties_text)

    def _check_for_visualization_request(self) -> None:
        """Check if there's a pending visualization request from the service."""
        if self.viz_service.has_pending_visualization():
            # Get the polygonal number settings from the service
            sides, index, is_centered = self.viz_service.get_polygonal_number()

            # Update the calculator directly
            self.calculator.set_sides(sides)
            self.calculator.set_index(index)
            self.calculator.set_centered(is_centered)

            # Update the control panel to match
            self.control_panel.sides_combo.setCurrentIndex(
                self.control_panel.sides_combo.findData(sides)
            )
            self.control_panel.regular_radio.setChecked(not is_centered)
            self.control_panel.centered_radio.setChecked(is_centered)
            self.control_panel.index_spin.setValue(index)
            self.control_panel.index_slider.setValue(index)

            # Update the display
            self._update_display()

            # Clear the pending flag
            self.viz_service.clear_pending_visualization()

            # Switch to the visualization tab (parent widget has the tab_widget)
            if hasattr(self.parent(), 'setCurrentWidget'):
                self.parent().setCurrentWidget(self)
            elif hasattr(self, 'tab_widget'):
                self.tab_widget.setCurrentIndex(0)  # Visualization tab

            # Log the visualization request
            import logging
            logging.getLogger(__name__).debug(
                f"Visualizing polygonal number: sides={sides}, index={index}, centered={is_centered}"
            )

    def _get_formula_text(self) -> str:
        """Get the formula text for the current polygonal number.

        Returns:
            Formula text with explanation
        """
        sides = self.calculator.sides
        is_centered = self.calculator.is_centered

        if is_centered:
            formula = f"<b>Centered {sides}-gonal Number Formula:</b><br>"
            formula += f"C<sub>{sides}</sub>(n) = {sides}n(n-1)/2 + 1<br><br>"
            formula += "Where:<br>"
            formula += "- n is the index (layer number)<br>"
            formula += f"- {sides} is the number of sides in the polygon<br><br>"
            formula += "For the current value:<br>"
            formula += f"C<sub>{sides}</sub>({self.calculator.index}) = {self.calculator.calculate_value()}<br><br>"

            # Add explanation of centered polygonal numbers
            formula += "<b>About Centered Polygonal Numbers:</b><br>"
            formula += "Centered polygonal numbers represent dots arranged in a regular polygon with a dot in the center. "
            formula += "Each successive layer forms a complete polygon around the previous layers.<br><br>"

            # Add specific information for common centered polygonal numbers
            if sides == 3:
                formula += "<b>Centered Triangular Numbers:</b> These numbers form triangular patterns with a central dot. "
                formula += "They are related to triangular numbers and have applications in combinatorial geometry.<br>"
            elif sides == 4:
                formula += "<b>Centered Square Numbers:</b> Also known as 'square numbers of the second order'. "
                formula += "They form square patterns with a central dot and have connections to lattice theory.<br>"
            elif sides == 5:
                formula += "<b>Centered Pentagonal Numbers:</b> These form pentagonal patterns with a central dot. "
                formula += "They appear in various mathematical patterns and sequences.<br>"
            elif sides == 6:
                formula += "<b>Centered Hexagonal Numbers:</b> These form hexagonal patterns with a central dot. "
                formula += "They are closely related to the hexagonal lattice and appear in nature, such as in honeycombs.<br>"
        else:
            formula = f"<b>Regular {sides}-gonal Number Formula:</b><br>"
            formula += f"P<sub>{sides}</sub>(n) = (({sides}-2)n(n-1)/2) + n<br><br>"
            formula += "Where:<br>"
            formula += "- n is the index<br>"
            formula += f"- {sides} is the number of sides in the polygon<br><br>"
            formula += "For the current value:<br>"
            formula += f"P<sub>{sides}</sub>({self.calculator.index}) = {self.calculator.calculate_value()}<br><br>"

            # Add explanation of regular polygonal numbers
            formula += "<b>About Polygonal Numbers:</b><br>"
            formula += "Polygonal numbers represent dots arranged in the shape of a regular polygon. "
            formula += "Each successive number adds a new layer around the previous shape.<br><br>"

            # Add specific information for common polygonal numbers
            if sides == 3:
                formula += "<b>Triangular Numbers:</b> These are among the oldest known figurate numbers, studied by the Pythagoreans. "
                formula += "They represent the sum of the first n natural numbers and have numerous applications in combinatorics.<br>"
            elif sides == 4:
                formula += "<b>Square Numbers:</b> These are simply the squares of natural numbers. "
                formula += "They form perfect square arrangements of dots and have fundamental importance in mathematics.<br>"
            elif sides == 5:
                formula += "<b>Pentagonal Numbers:</b> These form pentagonal patterns and were studied by ancient mathematicians. "
                formula += "They appear in Euler's pentagonal number theorem and have connections to partition theory.<br>"
            elif sides == 6:
                formula += "<b>Hexagonal Numbers:</b> These form hexagonal patterns and are related to triangular numbers. "
                formula += "Every hexagonal number is also a triangular number (specifically, the nth hexagonal number equals the (2n-1)th triangular number).<br>"

        return formula

    def _get_sequence_text(self) -> str:
        """Get the sequence text for the current polygonal number type.

        Returns:
            Sequence text with first several values
        """
        sides = self.calculator.sides
        is_centered = self.calculator.is_centered

        # Get the name of the sequence
        name = self.calculator.get_polygonal_name()

        # Generate the first 10 values in the sequence
        sequence = []
        temp_calc = PolygonalNumbersCalculator(sides=sides)
        temp_calc.set_centered(is_centered)

        for i in range(1, 11):
            temp_calc.set_index(i)
            sequence.append(str(temp_calc.calculate_value()))

        sequence_str = ", ".join(sequence)

        result = f"<b>{name} Number Sequence:</b><br>"
        result += f"First 10 values: {sequence_str}, ...<br><br>"

        # Add OEIS reference if known
        oeis_refs = {
            (3, False): "A000217",  # Triangular numbers
            (4, False): "A000290",  # Square numbers
            (5, False): "A000326",  # Pentagonal numbers
            (6, False): "A000384",  # Hexagonal numbers
            (7, False): "A000566",  # Heptagonal numbers
            (8, False): "A000567",  # Octagonal numbers
            (9, False): "A001106",  # Nonagonal numbers
            (10, False): "A001107", # Decagonal numbers
            (3, True): "A005448",   # Centered triangular numbers
            (4, True): "A001844",   # Centered square numbers
            (5, True): "A001841",   # Centered pentagonal numbers
            (6, True): "A003215",   # Centered hexagonal numbers
            (7, True): "A069099",   # Centered heptagonal numbers
            (8, True): "A016754",   # Centered octagonal numbers
        }

        oeis_id = oeis_refs.get((sides, is_centered))
        if oeis_id:
            result += f"OEIS Reference: <a href='https://oeis.org/{oeis_id}'>{oeis_id}</a><br><br>"

        # Add recurrence relation
        if is_centered:
            result += "<b>Recurrence Relation:</b><br>"
            result += f"C<sub>{sides}</sub>(n+1) = C<sub>{sides}</sub>(n) + {sides}n<br><br>"
        else:
            result += "<b>Recurrence Relation:</b><br>"
            result += f"P<sub>{sides}</sub>(n+1) = P<sub>{sides}</sub>(n) + ({sides}-2)n + 1<br><br>"

        # Add interesting properties
        result += "<b>Interesting Properties:</b><br>"
        if sides == 3 and not is_centered:
            result += "• Sum of first n natural numbers: 1 + 2 + ... + n<br>"
            result += "• Binomial coefficient: T(n) = C(n+1, 2)<br>"
            result += "• T(n) = n(n+1)/2<br>"
        elif sides == 4 and not is_centered:
            result += "• Perfect squares: S(n) = n²<br>"
            result += "• Sum of first n odd numbers: 1 + 3 + ... + (2n-1)<br>"
        elif sides == 6 and not is_centered:
            result += "• Every hexagonal number is also a triangular number<br>"
            result += "• The nth hexagonal number equals the (2n-1)th triangular number<br>"
        elif sides == 3 and is_centered:
            result += "• Also known as 'triangular numbers of the second order'<br>"
            result += "• C₃(n) = 3n(n-1)/2 + 1<br>"
        elif sides == 6 and is_centered:
            result += "• Appear in the Catan board game (19 hexagons)<br>"
            result += "• Related to the hexagonal close packing of spheres<br>"

        return result

    def closeEvent(self, event) -> None:
        """Handle the panel being closed.

        Args:
            event: The close event
        """
        # Unregister from the visualization service
        self.viz_service.unregister_callback(self._check_for_visualization_request)

        # Call the parent class method
        super().closeEvent(event)

    def _get_properties_text(self, value: int) -> str:
        """Get the properties text for the current polygonal number value.

        Args:
            value: Current polygonal number value

        Returns:
            Properties text
        """
        # Get properties from the number service
        properties = self.number_service.get_number_properties(value)

        result = f"<b>Properties of {value}:</b><br><br>"

        # Basic properties
        if properties.get("is_prime", False):
            result += "• Prime number<br>"

        if properties.get("is_perfect", False):
            result += "• Perfect number<br>"

        if properties.get("is_triangular", False):
            result += f"• Triangular number (index: {properties.get('polygonal_3_index')})<br>"

        if properties.get("is_square", False):
            result += f"• Square number (index: {properties.get('polygonal_4_index')})<br>"

        # Check if it's also other polygonal numbers
        for k in range(3, 11):
            if k != self.calculator.sides or properties.get(f"polygonal_{k}_index") != self.calculator.index:
                if f"polygonal_{k}_index" in properties:
                    shape_name = {
                        3: "Triangular",
                        4: "Square",
                        5: "Pentagonal",
                        6: "Hexagonal",
                        7: "Heptagonal",
                        8: "Octagonal",
                        9: "Nonagonal",
                        10: "Decagonal",
                    }[k]
                    result += f"• {shape_name} number (index: {properties.get(f'polygonal_{k}_index')})<br>"

        # Check if it's also centered polygonal numbers
        for k in range(3, 11):
            if f"centered_{k}_index" in properties:
                shape_name = {
                    3: "Centered triangular",
                    4: "Centered square",
                    5: "Centered pentagonal",
                    6: "Centered hexagonal",
                    7: "Centered heptagonal",
                    8: "Centered octagonal",
                    9: "Centered nonagonal",
                    10: "Centered decagonal",
                }[k]
                result += f"• {shape_name} number (index: {properties.get(f'centered_{k}_index')})<br>"

        # Factors
        if "factors" in properties:
            factors = properties["factors"]
            if factors:
                result += f"<br><b>Factors:</b> {', '.join(map(str, factors))}<br>"

        return result

    def _toggle_selection_mode(self, checked: bool) -> None:
        """Toggle selection mode.

        Args:
            checked: Whether selection mode is enabled
        """
        # Update both the simple and interactive visualizations
        if hasattr(self, 'interactive') and self.interactive:
            self.interactive.visualization.set_selection_mode(checked)

            # Also update the radio button in the control panel
            if checked:
                self.control_panel.select_mode_radio.setChecked(True)
            else:
                self.control_panel.pan_mode_radio.setChecked(True)

    def _toggle_debug_mode(self) -> None:
        """Toggle debug mode to help diagnose selection issues."""
        is_debug_mode = self.debug_mode_check.isChecked()

        if hasattr(self, 'interactive') and self.interactive:
            # Set debug output flag in visualization
            self.interactive.visualization._debug_output = is_debug_mode

            # Force selection changed to trigger debug output
            if is_debug_mode:
                self.interactive.visualization._selection_changed = True
                print(f"Debug mode enabled. Current selection: {self.interactive.visualization.selected_dots}")
                print(f"Selection sum: {self.interactive.visualization.get_selected_sum()}")
                print(f"Dot positions: {len(self.interactive.visualization.dot_positions)} dots mapped")
                print(f"Selection groups: {self.interactive.visualization.selection_groups}")
            else:
                print("Debug mode disabled.")

            # Update the display
            self.interactive.update_info()
        else:
            print("Interactive visualization widget not initialized.")
