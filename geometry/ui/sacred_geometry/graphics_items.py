"""Graphics items for the Sacred Geometry Explorer.

This module contains the graphics items that represent geometric objects
on the canvas in the Sacred Geometry Explorer.
"""

import math
from typing import Any, List, Optional, Set

from loguru import logger
from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QFont,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
)
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from geometry.ui.sacred_geometry.model import (
    Circle,
    GeometricObject,
    Line,
    LineType,
    Point,
    Polygon,
    Text,
)


class GeometricGraphicsItem(QGraphicsItem):
    """Base class for all geometric graphics items.

    This class provides common functionality for all graphics items that
    represent geometric objects on the canvas.
    """

    # Selection handle size
    HANDLE_SIZE = 12  # Increased from 8 to make handles easier to select

    # Selection handle positions (for objects with handles)
    HANDLE_TOP_LEFT = 0
    HANDLE_TOP_MIDDLE = 1
    HANDLE_TOP_RIGHT = 2
    HANDLE_MIDDLE_LEFT = 3
    HANDLE_MIDDLE_MIDDLE = 4  # Center handle
    HANDLE_MIDDLE_RIGHT = 5
    HANDLE_BOTTOM_LEFT = 6
    HANDLE_BOTTOM_MIDDLE = 7
    HANDLE_BOTTOM_RIGHT = 8

    def __init__(self, geometric_object: GeometricObject) -> None:
        """Initialize a geometric graphics item.

        Args:
            geometric_object: The geometric object this item represents
        """
        super().__init__()
        self.geometric_object = geometric_object
        self.selected_handles: Set[int] = set()
        self.hover_handle: Optional[int] = None

        # Drag state
        self.drag_handle: Optional[int] = None
        self.drag_start_pos = QPointF()

        # Set item flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # Set item properties
        self.setAcceptHoverEvents(True)
        self.setZValue(0)  # Default z-value

        # Update the item's appearance
        self.update_appearance()

    def update_appearance(self) -> None:
        """Update the item's appearance based on the geometric object's properties."""
        # Update visibility
        self.setVisible(self.geometric_object.visible)

        # Update selection state
        self.setSelected(self.geometric_object.selected)

        # Update z-value based on object type
        if isinstance(self.geometric_object, Point):
            self.setZValue(10)  # Points on top
        elif isinstance(self.geometric_object, Line):
            self.setZValue(5)  # Lines in the middle
        elif isinstance(self.geometric_object, Circle):
            self.setZValue(1)  # Circles at the bottom

    def update_from_object(self) -> None:
        """Update the item's geometry and appearance from the geometric object."""
        # Update appearance
        self.update_appearance()

        # Update geometry (to be implemented by subclasses)

        # Update the item
        self.update()

    def update_object_from_item(self) -> None:
        """Update the geometric object's properties from the item."""
        # Update selection state
        self.geometric_object.selected = self.isSelected()

        # Update geometry (to be implemented by subclasses)

    def handle_at(self, point: QPointF) -> Optional[int]:
        """Get the handle at the given point.

        Args:
            point: Point in item coordinates

        Returns:
            Handle index or None if no handle at the point
        """
        # Base implementation returns None (no handles)
        # Subclasses should override this method if they have handles
        return None

    def handle_rect(self, handle: int) -> QRectF:
        """Get the rectangle for the given handle.

        Args:
            handle: Handle index

        Returns:
            Rectangle for the handle in item coordinates
        """
        # Base implementation returns an empty rectangle
        # Subclasses should override this method if they have handles
        return QRectF()

    def handle_cursor(self, handle: int) -> Qt.CursorShape:
        """Get the cursor shape for the given handle.

        Args:
            handle: Handle index

        Returns:
            Cursor shape for the handle
        """
        # Base implementation returns the default cursor
        # Subclasses should override this method if they have handles
        return Qt.CursorShape.ArrowCursor

    def move_handle(self, handle: int, point: QPointF) -> None:
        """Move the given handle to the given point.

        Args:
            handle: Handle index
            point: New position in item coordinates
        """
        # Base implementation does nothing
        # Subclasses should override this method if they have handles
        pass

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Draw selection handles if selected
        if self.isSelected():
            self.paint_selection_handles(painter)

    def paint_selection_handles(self, painter: QPainter) -> None:
        """Paint selection handles.

        Args:
            painter: Painter to use
        """
        # Set up painter with thicker border for better visibility
        painter.setPen(QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(Qt.GlobalColor.white))

        # Draw handles
        for handle in range(8):
            rect = self.handle_rect(handle)
            if not rect.isEmpty():
                if handle == self.hover_handle:
                    # Highlight hovered handle
                    painter.setBrush(QBrush(Qt.GlobalColor.yellow))
                    painter.drawRect(rect)
                    painter.setBrush(QBrush(Qt.GlobalColor.white))
                elif handle in self.selected_handles:
                    # Highlight selected handle
                    painter.setBrush(QBrush(Qt.GlobalColor.red))
                    painter.drawRect(rect)
                    painter.setBrush(QBrush(Qt.GlobalColor.white))
                else:
                    # Normal handle
                    painter.drawRect(rect)

    def hoverMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle hover move events.

        Args:
            event: Event information
        """
        # Check if mouse is over a handle
        handle = self.handle_at(event.pos())

        # Update hover handle
        if handle != self.hover_handle:
            self.hover_handle = handle
            self.update()

        # Set cursor based on handle
        if handle is not None:
            self.setCursor(self.handle_cursor(handle))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle hover leave events.

        Args:
            event: Event information
        """
        # Reset hover handle
        self.hover_handle = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse press events.

        Args:
            event: Event information
        """
        # Check if mouse is over a handle
        handle = self.handle_at(event.pos())

        if handle is not None:
            # Handle clicked - set cursor to the handle's cursor
            self.setCursor(self.handle_cursor(handle))

            # Store the handle for dragging
            self.drag_handle = handle
            self.drag_start_pos = event.pos()

            # Update handle selection
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Toggle handle selection with Ctrl
                if handle in self.selected_handles:
                    self.selected_handles.remove(handle)
                else:
                    self.selected_handles.add(handle)
            else:
                # Select only this handle
                self.selected_handles = {handle}

            # Make sure the item is selected
            if not self.isSelected():
                self.setSelected(True)

            self.update()
            event.accept()
        else:
            # No handle clicked, use default behavior
            self.drag_handle = None
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse move events.

        Args:
            event: Event information
        """
        # Check if we're dragging a handle
        if self.drag_handle is not None:
            # Log the event
            logger.debug(
                f"DEBUG: LineGraphicsItem.mouseMoveEvent with drag_handle={self.drag_handle}"
            )

            # Move the handle to the new position
            # We're directly passing the event position to move_handle
            # which will handle the coordinate conversion
            self.move_handle(self.drag_handle, event.pos())

            # CRITICAL: Do not call update_object_from_item() here as move_handle already updates the object
            # This prevents double-updating which could cause both endpoints to move

            # Force a redraw
            self.update()
            event.accept()
        elif self.selected_handles:
            # Log the event
            logger.debug(
                f"DEBUG: LineGraphicsItem.mouseMoveEvent with selected_handles={self.selected_handles}"
            )

            # Move selected handles
            for handle in self.selected_handles:
                self.move_handle(handle, event.pos())

            # CRITICAL: Do not call update_object_from_item() here as move_handle already updates the object
            # This prevents double-updating which could cause both endpoints to move

            # Force a redraw
            self.update()
            event.accept()
        else:
            # No handles selected, use default behavior for moving the entire line
            logger.debug(
                "DEBUG: LineGraphicsItem.mouseMoveEvent with no handles selected (moving entire line)"
            )
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse release events.

        Args:
            event: Event information
        """
        # Check if we were dragging a handle
        if self.drag_handle is not None:
            # Reset cursor
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # Reset drag handle
            self.drag_handle = None

            # No need to call update_object_from_item() here as we've already updated the object
            # This prevents double-updating which could cause both endpoints to move

            event.accept()
        elif self.selected_handles:
            # No need to call update_object_from_item() here as we've already updated the object
            # This prevents double-updating which could cause both endpoints to move

            event.accept()
        else:
            # No handles selected, use default behavior
            super().mouseReleaseEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Handle item changes.

        Args:
            change: Type of change
            value: New value

        Returns:
            Modified value
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update the object when the item position changes
            self.update_object_from_item()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Update the object when the item selection changes
            self.geometric_object.selected = bool(value)

        return super().itemChange(change, value)


class PointGraphicsItem(GeometricGraphicsItem):
    """Graphics item for a point."""

    def __init__(self, point: Point) -> None:
        """Initialize a point graphics item.

        Args:
            point: The point this item represents
        """
        super().__init__(point)
        self.point = point
        self.updating = False  # Flag to prevent recursive updates
        self.update_from_object()

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the item.

        Returns:
            Bounding rectangle in item coordinates
        """
        # Get point size
        size = self.point.style.point_size

        # Add margin for selection handles
        margin = max(self.HANDLE_SIZE / 2, size / 2)

        return QRectF(-margin, -margin, size + margin * 2, size + margin * 2)

    def update_from_object(self) -> None:
        """Update the item's geometry and appearance from the geometric object."""
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Update base properties
            super().update_from_object()

            # Update position
            self.setPos(self.point.x, self.point.y)
        finally:
            self.updating = False

    def update_object_from_item(self) -> None:
        """Update the geometric object's properties from the item."""
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Update base properties
            super().update_object_from_item()

            # Store old position for change detection
            old_x, old_y = self.point.x, self.point.y
            new_x, new_y = self.pos().x(), self.pos().y()

            # Log point movement
            logger.debug(
                f"Point {self.point.id} moving from ({old_x}, {old_y}) to ({new_x}, {new_y})"
            )

            # Update position in the model
            self.point.x = new_x
            self.point.y = new_y

            # Notify dependents if position changed
            if old_x != new_x or old_y != new_y:
                if self.scene() and hasattr(self.scene().views()[0], "canvas"):
                    # Find all dependent line graphics items
                    dependent_lines = []
                    for item in self.scene().items():
                        if isinstance(item, LineGraphicsItem):
                            # This code is no longer needed as Line objects don't have p1/p2 Point objects
                            # Instead, we'll skip this section as it's not applicable to the new Line implementation
                            is_p1 = False
                            is_p2 = False
                            if is_p1 or is_p2:
                                dependent_lines.append((item, is_p1, is_p2))

                    # Log dependent lines
                    if dependent_lines:
                        logger.debug(
                            f"  Point {self.point.id} has {len(dependent_lines)} dependent lines"
                        )
                    else:
                        logger.debug(f"  Point {self.point.id} has no dependent lines")

                    # Update each dependent line
                    lines_updated = 0
                    for line_item, is_p1, is_p2 in dependent_lines:
                        endpoint = "P1" if is_p1 else "P2"
                        logger.debug(
                            f"  Found dependent line {line_item.line.id} where this point is {endpoint}"
                        )

                        if not line_item.updating:  # Prevent recursive updates
                            # Temporarily disable updating to prevent recursive updates
                            old_updating = line_item.updating
                            line_item.updating = True

                            # This code is no longer needed as Line objects don't have p1/p2 Point objects
                            # Instead, we'll skip this section as it's not applicable to the new Line implementation
                            logger.debug(
                                "    Skipping line update as Line objects no longer use Point objects"
                            )

                            # Force a redraw of the line
                            line_item.prepareGeometryChange()
                            line_item.update()

                            # Restore updating flag
                            line_item.updating = old_updating
                            lines_updated += 1
                        else:
                            logger.debug(
                                "    Skipped updating line (already updating)"
                            )

                    logger.debug(f"  Updated {lines_updated} line graphics items")
        finally:
            self.updating = False

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Get point size
        size = self.point.style.point_size

        # Set up painter
        painter.setPen(QPen(self.point.style.stroke_color, 1))
        painter.setBrush(QBrush(self.point.style.fill_color))

        # Draw point
        painter.drawEllipse(QRectF(-size / 2, -size / 2, size, size))

        # Draw selection handles if selected
        if self.isSelected():
            super().paint(painter, option, widget)

    def handle_at(self, point: QPointF) -> Optional[int]:
        """Get the handle at the given point.

        Args:
            point: Point in item coordinates

        Returns:
            Handle index or None if no handle at the point
        """
        # Points only have one handle (the point itself)
        if QRectF(
            -self.HANDLE_SIZE / 2,
            -self.HANDLE_SIZE / 2,
            self.HANDLE_SIZE,
            self.HANDLE_SIZE,
        ).contains(point):
            return self.HANDLE_MIDDLE_MIDDLE

        return None

    def handle_rect(self, handle: int) -> QRectF:
        """Get the rectangle for the given handle.

        Args:
            handle: Handle index

        Returns:
            Rectangle for the handle in item coordinates
        """
        # Points only have one handle (the point itself)
        if handle == self.HANDLE_MIDDLE_MIDDLE:
            return QRectF(
                -self.HANDLE_SIZE / 2,
                -self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )

        return QRectF()

    def handle_cursor(self, handle: int) -> Qt.CursorShape:
        """Get the cursor shape for the given handle.

        Args:
            handle: Handle index

        Returns:
            Cursor shape for the handle
        """
        # Points only have one handle (the point itself)
        if handle == self.HANDLE_MIDDLE_MIDDLE:
            return Qt.CursorShape.SizeAllCursor

        return Qt.CursorShape.ArrowCursor

    def move_handle(self, handle: int, point: QPointF) -> None:
        """Move the given handle to the given point.

        Args:
            handle: Handle index
            point: New position in item coordinates
        """
        # Points only have one handle (the point itself)
        if handle == self.HANDLE_MIDDLE_MIDDLE:
            self.setPos(self.pos() + point)


