"""
Interactive Polygonal Numbers Widget.

This module provides a visualization widget for interactive exploration of polygonal numbers.
The controls are now handled by the UnifiedControlPanel in the parent panel.
"""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QFrame

from geometry.calculator.polygonal_numbers_calculator import PolygonalNumbersCalculator
from geometry.ui.widgets.polygonal_numbers_visualization import PolygonalNumbersVisualization


class PolygonalNumbersInteractive(QWidget):
    """Interactive widget combining visualization and controls for polygonal numbers."""

    def __init__(self, parent=None):
        """Initialize the polygonal numbers interactive widget."""
        super().__init__(parent)

        # Create the calculator
        self.calculator = PolygonalNumbersCalculator()

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)  # Add small margins for visual separation

        # Create a container widget to properly bound the visualization
        visualization_container = QFrame()  # Use QFrame instead of QWidget for border
        visualization_container.setFrameShape(QFrame.Shape.StyledPanel)  # Add a visible frame
        visualization_container.setFrameShadow(QFrame.Shadow.Sunken)  # Add shadow for depth
        visualization_container.setLineWidth(2)  # Make the frame more visible
        visualization_container.setAutoFillBackground(True)  # Ensure background is painted
        container_layout = QVBoxLayout(visualization_container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # Add margins inside container for spacing

        # Create the visualization widget
        self.visualization = PolygonalNumbersVisualization(visualization_container)
        self.visualization.set_calculator(self.calculator)

        # Add visualization to container layout
        container_layout.addWidget(self.visualization)

        # Add container to main layout
        self.layout.addWidget(visualization_container)

        # Set a minimum size for the visualization
        self.visualization.setMinimumWidth(500)
        self.visualization.setMinimumHeight(500)

        # Set a maximum width to prevent overflow
        self.visualization.setMaximumWidth(600)

        # Set a minimum size for the entire widget
        self.setMinimumSize(550, 600)

        # Set a maximum width for the entire widget
        self.setMaximumWidth(650)

        # Set size policy to ensure proper expansion
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # The control panel is now in the parent panel
        self.controls = None

    def connect_signals(self, control_panel=None):
        """Connect signals between components.

        Args:
            control_panel: The UnifiedControlPanel to connect signals to
        """
        # Store the control panel reference if provided
        if control_panel:
            self.control_panel = control_panel

            # Connect visualization signals to control panel
            self.visualization.selection_changed.connect(self._update_selection_status)

            # Connect control panel signals to visualization
            if hasattr(control_panel, 'selectionModeChanged'):
                control_panel.selectionModeChanged.connect(self.visualization.set_selection_mode)

            if hasattr(control_panel, 'clearSelectionsRequested'):
                control_panel.clearSelectionsRequested.connect(self._clear_selections)

            if hasattr(control_panel, 'selectAllRequested'):
                control_panel.selectAllRequested.connect(self._select_all)

            if hasattr(control_panel, 'selectionGroupChanged'):
                control_panel.selectionGroupChanged.connect(self._on_selection_group_changed)

            if hasattr(control_panel, 'connectDotsRequested'):
                control_panel.connectDotsRequested.connect(self.visualization.connect_selected_dots)

            if hasattr(control_panel, 'showConnectionsChanged'):
                control_panel.showConnectionsChanged.connect(self.visualization.toggle_connections)

            if hasattr(control_panel, 'closePolygonRequested'):
                control_panel.closePolygonRequested.connect(self.visualization.close_polygon)

            if hasattr(control_panel, 'selectLayerRequested'):
                control_panel.selectLayerRequested.connect(self.visualization.select_dots_by_layer)

    def _update_selection_status(self, selected_dots):
        """Update the selection status in the control panel."""
        if hasattr(self, 'control_panel'):
            dot_count = len(selected_dots)
            selected_sum = sum(selected_dots)

            # Update the control panel with selection info
            if hasattr(self.control_panel, 'update_selection_info'):
                self.control_panel.update_selection_info(dot_count, selected_sum)

    def _on_group_selected(self, group_name):
        """Handle group selection changes."""
        if not group_name:
            return

        # Make sure the group exists in selection groups
        if group_name not in self.visualization.selection_groups:
            self.visualization.selection_groups[group_name] = []

        # Update UI elements
        if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'group_status_label'):
            dot_count = len(self.visualization.selection_groups[group_name])
            self.control_panel.group_status_label.setText(f"Group '{group_name}': {dot_count} dots")

        # Display the selected group in the visualization
        selected_dots = self.visualization.selection_groups[group_name]
        self.visualization.selected_dots = selected_dots.copy()
        self.visualization.update()

    def set_calculator(self, calculator: PolygonalNumbersCalculator) -> None:
        """Set the calculator for the visualization.

        Args:
            calculator: The calculator to use
        """
        self.calculator = calculator
        self.visualization.set_calculator(calculator)
        self.visualization.update()

    def update_info(self):
        """Update information displays in control panel."""
        try:
            # This is called at intervals to update the control panel with current state
            if not hasattr(self, 'visualization') or not self.visualization:
                return

            if not hasattr(self, 'control_panel'):
                return

            # Get selection information
            try:
                selected_count = self.visualization.get_selected_count()
                selected_sum = self.visualization.get_selected_sum()
                connection_count = len(self.visualization.connections)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error getting selection info: {e}")
                return

            # Update the control panel
            try:
                # Update selection info
                if hasattr(self.control_panel, 'update_selection_info'):
                    self.control_panel.update_selection_info(selected_count, selected_sum)

                # Update connection info
                if hasattr(self.control_panel, 'update_connection_info'):
                    self.control_panel.update_connection_info(connection_count)

                # Update group status if we have the current group
                if hasattr(self.visualization, 'current_group') and hasattr(self.control_panel, 'group_status_label'):
                    group_name = self.visualization.current_group
                    if group_name in self.visualization.selection_groups:
                        dot_count = len(self.visualization.selection_groups[group_name])
                        self.control_panel.group_status_label.setText(f"Group '{group_name}': {dot_count} dots")
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error updating control panel: {e}")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in update_info: {e}")

    def resizeEvent(self, event):
        """Handle resize events.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        self.update()  # Ensure visual elements are properly updated

    def showEvent(self, event):
        """Handle show events.

        Args:
            event: Show event
        """
        super().showEvent(event)

        # Create a timer to periodically update the info panel
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(5000)  # Update every 5 seconds to reduce overhead

    def hideEvent(self, event):
        """Handle hide events.

        Args:
            event: Hide event
        """
        super().hideEvent(event)

        # Stop the timer when hidden to save resources
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()

    def _on_mode_changed(self, is_selection_mode):
        """Handle mode selection change.

        Args:
            is_selection_mode: True for selection mode, False for pan mode
        """
        if hasattr(self.visualization, 'set_selection_mode'):
            self.visualization.set_selection_mode(is_selection_mode)

    def _on_selection_group_changed(self, group_name):
        """Handle selection group change."""
        if group_name and hasattr(self.visualization, 'set_selection_group'):
            self.visualization.set_selection_group(group_name)

    def _clear_selections(self):
        """Clear all selections in the visualization."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("PolygonalNumbersInteractive._clear_selections called")

        if hasattr(self, 'visualization'):
            logger.debug("Clearing selections in visualization")
            self.visualization.clear_selections()

    def _select_all(self):
        """Select all dots in the visualization."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("PolygonalNumbersInteractive._select_all called")

        if hasattr(self, 'visualization'):
            logger.debug("Selecting all dots in visualization")

            # Make sure dot positions are up to date
            self.visualization.update_dot_positions()
            all_dots = list(self.visualization.dot_positions.keys())
            logger.debug(f"Found {len(all_dots)} dots in visualization")

            if all_dots:
                # Select all dots
                self.visualization.select_dots_by_indices(all_dots)
                logger.debug(f"Selected {len(all_dots)} dots")
            else:
                logger.debug("No dots available to select")