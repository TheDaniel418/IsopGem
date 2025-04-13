"""Tool system for the Sacred Geometry Explorer.

This module contains the tool system for the Sacred Geometry Explorer,
which provides the interface for creating and manipulating geometric objects.
"""

import math
from typing import List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QCursor, QPen, QBrush, QColor, QPolygonF
from PyQt6.QtWidgets import QGraphicsItem, QApplication, QDialog
from loguru import logger

from geometry.ui.sacred_geometry.model import GeometricObject, Point, Line, Circle, Polygon, Text, Style, LineType
from geometry.ui.sacred_geometry.text_dialog import TextDialog


class ToolState(Enum):
    """Enumeration of tool states."""
    IDLE = auto()       # Tool is idle, waiting for user input
    ACTIVE = auto()     # Tool is active, processing user input
    PREVIEW = auto()    # Tool is showing a preview
    COMPLETE = auto()   # Tool has completed its operation
    CANCELLED = auto()  # Tool operation was cancelled


@dataclass
class ToolOptions:
    """Options for geometric tools."""
    snap_to_grid: bool = True           # Snap to grid points
    snap_to_objects: bool = True        # Snap to existing objects
    snap_tolerance: float = 10.0        # Snap tolerance in pixels
    show_preview: bool = True           # Show preview during tool operation
    auto_complete: bool = False         # Automatically complete operation when possible
    continuous_creation: bool = False   # Create multiple objects without deactivating tool


class GeometryTool:
    """Base class for all geometry tools.

    This class provides common functionality for all geometry tools,
    such as mouse event handling and state management.
    """

    def __init__(self, name: str, icon_name: str = None) -> None:
        """Initialize a geometry tool.

        Args:
            name: Name of the tool
            icon_name: Name of the icon file (without extension)
        """
        self.name = name
        self.icon_name = icon_name or name.lower().replace(" ", "_")
        self.active = False
        self.state = ToolState.IDLE
        self.options = ToolOptions()
        self.data = {}  # Tool-specific data
        self.preview_items = []  # Preview items for visualization
        self.explorer = None  # Reference to the explorer (set when activated)
        self.canvas = None  # Reference to the canvas (set when activated)

    def activate(self, explorer=None) -> None:
        """Activate the tool.

        Args:
            explorer: Reference to the explorer
        """
        self.active = True
        self.state = ToolState.IDLE
        self.data = {}
        self.preview_items = []
        self.explorer = explorer

        # Get canvas from explorer
        if explorer and hasattr(explorer, 'canvas'):
            self.canvas = explorer.canvas

        # Initialize tool-specific state
        self._init_tool()

        logger.debug(f"Tool '{self.name}' activated")

    def deactivate(self) -> None:
        """Deactivate the tool."""
        # Clean up any preview items
        self._clear_preview()

        # Reset state
        self.active = False
        self.state = ToolState.IDLE
        self.data = {}

        # Tool-specific cleanup
        self._cleanup_tool()

        logger.debug(f"Tool '{self.name}' deactivated")

    def _init_tool(self) -> None:
        """Initialize tool-specific state.

        This method is called when the tool is activated.
        Override in derived classes to perform tool-specific initialization.
        """
        pass

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state.

        This method is called when the tool is deactivated.
        Override in derived classes to perform tool-specific cleanup.
        """
        pass

    def _clear_preview(self) -> None:
        """Clear any preview items."""
        # Remove preview items from canvas
        if self.canvas and hasattr(self.canvas, 'scene'):
            for item in self.preview_items:
                self.canvas.scene.removeItem(item)

        # Clear list
        self.preview_items = []

    def _update_preview(self) -> None:
        """Update preview visualization.

        This method is called to update the preview visualization.
        Override in derived classes to perform tool-specific preview updates.
        """
        pass

    def _snap_to_grid(self, pos: QPointF) -> QPointF:
        """Snap position to grid.

        Args:
            pos: Position to snap

        Returns:
            Snapped position
        """
        if not self.options.snap_to_grid or not self.canvas:
            return pos

        # Get grid spacing
        grid_spacing = getattr(self.canvas, 'grid_spacing', 50)

        # Snap to grid
        x = round(pos.x() / grid_spacing) * grid_spacing
        y = round(pos.y() / grid_spacing) * grid_spacing

        return QPointF(x, y)

    def _snap_to_objects(self, pos: QPointF) -> QPointF:
        """Snap position to existing objects.

        Args:
            pos: Position to snap

        Returns:
            Snapped position
        """
        if not self.options.snap_to_objects or not self.canvas:
            return pos

        # Get objects from canvas
        objects = getattr(self.canvas, 'objects', [])

        # Find closest object
        min_distance = float('inf')
        closest_pos = pos

        for obj in objects:
            # Check if object has a position
            if isinstance(obj, Point):
                # Point object
                obj_pos = QPointF(obj.x, obj.y)
                distance = (pos - obj_pos).manhattanLength()

                if distance < min_distance and distance <= self.options.snap_tolerance:
                    min_distance = distance
                    closest_pos = obj_pos

        return closest_pos if min_distance < float('inf') else pos

    def _snap_position(self, pos: QPointF) -> QPointF:
        """Snap position to grid and/or objects.

        Args:
            pos: Position to snap

        Returns:
            Snapped position
        """
        # First snap to grid
        if self.options.snap_to_grid:
            pos = self._snap_to_grid(pos)

        # Then snap to objects (takes precedence)
        if self.options.snap_to_objects:
            pos = self._snap_to_objects(pos)

        return pos

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                # Calculate distance to object
                dist = obj.distance_to(pos)

                # Check if this is the closest object within tolerance
                if dist < closest_dist and dist <= self.options.snap_tolerance:
                    closest_obj = obj
                    closest_dist = dist

                    # For points, snap to the point position
                    if isinstance(obj, Point):
                        closest_point = QPointF(obj.x, obj.y)

            # If we found a close object, snap to it
            if closest_obj:
                snap_type = 'object'
                snap_target = closest_obj

                # If we have a specific point to snap to, use it
                if closest_point:
                    snapped_pos = closest_point

        # If we didn't snap to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)
            if grid_pos != pos:
                snap_type = 'grid'
                snapped_pos = grid_pos

        return snapped_pos, snap_type, snap_target

    def _create_object(self, obj_type, **kwargs) -> Optional[GeometricObject]:
        """Create a geometric object.

        Args:
            obj_type: Type of object to create
            **kwargs: Additional arguments for the object constructor

        Returns:
            Created object, or None if creation failed
        """
        if not self.explorer:
            logger.warning(f"Cannot create object: no explorer reference")
            return None

        # Create object based on type
        if obj_type == 'point':
            return self.explorer.create_point(**kwargs)
        elif obj_type == 'line':
            return self.explorer.create_line(**kwargs)
        elif obj_type == 'circle':
            return self.explorer.create_circle(**kwargs)
        elif obj_type == 'polygon':
            return self.explorer.create_polygon(**kwargs)
        elif obj_type == 'text':
            return self.explorer.create_text(**kwargs)
        else:
            logger.warning(f"Unknown object type: {obj_type}")
            return None

    def _complete_operation(self) -> None:
        """Complete the current operation.

        This method is called when the operation is complete.
        Override in derived classes to perform tool-specific completion.
        """
        # Clear preview
        self._clear_preview()

        # Reset state
        self.state = ToolState.IDLE
        self.data = {}

        # If not continuous creation, deactivate tool
        if not self.options.continuous_creation and self.explorer:
            # Activate selection tool
            self.explorer._activate_tool('selection')

    def _cancel_operation(self) -> None:
        """Cancel the current operation.

        This method is called when the operation is cancelled.
        Override in derived classes to perform tool-specific cancellation.
        """
        # Clear preview
        self._clear_preview()

        # Reset state
        self.state = ToolState.IDLE
        self.data = {}

        logger.debug(f"Operation cancelled for tool '{self.name}'")

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Default implementation does nothing
        # Override in derived classes to handle mouse press events
        pass

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Default implementation does nothing
        # Override in derived classes to handle mouse move events
        pass

    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse release event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Default implementation does nothing
        # Override in derived classes to handle mouse release events
        pass

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool.

        Returns:
            Cursor to display when this tool is active
        """
        return QCursor(Qt.CursorShape.ArrowCursor)


