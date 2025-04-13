"""Geometry canvas for the Sacred Geometry Explorer.

This module contains the canvas component for the Sacred Geometry Explorer,
which provides the drawing area for geometric constructions.
"""

from loguru import logger
from typing import Optional, Tuple, List, Dict, Any
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QLineF, pyqtSignal, QEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QWidget, QMenu
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QMouseEvent, QWheelEvent, QKeyEvent, QTransform

from geometry.ui.sacred_geometry.model import GeometricObject, Point, Line, Circle
from geometry.ui.sacred_geometry.graphics_items import GraphicsItemFactory, GeometricGraphicsItem, LineGraphicsItem


class GeometryCanvas(QGraphicsView):
    """Canvas for geometric constructions.

    This class provides the drawing area for geometric constructions,
    with support for zooming, panning, and grid display.
    """

    # Signals
    mouse_pressed = pyqtSignal(QMouseEvent, QPointF)  # Event, scene position
    mouse_moved = pyqtSignal(QMouseEvent, QPointF)    # Event, scene position
    mouse_released = pyqtSignal(QMouseEvent, QPointF) # Event, scene position
    key_pressed = pyqtSignal(QKeyEvent)               # Key event
    object_selected = pyqtSignal(GeometricObject)     # Selected object
    object_deselected = pyqtSignal(GeometricObject)   # Deselected object
    object_modified = pyqtSignal(GeometricObject)     # Modified object

    def __init__(self, parent=None) -> None:
        """Initialize the geometry canvas.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Set scene rect (will be updated based on view size)
        self.scene.setSceneRect(QRectF(-1000, -1000, 2000, 2000))

        # Set view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Initialize view
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Set background color
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))

        # Grid properties
        self.show_grid = True
        self.grid_spacing = 50  # pixels at zoom level 1.0
        self.grid_subdivisions = 5
        self.major_grid_color = QColor(200, 200, 200)  # Light gray
        self.minor_grid_color = QColor(230, 230, 230)  # Lighter gray
        self.axis_color = QColor(150, 150, 150)  # Darker gray

        # Zoom properties
        self.zoom_factor = 1.2  # Zoom factor per step
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.current_zoom = 1.0

        # Object management
        self.objects = []  # List of geometric objects
        self.items_map = {}  # Map from object ID to graphics item
        self.updating = False  # Flag to prevent recursive updates

        # Connect signals
        self.scene.selectionChanged.connect(self._handle_selection_changed)

        # Mouse tracking
        self.setMouseTracking(True)  # Track mouse movements even when no button is pressed

        # Initialize the view
        self.reset_view()

        # Set tooltip
        self.setToolTip("Use mouse wheel to zoom in/out. Press Ctrl+0 to reset view. Press G to toggle grid.")

        logger.debug("GeometryCanvas initialized")

    def add_object(self, obj: GeometricObject) -> None:
        """Add a geometric object to the canvas.

        Args:
            obj: Geometric object to add
        """
        # Add object to list
        self.objects.append(obj)

        # Create graphics item
        item = GraphicsItemFactory.create_item(obj)
        if item is not None:
            # Add item to scene
            self.scene.addItem(item)

            # Add to items map
            self.items_map[obj.id] = item

            logger.debug(f"Added {obj.__class__.__name__} to canvas")
        else:
            logger.warning(f"Failed to create graphics item for {obj.__class__.__name__}")

    def add_objects(self, objects: List[GeometricObject]) -> None:
        """Add multiple geometric objects to the canvas.

        Args:
            objects: Geometric objects to add
        """
        for obj in objects:
            self.add_object(obj)

    def remove_object(self, obj: GeometricObject) -> None:
        """Remove a geometric object from the canvas.

        Args:
            obj: Geometric object to remove
        """
        # Remove from list
        if obj in self.objects:
            self.objects.remove(obj)

        # Remove graphics item
        if obj.id in self.items_map:
            item = self.items_map[obj.id]
            self.scene.removeItem(item)
            del self.items_map[obj.id]

            logger.debug(f"Removed {obj.__class__.__name__} from canvas")

    def clear_objects(self) -> None:
        """Remove all geometric objects from the canvas."""
        # Clear scene
        self.scene.clear()

        # Clear lists
        self.objects = []
        self.items_map = {}

        logger.debug("Cleared all objects from canvas")

    def update_object(self, obj: GeometricObject) -> None:
        """Update a geometric object on the canvas.

        Args:
            obj: Geometric object to update
        """
        # Prevent recursive updates
        if self.updating:
            logger.debug(f"DEBUG: Canvas.update_object skipped due to recursive update prevention")
            return

        self.updating = True

        try:
            # Log the object state before update
            if isinstance(obj, Line):
                logger.debug(f"DEBUG: Canvas.update_object called for Line {obj.id}")
                logger.debug(f"DEBUG: Before update: P1=({obj.x1}, {obj.y1}), P2=({obj.x2}, {obj.y2})")

                # Store metadata about which endpoint was moved (if any)
                # This is critical for preserving context across update paths
                moved_endpoint = None
                if hasattr(obj, 'metadata') and 'moved_endpoint' in obj.metadata:
                    moved_endpoint = obj.metadata['moved_endpoint']
                    logger.debug(f"DEBUG: Preserving moved_endpoint={moved_endpoint} metadata")
            else:
                logger.debug(f"DEBUG: Canvas.update_object called for {obj.__class__.__name__} {obj.id}")

            # Update graphics item
            if obj.id in self.items_map:
                item = self.items_map[obj.id]

                # Log the item state before update
                if isinstance(item, LineGraphicsItem):
                    logger.debug(f"DEBUG: Before item.update_from_object: P1=({item.line.x1}, {item.line.y1}), P2=({item.line.x2}, {item.line.y2})")

                # Perform the update
                item.update_from_object()

                # Log the item state after update
                if isinstance(item, LineGraphicsItem):
                    logger.debug(f"DEBUG: After item.update_from_object: P1=({item.line.x1}, {item.line.y1}), P2=({item.line.x2}, {item.line.y2})")

                    # Restore metadata about which endpoint was moved (if any)
                    # This ensures the metadata is preserved across all update paths
                    if moved_endpoint is not None and hasattr(item.line, 'metadata'):
                        item.line.metadata['moved_endpoint'] = moved_endpoint
                        logger.debug(f"DEBUG: Restored moved_endpoint={moved_endpoint} metadata")

                logger.debug(f"Updated {obj.__class__.__name__} on canvas")

                # Emit object_modified signal to update property panel
                # Only emit if the object is selected to avoid unnecessary updates
                if hasattr(self, 'object_modified') and obj.selected:
                    # Get the appropriate object to emit based on item type
                    if isinstance(item, LineGraphicsItem) and hasattr(item, 'line'):
                        # For lines, use the line from the item to ensure metadata is preserved
                        emit_obj = item.line
                    elif hasattr(item, 'geometric_object'):
                        # For other items, use the geometric_object if available
                        emit_obj = item.geometric_object
                    else:
                        # Fallback to the original object
                        emit_obj = obj

                    # Emit the signal with the appropriate object
                    self.object_modified.emit(emit_obj)
            else:
                logger.debug(f"DEBUG: Object {obj.id} not found in items_map")
        finally:
            self.updating = False

    def get_object_at(self, pos: QPointF, tolerance: float = 5.0) -> Optional[GeometricObject]:
        """Get the geometric object at the given position.

        Args:
            pos: Position in scene coordinates
            tolerance: Distance tolerance in pixels

        Returns:
            Geometric object at the position, or None if no object is found
        """
        # Check each object
        for obj in self.objects:
            if obj.contains_point(pos, tolerance):
                return obj

        return None

    def select_object(self, obj: GeometricObject) -> None:
        """Select a geometric object on the canvas.

        Args:
            obj: Geometric object to select
        """
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Update object
            obj.selected = True

            # Update graphics item
            if obj.id in self.items_map:
                item = self.items_map[obj.id]
                item.setSelected(True)

                logger.debug(f"Selected {obj.__class__.__name__} on canvas")
        finally:
            self.updating = False

    def deselect_object(self, obj: GeometricObject) -> None:
        """Deselect a geometric object on the canvas.

        Args:
            obj: Geometric object to deselect
        """
        # Update object
        obj.selected = False

        # Update graphics item
        if obj.id in self.items_map:
            item = self.items_map[obj.id]
            item.setSelected(False)

            logger.debug(f"Deselected {obj.__class__.__name__} on canvas")

    def select_all_objects(self) -> None:
        """Select all geometric objects on the canvas."""
        for obj in self.objects:
            self.select_object(obj)

    def deselect_all_objects(self) -> None:
        """Deselect all geometric objects on the canvas."""
        for obj in self.objects:
            self.deselect_object(obj)

    def get_selected_objects(self) -> List[GeometricObject]:
        """Get all selected geometric objects on the canvas.

        Returns:
            List of selected geometric objects
        """
        return [obj for obj in self.objects if obj.selected]

    def _handle_selection_changed(self) -> None:
        """Handle selection changes in the scene."""
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Get selected items
            selected_items = self.scene.selectedItems()

            # Update objects
            for obj in self.objects:
                item = self.items_map.get(obj.id)
                if item is not None:
                    selected = item in selected_items

                    # Check if selection state changed
                    if selected != obj.selected:
                        obj.selected = selected

                        # Emit signal
                        if selected:
                            self.object_selected.emit(obj)
                        else:
                            self.object_deselected.emit(obj)

            # Update status bar with selection count
            if hasattr(self.parent(), 'status_bar'):
                selected_count = len(selected_items)
                if selected_count == 0:
                    self.parent().status_bar.showMessage("No objects selected")
                elif selected_count == 1:
                    obj = self.get_selected_objects()[0]
                    self.parent().status_bar.showMessage(f"Selected: {obj.__class__.__name__} {obj.name or ''}")
                else:
                    self.parent().status_bar.showMessage(f"Selected: {selected_count} objects")

            logger.debug(f"Selection changed: {len(selected_items)} items selected")
        finally:
            self.updating = False

    def reset_view(self) -> None:
        """Reset the view to the default state."""
        # Reset transformation
        self.resetTransform()
        self.current_zoom = 1.0

        # Center on origin
        self.centerOn(0, 0)

        # Update the view
        self.update()

        logger.debug("View reset to default state")

    def zoom_in(self) -> None:
        """Zoom in by one step."""
        self.scale_view(self.zoom_factor)

    def zoom_out(self) -> None:
        """Zoom out by one step."""
        self.scale_view(1.0 / self.zoom_factor)

    def scale_view(self, factor: float) -> None:
        """Scale the view by the given factor.

        Args:
            factor: Scale factor
        """
        # Calculate new zoom level
        new_zoom = self.current_zoom * factor

        # Clamp to min/max zoom
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return

        # Update current zoom
        self.current_zoom = new_zoom

        # Scale the view
        self.scale(factor, factor)

        # Update the view
        self.update()

        logger.debug(f"View scaled by {factor}, current zoom: {self.current_zoom}")

    def set_grid_spacing(self, spacing: int, subdivisions: int = 5) -> None:
        """Set the grid spacing.

        Args:
            spacing: Grid spacing in pixels at zoom level 1.0
            subdivisions: Number of subdivisions between major grid lines
        """
        self.grid_spacing = max(10, spacing)  # Minimum 10 pixels
        self.grid_subdivisions = max(1, subdivisions)  # Minimum 1 subdivision

        # Update the view
        self.update()

        logger.debug(f"Grid spacing set to {self.grid_spacing} with {self.grid_subdivisions} subdivisions")

    def toggle_grid(self, show: bool = None) -> None:
        """Toggle grid visibility.

        Args:
            show: If provided, set grid visibility to this value
        """
        if show is None:
            self.show_grid = not self.show_grid
        else:
            self.show_grid = show

        # Update the view
        self.update()

        logger.debug(f"Grid visibility set to {self.show_grid}")

    def map_to_scene(self, pos: QPointF) -> QPointF:
        """Map a view position to scene coordinates.

        Args:
            pos: Position in view coordinates

        Returns:
            Position in scene coordinates
        """
        return self.mapToScene(pos)

    def map_from_scene(self, pos: QPointF) -> QPointF:
        """Map a scene position to view coordinates.

        Args:
            pos: Position in scene coordinates

        Returns:
            Position in view coordinates
        """
        return self.mapFromScene(pos)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw the background of the view.

        Args:
            painter: Painter to use for drawing
            rect: Rectangle to draw in scene coordinates
        """
        # Call base implementation to draw the background color
        super().drawBackground(painter, rect)

        # If grid is disabled, return
        if not self.show_grid:
            return

        # Get the visible rectangle in scene coordinates
        scene_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # Calculate grid spacing based on zoom level
        effective_spacing = self.grid_spacing

        # Calculate the range of grid lines to draw
        left = int(scene_rect.left() / effective_spacing) * effective_spacing
        right = int(scene_rect.right() / effective_spacing) * effective_spacing + effective_spacing
        top = int(scene_rect.top() / effective_spacing) * effective_spacing
        bottom = int(scene_rect.bottom() / effective_spacing) * effective_spacing + effective_spacing

        # Calculate minor grid spacing
        minor_spacing = effective_spacing / self.grid_subdivisions

        # Draw minor grid lines
        painter.setPen(QPen(self.minor_grid_color, 0))  # Width 0 means 1 pixel regardless of zoom

        # Draw minor vertical grid lines
        x = left
        while x <= right:
            for i in range(1, self.grid_subdivisions):
                minor_x = x + i * minor_spacing
                if minor_x != 0:  # Skip the axis which will be drawn later
                    painter.drawLine(QPointF(minor_x, top), QPointF(minor_x, bottom))
            x += effective_spacing

        # Draw minor horizontal grid lines
        y = top
        while y <= bottom:
            for i in range(1, self.grid_subdivisions):
                minor_y = y + i * minor_spacing
                if minor_y != 0:  # Skip the axis which will be drawn later
                    painter.drawLine(QPointF(left, minor_y), QPointF(right, minor_y))
            y += effective_spacing

        # Draw major grid lines
        painter.setPen(QPen(self.major_grid_color, 0))  # Width 0 means 1 pixel regardless of zoom

        # Draw major vertical grid lines
        x = left
        while x <= right:
            if x != 0:  # Skip the axis which will be drawn later
                painter.drawLine(QPointF(x, top), QPointF(x, bottom))
            x += effective_spacing

        # Draw major horizontal grid lines
        y = top
        while y <= bottom:
            if y != 0:  # Skip the axis which will be drawn later
                painter.drawLine(QPointF(left, y), QPointF(right, y))
            y += effective_spacing

        # Draw coordinate axes
        painter.setPen(QPen(self.axis_color, 0))  # Width 0 means 1 pixel regardless of zoom

        # Draw x-axis
        painter.drawLine(QPointF(left, 0), QPointF(right, 0))

        # Draw y-axis
        painter.drawLine(QPointF(0, top), QPointF(0, bottom))

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events for zooming.

        Use the mouse wheel to zoom in and out. Scroll up to zoom in, scroll down to zoom out.
        This is the primary method for zooming in the canvas.

        Args:
            event: Wheel event
        """
        # Calculate zoom factor based on wheel delta
        delta = event.angleDelta().y()
        if delta > 0:
            # Zoom in
            self.zoom_in()
        elif delta < 0:
            # Zoom out
            self.zoom_out()

        # Accept the event
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events.

        Args:
            event: Mouse event
        """
        # Get scene position
        scene_pos = self.mapToScene(event.position().toPoint())

        # Middle button or Alt+Left button for panning
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and \
            event.modifiers() & Qt.KeyboardModifier.AltModifier):
            # Set drag mode to scroll hand drag
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

            # Start drag
            fake_event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )
            super().mousePressEvent(fake_event)
        else:
            # Normal event handling
            super().mousePressEvent(event)

            # Emit signal
            self.mouse_pressed.emit(event, scene_pos)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events.

        Args:
            event: Mouse event
        """
        # Get scene position
        scene_pos = self.mapToScene(event.position().toPoint())

        # Normal event handling
        super().mouseMoveEvent(event)

        # Emit signal
        self.mouse_moved.emit(event, scene_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events.

        Args:
            event: Mouse event
        """
        # Get scene position
        scene_pos = self.mapToScene(event.position().toPoint())

        # Middle button or Alt+Left button for panning
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and \
            event.modifiers() & Qt.KeyboardModifier.AltModifier):
            # Reset drag mode
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

            # End drag
            fake_event = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )
            super().mouseReleaseEvent(fake_event)
        else:
            # Normal event handling
            super().mouseReleaseEvent(event)

            # Emit signal
            self.mouse_released.emit(event, scene_pos)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events.

        Args:
            event: Key event
        """
        # Handle specific keys
        if event.key() == Qt.Key.Key_0 and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Reset view with Ctrl+0
            self.reset_view()
            event.accept()
        elif event.key() == Qt.Key.Key_G:
            # Toggle grid
            self.toggle_grid()
            event.accept()
        else:
            # Normal event handling
            super().keyPressEvent(event)

            # Emit signal
            self.key_pressed.emit(event)
