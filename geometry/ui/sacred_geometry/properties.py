"""Properties panel for the Sacred Geometry Explorer.

This module contains the properties panel for the Sacred Geometry Explorer,
which provides the interface for viewing and editing object properties.
"""

from typing import List, Dict, Any, Optional, Tuple, Set, Union, Callable
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QPushButton,
    QColorDialog,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QSpacerItem,
)
from PyQt6.QtGui import QColor, QPalette, QFont
from loguru import logger

from geometry.ui.sacred_geometry.model import GeometricObject, Point, Line, Circle, Style, ObjectType, LineType


class PropertyEditor:
    """Base class for property editors.

    This class provides the interface for editing a specific property of an object.
    """

    def __init__(self, property_name: str, label: str) -> None:
        """Initialize the property editor.

        Args:
            property_name: Name of the property to edit
            label: Label to display for the property
        """
        self.property_name = property_name
        self.label = label
        self.widget = None
        self.objects = []

    def create_widget(self) -> QWidget:
        """Create the widget for editing the property.

        Returns:
            Widget for editing the property
        """
        # Base implementation returns a label
        self.widget = QLabel("Not editable")
        return self.widget

    def set_objects(self, objects: List[GeometricObject]) -> None:
        """Set the objects to edit properties for.

        Args:
            objects: Objects to edit properties for
        """
        self.objects = objects
        self.update_widget()

    def update_widget(self) -> None:
        """Update the widget based on the current objects."""
        # Base implementation does nothing
        pass

    def get_row_widgets(self) -> Tuple[str, QWidget]:
        """Get the label and widget for adding to a form layout.

        Returns:
            Tuple of (label, widget)
        """
        return self.label, self.create_widget()


class TextPropertyEditor(PropertyEditor):
    """Editor for text properties."""

    def __init__(self, property_name: str, label: str) -> None:
        """Initialize the text property editor.

        Args:
            property_name: Name of the property to edit
            label: Label to display for the property
        """
        super().__init__(property_name, label)
        self.text_edit = None
        self.updating = False

    def create_widget(self) -> QWidget:
        """Create the widget for editing the property.

        Returns:
            Widget for editing the property
        """
        self.text_edit = QLineEdit()
        self.text_edit.editingFinished.connect(self._on_text_changed)
        self.widget = self.text_edit
        return self.widget

    def update_widget(self) -> None:
        """Update the widget based on the current objects."""
        if not self.text_edit or not self.objects:
            return

        # Set updating flag to prevent feedback loop
        self.updating = True

        # Get property values
        values = set(getattr(obj, self.property_name, "") for obj in self.objects)

        # Set text
        if len(values) == 1:
            # All objects have the same value
            self.text_edit.setText(str(next(iter(values))))
            self.text_edit.setPlaceholderText("")
        else:
            # Objects have different values
            self.text_edit.setText("")
            self.text_edit.setPlaceholderText("Multiple values")

        # Clear updating flag
        self.updating = False

    def _on_text_changed(self) -> None:
        """Handle text changed event."""
        if self.updating or not self.text_edit or not self.objects:
            return

        # Get new value
        new_value = self.text_edit.text()

        # Update objects
        for obj in self.objects:
            if hasattr(obj, self.property_name):
                setattr(obj, self.property_name, new_value)

        # Emit property changed signal
        if hasattr(self.widget.parent(), "property_changed"):
            for obj in self.objects:
                self.widget.parent().property_changed.emit(obj.id, self.property_name, new_value)