class SelectionTool(GeometryTool):
    """Tool for selecting and manipulating objects.

    This tool allows users to select objects individually or in groups,
    and perform transformations such as moving, rotating, and scaling.
    """

    # Selection modes
    MODE_SELECT = 0  # Normal selection mode
    MODE_MOVE = 1    # Moving selected objects
    MODE_ROTATE = 2  # Rotating selected objects
    MODE_SCALE = 3   # Scaling selected objects

    def __init__(self) -> None:
        """Initialize the selection tool."""
        super().__init__("Selection", "selection")

        # Selection rectangle
        self.selection_rect_start = None
        self.selection_rect_current = None

        # Transformation state
        self.mode = self.MODE_SELECT
        self.transform_start_pos = None
        self.transform_current_pos = None
        self.transform_center = None

        # Original positions of objects before transformation
        self.original_positions = {}

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Reset selection rectangle
        self.selection_rect_start = None
        self.selection_rect_current = None

        # Reset transformation state
        self.mode = self.MODE_SELECT
        self.transform_start_pos = None
        self.transform_current_pos = None
        self.transform_center = None

        # Reset original positions
        self.original_positions = {}

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Check if we're clicking on an existing object
        if self.canvas:
            obj = self.canvas.get_object_at(scene_pos, tolerance=10.0)

            if obj:
                # Check if we should add to selection or start a new selection
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Toggle selection state
                    if obj.selected:
                        self.canvas.deselect_object(obj)
                    else:
                        self.canvas.select_object(obj)
                else:
                    # Start a new selection if the object is not already selected
                    if not obj.selected:
                        self.canvas.deselect_all_objects()
                        self.canvas.select_object(obj)

                    # Start moving the selected objects
                    self.mode = self.MODE_MOVE
                    self.transform_start_pos = scene_pos
                    self.transform_current_pos = scene_pos

                    # Store original positions of selected objects
                    self._store_original_positions()

                    # Update status message
                    if self.explorer and hasattr(self.explorer, 'status_bar'):
                        self.explorer.status_bar.showMessage("Moving selected objects")

                return

            # If we didn't click on an object, start a selection rectangle
            # unless Ctrl is pressed (which would add to selection)
            if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.canvas.deselect_all_objects()

            self.selection_rect_start = scene_pos
            self.selection_rect_current = scene_pos

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Drag to select objects")

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Clear previous preview
        self._clear_preview()

        if self.mode == self.MODE_MOVE and self.transform_start_pos is not None:
            # Moving selected objects
            self.transform_current_pos = scene_pos

            # Calculate delta
            dx = scene_pos.x() - self.transform_start_pos.x()
            dy = scene_pos.y() - self.transform_start_pos.y()

            # Move selected objects
            self._move_selected_objects(dx, dy)

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Moving selected objects by ({dx:.2f}, {dy:.2f})")

        elif self.mode == self.MODE_ROTATE and self.transform_start_pos is not None:
            # Rotating selected objects
            self.transform_current_pos = scene_pos

            # Calculate rotation angle
            angle = self._calculate_rotation_angle()

            # Rotate selected objects
            self._rotate_selected_objects(angle)

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Rotating selected objects by {angle:.2f} degrees")

        elif self.mode == self.MODE_SCALE and self.transform_start_pos is not None:
            # Scaling selected objects
            self.transform_current_pos = scene_pos

            # Calculate scale factors
            sx, sy = self._calculate_scale_factors()

            # Scale selected objects
            self._scale_selected_objects(sx, sy)

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Scaling selected objects by ({sx:.2f}, {sy:.2f})")

        elif self.selection_rect_start is not None:
            # Updating selection rectangle
            self.selection_rect_current = scene_pos

            # Draw selection rectangle preview
            self._draw_selection_rectangle()

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Drag to select objects")

    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse release event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self.mode == self.MODE_MOVE:
            # Finish moving selected objects
            self.mode = self.MODE_SELECT
            self.transform_start_pos = None
            self.transform_current_pos = None

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Objects moved")

        elif self.mode == self.MODE_ROTATE:
            # Finish rotating selected objects
            self.mode = self.MODE_SELECT
            self.transform_start_pos = None
            self.transform_current_pos = None
            self.transform_center = None

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Objects rotated")

        elif self.mode == self.MODE_SCALE:
            # Finish scaling selected objects
            self.mode = self.MODE_SELECT
            self.transform_start_pos = None
            self.transform_current_pos = None
            self.transform_center = None

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Objects scaled")

        elif self.selection_rect_start is not None:
            # Finish selection rectangle
            self._select_objects_in_rectangle()

            # Clear selection rectangle
            self.selection_rect_start = None
            self.selection_rect_current = None

            # Clear preview
            self._clear_preview()

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                selected_count = len(self.canvas.get_selected_objects()) if self.canvas else 0
                self.explorer.status_bar.showMessage(f"Selected {selected_count} objects")

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            if self.mode != self.MODE_SELECT:
                # Cancel transformation
                self._restore_original_positions()
                self.mode = self.MODE_SELECT
                self.transform_start_pos = None
                self.transform_current_pos = None
                self.transform_center = None

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Transformation cancelled")

                event.accept()
                return
            elif self.selection_rect_start is not None:
                # Cancel selection rectangle
                self.selection_rect_start = None
                self.selection_rect_current = None

                # Clear preview
                self._clear_preview()

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Selection cancelled")

                event.accept()
                return

        # Handle rotation mode
        elif event.key() == Qt.Key.Key_R and self.canvas and self.canvas.get_selected_objects():
            # Switch to rotation mode
            self.mode = self.MODE_ROTATE
            self.transform_start_pos = None
            self.transform_current_pos = None

            # Calculate center of rotation (centroid of selected objects)
            self.transform_center = self._calculate_selection_center()

            # Store original positions
            self._store_original_positions()

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click and drag to rotate selected objects")

            event.accept()
            return

        # Handle scale mode
        elif event.key() == Qt.Key.Key_S and self.canvas and self.canvas.get_selected_objects():
            # Switch to scale mode
            self.mode = self.MODE_SCALE
            self.transform_start_pos = None
            self.transform_current_pos = None

            # Calculate center of scaling (centroid of selected objects)
            self.transform_center = self._calculate_selection_center()

            # Store original positions
            self._store_original_positions()

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click and drag to scale selected objects")

            event.accept()
            return

        # Handle delete key
        elif event.key() == Qt.Key.Key_Delete and self.canvas:
            # Delete selected objects
            selected_objects = self.canvas.get_selected_objects()
            if selected_objects:
                for obj in selected_objects:
                    self.canvas.remove_object(obj)

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Deleted {len(selected_objects)} objects")

                event.accept()
                return

        # Handle select all (Ctrl+A)
        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier and self.canvas:
            # Select all objects
            self.canvas.select_all_objects()

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                selected_count = len(self.canvas.get_selected_objects())
                self.explorer.status_bar.showMessage(f"Selected all objects ({selected_count} total)")

            event.accept()
            return

        # Call base implementation for other keys
        super().key_press(event)

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        if self.mode == self.MODE_MOVE:
            return QCursor(Qt.CursorShape.SizeAllCursor)
        elif self.mode == self.MODE_ROTATE:
            return QCursor(Qt.CursorShape.CrossCursor)
        elif self.mode == self.MODE_SCALE:
            return QCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            return QCursor(Qt.CursorShape.ArrowCursor)

    def _draw_selection_rectangle(self) -> None:
        """Draw the selection rectangle preview."""
        if not self.selection_rect_start or not self.selection_rect_current or not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Calculate rectangle coordinates
        x1 = self.selection_rect_start.x()
        y1 = self.selection_rect_start.y()
        x2 = self.selection_rect_current.x()
        y2 = self.selection_rect_current.y()

        # Ensure x1,y1 is the top-left and x2,y2 is the bottom-right
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Create selection rectangle
        rect_item = self.canvas.scene.addRect(
            QRectF(left, top, width, height),
            QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DashLine),
            QBrush(QColor(100, 100, 255, 30))
        )
        self.preview_items.append(rect_item)

    def _select_objects_in_rectangle(self) -> None:
        """Select all objects that intersect with the selection rectangle."""
        if not self.selection_rect_start or not self.selection_rect_current or not self.canvas:
            return

        # Calculate rectangle coordinates
        x1 = self.selection_rect_start.x()
        y1 = self.selection_rect_start.y()
        x2 = self.selection_rect_current.x()
        y2 = self.selection_rect_current.y()

        # Create selection rectangle
        selection_rect = QRectF(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1)
        )

        # Check each object
        for obj in self.canvas.objects:
            # Get object bounds
            obj_bounds = obj.get_bounds()

            # Check if object intersects with selection rectangle
            if selection_rect.intersects(obj_bounds):
                self.canvas.select_object(obj)

    def _store_original_positions(self) -> None:
        """Store the original positions of selected objects before transformation."""
        if not self.canvas:
            return

        # Get selected objects
        selected_objects = self.canvas.get_selected_objects()

        # Store original positions
        self.original_positions = {}
        for obj in selected_objects:
            if isinstance(obj, Point):
                self.original_positions[obj.id] = {'type': 'point', 'x': obj.x, 'y': obj.y}
            elif isinstance(obj, Line):
                self.original_positions[obj.id] = {
                    'type': 'line',
                    'x1': obj.x1, 'y1': obj.y1,
                    'x2': obj.x2, 'y2': obj.y2
                }
            elif isinstance(obj, Circle):
                self.original_positions[obj.id] = {
                    'type': 'circle',
                    'center': {'x': obj.center.x, 'y': obj.center.y},
                    'radius': obj.radius
                }
            elif isinstance(obj, Polygon):
                vertices = []
                for vertex in obj.vertices:
                    vertices.append({'x': vertex.x, 'y': vertex.y})
                self.original_positions[obj.id] = {'type': 'polygon', 'vertices': vertices}

    def _restore_original_positions(self) -> None:
        """Restore the original positions of objects after cancelled transformation."""
        if not self.canvas:
            return

        # Restore each object
        for obj_id, data in self.original_positions.items():
            # Find the object
            obj = next((obj for obj in self.canvas.objects if obj.id == obj_id), None)
            if not obj:
                continue

            # Restore position based on object type
            if data['type'] == 'point' and isinstance(obj, Point):
                obj.x = data['x']
                obj.y = data['y']
            elif data['type'] == 'line' and isinstance(obj, Line):
                obj.x1 = data['x1']
                obj.y1 = data['y1']
                obj.x2 = data['x2']
                obj.y2 = data['y2']
            elif data['type'] == 'circle' and isinstance(obj, Circle):
                obj.center.x = data['center']['x']
                obj.center.y = data['center']['y']
                obj.radius = data['radius']
            elif data['type'] == 'polygon' and isinstance(obj, Polygon):
                for i, vertex_data in enumerate(data['vertices']):
                    if i < len(obj.vertices):
                        obj.vertices[i].x = vertex_data['x']
                        obj.vertices[i].y = vertex_data['y']

            # Update the object on the canvas
            self.canvas.update_object(obj)

    def _move_selected_objects(self, dx: float, dy: float) -> None:
        """Move selected objects by the given delta.

        Args:
            dx: X-axis delta
            dy: Y-axis delta
        """
        if not self.canvas:
            return

        # Get selected objects
        selected_objects = self.canvas.get_selected_objects()

        # Calculate delta from original positions
        if self.transform_start_pos:
            total_dx = self.transform_current_pos.x() - self.transform_start_pos.x()
            total_dy = self.transform_current_pos.y() - self.transform_start_pos.y()

            # Move each object
            for obj in selected_objects:
                # Get original position
                orig_data = self.original_positions.get(obj.id)
                if not orig_data:
                    continue

                # Move based on object type
                if orig_data['type'] == 'point' and isinstance(obj, Point):
                    obj.x = orig_data['x'] + total_dx
                    obj.y = orig_data['y'] + total_dy
                elif orig_data['type'] == 'line' and isinstance(obj, Line):
                    obj.x1 = orig_data['x1'] + total_dx
                    obj.y1 = orig_data['y1'] + total_dy
                    obj.x2 = orig_data['x2'] + total_dx
                    obj.y2 = orig_data['y2'] + total_dy
                elif orig_data['type'] == 'circle' and isinstance(obj, Circle):
                    obj.center.x = orig_data['center']['x'] + total_dx
                    obj.center.y = orig_data['center']['y'] + total_dy
                elif orig_data['type'] == 'polygon' and isinstance(obj, Polygon):
                    for i, vertex_data in enumerate(orig_data['vertices']):
                        if i < len(obj.vertices):
                            obj.vertices[i].x = vertex_data['x'] + total_dx
                            obj.vertices[i].y = vertex_data['y'] + total_dy

                # Update the object on the canvas
                self.canvas.update_object(obj)

    def _calculate_selection_center(self) -> QPointF:
        """Calculate the center point of the selected objects.

        Returns:
            Center point of the selection
        """
        if not self.canvas:
            return QPointF(0, 0)

        # Get selected objects
        selected_objects = self.canvas.get_selected_objects()
        if not selected_objects:
            return QPointF(0, 0)

        # Calculate bounding box of all selected objects
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        for obj in selected_objects:
            bounds = obj.get_bounds()
            min_x = min(min_x, bounds.left())
            min_y = min(min_y, bounds.top())
            max_x = max(max_x, bounds.right())
            max_y = max(max_y, bounds.bottom())

        # Calculate center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        return QPointF(center_x, center_y)

    def _calculate_rotation_angle(self) -> float:
        """Calculate the rotation angle based on current mouse position.

        Returns:
            Rotation angle in degrees
        """
        if not self.transform_start_pos or not self.transform_current_pos or not self.transform_center:
            return 0.0

        # Calculate vectors from center to start and current positions
        start_vec = QLineF(
            self.transform_center.x(),
            self.transform_center.y(),
            self.transform_start_pos.x(),
            self.transform_start_pos.y()
        )

        current_vec = QLineF(
            self.transform_center.x(),
            self.transform_center.y(),
            self.transform_current_pos.x(),
            self.transform_current_pos.y()
        )

        # Calculate angle between vectors
        start_angle = math.degrees(math.atan2(start_vec.dy(), start_vec.dx()))
        current_angle = math.degrees(math.atan2(current_vec.dy(), current_vec.dx()))

        # Calculate rotation angle
        angle = current_angle - start_angle

        return angle

    def _rotate_selected_objects(self, angle: float) -> None:
        """Rotate selected objects by the given angle.

        Args:
            angle: Rotation angle in degrees
        """
        if not self.canvas or not self.transform_center:
            return

        # Get selected objects
        selected_objects = self.canvas.get_selected_objects()

        # Rotate each object
        for obj in selected_objects:
            # Get original position
            orig_data = self.original_positions.get(obj.id)
            if not orig_data:
                continue

            # Rotate based on object type
            if orig_data['type'] == 'point' and isinstance(obj, Point):
                # Calculate new position after rotation
                x = orig_data['x'] - self.transform_center.x()
                y = orig_data['y'] - self.transform_center.y()

                # Rotate
                angle_rad = math.radians(angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a

                # Translate back
                obj.x = new_x + self.transform_center.x()
                obj.y = new_y + self.transform_center.y()

            elif orig_data['type'] == 'line' and isinstance(obj, Line):
                # Rotate each endpoint
                # First endpoint (x1, y1)
                x = orig_data['x1'] - self.transform_center.x()
                y = orig_data['y1'] - self.transform_center.y()

                # Rotate
                angle_rad = math.radians(angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a

                # Translate back
                obj.x1 = new_x + self.transform_center.x()
                obj.y1 = new_y + self.transform_center.y()

                # Second endpoint (x2, y2)
                x = orig_data['x2'] - self.transform_center.x()
                y = orig_data['y2'] - self.transform_center.y()

                # Rotate
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a

                # Translate back
                obj.x2 = new_x + self.transform_center.x()
                obj.y2 = new_y + self.transform_center.y()

            elif orig_data['type'] == 'circle' and isinstance(obj, Circle):
                # Rotate center
                x = orig_data['center']['x'] - self.transform_center.x()
                y = orig_data['center']['y'] - self.transform_center.y()

                # Rotate
                angle_rad = math.radians(angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a

                # Translate back
                obj.center.x = new_x + self.transform_center.x()
                obj.center.y = new_y + self.transform_center.y()

            elif orig_data['type'] == 'polygon' and isinstance(obj, Polygon):
                # Rotate each vertex
                for i, vertex_data in enumerate(orig_data['vertices']):
                    if i < len(obj.vertices):
                        x = vertex_data['x'] - self.transform_center.x()
                        y = vertex_data['y'] - self.transform_center.y()

                        # Rotate
                        angle_rad = math.radians(angle)
                        cos_a = math.cos(angle_rad)
                        sin_a = math.sin(angle_rad)
                        new_x = x * cos_a - y * sin_a
                        new_y = x * sin_a + y * cos_a

                        # Translate back
                        obj.vertices[i].x = new_x + self.transform_center.x()
                        obj.vertices[i].y = new_y + self.transform_center.y()

            # Update the object on the canvas
            self.canvas.update_object(obj)

    def _calculate_scale_factors(self) -> Tuple[float, float]:
        """Calculate the scale factors based on current mouse position.

        Returns:
            Tuple of (x_scale, y_scale)
        """
        if not self.transform_start_pos or not self.transform_current_pos or not self.transform_center:
            return 1.0, 1.0

        # Calculate distances from center to start and current positions
        start_dist_x = self.transform_start_pos.x() - self.transform_center.x()
        start_dist_y = self.transform_start_pos.y() - self.transform_center.y()
        current_dist_x = self.transform_current_pos.x() - self.transform_center.x()
        current_dist_y = self.transform_current_pos.y() - self.transform_center.y()

        # Calculate scale factors
        sx = 1.0
        sy = 1.0

        if abs(start_dist_x) > 1e-6:
            sx = current_dist_x / start_dist_x
        if abs(start_dist_y) > 1e-6:
            sy = current_dist_y / start_dist_y

        # Limit scale factors to reasonable values
        sx = max(0.1, min(10.0, sx))
        sy = max(0.1, min(10.0, sy))

        # If shift is pressed, maintain aspect ratio
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
            # Use the larger scale factor
            if abs(sx) > abs(sy):
                sy = sx * (1 if sy > 0 else -1)
            else:
                sx = sy * (1 if sx > 0 else -1)

        return sx, sy

    def _scale_selected_objects(self, sx: float, sy: float) -> None:
        """Scale selected objects by the given factors.

        Args:
            sx: X-axis scale factor
            sy: Y-axis scale factor
        """
        if not self.canvas or not self.transform_center:
            return

        # Get selected objects
        selected_objects = self.canvas.get_selected_objects()

        # Scale each object
        for obj in selected_objects:
            # Get original position
            orig_data = self.original_positions.get(obj.id)
            if not orig_data:
                continue

            # Scale based on object type
            if orig_data['type'] == 'point' and isinstance(obj, Point):
                # Calculate new position after scaling
                dx = orig_data['x'] - self.transform_center.x()
                dy = orig_data['y'] - self.transform_center.y()

                # Scale
                new_dx = dx * sx
                new_dy = dy * sy

                # Translate back
                obj.x = self.transform_center.x() + new_dx
                obj.y = self.transform_center.y() + new_dy

            elif orig_data['type'] == 'line' and isinstance(obj, Line):
                # Scale first endpoint (x1, y1)
                dx = orig_data['x1'] - self.transform_center.x()
                dy = orig_data['y1'] - self.transform_center.y()

                # Scale
                new_dx = dx * sx
                new_dy = dy * sy

                # Translate back
                obj.x1 = self.transform_center.x() + new_dx
                obj.y1 = self.transform_center.y() + new_dy

                # Scale second endpoint (x2, y2)
                dx = orig_data['x2'] - self.transform_center.x()
                dy = orig_data['y2'] - self.transform_center.y()

                # Scale
                new_dx = dx * sx
                new_dy = dy * sy

                # Translate back
                obj.x2 = self.transform_center.x() + new_dx
                obj.y2 = self.transform_center.y() + new_dy

            elif orig_data['type'] == 'circle' and isinstance(obj, Circle):
                # Scale center
                dx = orig_data['center']['x'] - self.transform_center.x()
                dy = orig_data['center']['y'] - self.transform_center.y()

                # Scale
                new_dx = dx * sx
                new_dy = dy * sy

                # Translate back
                obj.center.x = self.transform_center.x() + new_dx
                obj.center.y = self.transform_center.y() + new_dy

                # Scale radius (use average of sx and sy for uniform scaling)
                scale_factor = (abs(sx) + abs(sy)) / 2
                obj.radius = orig_data['radius'] * scale_factor

            elif orig_data['type'] == 'polygon' and isinstance(obj, Polygon):
                # Scale each vertex
                for i, vertex_data in enumerate(orig_data['vertices']):
                    if i < len(obj.vertices):
                        dx = vertex_data['x'] - self.transform_center.x()
                        dy = vertex_data['y'] - self.transform_center.y()

                        # Scale
                        new_dx = dx * sx
                        new_dy = dy * sy

                        # Translate back
                        obj.vertices[i].x = self.transform_center.x() + new_dx
                        obj.vertices[i].y = self.transform_center.y() + new_dy

            # Update the object on the canvas
            self.canvas.update_object(obj)


class PointTool(GeometryTool):
    """Tool for creating and manipulating points.

    This tool allows users to create points by clicking on the canvas,
    drag points to reposition them, and customize point appearance.
    Points can snap to grid and existing objects when appropriate.
    """

    def __init__(self) -> None:
        """Initialize the point tool."""
        super().__init__("Point", "point")

        # Point style options
        self.point_size = 5.0
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.fill_color = QColor(255, 255, 255)  # White

        # Dragging state
        self.dragging = False
        self.drag_point = None
        self.drag_start_pos = None

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'preview_point': None,  # Preview point for visualization
            'snap_target': None,    # Current snap target (object or grid point)
            'snap_type': None       # Type of snap (grid, object, none)
        }

        # Set state
        self.state = ToolState.IDLE

    def _update_preview(self) -> None:
        """Update preview visualization."""
        # Clear existing preview
        self._clear_preview()

        # If we have a canvas, create preview point
        if self.canvas and self.options.show_preview:
            # Get current mouse position
            current_pos = self.data.get('current_pos', QPointF(0, 0))

            # Create preview point
            if hasattr(self.canvas, 'scene'):
                # Create point item
                point_size = self.point_size
                point_item = self.canvas.scene.addEllipse(
                    QRectF(current_pos.x() - point_size/2, current_pos.y() - point_size/2, point_size, point_size),
                    QPen(QColor(100, 100, 255, 150)),
                    QBrush(QColor(200, 200, 255, 100))
                )

                # Add to preview items
                self.preview_items.append(point_item)

                # Show snap indicator if snapping
                snap_type = self.data.get('snap_type')
                if snap_type == 'grid':
                    # Add grid snap indicator
                    grid_indicator = self.canvas.scene.addEllipse(
                        QRectF(current_pos.x() - 3, current_pos.y() - 3, 6, 6),
                        QPen(QColor(0, 150, 0, 200)),
                        QBrush(Qt.BrushStyle.NoBrush)
                    )
                    self.preview_items.append(grid_indicator)
                elif snap_type == 'object':
                    # Add object snap indicator
                    obj_indicator = self.canvas.scene.addEllipse(
                        QRectF(current_pos.x() - 4, current_pos.y() - 4, 8, 8),
                        QPen(QColor(150, 0, 150, 200)),
                        QBrush(Qt.BrushStyle.NoBrush)
                    )
                    self.preview_items.append(obj_indicator)

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Check if we're clicking on an existing point (for dragging)
        if self.canvas:
            obj = self.canvas.get_object_at(scene_pos, tolerance=10.0)
            if obj and isinstance(obj, Point):
                # Start dragging the point
                self.dragging = True
                self.drag_point = obj
                self.drag_start_pos = scene_pos

                # Select the point
                self.canvas.select_object(obj)

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Dragging point {obj.name}")

                return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Create point with current style settings
        point = self._create_object(
            'point',
            x=pos.x(),
            y=pos.y(),
            style=self._create_point_style()
        )

        # Select the newly created point
        if point and self.canvas:
            self.canvas.select_object(point)

        # If continuous creation is enabled, stay in creation mode
        if self.options.continuous_creation:
            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Created point at ({pos.x():.2f}, {pos.y():.2f}). Click to create another.")
        else:
            # Complete operation
            self._complete_operation()

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Handle dragging
        if self.dragging and self.drag_point:
            # Snap position to grid/objects
            pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

            # Move the point
            self.drag_point.x = pos.x()
            self.drag_point.y = pos.y()

            # Update the canvas
            if self.canvas:
                self.canvas.update_object(self.drag_point)

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Dragging point to ({pos.x():.2f}, {pos.y():.2f})")

            return

        # Get snap information
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Store current position and snap info
        self.data['current_pos'] = pos
        self.data['snap_type'] = snap_type
        self.data['snap_target'] = snap_target

        # Update preview
        if self.options.show_preview:
            self._update_preview()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if snap_type == 'grid':
                self.explorer.status_bar.showMessage(f"Click to create point at grid point ({pos.x():.2f}, {pos.y():.2f})")
            elif snap_type == 'object' and snap_target:
                self.explorer.status_bar.showMessage(f"Click to create point on {snap_target.__class__.__name__} {snap_target.name}")
            else:
                self.explorer.status_bar.showMessage(f"Click to create point at ({pos.x():.2f}, {pos.y():.2f})")

    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse release event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # End dragging
        if self.dragging and self.drag_point:
            # Snap position to grid/objects
            pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

            # Move the point to the final position
            dx = pos.x() - self.drag_start_pos.x()
            dy = pos.y() - self.drag_start_pos.y()

            # Reset dragging state
            self.dragging = False
            self.drag_point = None
            self.drag_start_pos = None

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Point dragging completed")

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                # Skip the point we're currently dragging
                if self.dragging and self.drag_point and obj.id == self.drag_point.id:
                    continue

                # Calculate distance to object
                dist = obj.distance_to(pos)

                # Check if this is the closest object within tolerance
                if dist < closest_dist and dist <= self.options.snap_tolerance:
                    closest_obj = obj
                    closest_dist = dist

                    # For points, snap directly to the point
                    if isinstance(obj, Point):
                        closest_point = QPointF(obj.x, obj.y)
                    # For lines, find closest point on the line
                    elif isinstance(obj, Line):
                        # Calculate projection onto line
                        line_vec = QLineF(obj.x1, obj.y1, obj.x2, obj.y2)
                        line_length_sq = line_vec.length() ** 2

                        if line_length_sq > 0:
                            t = ((pos.x() - obj.x1) * (obj.x2 - obj.x1) +
                                 (pos.y() - obj.y1) * (obj.y2 - obj.y1)) / line_length_sq
                            t = max(0, min(1, t))  # Clamp to line segment

                            closest_point = QPointF(
                                obj.x1 + t * (obj.x2 - obj.x1),
                                obj.y1 + t * (obj.y2 - obj.y1)
                            )
                    # For circles, find closest point on the circumference
                    elif isinstance(obj, Circle):
                        # Calculate vector from center to position
                        dx = pos.x() - obj.center.x
                        dy = pos.y() - obj.center.y
                        dist_from_center = math.sqrt(dx * dx + dy * dy)

                        if dist_from_center > 0:
                            # Normalize and scale to radius
                            closest_point = QPointF(
                                obj.center.x + (dx / dist_from_center) * obj.radius,
                                obj.center.y + (dy / dist_from_center) * obj.radius
                            )

            # If we found a close object, snap to it
            if closest_obj and closest_point:
                snapped_pos = closest_point
                snap_type = 'object'
                snap_target = closest_obj

        # If not snapped to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)

            # Check if grid snap is within tolerance
            dx = grid_pos.x() - pos.x()
            dy = grid_pos.y() - pos.y()
            grid_dist = math.sqrt(dx * dx + dy * dy)

            if grid_dist <= self.options.snap_tolerance:
                snapped_pos = grid_pos
                snap_type = 'grid'

        return snapped_pos, snap_type, snap_target

    def _create_point_style(self) -> Style:
        """Create a style for new points based on current settings.

        Returns:
            Style object for the point
        """
        style = Style()
        style.stroke_color = self.stroke_color
        style.fill_color = self.fill_color
        style.point_size = self.point_size
        return style

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def set_point_size(self, size: float) -> None:
        """Set the point size for new points.

        Args:
            size: Point size in pixels
        """
        self.point_size = size

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new points.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new points.

        Args:
            color: Fill color
        """
        self.fill_color = color

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation or dragging
        if event.key() == Qt.Key.Key_Escape:
            if self.dragging:
                # Cancel dragging
                self.dragging = False
                self.drag_point = None
                self.drag_start_pos = None

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Point dragging cancelled")
            else:
                # Cancel operation
                self._cancel_operation()

            event.accept()
            return

        # Call base implementation for other keys
        super().key_press(event)


class LineTool(GeometryTool):
    """Tool for creating lines.

    This tool allows users to create different types of lines (segments, rays, or infinite lines)
    by selecting two points on the canvas. Lines can be customized with different styles.
    """

    def __init__(self) -> None:
        """Initialize the line tool."""
        super().__init__("Line", "line")

        # Line style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine

        # Line type
        self.line_type = LineType.SEGMENT

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'start_point': None,  # First point of the line
            'preview_line': None,  # Preview line item
            'snap_target': None,   # Current snap target (object or grid point)
            'snap_type': None      # Type of snap (grid, object, none)
        }

        # Set state
        self.state = ToolState.IDLE

    def _update_preview(self) -> None:
        """Update preview visualization."""
        # Clear existing preview
        self._clear_preview()

        # If we have a start point and canvas, create preview line
        if self.state == ToolState.ACTIVE and 'start_point' in self.data and self.data['start_point'] and self.canvas:
            # Get start point
            start_point = self.data['start_point']

            # Get current mouse position
            current_pos = self.data.get('current_pos', QPointF(0, 0))

            # Create preview line based on line type
            if hasattr(self.canvas, 'scene'):
                # Set up pen for preview
                preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

                # Draw different line types
                if self.line_type == LineType.SEGMENT:
                    # Draw line segment
                    line_item = self.canvas.scene.addLine(
                        QLineF(start_point.x(), start_point.y(), current_pos.x(), current_pos.y()),
                        preview_pen
                    )
                    self.preview_items.append(line_item)
                elif self.line_type == LineType.RAY:
                    # Draw ray (from start_point extending through current_pos)
                    # Calculate direction vector
                    dx = current_pos.x() - start_point.x()
                    dy = current_pos.y() - start_point.y()

                    # Normalize direction vector
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        dx /= length
                        dy /= length

                    # Extend the line by a large amount in the direction of current_pos
                    extension = 10000  # A large value to ensure the line extends beyond the visible area
                    extended_x = start_point.x() + dx * extension
                    extended_y = start_point.y() + dy * extension

                    # Draw the ray
                    line_item = self.canvas.scene.addLine(
                        QLineF(start_point.x(), start_point.y(), extended_x, extended_y),
                        preview_pen
                    )
                    self.preview_items.append(line_item)
                else:  # LineType.INFINITE
                    # Draw infinite line (extending in both directions)
                    # Calculate direction vector
                    dx = current_pos.x() - start_point.x()
                    dy = current_pos.y() - start_point.y()

                    # Normalize direction vector
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        dx /= length
                        dy /= length

                    # Extend the line by a large amount in both directions
                    extension = 10000  # A large value to ensure the line extends beyond the visible area
                    extended_x1 = start_point.x() - dx * extension
                    extended_y1 = start_point.y() - dy * extension
                    extended_x2 = current_pos.x() + dx * extension
                    extended_y2 = current_pos.y() + dy * extension

                    # Draw the infinite line
                    line_item = self.canvas.scene.addLine(
                        QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                        preview_pen
                    )
                    self.preview_items.append(line_item)

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.state == ToolState.IDLE:
            # First point
            self.data['start_point'] = QPointF(pos)
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                line_type_name = self.line_type.name.lower()
                self.explorer.status_bar.showMessage(f"Click to place second point for {line_type_name}")

        elif self.state == ToolState.ACTIVE:
            # Second point - create line
            start_point = self.data['start_point']

            # Create line style
            style = self._create_line_style()

            # Create line
            self._create_object(
                'line',
                x1=start_point.x(),
                y1=start_point.y(),
                x2=pos.x(),
                y2=pos.y(),
                style=style,
                line_type=self.line_type
            )

            # Complete operation
            self._complete_operation()

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Store current position
        self.data['current_pos'] = pos
        self.data['snap_type'] = snap_type
        self.data['snap_target'] = snap_target

        # Update preview
        if self.state == ToolState.ACTIVE and self.options.show_preview:
            self._update_preview()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            line_type_name = self.line_type.name.lower()
            if self.state == ToolState.IDLE:
                self.explorer.status_bar.showMessage(
                    f"Click to place first point of {line_type_name} at ({pos.x():.2f}, {pos.y():.2f})"
                )
            elif self.state == ToolState.ACTIVE:
                start_point = self.data['start_point']
                self.explorer.status_bar.showMessage(
                    f"{line_type_name.capitalize()} from ({start_point.x():.2f}, {start_point.y():.2f}) to ({pos.x():.2f}, {pos.y():.2f})"
                )

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Line creation cancelled")

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def set_line_type(self, line_type: LineType) -> None:
        """Set the line type for new lines.

        Args:
            line_type: Type of line (segment, ray, or infinite)
        """
        self.line_type = line_type

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new lines.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new lines.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new lines.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def _create_line_style(self) -> Style:
        """Create a style object for new lines.

        Returns:
            Style object for new lines
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style
        )

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                try:
                    # Calculate distance to object
                    dist = obj.distance_to(pos)

                    # Check if this is the closest object within tolerance
                    if dist < closest_dist and dist <= self.options.snap_tolerance:
                        closest_obj = obj
                        closest_dist = dist

                        # For points, snap directly to the point
                        if isinstance(obj, Point):
                            closest_point = QPointF(obj.x, obj.y)
                        # For lines, find closest point on the line
                        elif isinstance(obj, Line):
                            # Calculate projection onto line
                            x1, y1 = obj.x1, obj.y1
                            x2, y2 = obj.x2, obj.y2
                            x0, y0 = pos.x(), pos.y()

                            # Calculate line length squared
                            line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

                            if line_length_sq > 1e-10:  # Avoid division by zero
                                # Calculate projection of point onto line
                                t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

                                # Clamp t based on line type
                                if obj.line_type == LineType.SEGMENT:
                                    t = max(0, min(1, t))
                                elif obj.line_type == LineType.RAY:
                                    t = max(0, t)

                                # Calculate closest point on line
                                closest_x = x1 + t * (x2 - x1)
                                closest_y = y1 + t * (y2 - y1)
                                closest_point = QPointF(closest_x, closest_y)
                        # For circles, find closest point on the circle
                        elif isinstance(obj, Circle):
                            # Calculate vector from center to pos
                            cx, cy = obj.center.x, obj.center.y
                            dx = pos.x() - cx
                            dy = pos.y() - cy

                            # Calculate distance from center
                            dist_from_center = math.sqrt(dx * dx + dy * dy)

                            if dist_from_center > 1e-10:  # Avoid division by zero
                                # Normalize vector
                                dx /= dist_from_center
                                dy /= dist_from_center

                                # Calculate point on circle
                                closest_x = cx + dx * obj.radius
                                closest_y = cy + dy * obj.radius
                                closest_point = QPointF(closest_x, closest_y)
                        # For polygons, find closest point on the polygon
                        elif isinstance(obj, Polygon):
                            # For polygons, we already have the distance from distance_to method
                            # We need to find the closest point on the polygon
                            # For simplicity, we'll use the closest vertex for now
                            if obj.vertices:
                                # Find the closest vertex
                                closest_vertex = None
                                min_vertex_dist = float('inf')

                                for vertex in obj.vertices:
                                    dx = vertex.x - pos.x()
                                    dy = vertex.y - pos.y()
                                    vertex_dist = math.sqrt(dx * dx + dy * dy)

                                    if vertex_dist < min_vertex_dist:
                                        min_vertex_dist = vertex_dist
                                        closest_vertex = vertex

                                if closest_vertex:
                                    closest_point = QPointF(closest_vertex.x, closest_vertex.y)
                except AttributeError:
                    # Skip objects that don't have the required attributes
                    continue

            # If we found a close object, snap to it
            if closest_obj and closest_point:
                snapped_pos = closest_point
                snap_type = 'object'
                snap_target = closest_obj

        # If not snapped to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)

            # Check if grid snap is within tolerance
            dx = grid_pos.x() - pos.x()
            dy = grid_pos.y() - pos.y()
            grid_dist = math.sqrt(dx * dx + dy * dy)

            if grid_dist <= self.options.snap_tolerance:
                snapped_pos = grid_pos
                snap_type = 'grid'

        return snapped_pos, snap_type, snap_target


class PolygonTool(GeometryTool):
    """Tool for creating polygons.

    This tool allows users to create polygons by selecting vertices one by one.
    Polygons can be completed by double-clicking, clicking near the starting vertex,
    or pressing Enter. Polygons can be customized with different styles.
    """

    def __init__(self) -> None:
        """Initialize the polygon tool."""
        super().__init__("Polygon", "polygon")

        # Polygon style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine
        self.fill_color = QColor(255, 255, 255, 50)  # Transparent white
        self.fill_style = Qt.BrushStyle.SolidPattern

        # Completion options
        self.close_distance = 15.0  # Distance to first vertex to auto-close
        self.min_vertices = 3  # Minimum number of vertices for a valid polygon

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'vertices': [],  # List of vertices (Point objects)
            'preview_vertices': [],  # List of vertex positions (QPointF objects)
            'snap_target': None,     # Current snap target (object or grid point)
            'snap_type': None,       # Type of snap (grid, object, none)
            'last_click_time': 0,    # Time of last click (for double-click detection)
            'double_click_interval': 400  # Maximum time between clicks for double-click (ms)
        }

        # Set state
        self.state = ToolState.IDLE

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Get current time for double-click detection
        current_time = event.timestamp()
        last_click_time = self.data.get('last_click_time', 0)
        self.data['last_click_time'] = current_time

        # Check for double-click
        is_double_click = (current_time - last_click_time) <= self.data['double_click_interval']

        # If we're in idle state, start a new polygon
        if self.state == ToolState.IDLE:
            # Create first vertex
            first_vertex = Point(pos.x(), pos.y())
            self.data['vertices'] = [first_vertex]
            self.data['preview_vertices'] = [QPointF(pos)]
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click to add vertices. To complete polygon: 1) Double-click, 2) Press Enter, or 3) Click near first vertex")

        # If we're in active state, add a vertex or complete the polygon
        elif self.state == ToolState.ACTIVE:
            # Check if we're clicking near the first vertex to close the polygon
            if len(self.data['vertices']) >= self.min_vertices:
                first_vertex = self.data['vertices'][0]
                dx = pos.x() - first_vertex.x
                dy = pos.y() - first_vertex.y
                distance_to_first = math.sqrt(dx * dx + dy * dy)

                if distance_to_first <= self.close_distance:
                    # Close the polygon
                    self._complete_polygon()
                    return

            # Check for double-click to complete the polygon
            if is_double_click and len(self.data['vertices']) >= self.min_vertices:
                # Complete the polygon
                self._complete_polygon()
                return

            # Add a new vertex
            new_vertex = Point(pos.x(), pos.y())
            self.data['vertices'].append(new_vertex)
            self.data['preview_vertices'].append(QPointF(pos))

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                vertex_count = len(self.data['vertices'])
                self.explorer.status_bar.showMessage(
                    f"Added vertex {vertex_count}. Click to add more, double-click or press Enter to complete."
                )

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Store current position and snap info
        self.data['current_pos'] = pos
        self.data['snap_type'] = snap_type
        self.data['snap_target'] = snap_target

        # Update preview
        if self.options.show_preview:
            self._update_preview()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.state == ToolState.IDLE:
                self.explorer.status_bar.showMessage(f"Click to place first vertex at ({pos.x():.2f}, {pos.y():.2f})")
            elif self.state == ToolState.ACTIVE:
                vertex_count = len(self.data['vertices'])
                if vertex_count >= self.min_vertices:
                    # Check if we're near the first vertex
                    first_vertex = self.data['vertices'][0]
                    dx = pos.x() - first_vertex.x
                    dy = pos.y() - first_vertex.y
                    distance_to_first = math.sqrt(dx * dx + dy * dy)

                    if distance_to_first <= self.close_distance:
                        self.explorer.status_bar.showMessage(
                            f"Click to close polygon with {vertex_count} vertices"
                        )
                        return

                self.explorer.status_bar.showMessage(
                    f"Polygon with {vertex_count} vertices. Click to add more, double-click or press Enter to complete."
                )

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle enter key to complete polygon
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.state == ToolState.ACTIVE and len(self.data['vertices']) >= self.min_vertices:
                self._complete_polygon()
                event.accept()
                return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketLeft:
                # Decrease fill opacity
                opacity = max(0, self.fill_color.alpha() - 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketRight:
                # Increase fill opacity
                opacity = min(255, self.fill_color.alpha() + 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _update_preview(self) -> None:
        """Update preview visualization."""
        # Clear existing preview
        self._clear_preview()

        # Only proceed if we have a canvas
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Get current mouse position
        current_pos = self.data.get('current_pos', QPointF(0, 0))

        # Set up pen and brush for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)
        preview_brush = QBrush(QColor(100, 100, 255, 30), Qt.BrushStyle.SolidPattern)

        # If we have vertices, draw the preview polygon
        if self.state == ToolState.ACTIVE and self.data['preview_vertices']:
            vertices = self.data['preview_vertices']

            # Draw lines connecting the vertices
            for i in range(len(vertices) - 1):
                line_item = self.canvas.scene.addLine(
                    vertices[i].x(), vertices[i].y(),
                    vertices[i+1].x(), vertices[i+1].y(),
                    preview_pen
                )
                self.preview_items.append(line_item)

            # Draw line from last vertex to current mouse position
            if vertices:
                last_vertex = vertices[-1]
                line_item = self.canvas.scene.addLine(
                    last_vertex.x(), last_vertex.y(),
                    current_pos.x(), current_pos.y(),
                    preview_pen
                )
                self.preview_items.append(line_item)

            # If we have enough vertices, draw a preview polygon
            if len(vertices) >= 2:
                # Create a polygon with the current vertices plus the current mouse position
                polygon_points = [QPointF(v) for v in vertices]
                polygon_points.append(current_pos)

                # Check if we're near the first vertex to close the polygon
                if len(vertices) >= self.min_vertices:
                    first_vertex = vertices[0]
                    dx = current_pos.x() - first_vertex.x()
                    dy = current_pos.y() - first_vertex.y()
                    distance_to_first = math.sqrt(dx * dx + dy * dy)

                    if distance_to_first <= self.close_distance:
                        # Use the first vertex position instead of current mouse position
                        polygon_points[-1] = QPointF(first_vertex)

                        # Draw a highlight around the first vertex
                        highlight_item = self.canvas.scene.addEllipse(
                            first_vertex.x() - self.close_distance / 2,
                            first_vertex.y() - self.close_distance / 2,
                            self.close_distance,
                            self.close_distance,
                            QPen(QColor(100, 255, 100, 150), 1, Qt.PenStyle.DotLine),
                            QBrush(QColor(100, 255, 100, 50))
                        )
                        self.preview_items.append(highlight_item)

                # Create a QPolygonF for the preview
                qpolygon = QPolygonF(polygon_points)

                # Add the polygon to the scene
                polygon_item = self.canvas.scene.addPolygon(qpolygon, preview_pen, preview_brush)
                self.preview_items.append(polygon_item)

    def _complete_polygon(self) -> None:
        """Complete the polygon and create it."""
        # Check if we have enough vertices
        if len(self.data['vertices']) < self.min_vertices:
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(
                    f"Need at least {self.min_vertices} vertices to create a polygon. Current: {len(self.data['vertices'])}"
                )
            return

        # Create polygon style
        style = self._create_polygon_style()

        # Create polygon
        self._create_object(
            'polygon',
            vertices=self.data['vertices'],
            style=style
        )

        # Complete operation
        self._complete_operation()

    def _create_polygon_style(self) -> Style:
        """Create a style object for new polygons.

        Returns:
            Style object for new polygons
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style,
            fill_color=self.fill_color,
            fill_style=self.fill_style
        )

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                # Calculate distance to object
                dist = obj.distance_to(pos)

                # Check if this is the closest object within tolerance
                if dist < closest_dist and dist <= self.options.snap_tolerance:
                    closest_obj = obj
                    closest_dist = dist

                    # For points, snap directly to the point
                    if isinstance(obj, Point):
                        closest_point = QPointF(obj.x, obj.y)
                    # For lines, find closest point on the line
                    elif isinstance(obj, Line):
                        # Calculate projection onto line
                        x1, y1 = obj.x1, obj.y1
                        x2, y2 = obj.x2, obj.y2
                        x0, y0 = pos.x(), pos.y()

                        # Calculate line length squared
                        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

                        if line_length_sq > 1e-10:  # Avoid division by zero
                            # Calculate projection of point onto line
                            t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

                            # Clamp t based on line type
                            if obj.line_type == LineType.SEGMENT:
                                t = max(0, min(1, t))
                            elif obj.line_type == LineType.RAY:
                                t = max(0, t)

                            # Calculate closest point on line
                            closest_x = x1 + t * (x2 - x1)
                            closest_y = y1 + t * (y2 - y1)
                            closest_point = QPointF(closest_x, closest_y)
                    # For circles, find closest point on the circle
                    elif isinstance(obj, Circle):
                        # Calculate vector from center to pos
                        cx, cy = obj.center.x, obj.center.y
                        dx = pos.x() - cx
                        dy = pos.y() - cy

                        # Calculate distance from center
                        dist_from_center = math.sqrt(dx * dx + dy * dy)

                        if dist_from_center > 1e-10:  # Avoid division by zero
                            # Normalize vector
                            dx /= dist_from_center
                            dy /= dist_from_center

                            # Calculate point on circle
                            closest_x = cx + dx * obj.radius
                            closest_y = cy + dy * obj.radius
                            closest_point = QPointF(closest_x, closest_y)

            # If we found a close object, snap to it
            if closest_obj and closest_point:
                snapped_pos = closest_point
                snap_type = 'object'
                snap_target = closest_obj

        # If not snapped to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)

            # Check if grid snap is within tolerance
            dx = grid_pos.x() - pos.x()
            dy = grid_pos.y() - pos.y()
            grid_dist = math.sqrt(dx * dx + dy * dy)

            if grid_dist <= self.options.snap_tolerance:
                snapped_pos = grid_pos
                snap_type = 'grid'

        return snapped_pos, snap_type, snap_target

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new polygons.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new polygons.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new polygons.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new polygons.

        Args:
            color: Fill color
        """
        self.fill_color = color

    def set_fill_style(self, style: Qt.BrushStyle) -> None:
        """Set the fill style for new polygons.

        Args:
            style: Fill style
        """
        self.fill_style = style

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)


class RegularPolygonTool(GeometryTool):
    """Tool for creating regular polygons.

    This tool allows users to create regular polygons with a specified number of sides.
    Regular polygons can be created by specifying a center point and a vertex.
    The number of sides and orientation can be customized.
    """

    # Orientation options
    ORIENTATION_VERTEX_TOP = "vertex_top"  # Vertex at the top
    ORIENTATION_SIDE_TOP = "side_top"  # Side at the top

    def __init__(self) -> None:
        """Initialize the regular polygon tool."""
        super().__init__("Regular Polygon", "regular_polygon")

        # Polygon style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine
        self.fill_color = QColor(255, 255, 255, 50)  # Transparent white
        self.fill_style = Qt.BrushStyle.SolidPattern

        # Regular polygon options
        self.sides = 6  # Default number of sides
        self.min_sides = 3  # Minimum number of sides
        self.max_sides = 20  # Maximum number of sides
        self.orientation = self.ORIENTATION_VERTEX_TOP  # Default orientation

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'center': None,  # Center point
            'vertex': None,  # Vertex point
            'preview_polygon': None,  # Preview polygon
            'snap_target': None,  # Current snap target
            'snap_type': None,  # Type of snap (grid, object, none)
        }

        # Set state
        self.state = ToolState.IDLE

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.state == ToolState.IDLE:
            # First click - set center point
            center_point = Point(pos.x(), pos.y())
            self.data['center'] = center_point
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(
                    f"Center point set at ({pos.x():.2f}, {pos.y():.2f}). Click to place vertex and create {self.sides}-sided polygon."
                )

        elif self.state == ToolState.ACTIVE:
            # Second click - create regular polygon
            if self.data['center']:
                # Create vertex point
                vertex_point = Point(pos.x(), pos.y())
                self.data['vertex'] = vertex_point

                # Create regular polygon
                self._create_regular_polygon()

                # Complete operation
                self._complete_operation()

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Store current position and snap info
        self.data['current_pos'] = pos
        self.data['snap_type'] = snap_type
        self.data['snap_target'] = snap_target

        # Update preview
        if self.options.show_preview:
            self._update_preview()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.state == ToolState.IDLE:
                self.explorer.status_bar.showMessage(
                    f"Click to place center point of {self.sides}-sided polygon at ({pos.x():.2f}, {pos.y():.2f})"
                )
            elif self.state == ToolState.ACTIVE and self.data['center']:
                center = self.data['center']
                # Calculate radius
                dx = pos.x() - center.x
                dy = pos.y() - center.y
                radius = math.sqrt(dx * dx + dy * dy)

                self.explorer.status_bar.showMessage(
                    f"Center at ({center.x:.2f}, {center.y:.2f}), radius: {radius:.2f}. Click to create {self.sides}-sided polygon."
                )

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle plus/minus keys to change number of sides
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.set_sides(min(self.max_sides, self.sides + 1))
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Number of sides: {self.sides}")
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Minus:
            self.set_sides(max(self.min_sides, self.sides - 1))
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Number of sides: {self.sides}")
            event.accept()
            return

        # Handle 'O' key to toggle orientation
        if event.key() == Qt.Key.Key_O:
            if self.orientation == self.ORIENTATION_VERTEX_TOP:
                self.set_orientation(self.ORIENTATION_SIDE_TOP)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Orientation: Side at top")
            else:
                self.set_orientation(self.ORIENTATION_VERTEX_TOP)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Orientation: Vertex at top")
            event.accept()
            return

        # Handle number keys to set number of sides directly
        if Qt.Key.Key_3 <= event.key() <= Qt.Key.Key_9:
            sides = event.key() - Qt.Key.Key_0  # Convert key code to number
            self.set_sides(sides)
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(f"Number of sides: {self.sides}")
            event.accept()
            return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketLeft:
                # Decrease fill opacity
                opacity = max(0, self.fill_color.alpha() - 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketRight:
                # Increase fill opacity
                opacity = min(255, self.fill_color.alpha() + 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _update_preview(self) -> None:
        """Update preview visualization."""
        # Clear existing preview
        self._clear_preview()

        # Only proceed if we have a canvas
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Get current mouse position
        current_pos = self.data.get('current_pos', QPointF(0, 0))

        # Set up pen and brush for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)
        preview_brush = QBrush(QColor(100, 100, 255, 30), Qt.BrushStyle.SolidPattern)

        # If we have a center point, draw the preview polygon
        if self.state == ToolState.ACTIVE and self.data['center']:
            center = self.data['center']

            # Calculate radius from mouse position
            dx = current_pos.x() - center.x
            dy = current_pos.y() - center.y
            radius = math.sqrt(dx * dx + dy * dy)

            # Calculate angle to mouse position
            angle = math.atan2(dy, dx)

            # Create regular polygon vertices
            vertices = self._calculate_regular_polygon_vertices(center, radius, angle)

            # Create a QPolygonF for the preview
            polygon_points = [QPointF(v.x, v.y) for v in vertices]
            qpolygon = QPolygonF(polygon_points)

            # Add the polygon to the scene
            polygon_item = self.canvas.scene.addPolygon(qpolygon, preview_pen, preview_brush)
            self.preview_items.append(polygon_item)

            # Draw center point
            center_item = self.canvas.scene.addEllipse(
                center.x - 3, center.y - 3, 6, 6,
                QPen(QColor(100, 100, 255, 150)),
                QBrush(QColor(100, 100, 255, 150))
            )
            self.preview_items.append(center_item)

            # Draw radius line
            radius_line = self.canvas.scene.addLine(
                center.x, center.y,
                current_pos.x(), current_pos.y(),
                QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DotLine)
            )
            self.preview_items.append(radius_line)

    def _calculate_regular_polygon_vertices(self, center: Point, radius: float, reference_angle: float = 0) -> List[Point]:
        """Calculate the vertices of a regular polygon.

        Args:
            center: Center point of the polygon
            radius: Radius of the polygon (distance from center to vertices)
            reference_angle: Reference angle for the first vertex

        Returns:
            List of vertex points
        """
        vertices = []

        # Calculate angle offset based on orientation
        if self.orientation == self.ORIENTATION_VERTEX_TOP:
            # Vertex at top means the first vertex is at 90 degrees (π/2)
            # In PyQt, positive y is downward, so we use -sin for y calculation
            angle_offset = math.pi / 2 - reference_angle
        else:  # ORIENTATION_SIDE_TOP
            # Side at top means the first vertex is at 90 + (360/2n) degrees
            angle_offset = math.pi / 2 + math.pi / self.sides - reference_angle

        # Calculate vertices
        for i in range(self.sides):
            angle = 2 * math.pi * i / self.sides + angle_offset
            x = center.x + radius * math.cos(angle)
            y = center.y - radius * math.sin(angle)  # Note the negative sign for y
            vertices.append(Point(x, y))

        return vertices

    def _create_regular_polygon(self) -> None:
        """Create a regular polygon based on the current state."""
        if not self.data['center'] or not self.data['vertex']:
            return

        center = self.data['center']
        vertex = self.data['vertex']

        # Calculate radius and angle
        dx = vertex.x - center.x
        dy = vertex.y - center.y
        radius = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)

        # Calculate vertices
        vertices = self._calculate_regular_polygon_vertices(center, radius, angle)

        # Create polygon style
        style = self._create_polygon_style()

        # Create polygon
        self._create_object(
            'polygon',
            vertices=vertices,
            style=style
        )

    def _create_polygon_style(self) -> Style:
        """Create a style object for new polygons.

        Returns:
            Style object for new polygons
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style,
            fill_color=self.fill_color,
            fill_style=self.fill_style
        )

    def set_sides(self, sides: int) -> None:
        """Set the number of sides for the regular polygon.

        Args:
            sides: Number of sides
        """
        self.sides = max(self.min_sides, min(self.max_sides, sides))

        # Update preview if active
        if self.state == ToolState.ACTIVE and self.options.show_preview:
            self._update_preview()

    def set_orientation(self, orientation: str) -> None:
        """Set the orientation of the regular polygon.

        Args:
            orientation: Orientation (ORIENTATION_VERTEX_TOP or ORIENTATION_SIDE_TOP)
        """
        if orientation in (self.ORIENTATION_VERTEX_TOP, self.ORIENTATION_SIDE_TOP):
            self.orientation = orientation

            # Update preview if active
            if self.state == ToolState.ACTIVE and self.options.show_preview:
                self._update_preview()

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new polygons.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new polygons.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new polygons.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new polygons.

        Args:
            color: Fill color
        """
        self.fill_color = color

    def set_fill_style(self, style: Qt.BrushStyle) -> None:
        """Set the fill style for new polygons.

        Args:
            style: Fill style
        """
        self.fill_style = style

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                try:
                    # Calculate distance to object
                    dist = obj.distance_to(pos)

                    # Check if this is the closest object within tolerance
                    if dist < closest_dist and dist <= self.options.snap_tolerance:
                        closest_obj = obj
                        closest_dist = dist

                        # For points, snap directly to the point
                        if isinstance(obj, Point):
                            closest_point = QPointF(obj.x, obj.y)
                        # For lines, find closest point on the line
                        elif isinstance(obj, Line):
                            # Calculate projection onto line
                            x1, y1 = obj.x1, obj.y1
                            x2, y2 = obj.x2, obj.y2
                            x0, y0 = pos.x(), pos.y()

                            # Calculate line length squared
                            line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

                            if line_length_sq > 1e-10:  # Avoid division by zero
                                # Calculate projection of point onto line
                                t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

                                # Clamp t based on line type
                                if obj.line_type == LineType.SEGMENT:
                                    t = max(0, min(1, t))
                                elif obj.line_type == LineType.RAY:
                                    t = max(0, t)

                                # Calculate closest point on line
                                closest_x = x1 + t * (x2 - x1)
                                closest_y = y1 + t * (y2 - y1)
                                closest_point = QPointF(closest_x, closest_y)
                        # For circles, find closest point on the circle
                        elif isinstance(obj, Circle):
                            # Calculate vector from center to pos
                            cx, cy = obj.center.x, obj.center.y
                            dx = pos.x() - cx
                            dy = pos.y() - cy

                            # Calculate distance from center
                            dist_from_center = math.sqrt(dx * dx + dy * dy)

                            if dist_from_center > 1e-10:  # Avoid division by zero
                                # Normalize vector
                                dx /= dist_from_center
                                dy /= dist_from_center

                                # Calculate point on circle
                                closest_x = cx + dx * obj.radius
                                closest_y = cy + dy * obj.radius
                                closest_point = QPointF(closest_x, closest_y)
                        # For polygons, find closest point on the polygon
                        elif isinstance(obj, Polygon):
                            # For polygons, we already have the distance from distance_to method
                            # We need to find the closest point on the polygon
                            # For simplicity, we'll use the closest vertex for now
                            if obj.vertices:
                                # Find the closest vertex
                                closest_vertex = None
                                min_vertex_dist = float('inf')

                                for vertex in obj.vertices:
                                    dx = vertex.x - pos.x()
                                    dy = vertex.y - pos.y()
                                    vertex_dist = math.sqrt(dx * dx + dy * dy)

                                    if vertex_dist < min_vertex_dist:
                                        min_vertex_dist = vertex_dist
                                        closest_vertex = vertex

                                if closest_vertex:
                                    closest_point = QPointF(closest_vertex.x, closest_vertex.y)
                except AttributeError:
                    # Skip objects that don't have the required attributes
                    continue

            # If we found a close object, snap to it
            if closest_obj and closest_point:
                snapped_pos = closest_point
                snap_type = 'object'
                snap_target = closest_obj

        # If not snapped to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)

            # Check if grid snap is within tolerance
            dx = grid_pos.x() - pos.x()
            dy = grid_pos.y() - pos.y()
            grid_dist = math.sqrt(dx * dx + dy * dy)

            if grid_dist <= self.options.snap_tolerance:
                snapped_pos = grid_pos
                snap_type = 'grid'

        return snapped_pos, snap_type, snap_target

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)