class LineGraphicsItem(GeometricGraphicsItem):
    """Graphics item for a line."""

    def __init__(self, line: Line) -> None:
        """Initialize a line graphics item.

        Args:
            line: The line this item represents
        """
        super().__init__(line)
        self.line = line
        self.updating = False  # Flag to prevent recursive updates
        self.update_from_object()

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the item.

        Returns:
            Bounding rectangle in item coordinates
        """
        # Use the line's get_bounds method which handles different line types
        bounds = self.line.get_bounds()

        # Add extra padding for the handles
        padding = self.HANDLE_SIZE
        return bounds.adjusted(-padding, -padding, padding, padding)

    def shape(self) -> QPainterPath:
        """Get the shape of the item for collision detection.

        Returns:
            Shape path that includes the line and its handles
        """
        path = QPainterPath()

        # Add the line to the path
        x1, y1 = self.line.x1, self.line.y1
        x2, y2 = self.line.x2, self.line.y2

        if self.line.line_type == LineType.SEGMENT:
            path.moveTo(x1, y1)
            path.lineTo(x2, y2)
        else:
            # For rays and infinite lines, use the bounding rect
            path.addRect(self.boundingRect())

        # Add handle shapes to the path
        for handle in [self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            rect = self.handle_rect(handle)
            if not rect.isEmpty():
                path.addRect(rect)

        # Set a reasonable stroke width for hit detection
        stroke_width = max(self.line.style.stroke_width, self.HANDLE_SIZE)
        stroker = QPainterPathStroker()
        stroker.setWidth(stroke_width)
        return stroker.createStroke(path)

    def update_from_object(self) -> None:
        """Update the item's geometry and appearance from the geometric object."""
        # Prevent recursive updates
        if self.updating:
            logger.debug(
                "DEBUG: LineGraphicsItem.update_from_object skipped due to recursive update prevention"
            )
            return

        self.updating = True

        try:
            # Store original values for debugging
            old_x1, old_y1 = self.line.x1, self.line.y1
            old_x2, old_y2 = self.line.x2, self.line.y2

            # Log before update
            logger.debug(
                f"DEBUG: LineGraphicsItem.update_from_object called for Line {self.line.id}"
            )
            logger.debug(
                f"DEBUG: Before update_from_object: P1=({old_x1}, {old_y1}), P2=({old_x2}, {old_y2})"
            )

            # Update base properties (color, style, etc.)
            super().update_from_object()

            # CRITICAL: Always ensure the line's position is at (0,0)
            # This ensures that the line's endpoints are in scene coordinates
            # and the line doesn't move as a unit
            self.setPos(0, 0)

            # Log the update
            logger.debug(
                f"Updating LineGraphicsItem from Line object: P1=({self.line.x1}, {self.line.y1}), P2=({self.line.x2}, {self.line.y2})"
            )

            # Check if endpoints changed
            if old_x1 != self.line.x1 or old_y1 != self.line.y1:
                logger.debug(
                    f"DEBUG: Endpoint 1 changed from ({old_x1}, {old_y1}) to ({self.line.x1}, {self.line.y1})"
                )
            if old_x2 != self.line.x2 or old_y2 != self.line.y2:
                logger.debug(
                    f"DEBUG: Endpoint 2 changed from ({old_x2}, {old_y2}) to ({self.line.x2}, {self.line.y2})"
                )

            # Force a redraw to reflect any changes in endpoint positions
            self.prepareGeometryChange()

            # Update the item
            self.update()
            logger.debug("DEBUG: LineGraphicsItem.update_from_object completed")
        finally:
            self.updating = False

    def update_object_from_item(self) -> None:
        """Update the geometric object's properties from the item."""
        # Prevent recursive updates
        if self.updating:
            logger.debug(
                "DEBUG: LineGraphicsItem.update_object_from_item skipped due to recursive update prevention"
            )
            return

        self.updating = True

        try:
            # Update base properties
            super().update_object_from_item()

            # Get the position delta
            dx = self.pos().x()
            dy = self.pos().y()

            # If the line has been moved (not at origin), move its endpoints too
            if dx != 0 or dy != 0:
                # Log before movement
                logger.debug(f"DEBUG: Line {self.line.id} moving by ({dx}, {dy})")
                logger.debug(
                    f"DEBUG: Before update_object_from_item: P1=({self.line.x1}, {self.line.y1}), P2=({self.line.x2}, {self.line.y2})"
                )

                # Create a copy of the line to modify
                from copy import deepcopy

                modified_line = deepcopy(self.line)

                # Move the entire line by updating both endpoints
                # This is only used when dragging the whole line, not when dragging endpoints
                modified_line.x1 += dx
                modified_line.y1 += dy
                modified_line.x2 += dx
                modified_line.y2 += dy
                logger.debug(f"DEBUG: Moving entire line by ({dx}, {dy})")

                # Update the actual line
                self.line.x1 = modified_line.x1
                self.line.y1 = modified_line.y1
                self.line.x2 = modified_line.x2
                self.line.y2 = modified_line.y2

                # Log after movement
                logger.debug(
                    f"DEBUG: After update_object_from_item: P1=({self.line.x1}, {self.line.y1}), P2=({self.line.x2}, {self.line.y2})"
                )

                # Reset the line position to origin
                self.setPos(0, 0)
        finally:
            self.updating = False

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Handle item changes.

        Args:
            change: Type of change
            value: New value

        Returns:
            Modified value
        """
        if (
            change == QGraphicsItem.GraphicsItemChange.ItemPositionChange
            and self.scene()
        ):
            # When the line is moved, we need to move its endpoints too
            # This is handled in update_object_from_item
            pass

        return super().itemChange(change, value)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Get line points
        x1, y1 = self.line.x1, self.line.y1
        x2, y2 = self.line.x2, self.line.y2

        # Set up painter
        pen = QPen(self.line.style.stroke_color, self.line.style.stroke_width)
        pen.setStyle(self.line.style.stroke_style)
        painter.setPen(pen)

        # Draw line based on line type
        if self.line.line_type == LineType.SEGMENT:
            # Draw line segment
            painter.drawLine(QLineF(x1, y1, x2, y2))
        elif self.line.line_type == LineType.RAY:
            # Draw ray (from p1 extending through p2)
            # Calculate direction vector
            dx = x2 - x1
            dy = y2 - y1

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of p2
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = x1 + dx * extension
            extended_y = y1 + dy * extension

            # Draw the ray
            painter.drawLine(QLineF(x1, y1, extended_x, extended_y))
        else:  # LineType.INFINITE
            # Draw infinite line (extending in both directions)
            # Calculate direction vector
            dx = x2 - x1
            dy = y2 - y1

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = x1 - dx * extension
            extended_y1 = y1 - dy * extension
            extended_x2 = x2 + dx * extension
            extended_y2 = y2 + dy * extension

            # Draw the infinite line
            painter.drawLine(QLineF(extended_x1, extended_y1, extended_x2, extended_y2))

        # Draw selection handles if selected
        if self.isSelected():
            self.paint_selection_handles(painter)

    def paint_selection_handles(self, painter: QPainter) -> None:
        """Paint selection handles for the line endpoints.

        Args:
            painter: Painter to use
        """
        # Set up painter with thicker border for better visibility
        painter.setPen(QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(Qt.GlobalColor.white))

        # Draw handles for both endpoints
        for handle in [self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            rect = self.handle_rect(handle)
            if not rect.isEmpty():
                if handle == self.hover_handle:
                    # Highlight hovered handle
                    painter.setBrush(QBrush(Qt.GlobalColor.yellow))
                    painter.drawRect(rect)
                    painter.setBrush(QBrush(Qt.GlobalColor.white))
                elif handle in self.selected_handles:
                    # Highlight selected handle
                    painter.setBrush(QBrush(Qt.GlobalColor.red))
                    painter.drawRect(rect)
                    painter.setBrush(QBrush(Qt.GlobalColor.white))
                else:
                    # Normal handle
                    painter.drawRect(rect)

    def handle_at(self, point: QPointF) -> Optional[int]:
        """Get the handle at the given point.

        Args:
            point: Point in item coordinates

        Returns:
            Handle index or None if no handle at the point
        """
        # Lines have two handles (start and end points)
        for handle in [self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            if self.handle_rect(handle).contains(point):
                return handle

        return None

    def handle_rect(self, handle: int) -> QRectF:
        """Get the rectangle for the given handle.

        Args:
            handle: Handle index

        Returns:
            Rectangle for the handle in item coordinates
        """
        # Lines have two handles (start and end points)
        if handle == self.HANDLE_TOP_LEFT:
            # Start point
            x, y = self.line.x1, self.line.y1
            return QRectF(
                x - self.HANDLE_SIZE / 2,
                y - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
        elif handle == self.HANDLE_BOTTOM_RIGHT:
            # End point
            x, y = self.line.x2, self.line.y2
            return QRectF(
                x - self.HANDLE_SIZE / 2,
                y - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )

        return QRectF()

    def handle_cursor(self, handle: int) -> Qt.CursorShape:
        """Get the cursor shape for the given handle.

        Args:
            handle: Handle index

        Returns:
            Cursor shape for the handle
        """
        # Lines have two handles (start and end points)
        if handle in [self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            return Qt.CursorShape.SizeAllCursor

        return Qt.CursorShape.ArrowCursor

    def move_handle(self, handle: int, point: QPointF) -> None:
        """Move the given handle to the given point.

        Args:
            handle: Handle index
            point: New position in item coordinates
        """
        # Prevent recursive updates
        if self.updating:
            logger.debug(
                "DEBUG: LineGraphicsItem.move_handle skipped due to recursive update prevention"
            )
            return

        self.updating = True

        try:
            # Convert point to scene coordinates
            scene_point = self.mapToScene(point)
            new_x = scene_point.x()
            new_y = scene_point.y()

            # Log handle movement
            handle_name = (
                "P1 (TOP_LEFT)"
                if handle == self.HANDLE_TOP_LEFT
                else "P2 (BOTTOM_RIGHT)"
                if handle == self.HANDLE_BOTTOM_RIGHT
                else f"Unknown ({handle})"
            )
            logger.debug(
                f"DEBUG: LineGraphicsItem.move_handle called for Line {self.line.id} handle {handle_name} to ({new_x}, {new_y})"
            )

            # Store original values for debugging
            orig_x1, orig_y1 = self.line.x1, self.line.y1
            orig_x2, orig_y2 = self.line.x2, self.line.y2
            logger.debug(
                f"DEBUG: Before move_handle: P1=({orig_x1}, {orig_y1}), P2=({orig_x2}, {orig_y2})"
            )

            # Create a new line with the same properties as the current line
            from copy import deepcopy

            new_line = deepcopy(self.line)

            # Store which endpoint is being moved in the line's metadata
            # This will be used by the properties panel to only update the relevant fields
            if "metadata" not in new_line.__dict__:
                new_line.metadata = {}

            # Update only the endpoint that's being moved
            if handle == self.HANDLE_TOP_LEFT:
                new_line.x1 = new_x
                new_line.y1 = new_y
                new_line.metadata["moved_endpoint"] = 1  # Endpoint 1 was moved
                logger.debug(
                    f"  New line: P1=({new_line.x1}, {new_line.y1}), P2=({new_line.x2}, {new_line.y2})"
                )
            elif handle == self.HANDLE_BOTTOM_RIGHT:
                new_line.x2 = new_x
                new_line.y2 = new_y
                new_line.metadata["moved_endpoint"] = 2  # Endpoint 2 was moved
                logger.debug(
                    f"  New line: P1=({new_line.x1}, {new_line.y1}), P2=({new_line.x2}, {new_line.y2})"
                )

            # Update our internal line object first
            self.line = new_line

            # Force a redraw to reflect changes
            self.prepareGeometryChange()
            self.update()

            # Find the canvas through the scene's views
            if hasattr(self, "scene") and self.scene():
                for view in self.scene().views():
                    if hasattr(view, "update_object"):
                        logger.debug("  Updating canvas with new line")
                        view.update_object(new_line)
                        break
                else:
                    # If we get here, we didn't find a view with update_object
                    logger.error("  Cannot find canvas in scene views")

            # Don't call any other update methods - let the explorer handle it
            logger.debug(
                f"DEBUG: LineGraphicsItem.move_handle completed for Line {self.line.id}"
            )
        finally:
            self.updating = False


class CircleGraphicsItem(GeometricGraphicsItem):
    """Graphics item for a circle."""

    def __init__(self, circle: Circle) -> None:
        """Initialize a circle graphics item.

        Args:
            circle: The circle this item represents
        """
        super().__init__(circle)
        self.circle = circle
        self.updating = False  # Flag to prevent recursive updates
        self.update_from_object()

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the item.

        Returns:
            Bounding rectangle in item coordinates
        """
        # Get circle properties
        cx, cy = self.circle.center.x, self.circle.center.y
        r = self.circle.radius

        # Calculate bounding rect
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)

        # Add margin for line width and selection handles
        margin = max(self.HANDLE_SIZE / 2, self.circle.style.stroke_width / 2)
        rect.adjust(-margin, -margin, margin, margin)

        return rect

    def update_from_object(self) -> None:
        """Update the item's geometry and appearance from the geometric object."""
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Update base properties
            super().update_from_object()

            # Update position (circles are drawn in scene coordinates)
            self.setPos(0, 0)

            # Log the update
            logger.debug(
                f"Updating CircleGraphicsItem from Circle object: center=({self.circle.center_x}, {self.circle.center_y}), radius={self.circle.radius}"
            )

            # Force a redraw to reflect any changes in center position or radius
            self.prepareGeometryChange()

            # Update the item
            self.update()
        finally:
            self.updating = False

    def update_object_from_item(self) -> None:
        """Update the geometric object's properties from the item."""
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Update base properties
            super().update_object_from_item()

            # Log the update
            logger.debug(
                f"Updating Circle object from CircleGraphicsItem: center=({self.circle.center_x}, {self.circle.center_y}), radius={self.circle.radius}"
            )

            # Circles are updated through handle movement
        finally:
            self.updating = False

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Get circle properties
        cx, cy = self.circle.center_x, self.circle.center_y
        r = self.circle.radius

        # Set up painter
        pen = QPen(self.circle.style.stroke_color, self.circle.style.stroke_width)
        pen.setStyle(self.circle.style.stroke_style)
        painter.setPen(pen)

        brush = QBrush(self.circle.style.fill_color)
        brush.setStyle(self.circle.style.fill_style)
        painter.setBrush(brush)

        # Draw circle
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Draw selection handles if selected
        if self.isSelected():
            super().paint(painter, option, widget)

    def handle_at(self, point: QPointF) -> Optional[int]:
        """Get the handle at the given point.

        Args:
            point: Point in item coordinates

        Returns:
            Handle index or None if no handle at the point
        """
        # Circles have 5 handles (center, top, right, bottom, left)
        for handle in [
            self.HANDLE_MIDDLE_MIDDLE,
            self.HANDLE_TOP_MIDDLE,
            self.HANDLE_MIDDLE_RIGHT,
            self.HANDLE_BOTTOM_MIDDLE,
            self.HANDLE_MIDDLE_LEFT,
        ]:
            if self.handle_rect(handle).contains(point):
                return handle

        return None

    def handle_rect(self, handle: int) -> QRectF:
        """Get the rectangle for the given handle.

        Args:
            handle: Handle index

        Returns:
            Rectangle for the handle in item coordinates
        """
        # Get circle properties
        cx, cy = self.circle.center_x, self.circle.center_y
        r = self.circle.radius

        # Circles have 5 handles (center, top, right, bottom, left)
        if handle == self.HANDLE_MIDDLE_MIDDLE:
            # Center
            return QRectF(
                cx - self.HANDLE_SIZE / 2,
                cy - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
        elif handle == self.HANDLE_TOP_MIDDLE:
            # Top
            return QRectF(
                cx - self.HANDLE_SIZE / 2,
                cy - r - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
        elif handle == self.HANDLE_MIDDLE_RIGHT:
            # Right
            return QRectF(
                cx + r - self.HANDLE_SIZE / 2,
                cy - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
        elif handle == self.HANDLE_BOTTOM_MIDDLE:
            # Bottom
            return QRectF(
                cx - self.HANDLE_SIZE / 2,
                cy + r - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
        elif handle == self.HANDLE_MIDDLE_LEFT:
            # Left
            return QRectF(
                cx - r - self.HANDLE_SIZE / 2,
                cy - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )

        return QRectF()

    def handle_cursor(self, handle: int) -> Qt.CursorShape:
        """Get the cursor shape for the given handle.

        Args:
            handle: Handle index

        Returns:
            Cursor shape for the handle
        """
        # Circles have 5 handles (center, top, right, bottom, left)
        if handle == self.HANDLE_MIDDLE_MIDDLE:
            # Center
            return Qt.CursorShape.SizeAllCursor
        elif handle in [self.HANDLE_TOP_MIDDLE, self.HANDLE_BOTTOM_MIDDLE]:
            # Top, Bottom
            return Qt.CursorShape.SizeVerCursor
        elif handle in [self.HANDLE_MIDDLE_LEFT, self.HANDLE_MIDDLE_RIGHT]:
            # Left, Right
            return Qt.CursorShape.SizeHorCursor

        return Qt.CursorShape.ArrowCursor

    def move_handle(self, handle: int, point: QPointF) -> None:
        """Move the given handle to the given point.

        Args:
            handle: Handle index
            point: New position in item coordinates
        """
        # Prevent recursive updates
        if self.updating:
            return

        self.updating = True

        try:
            # Get circle properties
            cx, cy = self.circle.center_x, self.circle.center_y

            # Circles have 5 handles (center, top, right, bottom, left)
            if handle == self.HANDLE_MIDDLE_MIDDLE:
                # Move center
                old_x, old_y = self.circle.center_x, self.circle.center_y
                new_x, new_y = point.x(), point.y()
                logger.debug(
                    f"Moving circle {self.circle.id} center from ({old_x}, {old_y}) to ({new_x}, {new_y})"
                )
                self.circle.center_x = new_x
                self.circle.center_y = new_y
            elif handle == self.HANDLE_TOP_MIDDLE:
                # Resize from top
                old_radius = self.circle.radius
                new_radius = abs(point.y() - cy)
                logger.debug(
                    f"Resizing circle {self.circle.id} radius from {old_radius} to {new_radius} (top)"
                )
                self.circle.radius = new_radius
            elif handle == self.HANDLE_MIDDLE_RIGHT:
                # Resize from right
                old_radius = self.circle.radius
                new_radius = abs(point.x() - cx)
                logger.debug(
                    f"Resizing circle {self.circle.id} radius from {old_radius} to {new_radius} (right)"
                )
                self.circle.radius = new_radius
            elif handle == self.HANDLE_BOTTOM_MIDDLE:
                # Resize from bottom
                old_radius = self.circle.radius
                new_radius = abs(point.y() - cy)
                logger.debug(
                    f"Resizing circle {self.circle.id} radius from {old_radius} to {new_radius} (bottom)"
                )
                self.circle.radius = new_radius
            elif handle == self.HANDLE_MIDDLE_LEFT:
                # Resize from left
                old_radius = self.circle.radius
                new_radius = abs(point.x() - cx)
                logger.debug(
                    f"Resizing circle {self.circle.id} radius from {old_radius} to {new_radius} (left)"
                )
                self.circle.radius = new_radius

            # Force a redraw
            self.prepareGeometryChange()
            self.update()
            logger.debug(f"Circle {self.circle.id} updated after handle move")
        finally:
            self.updating = False


class PolygonGraphicsItem(GeometricGraphicsItem):
    """Graphics item for a polygon."""

    def __init__(self, polygon: Polygon) -> None:
        """Initialize a polygon graphics item.

        Args:
            polygon: Polygon to represent
        """
        # Call the parent class constructor with the polygon object
        super().__init__(geometric_object=polygon)

        # Store a reference to the polygon
        self.polygon = polygon

        # Create a QPolygonF for the shape
        self.polygon_shape = QPolygonF()

        # Update the geometry
        self.update_geometry()

    def update_geometry(self) -> None:
        """Update the geometry of the item."""
        # Clear the existing polygon shape
        self.polygon_shape = QPolygonF()

        # Add all vertices to the polygon shape
        for vertex in self.polygon.vertices:
            self.polygon_shape.append(QPointF(vertex.x, vertex.y))

        # Update the bounding rect
        self.prepareGeometryChange()

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the item.

        Returns:
            Bounding rectangle
        """
        # Add padding for stroke width
        padding = self.polygon.style.stroke_width / 2
        rect = self.polygon_shape.boundingRect()
        return rect.adjusted(-padding, -padding, padding, padding)

    def shape(self) -> QPainterPath:
        """Get the shape of the item for collision detection.

        Returns:
            Shape path
        """
        path = QPainterPath()
        path.addPolygon(self.polygon_shape)
        return path

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Set up pen and brush based on style
        pen = QPen(self.polygon.style.stroke_color)
        pen.setWidthF(self.polygon.style.stroke_width)
        pen.setStyle(self.polygon.style.stroke_style)

        brush = QBrush(self.polygon.style.fill_color)
        brush.setStyle(self.polygon.style.fill_style)

        # Draw the polygon
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPolygon(self.polygon_shape)

        # Draw selection handles if selected
        if self.isSelected():
            self.paint_selection_handles(painter)

    def paint_selection_handles(self, painter: QPainter) -> None:
        """Paint selection handles for the polygon.

        Args:
            painter: Painter to use
        """
        # Set up pen and brush for handles
        painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(Qt.GlobalColor.blue, Qt.BrushStyle.SolidPattern))

        # Draw a handle at each vertex
        for vertex in self.polygon.vertices:
            handle_rect = QRectF(
                vertex.x - self.HANDLE_SIZE / 2,
                vertex.y - self.HANDLE_SIZE / 2,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE,
            )
            painter.drawRect(handle_rect)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Handle item changes.

        Args:
            change: Type of change
            value: New value

        Returns:
            Modified value
        """
        if (
            change == QGraphicsItem.GraphicsItemChange.ItemPositionChange
            and self.scene()
        ):
            # Get the position delta
            old_pos = self.pos()
            new_pos = value
            dx = new_pos.x() - old_pos.x()
            dy = new_pos.y() - old_pos.y()

            # Move all vertices
            for vertex in self.polygon.vertices:
                vertex.move_by(dx, dy)

            # Update geometry
            self.update_geometry()

            # Notify scene of change
            if self.scene():
                self.scene().update()

        return super().itemChange(change, value)


class TextGraphicsItem(GeometricGraphicsItem):
    """Graphics item for a text label."""

    def __init__(self, text: Text) -> None:
        """Initialize a text graphics item.

        Args:
            text: The text object this item represents
        """
        super().__init__(text)
        self.text = text
        self.update_from_object()

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the item.

        Returns:
            Bounding rectangle in item coordinates
        """
        # Create a font to measure the text
        font = QFont(self.text.style.font_family, self.text.style.font_size)

        # Set font style (bold, italic, etc.)
        if self.text.style.font_style & 1:  # Bold
            font.setBold(True)
        if self.text.style.font_style & 2:  # Italic
            font.setItalic(True)

        # Measure the text
        metrics = QFontMetricsF(font)
        text_rect = metrics.boundingRect(self.text.content)

        # Add margin for selection handles
        margin = self.HANDLE_SIZE / 2
        return text_rect.adjusted(-margin, -margin, margin, margin)

    def update_from_object(self) -> None:
        """Update the item's geometry and appearance from the geometric object."""
        # Update base properties
        super().update_from_object()

        # Update position
        self.setPos(self.text.position.x, self.text.position.y)

        # Update the item
        self.update()

    def update_object_from_item(self) -> None:
        """Update the geometric object's properties from the item."""
        # Update base properties
        super().update_object_from_item()

        # Update position
        self.text.position.x = self.pos().x()
        self.text.position.y = self.pos().y()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Paint the item.

        Args:
            painter: Painter to use
            option: Style options
            widget: Widget being painted on
        """
        # Create a font for the text
        font = QFont(self.text.style.font_family, self.text.style.font_size)

        # Set font style (bold, italic, etc.)
        if self.text.style.font_style & 1:  # Bold
            font.setBold(True)
        if self.text.style.font_style & 2:  # Italic
            font.setItalic(True)

        # Set up painter
        painter.setFont(font)
        painter.setPen(QPen(self.text.style.stroke_color))

        # Draw text
        painter.drawText(0, 0, self.text.content)

        # Draw selection handles if selected
        if self.isSelected():
            super().paint(painter, option, widget)


class GraphicsItemFactory:
    """Factory class for creating graphics items from geometric objects."""

    @staticmethod
    def create_item(obj: GeometricObject) -> Optional[GeometricGraphicsItem]:
        """Create a graphics item for the given geometric object.

        Args:
            obj: Geometric object to create an item for

        Returns:
            Graphics item for the object, or None if the object type is not supported
        """
        if isinstance(obj, Point):
            return PointGraphicsItem(obj)
        elif isinstance(obj, Line):
            return LineGraphicsItem(obj)
        elif isinstance(obj, Circle):
            return CircleGraphicsItem(obj)
        elif isinstance(obj, Polygon):
            return PolygonGraphicsItem(obj)
        elif isinstance(obj, Text):
            return TextGraphicsItem(obj)
        else:
            logger.warning(f"Unsupported geometric object type: {type(obj).__name__}")
            return None

    @staticmethod
    def create_items(objects: List[GeometricObject]) -> List[GeometricGraphicsItem]:
        """Create graphics items for the given geometric objects.

        Args:
            objects: Geometric objects to create items for

        Returns:
            List of graphics items for the objects
        """
        items = []
        for obj in objects:
            item = GraphicsItemFactory.create_item(obj)
            if item is not None:
                items.append(item)
        return items