class NumberPropertyEditor(PropertyEditor):
    """Editor for numeric properties."""

    def __init__(self, property_name: str, label: str, min_value: float = -1000, max_value: float = 1000, decimals: int = 2, step: float = 1.0) -> None:
        """Initialize the number property editor.

        Args:
            property_name: Name of the property to edit
            label: Label to display for the property
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            decimals: Number of decimal places to display
            step: Step size for the spin box
        """
        super().__init__(property_name, label)
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals
        self.step = step
        self.spin_box = None
        self.updating = False

        # Custom getter and setter for properties that need special handling
        self.get_property_value = None
        self.set_property_value = None

    def create_widget(self) -> QWidget:
        """Create the widget for editing the property.

        Returns:
            Widget for editing the property
        """
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setRange(self.min_value, self.max_value)
        self.spin_box.setDecimals(self.decimals)
        self.spin_box.setSingleStep(self.step)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        self.widget = self.spin_box
        return self.widget

    def update_widget(self) -> None:
        """Update the widget based on the current objects."""
        if not self.spin_box or not self.objects:
            return

        # Set updating flag to prevent feedback loop
        self.updating = True

        # Get property values
        values = set()
        for obj in self.objects:
            # Use custom getter if provided
            if self.get_property_value is not None:
                values.add(self.get_property_value(obj))
            # Handle nested properties (e.g., 'endpoint1_x')
            elif '.' in self.property_name:
                parts = self.property_name.split('.')
                value = obj
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        value = 0
                        break
                values.add(value)
            else:
                # Direct property
                values.add(getattr(obj, self.property_name, 0))

        # Set value
        if len(values) == 1:
            # All objects have the same value
            self.spin_box.setValue(next(iter(values)))
            self.spin_box.setSpecialValueText("")
        else:
            # Objects have different values
            self.spin_box.setValue(self.min_value)
            self.spin_box.setSpecialValueText("Multiple values")

        # Clear updating flag
        self.updating = False

    def _on_value_changed(self, value: float) -> None:
        """Handle value changed event.

        Args:
            value: New value
        """
        if self.updating or not self.spin_box or not self.objects:
            return

        # Log the property change
        logger.debug(f"Property changing: {self.property_name} = {value} for {len(self.objects)} objects")

        # Update objects
        for obj in self.objects:
            # Use custom setter if provided
            if self.set_property_value is not None:
                self.set_property_value(obj, value)
            # Handle nested properties (e.g., 'endpoint1_x')
            elif '.' in self.property_name:
                parts = self.property_name.split('.')
                target = obj
                for part in parts[:-1]:  # All parts except the last one
                    if hasattr(target, part):
                        target = getattr(target, part)
                    else:
                        logger.warning(f"Object {obj.__class__.__name__} {obj.id} does not have property {part}")
                        break
                else:  # This executes if the for loop completes without a break
                    if hasattr(target, parts[-1]):
                        logger.debug(f"Setting {obj.__class__.__name__} {obj.id} {self.property_name} = {value}")
                        setattr(target, parts[-1], value)
                    else:
                        logger.warning(f"Object {obj.__class__.__name__} {obj.id} does not have property {parts[-1]}")
            else:
                # Direct property
                if hasattr(obj, self.property_name):
                    logger.debug(f"Setting {obj.__class__.__name__} {obj.id} {self.property_name} = {value}")
                    setattr(obj, self.property_name, value)

        # Emit property changed signal
        if hasattr(self.widget.parent(), "property_changed"):
            for obj in self.objects:
                logger.debug(f"Emitting property_changed signal for {obj.__class__.__name__} {obj.id}")
                self.widget.parent().property_changed.emit(obj.id, self.property_name, value)


class BooleanPropertyEditor(PropertyEditor):
    """Editor for boolean properties."""

    def __init__(self, property_name: str, label: str) -> None:
        """Initialize the boolean property editor.

        Args:
            property_name: Name of the property to edit
            label: Label to display for the property
        """
        super().__init__(property_name, label)
        self.check_box = None
        self.updating = False

    def create_widget(self) -> QWidget:
        """Create the widget for editing the property.

        Returns:
            Widget for editing the property
        """
        self.check_box = QCheckBox(self.label)
        self.check_box.stateChanged.connect(self._on_state_changed)
        self.widget = self.check_box
        return self.widget

    def get_row_widgets(self) -> Tuple[str, QWidget]:
        """Get the label and widget for adding to a form layout.

        Returns:
            Tuple of (label, widget)
        """
        # For checkboxes, we don't need a separate label
        return "", self.create_widget()

    def update_widget(self) -> None:
        """Update the widget based on the current objects."""
        if not self.check_box or not self.objects:
            return

        # Set updating flag to prevent feedback loop
        self.updating = True

        # Get property values
        values = set(getattr(obj, self.property_name, False) for obj in self.objects)

        # Set state
        if len(values) == 1:
            # All objects have the same value
            self.check_box.setChecked(next(iter(values)))
            self.check_box.setText(self.label)
        else:
            # Objects have different values - use tristate
            self.check_box.setTristate(True)
            self.check_box.setCheckState(Qt.CheckState.PartiallyChecked)
            self.check_box.setText(f"{self.label} (Mixed)")

        # Clear updating flag
        self.updating = False

    def _on_state_changed(self, state: int) -> None:
        """Handle state changed event.

        Args:
            state: New state
        """
        if self.updating or not self.check_box or not self.objects:
            return

        # Convert state to boolean
        new_value = state == Qt.CheckState.Checked.value

        # Update objects
        for obj in self.objects:
            if hasattr(obj, self.property_name):
                setattr(obj, self.property_name, new_value)

        # Emit property changed signal
        if hasattr(self.widget.parent(), "property_changed"):
            for obj in self.objects:
                self.widget.parent().property_changed.emit(obj.id, self.property_name, new_value)

        # Reset tristate
        self.check_box.setTristate(False)