class CircleTool(GeometryTool):
    """Tool for creating circles.

    This tool allows users to create circles using different methods:
    - By center and point on circumference
    - With a fixed radius
    - By diameter (two points)
    - Through three points

    Circles can be customized with different styles.
    """

    # Circle creation modes
    MODE_CENTER_POINT = "center_point"  # Circle by center and point on circumference
    MODE_FIXED_RADIUS = "fixed_radius"  # Circle with fixed radius
    MODE_DIAMETER = "diameter"  # Circle by diameter (two points)
    MODE_THREE_POINTS = "three_points"  # Circle through three points

    def __init__(self) -> None:
        """Initialize the circle tool."""
        super().__init__("Circle", "circle")

        # Circle style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine
        self.fill_color = QColor(255, 255, 255, 50)  # Transparent white
        self.fill_style = Qt.BrushStyle.SolidPattern

        # Circle creation mode
        self.mode = self.MODE_CENTER_POINT
        self.fixed_radius = 100.0  # Default fixed radius

        # Toolbar reference
        self.toolbar = None

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'center_point': None,  # Center of the circle
            'preview_circle': None,  # Preview circle item
            'snap_target': None,     # Current snap target (object or grid point)
            'snap_type': None,       # Type of snap (grid, object, none)
            'points': []            # Points for diameter and three-point modes
        }

        # Set state
        self.state = ToolState.IDLE

        # Create toolbar if explorer exists
        if self.explorer:
            from geometry.ui.sacred_geometry.circle_toolbar import CircleToolbar

            # Create toolbar if it doesn't exist
            if not self.toolbar:
                self.toolbar = CircleToolbar()
                self.explorer.toolbar.addSeparator()
                self.explorer.toolbar.addWidget(self.toolbar)

                # Connect signals
                self.toolbar.mode_changed.connect(self._on_mode_changed)
                self.toolbar.radius_changed.connect(self._on_radius_changed)

                logger.debug("Circle toolbar added")

            # Show toolbar
            self.toolbar.setVisible(True)

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Hide toolbar
        if self.toolbar:
            self.toolbar.setVisible(False)

        # Call base implementation
        super()._cleanup_tool()

    def _on_mode_changed(self, mode: str) -> None:
        """Handle mode change from toolbar.

        Args:
            mode: New mode
        """
        # Update mode
        self.mode = mode

        # Reset state
        self._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if mode == self.MODE_CENTER_POINT:
                self.explorer.status_bar.showMessage("Click to place center point")
            elif mode == self.MODE_FIXED_RADIUS:
                self.explorer.status_bar.showMessage(f"Click to place center of circle with radius {self.fixed_radius:.2f}")
            elif mode == self.MODE_DIAMETER:
                self.explorer.status_bar.showMessage("Click to place first point of diameter")
            elif mode == self.MODE_THREE_POINTS:
                self.explorer.status_bar.showMessage("Click to place first point of circle")

    def _on_radius_changed(self, radius: float) -> None:
        """Handle radius change from toolbar.

        Args:
            radius: New radius
        """
        # Update fixed radius
        self.fixed_radius = radius

        # Update preview
        if self.state == ToolState.ACTIVE and self.mode == self.MODE_FIXED_RADIUS:
            self._update_preview()

    def _update_preview(self) -> None:
        """Update preview visualization."""
        # Clear existing preview
        self._clear_preview()

        # Only proceed if we have a canvas
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Get current mouse position
        current_pos = self.data.get('current_pos', QPointF(0, 0))

        # Set up pen and brush for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)
        preview_brush = QBrush(QColor(100, 100, 255, 30), Qt.BrushStyle.SolidPattern)

        # Handle preview based on mode
        if self.mode == self.MODE_CENTER_POINT:
            self._update_center_point_preview(current_pos, preview_pen, preview_brush)
        elif self.mode == self.MODE_FIXED_RADIUS:
            self._update_fixed_radius_preview(current_pos, preview_pen, preview_brush)
        elif self.mode == self.MODE_DIAMETER:
            self._update_diameter_preview(current_pos, preview_pen, preview_brush)
        elif self.mode == self.MODE_THREE_POINTS:
            self._update_three_points_preview(current_pos, preview_pen, preview_brush)

    def _update_center_point_preview(self, current_pos: QPointF, pen: QPen, brush: QBrush) -> None:
        """Update preview for center-point mode.

        Args:
            current_pos: Current mouse position
            pen: Pen to use for preview
            brush: Brush to use for preview
        """
        # If we have a center point, create preview circle
        if self.state == ToolState.ACTIVE and 'center_point' in self.data and self.data['center_point']:
            # Get center point
            center_point = self.data['center_point']

            # Calculate radius from mouse position
            dx = current_pos.x() - center_point.x()
            dy = current_pos.y() - center_point.y()
            radius = (dx * dx + dy * dy) ** 0.5

            # Create preview circle
            circle_item = self.canvas.scene.addEllipse(
                center_point.x() - radius,
                center_point.y() - radius,
                radius * 2,
                radius * 2,
                pen,
                brush
            )

            # Add to preview items
            self.preview_items.append(circle_item)

            # Draw radius line
            radius_line = self.canvas.scene.addLine(
                center_point.x(), center_point.y(),
                current_pos.x(), current_pos.y(),
                QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DotLine)
            )

            # Add to preview items
            self.preview_items.append(radius_line)

    def _update_fixed_radius_preview(self, current_pos: QPointF, pen: QPen, brush: QBrush) -> None:
        """Update preview for fixed-radius mode.

        Args:
            current_pos: Current mouse position
            pen: Pen to use for preview
            brush: Brush to use for preview
        """
        # Create preview circle at mouse position with fixed radius
        circle_item = self.canvas.scene.addEllipse(
            current_pos.x() - self.fixed_radius,
            current_pos.y() - self.fixed_radius,
            self.fixed_radius * 2,
            self.fixed_radius * 2,
            pen,
            brush
        )

        # Add to preview items
        self.preview_items.append(circle_item)

        # Draw radius line
        angle = 0  # Horizontal radius line
        circ_x = current_pos.x() + self.fixed_radius * math.cos(angle)
        circ_y = current_pos.y() + self.fixed_radius * math.sin(angle)

        radius_line = self.canvas.scene.addLine(
            current_pos.x(), current_pos.y(),
            circ_x, circ_y,
            QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DotLine)
        )

        # Add to preview items
        self.preview_items.append(radius_line)

    def _update_diameter_preview(self, current_pos: QPointF, pen: QPen, brush: QBrush) -> None:
        """Update preview for diameter mode.

        Args:
            current_pos: Current mouse position
            pen: Pen to use for preview
            brush: Brush to use for preview
        """
        if self.state == ToolState.ACTIVE and 'points' in self.data and len(self.data['points']) > 0:
            # Get first point of diameter
            p1 = self.data['points'][0]
            p2 = current_pos

            # Calculate center and radius from diameter
            center_x = (p1.x() + p2.x()) / 2
            center_y = (p1.y() + p2.y()) / 2
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            radius = math.sqrt(dx * dx + dy * dy) / 2

            # Create preview circle
            circle_item = self.canvas.scene.addEllipse(
                center_x - radius,
                center_y - radius,
                radius * 2,
                radius * 2,
                pen,
                brush
            )

            # Add to preview items
            self.preview_items.append(circle_item)

            # Draw diameter line
            diameter_line = self.canvas.scene.addLine(
                p1.x(), p1.y(),
                p2.x(), p2.y(),
                QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DotLine)
            )

            # Add to preview items
            self.preview_items.append(diameter_line)

    def _update_three_points_preview(self, current_pos: QPointF, pen: QPen, brush: QBrush) -> None:
        """Update preview for three-points mode.

        Args:
            current_pos: Current mouse position
            pen: Pen to use for preview
            brush: Brush to use for preview
        """
        if self.state == ToolState.ACTIVE and 'points' in self.data:
            points = self.data['points']

            # Draw lines connecting the points
            for i in range(len(points)):
                # Connect to next point or current mouse position
                next_point = points[(i + 1) % len(points)] if i < len(points) - 1 else current_pos

                line_item = self.canvas.scene.addLine(
                    points[i].x(), points[i].y(),
                    next_point.x(), next_point.y(),
                    QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DotLine)
                )

                # Add to preview items
                self.preview_items.append(line_item)

            # If we have all three points, try to draw the circle
            if len(points) == 2:
                try:
                    p1 = points[0]
                    p2 = points[1]
                    p3 = current_pos

                    # Calculate center and radius
                    center, radius = self._calculate_circle_from_three_points(p1, p2, p3)

                    # Create preview circle
                    circle_item = self.canvas.scene.addEllipse(
                        center.x() - radius,
                        center.y() - radius,
                        radius * 2,
                        radius * 2,
                        pen,
                        brush
                    )

                    # Add to preview items
                    self.preview_items.append(circle_item)
                except Exception:
                    # Ignore errors during preview (e.g., collinear points)
                    pass

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Handle based on current mode
        if self.mode == self.MODE_CENTER_POINT:
            self._handle_center_point_mode(pos)
        elif self.mode == self.MODE_FIXED_RADIUS:
            self._handle_fixed_radius_mode(pos)
        elif self.mode == self.MODE_DIAMETER:
            self._handle_diameter_mode(pos)
        elif self.mode == self.MODE_THREE_POINTS:
            self._handle_three_points_mode(pos)

    def _handle_center_point_mode(self, pos: QPointF) -> None:
        """Handle mouse press in center-point mode.

        Args:
            pos: Position in scene coordinates
        """
        if self.state == ToolState.IDLE:
            # Center point
            self.data['center_point'] = QPointF(pos)
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click to set radius")

        elif self.state == ToolState.ACTIVE:
            # Radius point - create circle
            center_point = self.data['center_point']

            # Calculate radius from mouse position
            dx = pos.x() - center_point.x()
            dy = pos.y() - center_point.y()
            radius = (dx * dx + dy * dy) ** 0.5

            # Create circle style
            style = self._create_circle_style()

            # Create circle
            self._create_object(
                'circle',
                cx=center_point.x(),
                cy=center_point.y(),
                radius=radius,
                style=style
            )

            # Complete operation
            self._complete_operation()

    def _handle_fixed_radius_mode(self, pos: QPointF) -> None:
        """Handle mouse press in fixed-radius mode.

        Args:
            pos: Position in scene coordinates
        """
        # Create circle at the clicked position with fixed radius
        # Create circle style
        style = self._create_circle_style()

        # Create circle
        self._create_object(
            'circle',
            cx=pos.x(),
            cy=pos.y(),
            radius=self.fixed_radius,
            style=style
        )

        # No need to change state - can create multiple circles
        # Just update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage(f"Created circle with radius {self.fixed_radius:.2f}. Click to create another.")

    def _handle_diameter_mode(self, pos: QPointF) -> None:
        """Handle mouse press in diameter mode.

        Args:
            pos: Position in scene coordinates
        """
        if self.state == ToolState.IDLE:
            # First point of diameter
            self.data['points'] = [QPointF(pos)]
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click to set second point of diameter")

        elif self.state == ToolState.ACTIVE:
            # Second point of diameter - create circle
            p1 = self.data['points'][0]
            p2 = QPointF(pos)

            # Calculate center and radius from diameter
            center_x = (p1.x() + p2.x()) / 2
            center_y = (p1.y() + p2.y()) / 2
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            radius = math.sqrt(dx * dx + dy * dy) / 2

            # Create circle style
            style = self._create_circle_style()

            # Create circle
            self._create_object(
                'circle',
                cx=center_x,
                cy=center_y,
                radius=radius,
                style=style
            )

            # Complete operation
            self._complete_operation()

    def _handle_three_points_mode(self, pos: QPointF) -> None:
        """Handle mouse press in three-points mode.

        Args:
            pos: Position in scene coordinates
        """
        if self.state == ToolState.IDLE:
            # First point
            self.data['points'] = [QPointF(pos)]
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click to set second point of circle")

        elif self.state == ToolState.ACTIVE and len(self.data['points']) == 1:
            # Second point
            self.data['points'].append(QPointF(pos))

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Click to set third point of circle")

        elif self.state == ToolState.ACTIVE and len(self.data['points']) == 2:
            # Third point - create circle
            p1 = self.data['points'][0]
            p2 = self.data['points'][1]
            p3 = QPointF(pos)

            # Calculate center and radius from three points
            try:
                center, radius = self._calculate_circle_from_three_points(p1, p2, p3)

                # Create circle style
                style = self._create_circle_style()

                # Create circle
                self._create_object(
                    'circle',
                    cx=center.x(),
                    cy=center.y(),
                    radius=radius,
                    style=style
                )

                # Complete operation
                self._complete_operation()
            except Exception as e:
                # Handle error (e.g., points are collinear)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Error creating circle: {str(e)}")
                logger.error(f"Error creating circle from three points: {str(e)}")
                self._cancel_operation()

    def _calculate_circle_from_three_points(self, p1: QPointF, p2: QPointF, p3: QPointF) -> Tuple[QPointF, float]:
        """Calculate the center and radius of a circle passing through three points.

        Args:
            p1: First point
            p2: Second point
            p3: Third point

        Returns:
            Tuple of (center, radius)

        Raises:
            ValueError: If the points are collinear (no circle passes through them)
        """
        # Convert to numpy arrays for easier calculation
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        x3, y3 = p3.x(), p3.y()

        # Check if points are collinear
        if abs((y2 - y1) * (x3 - x2) - (y3 - y2) * (x2 - x1)) < 1e-10:
            raise ValueError("The three points are collinear, no circle passes through them")

        # Calculate circle center using perpendicular bisectors
        # Midpoints
        mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
        mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2

        # Slopes of lines
        if abs(x2 - x1) < 1e-10:
            # First line is vertical, slope of perpendicular is 0
            s1 = 0
        elif abs(y2 - y1) < 1e-10:
            # First line is horizontal, slope of perpendicular is infinity
            # Handle this case separately
            s1 = float('inf')
        else:
            s1 = -1 / ((y2 - y1) / (x2 - x1))

        if abs(x3 - x2) < 1e-10:
            # Second line is vertical, slope of perpendicular is 0
            s2 = 0
        elif abs(y3 - y2) < 1e-10:
            # Second line is horizontal, slope of perpendicular is infinity
            # Handle this case separately
            s2 = float('inf')
        else:
            s2 = -1 / ((y3 - y2) / (x3 - x2))

        # Handle special cases with infinite slopes
        if s1 == float('inf'):
            # First perpendicular bisector is vertical
            cx = mx1
            cy = s2 * (cx - mx2) + my2
        elif s2 == float('inf'):
            # Second perpendicular bisector is vertical
            cx = mx2
            cy = s1 * (cx - mx1) + my1
        else:
            # Calculate intersection of perpendicular bisectors
            cx = (s1 * mx1 - s2 * mx2 + my2 - my1) / (s1 - s2)
            cy = s1 * (cx - mx1) + my1

        # Calculate radius
        dx = cx - x1
        dy = cy - y1
        radius = math.sqrt(dx * dx + dy * dy)

        return QPointF(cx, cy), radius

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Store current position and snap info
        self.data['current_pos'] = pos
        self.data['snap_type'] = snap_type
        self.data['snap_target'] = snap_target

        # Update preview
        if self.options.show_preview:
            self._update_preview()

        # Update status message based on mode
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.mode == self.MODE_CENTER_POINT:
                self._update_center_point_status(pos)
            elif self.mode == self.MODE_FIXED_RADIUS:
                self._update_fixed_radius_status(pos)
            elif self.mode == self.MODE_DIAMETER:
                self._update_diameter_status(pos)
            elif self.mode == self.MODE_THREE_POINTS:
                self._update_three_points_status(pos)

    def _update_center_point_status(self, pos: QPointF) -> None:
        """Update status message for center-point mode.

        Args:
            pos: Current mouse position
        """
        if self.state == ToolState.IDLE:
            self.explorer.status_bar.showMessage(f"Click to place center at ({pos.x():.2f}, {pos.y():.2f})")
        elif self.state == ToolState.ACTIVE:
            center_point = self.data['center_point']
            dx = pos.x() - center_point.x()
            dy = pos.y() - center_point.y()
            radius = (dx * dx + dy * dy) ** 0.5
            self.explorer.status_bar.showMessage(
                f"Circle with center ({center_point.x():.2f}, {center_point.y():.2f}) and radius {radius:.2f}"
            )

    def _update_fixed_radius_status(self, pos: QPointF) -> None:
        """Update status message for fixed-radius mode.

        Args:
            pos: Current mouse position
        """
        self.explorer.status_bar.showMessage(
            f"Click to place circle with radius {self.fixed_radius:.2f} at ({pos.x():.2f}, {pos.y():.2f})"
        )

    def _update_diameter_status(self, pos: QPointF) -> None:
        """Update status message for diameter mode.

        Args:
            pos: Current mouse position
        """
        if self.state == ToolState.IDLE:
            self.explorer.status_bar.showMessage(f"Click to place first point of diameter at ({pos.x():.2f}, {pos.y():.2f})")
        elif self.state == ToolState.ACTIVE:
            p1 = self.data['points'][0]
            p2 = pos

            # Calculate center and radius from diameter
            center_x = (p1.x() + p2.x()) / 2
            center_y = (p1.y() + p2.y()) / 2
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            diameter = math.sqrt(dx * dx + dy * dy)
            radius = diameter / 2

            self.explorer.status_bar.showMessage(
                f"Diameter: {diameter:.2f}, Radius: {radius:.2f}, Center: ({center_x:.2f}, {center_y:.2f})"
            )

    def _update_three_points_status(self, pos: QPointF) -> None:
        """Update status message for three-points mode.

        Args:
            pos: Current mouse position
        """
        if self.state == ToolState.IDLE:
            self.explorer.status_bar.showMessage(f"Click to place first point of circle at ({pos.x():.2f}, {pos.y():.2f})")
        elif self.state == ToolState.ACTIVE:
            if len(self.data['points']) == 1:
                p1 = self.data['points'][0]
                self.explorer.status_bar.showMessage(
                    f"First point at ({p1.x():.2f}, {p1.y():.2f}), click to place second point at ({pos.x():.2f}, {pos.y():.2f})"
                )
            elif len(self.data['points']) == 2:
                p1 = self.data['points'][0]
                p2 = self.data['points'][1]
                self.explorer.status_bar.showMessage(
                    f"Two points at ({p1.x():.2f}, {p1.y():.2f}) and ({p2.x():.2f}, {p2.y():.2f}), click to place third point"
                )

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Circle creation cancelled")

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def set_fixed_radius_mode(self, enabled: bool) -> None:
        """Set whether to use fixed radius mode.

        Args:
            enabled: Whether to enable fixed radius mode
        """
        self.fixed_radius_mode = enabled

    def set_fixed_radius(self, radius: float) -> None:
        """Set the fixed radius for new circles.

        Args:
            radius: Fixed radius
        """
        self.fixed_radius = max(0.1, radius)  # Ensure radius is positive

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new circles.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new circles.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new circles.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new circles.

        Args:
            color: Fill color
        """
        self.fill_color = color

    def set_fill_style(self, style: Qt.BrushStyle) -> None:
        """Set the fill style for new circles.

        Args:
            style: Fill style
        """
        self.fill_style = style

    def _create_circle_style(self) -> Style:
        """Create a style object for new circles.

        Returns:
            Style object for new circles
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style,
            fill_color=self.fill_color,
            fill_style=self.fill_style
        )

    def _snap_position_with_info(self, pos: QPointF) -> Tuple[QPointF, str, Optional[GeometricObject]]:
        """Snap position to grid or objects and return snap information.

        Args:
            pos: Position to snap

        Returns:
            Tuple of (snapped position, snap type, snap target)
        """
        snap_type = 'none'
        snap_target = None
        snapped_pos = pos

        # Snap to objects if enabled
        if self.options.snap_to_objects and self.canvas:
            # Find closest object
            closest_obj = None
            closest_dist = float('inf')
            closest_point = None

            for obj in self.canvas.objects:
                # Calculate distance to object
                dist = obj.distance_to(pos)

                # Check if this is the closest object within tolerance
                if dist < closest_dist and dist <= self.options.snap_tolerance:
                    closest_obj = obj
                    closest_dist = dist

                    # For points, snap directly to the point
                    if isinstance(obj, Point):
                        closest_point = QPointF(obj.x, obj.y)
                    # For lines, find closest point on the line
                    elif isinstance(obj, Line):
                        # Calculate projection onto line
                        x1, y1 = obj.x1, obj.y1
                        x2, y2 = obj.x2, obj.y2
                        x0, y0 = pos.x(), pos.y()

                        # Calculate line length squared
                        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

                        if line_length_sq > 1e-10:  # Avoid division by zero
                            # Calculate projection of point onto line
                            t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

                            # Clamp t based on line type
                            if obj.line_type == LineType.SEGMENT:
                                t = max(0, min(1, t))
                            elif obj.line_type == LineType.RAY:
                                t = max(0, t)

                            # Calculate closest point on line
                            closest_x = x1 + t * (x2 - x1)
                            closest_y = y1 + t * (y2 - y1)
                            closest_point = QPointF(closest_x, closest_y)
                    # For circles, find closest point on the circle
                    elif isinstance(obj, Circle):
                        # Calculate vector from center to pos
                        cx, cy = obj.center.x, obj.center.y
                        dx = pos.x() - cx
                        dy = pos.y() - cy

                        # Calculate distance from center
                        dist_from_center = math.sqrt(dx * dx + dy * dy)

                        if dist_from_center > 1e-10:  # Avoid division by zero
                            # Normalize vector
                            dx /= dist_from_center
                            dy /= dist_from_center

                            # Calculate point on circle
                            closest_x = cx + dx * obj.radius
                            closest_y = cy + dy * obj.radius
                            closest_point = QPointF(closest_x, closest_y)

            # If we found a close object, snap to it
            if closest_obj and closest_point:
                snapped_pos = closest_point
                snap_type = 'object'
                snap_target = closest_obj

        # If not snapped to an object, try snapping to grid
        if snap_type == 'none' and self.options.snap_to_grid:
            grid_pos = self._snap_to_grid(pos)

            # Check if grid snap is within tolerance
            dx = grid_pos.x() - pos.x()
            dy = grid_pos.y() - pos.y()
            grid_dist = math.sqrt(dx * dx + dy * dy)

            if grid_dist <= self.options.snap_tolerance:
                snapped_pos = grid_pos
                snap_type = 'grid'

        return snapped_pos, snap_type, snap_target

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle keyboard shortcuts for circle modes
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_1:
                # Center-point mode
                if self.toolbar:
                    self.toolbar.center_point_action.trigger()
                else:
                    self._on_mode_changed(self.MODE_CENTER_POINT)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_2:
                # Fixed radius mode
                if self.toolbar:
                    self.toolbar.fixed_radius_action.trigger()
                else:
                    self._on_mode_changed(self.MODE_FIXED_RADIUS)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_3:
                # Diameter mode
                if self.toolbar:
                    self.toolbar.diameter_action.trigger()
                else:
                    self._on_mode_changed(self.MODE_DIAMETER)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_4:
                # Three points mode
                if self.toolbar:
                    self.toolbar.three_points_action.trigger()
                else:
                    self._on_mode_changed(self.MODE_THREE_POINTS)
                event.accept()
                return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketLeft:
                # Decrease fill opacity
                opacity = max(0, self.fill_color.alpha() - 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_BracketRight:
                # Increase fill opacity
                opacity = min(255, self.fill_color.alpha() + 25)
                color = QColor(self.fill_color)
                color.setAlpha(opacity)
                self.set_fill_color(color)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Fill opacity: {opacity}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)


class PerpendicularLineTool(GeometryTool):
    """Tool for creating perpendicular lines.

    This tool allows users to create lines that are perpendicular to existing lines.
    It supports two modes:
    1. From a point to a line: Creates a perpendicular line from a selected point to a line
    2. Through a point on a line: Creates a perpendicular line through a point on a line
    """

    # Mode constants
    MODE_POINT_TO_LINE = 0  # From a point to a line
    MODE_THROUGH_POINT = 1  # Through a point on a line

    def __init__(self) -> None:
        """Initialize the perpendicular line tool."""
        super().__init__("Perpendicular Line", "perpendicular_line")

        # Line style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine

        # Line type
        self.line_type = LineType.SEGMENT

        # Current mode
        self.mode = self.MODE_POINT_TO_LINE

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Reset data
        self.data = {
            'reference_point': None,  # Point from which to draw perpendicular (mode 0) or point on line (mode 1)
            'reference_line': None,   # Line to which perpendicular will be drawn
        }

        # Set state
        self.state = ToolState.IDLE

        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.mode == self.MODE_POINT_TO_LINE:
                self.explorer.status_bar.showMessage("Select a point from which to draw the perpendicular line")
            else:  # MODE_THROUGH_POINT
                self.explorer.status_bar.showMessage("Select a point on a line through which to draw the perpendicular")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Clear preview
        self._clear_preview()

        # Reset data
        self.data = {}

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.mode == self.MODE_POINT_TO_LINE:
            self._handle_point_to_line_mode(pos, snap_type, snap_target)
        else:  # MODE_THROUGH_POINT
            self._handle_through_point_mode(pos, snap_type, snap_target)

    def _handle_point_to_line_mode(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press in point-to-line mode.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        if self.state == ToolState.IDLE:
            # First click - select reference point
            if snap_type == 'object' and isinstance(snap_target, Point):
                # Use existing point
                self.data['reference_point'] = snap_target
            else:
                # Create new point
                style = self._create_point_style()
                point = self._create_object(
                    'point',
                    x=pos.x(),
                    y=pos.y(),
                    style=style
                )
                self.data['reference_point'] = point

            # Update state
            self.state = ToolState.ACTIVE

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Select a line to which the perpendicular will be drawn")

        elif self.state == ToolState.ACTIVE:
            # Second click - select reference line
            if snap_type == 'object' and isinstance(snap_target, Line):
                # Use existing line
                self.data['reference_line'] = snap_target

                # Create perpendicular line
                self._create_perpendicular_line_from_point()

                # Complete operation
                self._complete_operation()
            else:
                # No line selected
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Please select a line to which the perpendicular will be drawn")

    def _handle_through_point_mode(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press in through-point mode.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        # In this mode, we need to select a point that is on a line
        if snap_type == 'object':
            if isinstance(snap_target, Point):
                # Check if this point is on a line
                if self.canvas:
                    for obj in self.canvas.objects:
                        if isinstance(obj, Line):
                            # Check if point is on the line
                            if obj.distance_to(QPointF(snap_target.x, snap_target.y)) < 1e-6:
                                # Point is on the line
                                self.data['reference_point'] = snap_target
                                self.data['reference_line'] = obj

                                # Create perpendicular line
                                self._create_perpendicular_line_through_point()

                                # Complete operation
                                self._complete_operation()
                                return

            elif isinstance(snap_target, Line):
                # Create a point at the clicked position on the line
                style = self._create_point_style()
                point = self._create_object(
                    'point',
                    x=pos.x(),
                    y=pos.y(),
                    style=style
                )
                self.data['reference_point'] = point
                self.data['reference_line'] = snap_target

                # Create perpendicular line
                self._create_perpendicular_line_through_point()

                # Complete operation
                self._complete_operation()
                return

        # If we get here, no valid selection was made
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Please select a point on a line or a line itself")

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Clear previous preview
        self._clear_preview()

        # Store current position for preview
        self.data['current_pos'] = scene_pos

        # Create preview based on current state
        if self.state == ToolState.ACTIVE and self.data.get('reference_point') and self.canvas:
            # Get reference point
            ref_point = self.data['reference_point']
            ref_point_pos = QPointF(ref_point.x, ref_point.y)

            # Snap position to objects
            pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

            # Create preview based on mode
            if self.mode == self.MODE_POINT_TO_LINE and snap_type == 'object' and isinstance(snap_target, Line):
                # Preview perpendicular line from point to line
                self._preview_perpendicular_from_point(ref_point_pos, snap_target)
            elif self.mode == self.MODE_THROUGH_POINT and self.data.get('reference_line'):
                # Preview perpendicular line through point on line
                self._preview_perpendicular_through_point(ref_point_pos, self.data['reference_line'])

        # Update status message
        self._update_status_message(scene_pos)

    def _update_status_message(self, pos: QPointF) -> None:
        """Update the status message based on current state.

        Args:
            pos: Current mouse position
        """
        if not self.explorer or not hasattr(self.explorer, 'status_bar'):
            return

        if self.state == ToolState.IDLE:
            if self.mode == self.MODE_POINT_TO_LINE:
                self.explorer.status_bar.showMessage("Select a point from which to draw the perpendicular line")
            else:  # MODE_THROUGH_POINT
                self.explorer.status_bar.showMessage("Select a point on a line through which to draw the perpendicular")
        elif self.state == ToolState.ACTIVE:
            if self.mode == self.MODE_POINT_TO_LINE:
                self.explorer.status_bar.showMessage("Select a line to which the perpendicular will be drawn")

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle mode switching
        if event.key() == Qt.Key.Key_1:
            self.set_mode(self.MODE_POINT_TO_LINE)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_2:
            self.set_mode(self.MODE_THROUGH_POINT)
            event.accept()
            return
        # Handle escape key to cancel operation
        elif event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle line type switching
        if event.key() == Qt.Key.Key_S:
            self.set_line_type(LineType.SEGMENT)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_R:
            self.set_line_type(LineType.RAY)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_I:
            self.set_line_type(LineType.INFINITE)
            event.accept()
            return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Perpendicular line creation cancelled")

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def set_mode(self, mode: int) -> None:
        """Set the mode for the perpendicular line tool.

        Args:
            mode: Mode to set (MODE_POINT_TO_LINE or MODE_THROUGH_POINT)
        """
        if mode != self.mode:
            self.mode = mode
            self._cancel_operation()
            self._init_tool()

    def set_line_type(self, line_type: LineType) -> None:
        """Set the line type for new lines.

        Args:
            line_type: Type of line (segment, ray, or infinite)
        """
        self.line_type = line_type

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            line_type_name = self.line_type.name.lower()
            self.explorer.status_bar.showMessage(f"Line type set to {line_type_name}")

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new lines.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new lines.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new lines.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def _create_point_style(self) -> Style:
        """Create a style object for new points.

        Returns:
            Style object for new points
        """
        return Style(
            point_size=5.0,
            stroke_color=QColor(0, 0, 0),
            fill_color=QColor(255, 255, 255)
        )

    def _create_line_style(self) -> Style:
        """Create a style object for new lines.

        Returns:
            Style object for new lines
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style
        )

    def _create_perpendicular_line_from_point(self) -> None:
        """Create a perpendicular line from a point to a line."""
        # Get reference point and line
        ref_point = self.data['reference_point']
        ref_line = self.data['reference_line']

        # Calculate perpendicular line
        p1 = QPointF(ref_point.x, ref_point.y)
        p2 = self._calculate_perpendicular_point_on_line(p1, ref_line)

        # Create line style
        style = self._create_line_style()

        # Create line
        self._create_object(
            'line',
            x1=p1.x(),
            y1=p1.y(),
            x2=p2.x(),
            y2=p2.y(),
            style=style,
            line_type=self.line_type
        )

    def _create_perpendicular_line_through_point(self) -> None:
        """Create a perpendicular line through a point on a line."""
        # Get reference point and line
        ref_point = self.data['reference_point']
        ref_line = self.data['reference_line']

        # Calculate perpendicular line
        p1 = QPointF(ref_point.x, ref_point.y)
        p2 = self._calculate_perpendicular_point_through_line(p1, ref_line)

        # Create line style
        style = self._create_line_style()

        # Create line
        self._create_object(
            'line',
            x1=p1.x(),
            y1=p1.y(),
            x2=p2.x(),
            y2=p2.y(),
            style=style,
            line_type=self.line_type
        )

    def _calculate_perpendicular_point_on_line(self, point: QPointF, line: Line) -> QPointF:
        """Calculate the point on a line that is perpendicular to the given point.

        Args:
            point: Point from which to draw perpendicular
            line: Line to which perpendicular will be drawn

        Returns:
            Point on the line that forms a perpendicular with the given point
        """
        # Get line points
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2
        x0, y0 = point.x(), point.y()

        # Calculate line length squared
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

        # If line is actually a point, return that point
        if line_length_sq < 1e-10:
            return QPointF(x1, y1)

        # Calculate projection of point onto line
        t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

        # Calculate closest point on line
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)

        return QPointF(closest_x, closest_y)

    def _calculate_perpendicular_point_through_line(self, point: QPointF, line: Line) -> QPointF:
        """Calculate a point that forms a perpendicular line through the given point on a line.

        Args:
            point: Point on the line through which to draw perpendicular
            line: Line on which the point lies

        Returns:
            Point that forms a perpendicular line through the given point
        """
        # Get line points
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2
        x0, y0 = point.x(), point.y()

        # Calculate perpendicular direction vector (rotate line direction by 90 degrees)
        dx = x2 - x1
        dy = y2 - y1

        # Perpendicular vector (rotate 90 degrees)
        perp_dx = -dy
        perp_dy = dx

        # Normalize perpendicular vector
        length = math.sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
        if length > 0:
            perp_dx /= length
            perp_dy /= length

        # Calculate point at a distance along the perpendicular direction
        distance = 100  # Arbitrary distance
        perp_x = x0 + perp_dx * distance
        perp_y = y0 + perp_dy * distance

        return QPointF(perp_x, perp_y)

    def _preview_perpendicular_from_point(self, point: QPointF, line: Line) -> None:
        """Preview a perpendicular line from a point to a line.

        Args:
            point: Point from which to draw perpendicular
            line: Line to which perpendicular will be drawn
        """
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Calculate perpendicular point on line
        perp_point = self._calculate_perpendicular_point_on_line(point, line)

        # Set up pen for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

        # Draw preview line based on line type
        if self.line_type == LineType.SEGMENT:
            # Draw line segment
            line_item = self.canvas.scene.addLine(
                QLineF(point.x(), point.y(), perp_point.x(), perp_point.y()),
                preview_pen
            )
            self.preview_items.append(line_item)
        elif self.line_type == LineType.RAY:
            # Draw ray (from point extending through perp_point)
            # Calculate direction vector
            dx = perp_point.x() - point.x()
            dy = perp_point.y() - point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of perp_point
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = point.x() + dx * extension
            extended_y = point.y() + dy * extension

            # Draw the ray
            line_item = self.canvas.scene.addLine(
                QLineF(point.x(), point.y(), extended_x, extended_y),
                preview_pen
            )
            self.preview_items.append(line_item)
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = perp_point.x() - point.x()
            dy = perp_point.y() - point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = point.x() - dx * extension
            extended_y1 = point.y() - dy * extension
            extended_x2 = perp_point.x() + dx * extension
            extended_y2 = perp_point.y() + dy * extension

            # Draw the infinite line
            line_item = self.canvas.scene.addLine(
                QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                preview_pen
            )
            self.preview_items.append(line_item)

    def _preview_perpendicular_through_point(self, point: QPointF, line: Line) -> None:
        """Preview a perpendicular line through a point on a line.

        Args:
            point: Point on the line through which to draw perpendicular
            line: Line on which the point lies
        """
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Calculate perpendicular point
        perp_point = self._calculate_perpendicular_point_through_line(point, line)

        # Set up pen for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

        # Draw preview line based on line type
        if self.line_type == LineType.SEGMENT:
            # Draw line segment
            line_item = self.canvas.scene.addLine(
                QLineF(point.x(), point.y(), perp_point.x(), perp_point.y()),
                preview_pen
            )
            self.preview_items.append(line_item)
        elif self.line_type == LineType.RAY:
            # Draw ray (from point extending through perp_point)
            # Calculate direction vector
            dx = perp_point.x() - point.x()
            dy = perp_point.y() - point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of perp_point
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = point.x() + dx * extension
            extended_y = point.y() + dy * extension

            # Draw the ray
            line_item = self.canvas.scene.addLine(
                QLineF(point.x(), point.y(), extended_x, extended_y),
                preview_pen
            )
            self.preview_items.append(line_item)
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = perp_point.x() - point.x()
            dy = perp_point.y() - point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = point.x() - dx * extension
            extended_y1 = point.y() - dy * extension
            extended_x2 = perp_point.x() + dx * extension
            extended_y2 = perp_point.y() + dy * extension

            # Draw the infinite line
            line_item = self.canvas.scene.addLine(
                QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                preview_pen
            )
            self.preview_items.append(line_item)


class ParallelLineTool(GeometryTool):
    """Tool for creating parallel lines.

    This tool allows users to create lines that are parallel to existing lines.
    It supports creating parallel lines through a point and measuring the distance
    between parallel lines.
    """

    def __init__(self) -> None:
        """Initialize the parallel line tool."""
        super().__init__("Parallel Line", "parallel_line")

        # Line style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine

        # Line type
        self.line_type = LineType.SEGMENT

        # Distance measurement
        self.show_distance = True

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Reset data
        self.data = {
            'reference_line': None,   # Line to which parallel will be drawn
            'reference_point': None,  # Point through which parallel will be drawn
            'distance': None,         # Distance between parallel lines (if measured)
        }

        # Set state
        self.state = ToolState.IDLE

        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Select a line to which the parallel will be drawn")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Clear preview
        self._clear_preview()

        # Reset data
        self.data = {}

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.state == ToolState.IDLE:
            # First click - select reference line
            if snap_type == 'object' and isinstance(snap_target, Line):
                # Use existing line
                self.data['reference_line'] = snap_target
                self.state = ToolState.ACTIVE

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Select a point through which the parallel line will pass")
            else:
                # No line selected
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Please select a line to which the parallel will be drawn")

        elif self.state == ToolState.ACTIVE:
            # Second click - select reference point
            if snap_type == 'object' and isinstance(snap_target, Point):
                # Use existing point
                self.data['reference_point'] = snap_target
            else:
                # Create new point
                style = self._create_point_style()
                point = self._create_object(
                    'point',
                    x=pos.x(),
                    y=pos.y(),
                    style=style
                )
                self.data['reference_point'] = point

            # Create parallel line
            self._create_parallel_line()

            # Complete operation
            self._complete_operation()

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Clear previous preview
        self._clear_preview()

        # Create preview based on current state
        if self.state == ToolState.ACTIVE and self.data.get('reference_line') and self.canvas:
            # Get reference line
            ref_line = self.data['reference_line']

            # Snap position to grid/objects
            pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

            # Preview parallel line through current position
            self._preview_parallel_line(pos, ref_line)

            # Update status message with distance if enabled
            if self.show_distance:
                distance = self._calculate_distance_to_line(pos, ref_line)
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(
                        f"Distance to reference line: {distance:.2f} units. Click to create parallel line."
                    )
            else:
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Click to create parallel line")

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle line type switching
        if event.key() == Qt.Key.Key_S:
            self.set_line_type(LineType.SEGMENT)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_R:
            self.set_line_type(LineType.RAY)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_I:
            self.set_line_type(LineType.INFINITE)
            event.accept()
            return

        # Toggle distance measurement
        if event.key() == Qt.Key.Key_D:
            self.show_distance = not self.show_distance
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                status = "enabled" if self.show_distance else "disabled"
                self.explorer.status_bar.showMessage(f"Distance measurement {status}")
            event.accept()
            return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Parallel line creation cancelled")

    def set_line_type(self, line_type: LineType) -> None:
        """Set the line type for new lines.

        Args:
            line_type: Type of line (segment, ray, or infinite)
        """
        self.line_type = line_type

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            line_type_name = self.line_type.name.lower()
            self.explorer.status_bar.showMessage(f"Line type set to {line_type_name}")

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new lines.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new lines.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new lines.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def _create_point_style(self) -> Style:
        """Create a style object for new points.

        Returns:
            Style object for new points
        """
        return Style(
            point_size=5.0,
            stroke_color=QColor(0, 0, 0),
            fill_color=QColor(255, 255, 255)
        )

    def _create_line_style(self) -> Style:
        """Create a style object for new lines.

        Returns:
            Style object for new lines
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style
        )

    def _calculate_distance_to_line(self, point: QPointF, line: Line) -> float:
        """Calculate the perpendicular distance from a point to a line.

        Args:
            point: Point to calculate distance from
            line: Line to calculate distance to

        Returns:
            Perpendicular distance from point to line
        """
        # Get line points
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2
        x0, y0 = point.x(), point.y()

        # Calculate line length
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # If line is actually a point, return distance to that point
        if line_length < 1e-10:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        # Calculate perpendicular distance
        # d = |Ax0 + By0 + C| / sqrt(A^2 + B^2)
        # where Ax + By + C = 0 is the line equation
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        distance = abs(A * x0 + B * y0 + C) / math.sqrt(A * A + B * B)

        return distance

    def _calculate_parallel_line_points(self, point: QPointF, line: Line) -> Tuple[QPointF, QPointF]:
        """Calculate the points for a parallel line through a given point.

        Args:
            point: Point through which the parallel line will pass
            line: Line to which the new line will be parallel

        Returns:
            Tuple of two points defining the parallel line
        """
        # Get line points
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2
        x0, y0 = point.x(), point.y()

        # Calculate direction vector of the original line
        dx = x2 - x1
        dy = y2 - y1

        # Calculate length of the direction vector
        length = math.sqrt(dx * dx + dy * dy)

        # If line is actually a point, return a horizontal line through the given point
        if length < 1e-10:
            return QPointF(x0 - 100, y0), QPointF(x0 + 100, y0)

        # Normalize direction vector
        dx /= length
        dy /= length

        # Calculate points for the parallel line
        # Use the same direction vector, but starting from the given point
        p1 = QPointF(x0 - dx * 100, y0 - dy * 100)
        p2 = QPointF(x0 + dx * 100, y0 + dy * 100)

        return p1, p2

    def _create_parallel_line(self) -> None:
        """Create a parallel line through the reference point."""
        # Get reference point and line
        ref_point = self.data['reference_point']
        ref_line = self.data['reference_line']

        # Calculate parallel line points
        p1, p2 = self._calculate_parallel_line_points(QPointF(ref_point.x, ref_point.y), ref_line)

        # Create line style
        style = self._create_line_style()

        # Create line
        line = self._create_object(
            'line',
            x1=p1.x(),
            y1=p1.y(),
            x2=p2.x(),
            y2=p2.y(),
            style=style,
            line_type=self.line_type
        )

        # Store distance if measurement is enabled
        if self.show_distance:
            distance = self._calculate_distance_to_line(QPointF(ref_point.x, ref_point.y), ref_line)
            self.data['distance'] = distance

            # Add distance to line metadata
            if hasattr(line, 'metadata'):
                line.metadata['parallel_distance'] = distance

    def _preview_parallel_line(self, point: QPointF, line: Line) -> None:
        """Preview a parallel line through a given point.

        Args:
            point: Point through which the parallel line will pass
            line: Line to which the new line will be parallel
        """
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Calculate parallel line points
        p1, p2 = self._calculate_parallel_line_points(point, line)

        # Set up pen for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

        # Draw preview line based on line type
        if self.line_type == LineType.SEGMENT:
            # Draw line segment
            line_item = self.canvas.scene.addLine(
                QLineF(p1.x(), p1.y(), p2.x(), p2.y()),
                preview_pen
            )
            self.preview_items.append(line_item)
        elif self.line_type == LineType.RAY:
            # Draw ray (from point extending in the direction of the original line)
            # Calculate direction vector
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of the original line
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = point.x() + dx * extension
            extended_y = point.y() + dy * extension

            # Draw the ray
            line_item = self.canvas.scene.addLine(
                QLineF(point.x(), point.y(), extended_x, extended_y),
                preview_pen
            )
            self.preview_items.append(line_item)
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = point.x() - dx * extension
            extended_y1 = point.y() - dy * extension
            extended_x2 = point.x() + dx * extension
            extended_y2 = point.y() + dy * extension

            # Draw the infinite line
            line_item = self.canvas.scene.addLine(
                QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                preview_pen
            )
            self.preview_items.append(line_item)

        # If distance measurement is enabled, show the distance
        if self.show_distance:
            distance = self._calculate_distance_to_line(point, line)

            # Draw a small text label with the distance
            text_item = self.canvas.scene.addSimpleText(f"{distance:.2f}")
            text_item.setPos(point.x() + 10, point.y() + 10)  # Offset from point
            text_item.setBrush(QBrush(QColor(0, 0, 200, 200)))
            self.preview_items.append(text_item)


class AngleBisectorTool(GeometryTool):
    """Tool for creating angle bisectors.

    This tool allows users to create lines that bisect angles. It supports two modes:
    1. Three Points mode: Creates a bisector of the angle formed by three points
    2. Two Lines mode: Creates a bisector of the angle formed by two lines
    """

    # Mode constants
    MODE_THREE_POINTS = 0  # Angle defined by three points
    MODE_TWO_LINES = 1     # Angle defined by two lines

    def __init__(self) -> None:
        """Initialize the angle bisector tool."""
        super().__init__("Angle Bisector", "angle_bisector")

        # Line style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine

        # Line type
        self.line_type = LineType.RAY

        # Current mode
        self.mode = self.MODE_THREE_POINTS

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Reset data
        self.data = {
            'points': [],  # Points defining the angle (for MODE_THREE_POINTS)
            'lines': [],   # Lines defining the angle (for MODE_TWO_LINES)
        }

        # Set state
        self.state = ToolState.IDLE

        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.mode == self.MODE_THREE_POINTS:
                self.explorer.status_bar.showMessage("Select three points to define an angle")
            else:  # MODE_TWO_LINES
                self.explorer.status_bar.showMessage("Select two lines to define an angle")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Clear preview
        self._clear_preview()

        # Reset data
        self.data = {}

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.mode == self.MODE_THREE_POINTS:
            self._handle_three_points_mode(pos, snap_type, snap_target)
        else:  # MODE_TWO_LINES
            self._handle_two_lines_mode(pos, snap_type, snap_target)

    def _handle_three_points_mode(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press in three-points mode.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        points = self.data.get('points', [])

        if len(points) < 3:
            # We need to collect three points
            if snap_type == 'object' and isinstance(snap_target, Point):
                # Use existing point
                point = snap_target
            else:
                # Create new point
                style = self._create_point_style()
                point = self._create_object(
                    'point',
                    x=pos.x(),
                    y=pos.y(),
                    style=style
                )

            # Add point to list
            points.append(point)
            self.data['points'] = points

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                if len(points) == 1:
                    self.explorer.status_bar.showMessage("Select second point to define the angle")
                elif len(points) == 2:
                    self.explorer.status_bar.showMessage("Select third point to complete the angle")

            # If we have all three points, create the bisector
            if len(points) == 3:
                self._create_angle_bisector_from_points()
                self._complete_operation()

    def _handle_two_lines_mode(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press in two-lines mode.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        lines = self.data.get('lines', [])

        if len(lines) < 2:
            # We need to collect two lines
            if snap_type == 'object' and isinstance(snap_target, Line):
                # Use existing line
                line = snap_target

                # Check if this line is already selected
                if line in lines:
                    if self.explorer and hasattr(self.explorer, 'status_bar'):
                        self.explorer.status_bar.showMessage("Line already selected. Please select a different line.")
                    return

                # Add line to list
                lines.append(line)
                self.data['lines'] = lines

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    if len(lines) == 1:
                        self.explorer.status_bar.showMessage("Select second line to complete the angle")

                # If we have both lines, create the bisector
                if len(lines) == 2:
                    self._create_angle_bisector_from_lines()
                    self._complete_operation()
            else:
                # No line selected
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Please select a line to define the angle")

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Clear previous preview
        self._clear_preview()

        # Create preview based on current state
        if self.mode == self.MODE_THREE_POINTS:
            points = self.data.get('points', [])
            if len(points) == 2:
                # We have two points, preview the angle bisector for the current mouse position
                pos, _, _ = self._snap_position_with_info(scene_pos)
                self._preview_angle_bisector_from_points(points[0], points[1], pos)
        else:  # MODE_TWO_LINES
            lines = self.data.get('lines', [])
            if len(lines) == 1:
                # We have one line, preview the angle bisector for the current mouse position
                pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)
                if snap_type == 'object' and isinstance(snap_target, Line) and snap_target != lines[0]:
                    self._preview_angle_bisector_from_lines(lines[0], snap_target)

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle mode switching
        if event.key() == Qt.Key.Key_1:
            self.set_mode(self.MODE_THREE_POINTS)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_2:
            self.set_mode(self.MODE_TWO_LINES)
            event.accept()
            return
        # Handle escape key to cancel operation
        elif event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

        # Handle line type switching
        if event.key() == Qt.Key.Key_S:
            self.set_line_type(LineType.SEGMENT)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_R:
            self.set_line_type(LineType.RAY)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_I:
            self.set_line_type(LineType.INFINITE)
            event.accept()
            return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Angle bisector creation cancelled")

    def set_mode(self, mode: int) -> None:
        """Set the mode for the angle bisector tool.

        Args:
            mode: Mode to set (MODE_THREE_POINTS or MODE_TWO_LINES)
        """
        if mode != self.mode:
            self.mode = mode
            self._cancel_operation()
            self._init_tool()

    def set_line_type(self, line_type: LineType) -> None:
        """Set the line type for new lines.

        Args:
            line_type: Type of line (segment, ray, or infinite)
        """
        self.line_type = line_type

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            line_type_name = self.line_type.name.lower()
            self.explorer.status_bar.showMessage(f"Line type set to {line_type_name}")

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new lines.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new lines.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new lines.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def _create_point_style(self) -> Style:
        """Create a style object for new points.

        Returns:
            Style object for new points
        """
        return Style(
            point_size=5.0,
            stroke_color=QColor(0, 0, 0),
            fill_color=QColor(255, 255, 255)
        )

    def _create_line_style(self) -> Style:
        """Create a style object for new lines.

        Returns:
            Style object for new lines
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style
        )

    def _calculate_angle_bisector_from_points(self, p1: Point, p2: Point, p3: Point) -> Tuple[QPointF, QPointF]:
        """Calculate the angle bisector from three points.

        The angle is defined by p1-p2-p3, with p2 being the vertex.

        Args:
            p1: First point
            p2: Vertex point
            p3: Third point

        Returns:
            Tuple of (start_point, end_point) defining the bisector line
        """
        # Convert points to QPointF
        p1_pos = QPointF(p1.x, p1.y)
        p2_pos = QPointF(p2.x, p2.y)
        p3_pos = QPointF(p3.x, p3.y)

        # Calculate vectors from vertex to other points
        v1 = QPointF(p1_pos.x() - p2_pos.x(), p1_pos.y() - p2_pos.y())
        v2 = QPointF(p3_pos.x() - p2_pos.x(), p3_pos.y() - p2_pos.y())

        # Normalize vectors
        v1_length = math.sqrt(v1.x() * v1.x() + v1.y() * v1.y())
        v2_length = math.sqrt(v2.x() * v2.x() + v2.y() * v2.y())

        if v1_length < 1e-10 or v2_length < 1e-10:
            # One of the vectors is too short, can't calculate bisector
            # Return a default horizontal line through the vertex
            return p2_pos, QPointF(p2_pos.x() + 100, p2_pos.y())

        # Normalize vectors
        v1_normalized = QPointF(v1.x() / v1_length, v1.y() / v1_length)
        v2_normalized = QPointF(v2.x() / v2_length, v2.y() / v2_length)

        # Calculate bisector vector (sum of normalized vectors)
        bisector_x = v1_normalized.x() + v2_normalized.x()
        bisector_y = v1_normalized.y() + v2_normalized.y()

        # Normalize bisector vector
        bisector_length = math.sqrt(bisector_x * bisector_x + bisector_y * bisector_y)

        if bisector_length < 1e-10:
            # Vectors are in opposite directions, bisector is perpendicular
            # Rotate v1 by 90 degrees to get perpendicular
            bisector_x = -v1_normalized.y()
            bisector_y = v1_normalized.x()
        else:
            # Normalize bisector
            bisector_x /= bisector_length
            bisector_y /= bisector_length

        # Calculate end point at a distance along the bisector
        distance = 100  # Arbitrary distance
        end_x = p2_pos.x() + bisector_x * distance
        end_y = p2_pos.y() + bisector_y * distance

        return p2_pos, QPointF(end_x, end_y)

    def _calculate_angle_bisector_from_lines(self, line1: Line, line2: Line) -> Tuple[QPointF, QPointF]:
        """Calculate the angle bisector from two lines.

        Args:
            line1: First line
            line2: Second line

        Returns:
            Tuple of (start_point, end_point) defining the bisector line
        """
        # Find intersection point of the two lines
        intersections = line1.intersect(line2)

        if not intersections:
            # Lines are parallel or don't intersect
            # Return a default horizontal line through the midpoint of the lines
            midpoint_x = (line1.x1 + line1.x2 + line2.x1 + line2.x2) / 4
            midpoint_y = (line1.y1 + line1.y2 + line2.y1 + line2.y2) / 4
            return QPointF(midpoint_x, midpoint_y), QPointF(midpoint_x + 100, midpoint_y)

        # Get intersection point
        intersection = intersections[0]

        # Calculate direction vectors of the lines
        v1_x = line1.x2 - line1.x1
        v1_y = line1.y2 - line1.y1
        v2_x = line2.x2 - line2.x1
        v2_y = line2.y2 - line2.y1

        # Normalize vectors
        v1_length = math.sqrt(v1_x * v1_x + v1_y * v1_y)
        v2_length = math.sqrt(v2_x * v2_x + v2_y * v2_y)

        if v1_length < 1e-10 or v2_length < 1e-10:
            # One of the vectors is too short, can't calculate bisector
            # Return a default horizontal line through the intersection
            return intersection, QPointF(intersection.x() + 100, intersection.y())

        # Normalize vectors
        v1_x /= v1_length
        v1_y /= v1_length
        v2_x /= v2_length
        v2_y /= v2_length

        # Calculate bisector vector (sum of normalized vectors)
        bisector_x = v1_x + v2_x
        bisector_y = v1_y + v2_y

        # Normalize bisector vector
        bisector_length = math.sqrt(bisector_x * bisector_x + bisector_y * bisector_y)

        if bisector_length < 1e-10:
            # Vectors are in opposite directions, bisector is perpendicular
            # Rotate v1 by 90 degrees to get perpendicular
            bisector_x = -v1_y
            bisector_y = v1_x
        else:
            # Normalize bisector
            bisector_x /= bisector_length
            bisector_y /= bisector_length

        # Calculate end point at a distance along the bisector
        distance = 100  # Arbitrary distance
        end_x = intersection.x() + bisector_x * distance
        end_y = intersection.y() + bisector_y * distance

        return intersection, QPointF(end_x, end_y)

    def _create_angle_bisector_from_points(self) -> None:
        """Create an angle bisector from three points."""
        # Get points
        points = self.data.get('points', [])
        if len(points) != 3:
            return

        # Calculate bisector
        start_point, end_point = self._calculate_angle_bisector_from_points(points[0], points[1], points[2])

        # Create line style
        style = self._create_line_style()

        # Create line
        self._create_object(
            'line',
            x1=start_point.x(),
            y1=start_point.y(),
            x2=end_point.x(),
            y2=end_point.y(),
            style=style,
            line_type=self.line_type
        )

    def _create_angle_bisector_from_lines(self) -> None:
        """Create an angle bisector from two lines."""
        # Get lines
        lines = self.data.get('lines', [])
        if len(lines) != 2:
            return

        # Calculate bisector
        start_point, end_point = self._calculate_angle_bisector_from_lines(lines[0], lines[1])

        # Create line style
        style = self._create_line_style()

        # Create line
        self._create_object(
            'line',
            x1=start_point.x(),
            y1=start_point.y(),
            x2=end_point.x(),
            y2=end_point.y(),
            style=style,
            line_type=self.line_type
        )

    def _preview_angle_bisector_from_points(self, p1: Point, p2: Point, p3_pos: QPointF) -> None:
        """Preview an angle bisector from two points and a position.

        Args:
            p1: First point
            p2: Vertex point
            p3_pos: Current mouse position (third point)
        """
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Create a temporary point for p3
        p3 = Point(p3_pos.x(), p3_pos.y())

        # Calculate bisector
        start_point, end_point = self._calculate_angle_bisector_from_points(p1, p2, p3)

        # Set up pen for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

        # Draw preview line based on line type
        if self.line_type == LineType.SEGMENT:
            # Draw line segment
            line_item = self.canvas.scene.addLine(
                QLineF(start_point.x(), start_point.y(), end_point.x(), end_point.y()),
                preview_pen
            )
            self.preview_items.append(line_item)
        elif self.line_type == LineType.RAY:
            # Draw ray (from start_point extending through end_point)
            # Calculate direction vector
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of end_point
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = start_point.x() + dx * extension
            extended_y = start_point.y() + dy * extension

            # Draw the ray
            line_item = self.canvas.scene.addLine(
                QLineF(start_point.x(), start_point.y(), extended_x, extended_y),
                preview_pen
            )
            self.preview_items.append(line_item)
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = start_point.x() - dx * extension
            extended_y1 = start_point.y() - dy * extension
            extended_x2 = start_point.x() + dx * extension
            extended_y2 = start_point.y() + dy * extension

            # Draw the infinite line
            line_item = self.canvas.scene.addLine(
                QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                preview_pen
            )
            self.preview_items.append(line_item)

        # Draw angle lines for clarity
        angle_pen = QPen(QColor(200, 200, 200, 100), 1, Qt.PenStyle.DotLine)

        # Line from vertex to first point
        line_item = self.canvas.scene.addLine(
            QLineF(p2.x, p2.y, p1.x, p1.y),
            angle_pen
        )
        self.preview_items.append(line_item)

        # Line from vertex to third point (mouse position)
        line_item = self.canvas.scene.addLine(
            QLineF(p2.x, p2.y, p3_pos.x(), p3_pos.y()),
            angle_pen
        )
        self.preview_items.append(line_item)

    def _preview_angle_bisector_from_lines(self, line1: Line, line2: Line) -> None:
        """Preview an angle bisector from two lines.

        Args:
            line1: First line
            line2: Second line
        """
        if not self.canvas or not hasattr(self.canvas, 'scene'):
            return

        # Calculate bisector
        start_point, end_point = self._calculate_angle_bisector_from_lines(line1, line2)

        # Set up pen for preview
        preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)

        # Draw preview line based on line type
        if self.line_type == LineType.SEGMENT:
            # Draw line segment
            line_item = self.canvas.scene.addLine(
                QLineF(start_point.x(), start_point.y(), end_point.x(), end_point.y()),
                preview_pen
            )
            self.preview_items.append(line_item)
        elif self.line_type == LineType.RAY:
            # Draw ray (from start_point extending through end_point)
            # Calculate direction vector
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of end_point
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = start_point.x() + dx * extension
            extended_y = start_point.y() + dy * extension

            # Draw the ray
            line_item = self.canvas.scene.addLine(
                QLineF(start_point.x(), start_point.y(), extended_x, extended_y),
                preview_pen
            )
            self.preview_items.append(line_item)
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = start_point.x() - dx * extension
            extended_y1 = start_point.y() - dy * extension
            extended_x2 = start_point.x() + dx * extension
            extended_y2 = start_point.y() + dy * extension

            # Draw the infinite line
            line_item = self.canvas.scene.addLine(
                QLineF(extended_x1, extended_y1, extended_x2, extended_y2),
                preview_pen
            )
            self.preview_items.append(line_item)


class TextTool(GeometryTool):
    """Tool for creating and editing text labels.

    This tool allows users to add text labels to the canvas and to label existing
    geometric objects. Text can be formatted with different fonts, sizes, and colors.
    """

    # Mode constants
    MODE_FREE_TEXT = 0  # Create standalone text
    MODE_LABEL_OBJECT = 1  # Label an existing object

    def __init__(self) -> None:
        """Initialize the text tool."""
        super().__init__("Text", "text")

        # Text style options
        self.font_family = "Arial"
        self.font_size = 12.0
        self.font_style = 0  # 0 = normal, 1 = bold, 2 = italic, 3 = bold italic
        self.text_color = QColor(0, 0, 0)  # Black

        # Current mode
        self.mode = self.MODE_FREE_TEXT

        # Auto-position flag
        self.auto_position = True

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Initialize data
        self.data = {
            'text': "",  # Text content
            'position': None,  # Text position
            'target_object': None,  # Object being labeled
        }

        # Set state
        self.state = ToolState.IDLE

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            if self.mode == self.MODE_FREE_TEXT:
                self.explorer.status_bar.showMessage("Click to place text")
            else:  # MODE_LABEL_OBJECT
                self.explorer.status_bar.showMessage("Select an object to label")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Clear preview
        self._clear_preview()

        # Reset data
        self.data = {}

    def _create_text_style(self) -> Style:
        """Create a style for new text based on current settings.

        Returns:
            Style object for the text
        """
        style = Style()
        style.stroke_color = self.text_color
        style.font_family = self.font_family
        style.font_size = self.font_size
        style.font_style = self.font_style
        return style

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.IBeamCursor)

    def set_mode(self, mode: int) -> None:
        """Set the tool mode.

        Args:
            mode: Tool mode (MODE_FREE_TEXT or MODE_LABEL_OBJECT)
        """
        self.mode = mode
        if self.active:
            self._init_tool()

    def set_font_family(self, font_family: str) -> None:
        """Set the font family for new text.

        Args:
            font_family: Font family name
        """
        self.font_family = font_family

    def set_font_size(self, size: float) -> None:
        """Set the font size for new text.

        Args:
            size: Font size in points
        """
        self.font_size = size

    def set_font_style(self, style: int) -> None:
        """Set the font style for new text.

        Args:
            style: Font style (0 = normal, 1 = bold, 2 = italic, 3 = bold italic)
        """
        self.font_style = style

    def set_text_color(self, color: QColor) -> None:
        """Set the text color for new text.

        Args:
            color: Text color
        """
        self.text_color = color

    def set_auto_position(self, auto_position: bool) -> None:
        """Set whether to automatically position text labels relative to objects.

        Args:
            auto_position: Whether to automatically position text
        """
        self.auto_position = auto_position

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self.mode == self.MODE_FREE_TEXT:
            # Create free text at the clicked position
            self._handle_free_text_mode(scene_pos)
        else:  # MODE_LABEL_OBJECT
            # Label the object at the clicked position
            self._handle_label_object_mode(scene_pos)

    def _handle_free_text_mode(self, scene_pos: QPointF) -> None:
        """Handle mouse press in free text mode.

        Args:
            scene_pos: Position in scene coordinates
        """
        # Store the position
        self.data['position'] = scene_pos

        # Prompt for text input
        self._prompt_for_text_input()

    def _handle_label_object_mode(self, scene_pos: QPointF) -> None:
        """Handle mouse press in label object mode.

        Args:
            scene_pos: Position in scene coordinates
        """
        # Get object at position
        obj = self.canvas.get_object_at(scene_pos) if self.canvas else None

        if obj:
            # Store the target object
            self.data['target_object'] = obj

            # Prompt for text input
            self._prompt_for_text_input()
        else:
            # No object found, show message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("No object found. Please click on an object to label.")

    def _prompt_for_text_input(self) -> None:
        """Prompt the user for text input."""
        # Create a text dialog
        is_label = self.mode == self.MODE_LABEL_OBJECT
        dialog = TextDialog(
            parent=self.explorer,
            initial_text="" if not is_label else "Label",
            initial_font_family=self.font_family,
            initial_font_size=self.font_size,
            initial_font_style=self.font_style,
            initial_color=self.text_color,
            initial_auto_position=self.auto_position,
            is_label=is_label
        )

        # Show the dialog
        if dialog.exec():
            # Get values from dialog
            self.data['text'] = dialog.get_text()
            self.font_family = dialog.get_font_family()
            self.font_size = dialog.get_font_size()
            self.font_style = dialog.get_font_style()
            self.text_color = dialog.get_color()
            self.auto_position = dialog.get_auto_position()

            # Create the text object
            self._create_text_object()
        else:
            # Dialog cancelled
            self._cancel_operation()

    def _create_text_object(self) -> None:
        """Create a text object based on the current data."""
        if not self.canvas:
            return

        # Get text content
        text_content = self.data.get('text', "")
        if not text_content:
            return

        # Create style
        style = self._create_text_style()

        # Create text object
        if self.mode == self.MODE_FREE_TEXT:
            # Create standalone text
            position = self.data.get('position')
            if not position:
                return

            text_obj = self._create_object(
                'text',
                x=position.x(),
                y=position.y(),
                text=text_content,
                style=style
            )
        else:  # MODE_LABEL_OBJECT
            # Create text as a label for an object
            target_obj = self.data.get('target_object')
            if not target_obj:
                return

            # Create text with target object
            text_obj = self._create_object(
                'text',
                x=0,  # Will be positioned automatically
                y=0,  # Will be positioned automatically
                text=text_content,
                style=style,
                target_object=target_obj,
                auto_position=self.auto_position
            )

            # Update position based on target object
            if self.auto_position:
                text_obj.update_position_from_target()

        # Complete operation
        self._complete_operation()

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Update cursor based on what's under the mouse
        if self.mode == self.MODE_LABEL_OBJECT:
            obj = self.canvas.get_object_at(scene_pos) if self.canvas else None
            if obj:
                self.canvas.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.canvas.setCursor(self.get_cursor())

    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse release event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Nothing to do on release
        pass

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            return

        # Call base implementation for other keys
        super().key_press(event)


class CompassTool(GeometryTool):
    """Tool for drawing circles with radius equal to a given distance.

    This tool allows users to create circles with a radius equal to the distance
    between two points, implementing the classical compass-and-straightedge construction.
    """

    # Tool states
    STATE_SELECTING_RADIUS = "selecting_radius"  # Selecting two points to define radius
    STATE_DRAWING_CIRCLES = "drawing_circles"   # Drawing circles with the selected radius

    def __init__(self) -> None:
        """Initialize the compass tool."""
        super().__init__("Compass", "compass")

        # Circle style options
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.stroke_width = 1.0
        self.stroke_style = Qt.PenStyle.SolidLine
        self.fill_color = QColor(255, 255, 255, 50)  # Transparent white
        self.fill_style = Qt.BrushStyle.SolidPattern

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Reset data
        self.data = {
            'radius_points': [],  # Points defining the radius
            'radius': None,       # Calculated radius
        }

        # Set state
        self.state = self.STATE_SELECTING_RADIUS

        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Select first point to define radius")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Clear preview
        self._clear_preview()

        # Reset data
        self.data = {}

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        if self.state == self.STATE_SELECTING_RADIUS:
            # Selecting points to define radius
            self._handle_radius_selection(pos, snap_type, snap_target)
        elif self.state == self.STATE_DRAWING_CIRCLES:
            # Drawing circles with the selected radius
            self._handle_circle_creation(pos, snap_type, snap_target)

    def _handle_radius_selection(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press when selecting radius points.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        radius_points = self.data.get('radius_points', [])

        if len(radius_points) < 2:
            # We need to collect two points to define the radius
            if snap_type == 'object' and isinstance(snap_target, Point):
                # Use existing point
                point = snap_target
            else:
                # Create new point
                style = self._create_point_style()
                point = self._create_object(
                    'point',
                    x=pos.x(),
                    y=pos.y(),
                    style=style
                )

            # Add point to list
            radius_points.append(point)
            self.data['radius_points'] = radius_points

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                if len(radius_points) == 1:
                    self.explorer.status_bar.showMessage("Select second point to define radius")

            # If we have both points, calculate radius and switch to drawing mode
            if len(radius_points) == 2:
                # Calculate radius
                p1 = radius_points[0]
                p2 = radius_points[1]
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                radius = math.sqrt(dx * dx + dy * dy)

                # Store radius
                self.data['radius'] = radius

                # Switch to drawing mode
                self.state = self.STATE_DRAWING_CIRCLES

                # Update status message
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(
                        f"Radius set to {radius:.2f}. Click to create circles with this radius."
                    )

    def _handle_circle_creation(self, pos: QPointF, snap_type: str, snap_target: Optional[GeometricObject]) -> None:
        """Handle mouse press when creating circles.

        Args:
            pos: Position in scene coordinates
            snap_type: Type of snap ('grid', 'object', or 'none')
            snap_target: Object that was snapped to, if any
        """
        # Get radius
        radius = self.data.get('radius')
        if radius is None:
            # No radius defined, switch back to radius selection
            self.state = self.STATE_SELECTING_RADIUS
            self.data['radius_points'] = []
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Select first point to define radius")
            return

        # Create circle at the clicked position with the selected radius
        if snap_type == 'object' and isinstance(snap_target, Point):
            # Use existing point as center
            center_x = snap_target.x
            center_y = snap_target.y
        else:
            # Use clicked position as center
            center_x = pos.x()
            center_y = pos.y()

        # Create circle style
        style = self._create_circle_style()

        # Create circle
        self._create_object(
            'circle',
            cx=center_x,
            cy=center_y,
            radius=radius,
            style=style
        )

        # No need to change state - can create multiple circles
        # Just update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage(
                f"Created circle with radius {radius:.2f}. Click to create another, or press Escape to reset radius."
            )

    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Clear previous preview
        self._clear_preview()

        # Snap position to grid/objects
        pos, snap_type, snap_target = self._snap_position_with_info(scene_pos)

        # Create preview based on current state
        if self.state == self.STATE_SELECTING_RADIUS:
            # Preview radius line
            self._preview_radius_line(pos)
        elif self.state == self.STATE_DRAWING_CIRCLES:
            # Preview circle
            self._preview_circle(pos)

        # Update status message
        self._update_status_message(pos)

    def _preview_radius_line(self, pos: QPointF) -> None:
        """Preview the radius line during radius selection.

        Args:
            pos: Current mouse position
        """
        radius_points = self.data.get('radius_points', [])

        if len(radius_points) == 1 and self.canvas and hasattr(self.canvas, 'scene'):
            # Draw line from first point to current position
            p1 = radius_points[0]
            p1_pos = QPointF(p1.x, p1.y)

            # Set up pen for preview
            preview_pen = QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DashLine)

            # Draw preview line
            line_item = self.canvas.scene.addLine(
                QLineF(p1_pos.x(), p1_pos.y(), pos.x(), pos.y()),
                preview_pen
            )
            self.preview_items.append(line_item)

            # Calculate and display distance
            dx = pos.x() - p1_pos.x()
            dy = pos.y() - p1_pos.y()
            distance = math.sqrt(dx * dx + dy * dy)

            # Add text label with distance
            mid_x = (p1_pos.x() + pos.x()) / 2
            mid_y = (p1_pos.y() + pos.y()) / 2
            text_item = self.canvas.scene.addSimpleText(f"{distance:.2f}")
            text_item.setPos(mid_x, mid_y)
            text_item.setBrush(QBrush(QColor(0, 0, 200, 200)))
            self.preview_items.append(text_item)

    def _preview_circle(self, pos: QPointF) -> None:
        """Preview the circle during circle creation.

        Args:
            pos: Current mouse position (center of circle)
        """
        radius = self.data.get('radius')

        if radius is not None and self.canvas and hasattr(self.canvas, 'scene'):
            # Set up pen and brush for preview
            preview_pen = QPen(QColor(100, 100, 255, 150), self.stroke_width, Qt.PenStyle.DashLine)
            preview_brush = QBrush(QColor(100, 100, 255, 30), Qt.BrushStyle.SolidPattern)

            # Draw preview circle
            circle_item = self.canvas.scene.addEllipse(
                pos.x() - radius,
                pos.y() - radius,
                radius * 2,
                radius * 2,
                preview_pen,
                preview_brush
            )
            self.preview_items.append(circle_item)

    def _update_status_message(self, pos: QPointF) -> None:
        """Update the status message based on current state.

        Args:
            pos: Current mouse position
        """
        if not self.explorer or not hasattr(self.explorer, 'status_bar'):
            return

        if self.state == self.STATE_SELECTING_RADIUS:
            radius_points = self.data.get('radius_points', [])

            if len(radius_points) == 0:
                self.explorer.status_bar.showMessage(f"Select first point to define radius at ({pos.x():.2f}, {pos.y():.2f})")
            elif len(radius_points) == 1:
                p1 = radius_points[0]
                dx = pos.x() - p1.x
                dy = pos.y() - p1.y
                distance = math.sqrt(dx * dx + dy * dy)
                self.explorer.status_bar.showMessage(
                    f"First point at ({p1.x:.2f}, {p1.y:.2f}), radius: {distance:.2f}. Click to set."
                )
        elif self.state == self.STATE_DRAWING_CIRCLES:
            radius = self.data.get('radius')
            if radius is not None:
                self.explorer.status_bar.showMessage(
                    f"Click to create circle with radius {radius:.2f} at ({pos.x():.2f}, {pos.y():.2f})"
                )

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation or reset radius
        if event.key() == Qt.Key.Key_Escape:
            if self.state == self.STATE_DRAWING_CIRCLES:
                # Reset radius and go back to radius selection
                self.state = self.STATE_SELECTING_RADIUS
                self.data['radius_points'] = []
                self.data['radius'] = None
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage("Radius reset. Select first point to define new radius.")
            else:
                # Cancel operation
                self._cancel_operation()
            event.accept()
            return

        # Handle style shortcuts
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Increase stroke width
                self.set_stroke_width(min(10.0, self.stroke_width + 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                # Decrease stroke width
                self.set_stroke_width(max(0.5, self.stroke_width - 0.5))
                if self.explorer and hasattr(self.explorer, 'status_bar'):
                    self.explorer.status_bar.showMessage(f"Stroke width: {self.stroke_width:.1f}")
                event.accept()
                return

        # Call base implementation for other keys
        super().key_press(event)

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Call base implementation
        super()._cancel_operation()

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Compass operation cancelled")

    def set_stroke_width(self, width: float) -> None:
        """Set the stroke width for new circles.

        Args:
            width: Stroke width
        """
        self.stroke_width = width

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new circles.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_stroke_style(self, style: Qt.PenStyle) -> None:
        """Set the stroke style for new circles.

        Args:
            style: Stroke style
        """
        self.stroke_style = style

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new circles.

        Args:
            color: Fill color
        """
        self.fill_color = color

    def set_fill_style(self, style: Qt.BrushStyle) -> None:
        """Set the fill style for new circles.

        Args:
            style: Fill style
        """
        self.fill_style = style

    def _create_point_style(self) -> Style:
        """Create a style object for new points.

        Returns:
            Style object for new points
        """
        return Style(
            point_size=5.0,
            stroke_color=QColor(0, 0, 0),
            fill_color=QColor(255, 255, 255)
        )

    def _create_circle_style(self) -> Style:
        """Create a style object for new circles.

        Returns:
            Style object for new circles
        """
        return Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            stroke_style=self.stroke_style,
            fill_color=self.fill_color,
            fill_style=self.fill_style
        )


class IntersectionTool(GeometryTool):
    """Tool for finding and marking intersections between objects.

    This tool allows users to select two objects and automatically create
    points at their intersections. It supports finding intersections between:
    - Line and Line
    - Line and Circle
    - Circle and Circle
    """

    def __init__(self) -> None:
        """Initialize the intersection tool."""
        super().__init__("Intersection", "intersection")

        # Selection state
        self.first_object = None
        self.second_object = None

        # Point style options
        self.point_size = 5.0
        self.stroke_color = QColor(0, 0, 0)  # Black
        self.fill_color = QColor(255, 255, 255)  # White

    def _init_tool(self) -> None:
        """Initialize tool-specific state."""
        # Reset selection
        self.first_object = None
        self.second_object = None

        # Set cursor
        if self.canvas:
            self.canvas.setCursor(self.get_cursor())

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Select first object for intersection")

    def _cleanup_tool(self) -> None:
        """Clean up tool-specific state."""
        # Reset selection
        self.first_object = None
        self.second_object = None

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press event.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Only handle left button
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Get object at position
        obj = self.canvas.find_object_at(scene_pos)
        if not obj:
            # No object at position
            return

        # Check if we already have the first object
        if not self.first_object:
            # Set first object
            self.first_object = obj

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(
                    f"Selected {obj.__class__.__name__} as first object. Select second object for intersection."
                )
        else:
            # Set second object
            self.second_object = obj

            # Find and create intersections
            self._find_and_create_intersections()

            # Reset selection for next operation
            self.first_object = None
            self.second_object = None

            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage("Select first object for intersection")

    def key_press(self, event: QKeyEvent) -> None:
        """Handle key press event.

        Args:
            event: Key event
        """
        # Handle escape key to cancel operation
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_operation()
            event.accept()
            return

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        # Reset selection
        self.first_object = None
        self.second_object = None

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage("Intersection operation cancelled. Select first object for intersection.")

    def get_cursor(self) -> QCursor:
        """Get the cursor for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def _get_object_at_position(self, pos: QPointF) -> Optional[GeometricObject]:
        """Get the object at the given position.

        Args:
            pos: Position in scene coordinates

        Returns:
            Object at the position, or None if no object is found
        """
        if not self.canvas:
            return None

        # Use canvas method to find object at position
        return self.canvas.get_object_at(pos)

    def _find_and_create_intersections(self) -> None:
        """Find and create intersections between the selected objects."""
        if not self.first_object or not self.second_object:
            return

        # Find intersections
        intersections = self._find_intersections(self.first_object, self.second_object)

        # Create points at intersections
        if intersections:
            self._create_intersection_points(intersections)
        else:
            # Update status message
            if self.explorer and hasattr(self.explorer, 'status_bar'):
                self.explorer.status_bar.showMessage(
                    "No intersections found. Select first object for next intersection."
                )

    def _create_intersection_points(self, intersections: List[QPointF]) -> None:
        """Create points at the given intersection positions.

        Args:
            intersections: List of intersection points
        """
        created_points = []
        for intersection in intersections:
            # Create point style
            style = self._create_point_style()

            # Create point
            point = self._create_object(
                'point',
                x=intersection.x(),
                y=intersection.y(),
                style=style,
                name=f"Intersection"
            )

            if point:
                created_points.append(point)

        # Update status message
        if self.explorer and hasattr(self.explorer, 'status_bar'):
            self.explorer.status_bar.showMessage(
                f"Created {len(created_points)} intersection point(s). Select first object for next intersection."
            )

    def _find_intersections(self, obj1: GeometricObject, obj2: GeometricObject) -> List[QPointF]:
        """Find intersections between two objects.

        Args:
            obj1: First object
            obj2: Second object

        Returns:
            List of intersection points
        """
        # Use the intersect method of the objects
        return obj1.intersect(obj2)

    def _create_point_style(self) -> Style:
        """Create a style object for new intersection points.

        Returns:
            Style object for new points
        """
        style = Style()
        style.point_size = self.point_size
        style.stroke_color = self.stroke_color
        style.fill_color = self.fill_color
        return style

    def set_point_size(self, size: float) -> None:
        """Set the point size for new intersection points.

        Args:
            size: Point size in pixels
        """
        self.point_size = size

    def set_stroke_color(self, color: QColor) -> None:
        """Set the stroke color for new intersection points.

        Args:
            color: Stroke color
        """
        self.stroke_color = color

    def set_fill_color(self, color: QColor) -> None:
        """Set the fill color for new intersection points.

        Args:
            color: Fill color
        """
        self.fill_color = color