class PropertiesPanel(QWidget):
    """Panel for viewing and editing object properties.

    This class provides the interface for viewing and editing the properties
    of selected geometric objects.
    """

    property_changed = pyqtSignal(str, str, object)  # object_id, property_name, new_value

    def __init__(self, parent=None) -> None:
        """Initialize the properties panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(10)
        scroll_area.setWidget(self.content_widget)

        # Add placeholder label
        self.placeholder_label = QLabel("No objects selected")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.placeholder_label)

        # Add stretch to push content to the top
        self.content_layout.addStretch()

        # Current objects
        self.current_objects = []

        # Property editors
        self.property_editors = {}

        logger.debug("PropertiesPanel initialized")

    def set_objects(self, objects: List[GeometricObject]) -> None:
        """Set the objects to display properties for.

        Args:
            objects: List of objects to display properties for
        """
        # Check if we're already showing these objects
        if self.current_objects == objects:
            # Just update the existing property editors instead of recreating the panel
            for editor in self.property_editors.values():
                if hasattr(editor, 'update_widget'):
                    editor.update_widget()
            logger.debug(f"Updated existing property editors for {len(objects)} objects")
            return

        # Clear current content
        self.clear_content()

        # Store current objects
        self.current_objects = objects

        # If no objects, show placeholder
        if not objects:
            self.placeholder_label.setVisible(True)
            return

        # Hide placeholder
        self.placeholder_label.setVisible(False)

        # If single object, show all properties
        if len(objects) == 1:
            self._create_single_object_ui(objects[0])
        else:
            # If multiple objects, show common properties
            self._create_multiple_objects_ui(objects)

        logger.debug(f"Properties panel updated with {len(objects)} objects")

    def clear_content(self) -> None:
        """Clear the content of the properties panel."""
        # Remove all widgets except the placeholder label
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.placeholder_label:
                item.widget().deleteLater()

        # Clear property editors
        self.property_editors = {}

        # Show placeholder
        self.placeholder_label.setVisible(True)

    def _create_single_object_ui(self, obj: GeometricObject) -> None:
        """Create UI for a single object.

        Args:
            obj: Object to create UI for
        """
        # Create group box for common properties
        common_group = QGroupBox("Common Properties")
        common_layout = QFormLayout(common_group)

        # Add common property editors
        self._add_property_editor(common_layout, TextPropertyEditor("name", "Name"), [obj])
        self._add_property_editor(common_layout, BooleanPropertyEditor("visible", "Visible"), [obj])
        self._add_property_editor(common_layout, BooleanPropertyEditor("locked", "Locked"), [obj])

        # Add common group to layout
        self.content_layout.insertWidget(0, common_group)

        # Create group box for object-specific properties
        if isinstance(obj, Point):
            self._create_point_ui(obj)
        elif isinstance(obj, Line):
            self._create_line_ui(obj)
        elif isinstance(obj, Circle):
            self._create_circle_ui(obj)

    def _create_point_ui(self, point: Point) -> None:
        """Create UI for a point.

        Args:
            point: Point to create UI for
        """
        # Create group box for point properties
        point_group = QGroupBox("Point Properties")
        point_layout = QFormLayout(point_group)

        # Add point property editors
        self._add_property_editor(point_layout, NumberPropertyEditor("x", "X"), [point])
        self._add_property_editor(point_layout, NumberPropertyEditor("y", "Y"), [point])

        # Add point group to layout
        self.content_layout.insertWidget(1, point_group)

    def _create_line_ui(self, line: Line) -> None:
        """Create UI for a line.

        Args:
            line: Line to create UI for
        """
        # Create group box for line properties
        line_group = QGroupBox("Line Properties")
        line_layout = QFormLayout(line_group)

        # Add line property editors using direct property names
        self._add_property_editor(line_layout, NumberPropertyEditor("endpoint1_x", "Start X"), [line])
        self._add_property_editor(line_layout, NumberPropertyEditor("endpoint1_y", "Start Y"), [line])
        self._add_property_editor(line_layout, NumberPropertyEditor("endpoint2_x", "End X"), [line])
        self._add_property_editor(line_layout, NumberPropertyEditor("endpoint2_y", "End Y"), [line])

        # Add line type selector
        line_type_combo = QComboBox()
        line_type_combo.addItem("Segment", LineType.SEGMENT)
        line_type_combo.addItem("Ray", LineType.RAY)
        line_type_combo.addItem("Infinite", LineType.INFINITE)

        # Set current line type
        for i in range(line_type_combo.count()):
            if line_type_combo.itemData(i) == line.line_type:
                line_type_combo.setCurrentIndex(i)
                break

        # Connect line type change signal
        line_type_combo.currentIndexChanged.connect(
            lambda: self._on_line_type_changed(line, line_type_combo.currentData())
        )

        line_layout.addRow("Line Type:", line_type_combo)

        # Add style properties
        style_group = QGroupBox("Style")
        style_layout = QFormLayout(style_group)

        # Add stroke width editor
        stroke_width_editor = NumberPropertyEditor("style.stroke_width", "Stroke Width", min_value=0.1, max_value=10.0, step=0.1)
        self._add_property_editor(style_layout, stroke_width_editor, [line])

        # Add style group to layout
        line_layout.addRow(style_group)

        # Add line group to layout
        self.content_layout.insertWidget(1, line_group)

    def _create_endpoint_property_editor(self, line: Line, endpoint: int, coord: str, label: str) -> QDoubleSpinBox:
        """Create a property editor for a line endpoint coordinate.

        Args:
            line: Line to edit
            endpoint: Endpoint number (1 or 2)
            coord: Coordinate to edit ('x' or 'y')
            label: Label for the editor

        Returns:
            Spin box for editing the coordinate
        """
        # Create a spin box
        spin_box = QDoubleSpinBox()
        spin_box.setRange(-1000, 1000)
        spin_box.setDecimals(2)
        spin_box.setSingleStep(1.0)

        # Get the current value
        x, y = line.get_endpoint(endpoint)
        current_value = x if coord == 'x' else y
        spin_box.setValue(current_value)

        # Connect value changed signal
        spin_box.valueChanged.connect(
            lambda value: self._on_endpoint_changed(line, endpoint, coord, value)
        )

        return spin_box

    def _on_endpoint_changed(self, line: Line, endpoint: int, coord: str, value: float) -> None:
        """Handle endpoint coordinate change.

        Args:
            line: Line to update
            endpoint: Endpoint number (1 or 2)
            coord: Coordinate to edit ('x' or 'y')
            value: New value
        """
        # Get current endpoint coordinates
        x, y = line.get_endpoint(endpoint)

        # Update the appropriate coordinate
        if coord == 'x':
            line.move_endpoint(endpoint, value, y)
        else:  # coord == 'y'
            line.move_endpoint(endpoint, x, value)

        # Emit property changed signal
        property_name = f"endpoint{endpoint}_{coord}"
        self.property_changed.emit(line.id, property_name, value)

    def _on_line_type_changed(self, line: Line, line_type: LineType) -> None:
        """Handle line type changed event.

        Args:
            line: Line to update
            line_type: New line type
        """
        line.line_type = line_type

        # Emit property changed signal
        if hasattr(self, "property_changed"):
            self.property_changed.emit(line.id, "line_type", line_type)

    def _create_circle_ui(self, circle: Circle) -> None:
        """Create UI for a circle.

        Args:
            circle: Circle to create UI for
        """
        # Create group box for circle properties
        circle_group = QGroupBox("Circle Properties")
        circle_layout = QFormLayout(circle_group)

        # Add circle property editors
        self._add_property_editor(circle_layout, NumberPropertyEditor("center_x", "Center X"), [circle])
        self._add_property_editor(circle_layout, NumberPropertyEditor("center_y", "Center Y"), [circle])
        self._add_property_editor(circle_layout, NumberPropertyEditor("radius", "Radius", min_value=0.1), [circle])

        # Add style properties
        style_group = QGroupBox("Style")
        style_layout = QFormLayout(style_group)

        # Add stroke width editor
        stroke_width_editor = NumberPropertyEditor("style.stroke_width", "Stroke Width", min_value=0.1, max_value=10.0, step=0.1)
        self._add_property_editor(style_layout, stroke_width_editor, [circle])

        # Add fill opacity editor - use a custom editor for QColor alpha
        fill_opacity_editor = NumberPropertyEditor("style.fill_color.alpha()", "Fill Opacity", min_value=0, max_value=255, step=5)

        # We need to handle this property specially since QColor.alpha() is a method, not a property
        fill_opacity_editor.get_property_value = lambda obj: obj.style.fill_color.alpha()
        fill_opacity_editor.set_property_value = lambda obj, value: obj.style.fill_color.setAlpha(int(value))

        self._add_property_editor(style_layout, fill_opacity_editor, [circle])

        # Add style group to layout
        circle_layout.addRow(style_group)

        # Add circle group to layout
        self.content_layout.insertWidget(1, circle_group)

    def _create_multiple_objects_ui(self, objects: List[GeometricObject]) -> None:
        """Create UI for multiple objects.

        Args:
            objects: Objects to create UI for
        """
        # Create group box for common properties
        common_group = QGroupBox(f"Multiple Objects ({len(objects)})")
        common_layout = QFormLayout(common_group)

        # Add common property editors
        self._add_property_editor(common_layout, BooleanPropertyEditor("visible", "Visible"), objects)
        self._add_property_editor(common_layout, BooleanPropertyEditor("locked", "Locked"), objects)

        # Add common group to layout
        self.content_layout.insertWidget(0, common_group)

        # Group objects by type
        points = [obj for obj in objects if isinstance(obj, Point)]
        lines = [obj for obj in objects if isinstance(obj, Line)]
        circles = [obj for obj in objects if isinstance(obj, Circle)]

        # Create group boxes for each type if there are multiple objects of that type
        if len(points) > 1:
            self._create_multiple_points_ui(points)

        if len(lines) > 1:
            self._create_multiple_lines_ui(lines)

        if len(circles) > 1:
            self._create_multiple_circles_ui(circles)

    def _create_multiple_points_ui(self, points: List[Point]) -> None:
        """Create UI for multiple points.

        Args:
            points: Points to create UI for
        """
        # Create group box for point properties
        point_group = QGroupBox(f"Points ({len(points)})")
        point_layout = QFormLayout(point_group)

        # Add point property editors
        # For multiple points, we don't show coordinates as they would be different

        # Add point group to layout
        self.content_layout.insertWidget(1, point_group)

    def _create_multiple_lines_ui(self, lines: List[Line]) -> None:
        """Create UI for multiple lines.

        Args:
            lines: Lines to create UI for
        """
        # Create group box for line properties
        line_group = QGroupBox(f"Lines ({len(lines)})")
        line_layout = QFormLayout(line_group)

        # Add line property editors
        # For multiple lines, we don't show coordinates as they would be different

        # Add line group to layout
        self.content_layout.insertWidget(1, line_group)

    def _create_multiple_circles_ui(self, circles: List[Circle]) -> None:
        """Create UI for multiple circles.

        Args:
            circles: Circles to create UI for
        """
        # Create group box for circle properties
        circle_group = QGroupBox(f"Circles ({len(circles)})")
        circle_layout = QFormLayout(circle_group)

        # Add circle property editors
        # For multiple circles, we don't show coordinates as they would be different

        # Add circle group to layout
        self.content_layout.insertWidget(1, circle_group)

    def _add_property_editor(self, layout: QFormLayout, editor: PropertyEditor, objects: List[GeometricObject]) -> None:
        """Add a property editor to a layout.

        Args:
            layout: Layout to add the editor to
            editor: Property editor to add
            objects: Objects to edit properties for
        """
        # Get label and widget
        label, widget = editor.get_row_widgets()

        # Add to layout
        layout.addRow(label, widget)

        # Set objects
        editor.set_objects(objects)

        # Store editor
        self.property_editors[editor.property_name] = editor
