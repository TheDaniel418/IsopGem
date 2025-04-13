"""Sacred Geometry Explorer main window.

This module contains the main window for the Sacred Geometry Explorer,
which provides a GeoGebra-like environment for exploring and creating
sacred geometry constructions.
"""

from loguru import logger
from typing import Optional, List, Dict, Any, Tuple, Set, Union, cast
import os
import sys
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QCloseEvent, QMouseEvent, QKeyEvent, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QToolBar,
    QStatusBar,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QMenu,
    QApplication,
    QFrame,
)

from geometry.ui.sacred_geometry.file_format import save_construction, load_construction
from shared.ui.window_management import WindowManager

# Import our custom components
from geometry.ui.sacred_geometry.canvas import GeometryCanvas
from geometry.ui.sacred_geometry.properties import PropertiesPanel
# Import tools from tools.py
from geometry.ui.sacred_geometry.tools import GeometryTool, SelectionTool, PointTool, LineTool, CircleTool, PolygonTool, RegularPolygonTool, IntersectionTool, PerpendicularLineTool, ParallelLineTool, AngleBisectorTool, CompassTool, TextTool
from geometry.ui.sacred_geometry.text_toolbar import TextToolbar
from geometry.ui.sacred_geometry.commands import CommandHistory, GeometryCommand, CreateObjectCommand, DeleteObjectCommand, ModifyObjectCommand, CompoundCommand
from geometry.ui.sacred_geometry.model import GeometricObject, Point, Line, Circle, Polygon, Text, Style, GeometricObjectFactory, LineType


class SacredGeometryExplorer(QWidget):
    """Main window for the Sacred Geometry Explorer.

    This class provides a GeoGebra-like environment for exploring and creating
    sacred geometry constructions.
    """

    # Signal emitted when a construction is modified
    construction_modified = pyqtSignal()

    def __init__(self, window_manager: WindowManager) -> None:
        """Initialize the Sacred Geometry Explorer.

        Args:
            window_manager: The application window manager
        """
        super().__init__()
        self.window_manager = window_manager

        # Initialize instance variables
        self.canvas = None
        self.properties_panel = None
        self.status_bar = None
        self.toolbar = None
        self.tool_actions = {}
        self.active_tool = None
        self.command_history = CommandHistory()
        self.current_file_path = None
        self.modified = False
        self.default_file_extension = ".sgeo"  # Sacred Geometry file extension

        # Initialize UI components
        self._init_ui()

        # Initialize tools
        self._init_tools()

        # Set up signals and connections
        self._setup_connections()

        # Create test objects
        self.create_test_objects()

        # Initialize properties panel with selected objects
        if self.properties_panel and self.canvas:
            self.properties_panel.set_objects(self.get_selected_objects())

        logger.debug("Sacred Geometry Explorer initialized")

    def create_test_objects(self) -> None:
        """Create some test objects on the canvas."""
        # No test objects for a clean start
        logger.debug("No test objects created - starting with a blank canvas")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create toolbar
        self.toolbar = QToolBar("Tools")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        main_layout.addWidget(self.toolbar)

        # Create text toolbar
        self.text_toolbar = TextToolbar(self)
        self.text_toolbar.mode_changed.connect(self._on_text_mode_changed)
        self.text_toolbar.font_family_changed.connect(self._on_text_font_family_changed)
        self.text_toolbar.font_size_changed.connect(self._on_text_font_size_changed)
        self.text_toolbar.font_style_changed.connect(self._on_text_font_style_changed)
        self.text_toolbar.text_color_changed.connect(self._on_text_color_changed)
        self.text_toolbar.auto_position_changed.connect(self._on_text_auto_position_changed)
        self.text_toolbar.hide()
        main_layout.addWidget(self.text_toolbar)

        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, 1)  # 1 = stretch factor

        # Left panel for tools and properties
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Create properties panel
        self.properties_panel = PropertiesPanel()
        left_layout.addWidget(self.properties_panel)

        # Add left panel to splitter
        splitter.addWidget(left_panel)

        # Center area for canvas
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        # Create canvas
        self.canvas = GeometryCanvas()
        canvas_layout.addWidget(self.canvas)

        # Add canvas to splitter
        splitter.addWidget(canvas_container)

        # Set initial sizes for splitter
        splitter.setSizes([200, 600])  # Left panel: 200px, Canvas: 600px

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

        # Set window properties
        self.setMinimumSize(800, 600)
        self.setWindowTitle("Sacred Geometry Explorer")

        logger.debug("Sacred Geometry Explorer UI initialized")

    def _init_tools(self) -> None:
        """Initialize the geometric tools."""
        # Group 1: Selection tools
        self._add_tool_action("selection", SelectionTool(), "Selection", "Select and manipulate objects")

        # Add separator between selection and basic geometric tools
        self.toolbar.addSeparator()

        # Group 2: Basic geometric tools
        self._add_tool_action("point", PointTool(), "Point", "Create points")
        self._add_tool_action("line", LineTool(), "Line", "Create lines")
        self._add_tool_action("circle", CircleTool(), "Circle", "Create circles")
        self._add_tool_action("polygon", PolygonTool(), "Polygon", "Create polygons")
        self._add_tool_action("regular_polygon", RegularPolygonTool(), "Regular Polygon", "Create regular polygons")

        # Add separator between basic and advanced geometric tools
        self.toolbar.addSeparator()

        # Group 3: Advanced geometric tools
        self._add_tool_action("intersection", IntersectionTool(), "Intersection", "Find and mark intersections between objects")
        self._add_tool_action("perpendicular_line", PerpendicularLineTool(), "Perpendicular Line", "Create perpendicular lines")
        self._add_tool_action("parallel_line", ParallelLineTool(), "Parallel Line", "Create parallel lines with distance measurement")
        self._add_tool_action("angle_bisector", AngleBisectorTool(), "Angle Bisector", "Create angle bisectors from points or lines")
        self._add_tool_action("compass", CompassTool(), "Compass", "Create circles with radius equal to a given distance")

        # Add separator between advanced geometric tools and annotation tools
        self.toolbar.addSeparator()

        # Group 4: Annotation tools
        self._add_tool_action("text", TextTool(), "Text", "Add text and labels to the construction")

        # Add separator between tools and file operations
        self.toolbar.addSeparator()

        # Add undo/redo actions
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setToolTip("Undo the last action (Ctrl+Z)")
        self.undo_action.triggered.connect(self._on_undo)
        self.undo_action.setEnabled(False)
        self.toolbar.addAction(self.undo_action)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setToolTip("Redo the last undone action (Ctrl+Shift+Z)")
        self.redo_action.triggered.connect(self._on_redo)
        self.redo_action.setEnabled(False)
        self.toolbar.addAction(self.redo_action)

        # Add separator
        self.toolbar.addSeparator()

        # Add file actions
        new_action = QAction("New", self)
        new_action.setIcon(QIcon.fromTheme("document-new"))
        new_action.setToolTip("Create a new construction (Ctrl+N)")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_construction)
        self.toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setIcon(QIcon.fromTheme("document-open"))
        open_action.setToolTip("Open an existing construction (Ctrl+O)")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_construction)
        self.toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setIcon(QIcon.fromTheme("document-save"))
        save_action.setToolTip("Save the current construction")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_construction)
        self.toolbar.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setIcon(QIcon.fromTheme("document-save-as"))
        save_as_action.setToolTip("Save the current construction with a new name")
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_construction_as)
        self.toolbar.addAction(save_as_action)

        # Add separator
        self.toolbar.addSeparator()

        # Add undo/redo actions
        undo_action = QAction("Undo", self)
        undo_action.setIcon(QIcon.fromTheme("edit-undo"))
        undo_action.setToolTip("Undo the last action")
        undo_action.triggered.connect(self._undo)
        self.toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setIcon(QIcon.fromTheme("edit-redo"))
        redo_action.setToolTip("Redo the last undone action")
        redo_action.triggered.connect(self._redo)
        self.toolbar.addAction(redo_action)

        # Activate selection tool by default
        self._activate_tool("selection")

        logger.debug("Sacred Geometry Explorer tools initialized")

    def _add_tool_action(self, tool_id: str, tool: GeometryTool, name: str, tooltip: str) -> None:
        """Add a tool action to the toolbar.

        Args:
            tool_id: Unique identifier for the tool
            tool: The tool instance
            name: Display name for the tool
            tooltip: Tooltip text for the tool
        """
        # Create action with name
        action = QAction(name, self)
        action.setToolTip(tooltip)
        action.setCheckable(True)
        action.triggered.connect(lambda _=None, tid=tool_id: self._activate_tool(tid))

        # Set icon based on tool_id
        icon_name = self._get_icon_for_tool(tool_id)
        if icon_name:
            # Try to set icon from system theme
            action.setIcon(QIcon.fromTheme(icon_name))

        # Add action to toolbar
        self.toolbar.addAction(action)
        self.tool_actions[tool_id] = {
            "action": action,
            "tool": tool
        }

    def _get_icon_for_tool(self, tool_id: str) -> str:
        """Get the icon name for a tool.

        Args:
            tool_id: Tool identifier

        Returns:
            Icon name from system theme, or empty string if no icon
        """
        # Map tool IDs to system theme icon names
        icon_map = {
            "selection": "edit-select",
            "point": "draw-point",
            "line": "draw-line",
            "circle": "draw-circle",
            "polygon": "draw-polygon",
            "regular_polygon": "draw-polygon-star",
            "intersection": "draw-cross",
            "perpendicular_line": "draw-perpendicular",
            "parallel_line": "draw-parallel",
            "angle_bisector": "draw-angle",
            "compass": "draw-compass",
            "text": "draw-text"
        }

        return icon_map.get(tool_id, "")

    def _activate_tool(self, tool_id: str) -> None:
        """Activate a tool.

        Args:
            tool_id: ID of the tool to activate
        """
        # Deactivate current tool
        if self.active_tool:
            self.active_tool["action"].setChecked(False)
            self.active_tool["tool"].deactivate()

            # Hide any tool-specific toolbars
            if hasattr(self, 'text_toolbar'):
                self.text_toolbar.hide()

        # Activate new tool
        self.active_tool = self.tool_actions.get(tool_id)
        if self.active_tool:
            self.active_tool["action"].setChecked(True)
            self.active_tool["tool"].activate(self)
            self.status_bar.showMessage(f"Tool: {self.active_tool['action'].text()}")

            # Set cursor on canvas
            if self.canvas:
                self.canvas.setCursor(self.active_tool["tool"].get_cursor())

            # Show tool-specific toolbars
            if tool_id == 'text' and hasattr(self, 'text_toolbar'):
                self.text_toolbar.show()

        logger.debug(f"Activated tool: {tool_id}")

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Connect construction modified signal
        self.construction_modified.connect(self._on_construction_modified)

        # Connect canvas signals to tool handlers
        if self.canvas:
            self.canvas.mouse_pressed.connect(self._on_canvas_mouse_pressed)
            self.canvas.mouse_moved.connect(self._on_canvas_mouse_moved)
            self.canvas.mouse_released.connect(self._on_canvas_mouse_released)
            self.canvas.key_pressed.connect(self._on_canvas_key_pressed)
            self.canvas.object_selected.connect(self._on_object_selected)
            self.canvas.object_deselected.connect(self._on_object_deselected)
            self.canvas.object_modified.connect(self._on_object_modified)

        # Connect properties panel signals
        if self.properties_panel:
            self.properties_panel.property_changed.connect(self._on_property_changed)

        logger.debug("Sacred Geometry Explorer connections set up")

    def _on_canvas_mouse_pressed(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse press events from the canvas.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Forward to active tool
        if self.active_tool and self.active_tool["tool"].active:
            self.active_tool["tool"].mouse_press(event, scene_pos)

    def _on_canvas_mouse_moved(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse move events from the canvas.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Forward to active tool
        if self.active_tool and self.active_tool["tool"].active:
            self.active_tool["tool"].mouse_move(event, scene_pos)
        else:
            # Update status bar with coordinates if no tool is active
            self.status_bar.showMessage(f"Position: ({scene_pos.x():.2f}, {scene_pos.y():.2f})")

    def _on_canvas_mouse_released(self, event: QMouseEvent, scene_pos: QPointF) -> None:
        """Handle mouse release events from the canvas.

        Args:
            event: Mouse event
            scene_pos: Position in scene coordinates
        """
        # Forward to active tool
        if self.active_tool and self.active_tool["tool"].active:
            self.active_tool["tool"].mouse_release(event, scene_pos)

    def _on_canvas_key_pressed(self, event: QKeyEvent) -> None:
        """Handle key press events from the canvas.

        Args:
            event: Key event
        """
        # Handle escape key to cancel tool operation
        if event.key() == Qt.Key.Key_Escape and self.active_tool:
            # Activate selection tool
            self._activate_tool('selection')
            event.accept()
            return

        # Forward to active tool
        if self.active_tool and self.active_tool["tool"].active:
            self.active_tool["tool"].key_press(event)

    def create_point(self, x: float, y: float, name: str = None, style: Style = None) -> Point:
        """Create a point and add it to the canvas.

        Args:
            x: X coordinate
            y: Y coordinate
            name: Optional name for the point
            style: Optional style for the point

        Returns:
            Created point
        """
        # Create point
        point = Point(x, y, name, style)

        # Create and execute command
        command = CreateObjectCommand(self, point)
        self.command_history.execute(command)

        return point

    def create_line(self, x1: float, y1: float, x2: float, y2: float, name: str = None,
                   style: Style = None, line_type: LineType = LineType.SEGMENT) -> Line:
        """Create a line and add it to the canvas.

        Args:
            x1: X coordinate of first point
            y1: Y coordinate of first point
            x2: X coordinate of second point
            y2: Y coordinate of second point
            name: Optional name for the line
            style: Optional style for the line
            line_type: Type of line (segment, ray, or infinite)

        Returns:
            Created line
        """
        # Create line directly with coordinates
        line = Line(x1, y1, x2, y2, name, style, line_type)

        # Create and execute command
        command = CreateObjectCommand(self, line)
        self.command_history.execute(command)

        return line

    def create_circle(self, cx: float, cy: float, radius: float, name: str = None, style: Style = None) -> Circle:
        """Create a circle and add it to the canvas.

        Args:
            cx: X coordinate of center
            cy: Y coordinate of center
            radius: Radius
            name: Optional name for the circle
            style: Optional style for the circle

        Returns:
            Created circle
        """
        # Create circle directly with center coordinates
        circle = Circle(center_x=cx, center_y=cy, radius=radius, name=name, style=style)

        # Create and execute command
        command = CreateObjectCommand(self, circle)
        self.command_history.execute(command)

        return circle

    def create_polygon(self, vertices: List[Point], name: str = None, style: Style = None) -> Polygon:
        """Create a polygon and add it to the canvas.

        Args:
            vertices: List of vertex points
            name: Optional name for the polygon
            style: Optional style for the polygon

        Returns:
            Created polygon
        """
        # Create polygon
        polygon = Polygon(vertices, name, style)

        # Create and execute compound command
        commands = []

        # Add commands for vertices that don't exist in the canvas yet
        existing_vertex_ids = set(obj.id for obj in self.canvas.objects if isinstance(obj, Point))
        for vertex in vertices:
            if vertex.id not in existing_vertex_ids:
                commands.append(CreateObjectCommand(self, vertex))

        # Add command for the polygon itself
        commands.append(CreateObjectCommand(self, polygon))

        command = CompoundCommand(f"Create Polygon {name or ''}", commands)
        self.command_history.execute(command)

        return polygon

    def create_text(self, x: float, y: float, text: str, name: str = None, style: Style = None,
                   target_object: GeometricObject = None, auto_position: bool = False) -> Text:
        """Create a text label and add it to the canvas.

        Args:
            x: X coordinate
            y: Y coordinate
            text: Text content
            name: Optional name for the text
            style: Optional style for the text
            target_object: Optional target object that this text labels
            auto_position: Whether to automatically position the text relative to the target object

        Returns:
            Created text
        """
        # Create text object

        # Create text
        # Create a Point for the position
        position = Point(x, y)

        # Create text with proper parameters
        text_obj = Text(position=position, content=text, name=name, style=style)

        # Store target_object and auto_position in metadata
        if target_object:
            text_obj.metadata['target_object_id'] = target_object.id
        if auto_position is not None:
            text_obj.metadata['auto_position'] = auto_position

        # Create and execute command
        command = CreateObjectCommand(self, text_obj)
        self.command_history.execute(command)

        return text_obj

    def remove_object(self, obj: GeometricObject) -> None:
        """Remove a geometric object from the canvas.

        Args:
            obj: Geometric object to remove
        """
        # Create and execute command
        command = DeleteObjectCommand(self, obj)
        self.command_history.execute(command)

    def clear_objects(self) -> None:
        """Remove all geometric objects from the canvas."""
        # Create compound command for all objects
        if self.canvas and self.canvas.objects:
            commands = [DeleteObjectCommand(self, obj) for obj in self.canvas.objects.copy()]
            command = CompoundCommand("Clear All Objects", commands)
            self.command_history.execute(command)

    def modify_object(self, obj: GeometricObject, property_name: str, new_value: Any) -> None:
        """Modify a property of a geometric object.

        Args:
            obj: Object to modify
            property_name: Name of the property to modify
            new_value: New value for the property
        """
        # Get current value
        if '.' in property_name:
            # Handle nested properties (e.g., 'p1.x')
            parts = property_name.split('.')
            parent_obj = obj
            for part in parts[:-1]:
                if hasattr(parent_obj, part):
                    parent_obj = getattr(parent_obj, part)
                else:
                    logger.warning(f"Object {obj.__class__.__name__} has no attribute {part}")
                    return

            # Get property from parent object
            if hasattr(parent_obj, parts[-1]):
                old_value = getattr(parent_obj, parts[-1])
            else:
                logger.warning(f"Object {parent_obj.__class__.__name__} has no attribute {parts[-1]}")
                return
        else:
            # Get property directly from object
            if hasattr(obj, property_name):
                old_value = getattr(obj, property_name)
            else:
                logger.warning(f"Object {obj.__class__.__name__} has no attribute {property_name}")
                return

        # Create and execute command
        command = ModifyObjectCommand(self, obj, property_name, old_value, new_value)
        self.command_history.execute(command)

    def undo(self) -> bool:
        """Undo the last command.

        Returns:
            True if a command was undone, False otherwise
        """
        return self.command_history.undo()

    def redo(self) -> bool:
        """Redo the last undone command.

        Returns:
            True if a command was redone, False otherwise
        """
        return self.command_history.redo()

    def select_object(self, obj: GeometricObject) -> None:
        """Select a geometric object on the canvas.

        Args:
            obj: Geometric object to select
        """
        # Select on canvas
        if self.canvas:
            self.canvas.select_object(obj)

    def deselect_object(self, obj: GeometricObject) -> None:
        """Deselect a geometric object on the canvas.

        Args:
            obj: Geometric object to deselect
        """
        # Deselect on canvas
        if self.canvas:
            self.canvas.deselect_object(obj)

    def select_all_objects(self) -> None:
        """Select all geometric objects on the canvas."""
        # Select all on canvas
        if self.canvas:
            self.canvas.select_all_objects()

    def deselect_all_objects(self) -> None:
        """Deselect all geometric objects on the canvas."""
        # Deselect all on canvas
        if self.canvas:
            self.canvas.deselect_all_objects()

    def get_selected_objects(self) -> List[GeometricObject]:
        """Get all selected geometric objects on the canvas.

        Returns:
            List of selected geometric objects
        """
        # Get selected objects from canvas
        if self.canvas:
            return self.canvas.get_selected_objects()

        return []

    def _on_object_selected(self, obj: GeometricObject) -> None:
        """Handle object selected event.

        Args:
            obj: Selected object
        """
        # Update properties panel with selected objects
        if self.properties_panel:
            self.properties_panel.set_objects(self.get_selected_objects())

        logger.debug(f"Object selected: {obj.__class__.__name__} {obj.id}")

    def _on_object_deselected(self, obj: GeometricObject) -> None:
        """Handle object deselected event.

        Args:
            obj: Deselected object
        """
        # Update properties panel with selected objects
        if self.properties_panel:
            self.properties_panel.set_objects(self.get_selected_objects())

        logger.debug(f"Object deselected: {obj.__class__.__name__} {obj.id}")

    def _on_object_modified(self, obj: GeometricObject) -> None:
        """Handle object modified event.

        Args:
            obj: Modified object
        """
        # Update properties panel if this object is selected
        if obj.selected and self.properties_panel and hasattr(self.properties_panel, 'property_editors'):
            # Instead of recreating the entire panel, just update the property editors
            # that already exist for this object
            if isinstance(obj, Line):
                # IMPORTANT: Do NOT call set_objects as it recreates the entire panel
                # Instead, manually update each property editor

                # Get the current values from the line object
                x1, y1 = obj.x1, obj.y1
                x2, y2 = obj.x2, obj.y2

                # Check which endpoint was moved (stored in metadata)
                moved_endpoint = obj.metadata.get('moved_endpoint', None) if hasattr(obj, 'metadata') else None
                logger.debug(f"Moved endpoint: {moved_endpoint}")

                if moved_endpoint == 1:
                    # Only update endpoint 1 properties
                    if 'endpoint1_x' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint1_x']
                        if hasattr(editor, 'spin_box'):
                            # Directly set the value without triggering the update cycle
                            editor.updating = True
                            editor.spin_box.setValue(x1)
                            editor.updating = False
                            logger.debug(f"Updated property editor for endpoint1_x to {x1}")

                    if 'endpoint1_y' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint1_y']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(y1)
                            editor.updating = False
                            logger.debug(f"Updated property editor for endpoint1_y to {y1}")

                elif moved_endpoint == 2:
                    # Only update endpoint 2 properties
                    if 'endpoint2_x' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint2_x']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(x2)
                            editor.updating = False
                            logger.debug(f"Updated property editor for endpoint2_x to {x2}")

                    if 'endpoint2_y' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint2_y']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(y2)
                            editor.updating = False
                            logger.debug(f"Updated property editor for endpoint2_y to {y2}")

                else:
                    # If we don't know which endpoint was moved, update both (fallback)
                    logger.debug(f"No moved_endpoint metadata, updating all properties")
                    # Update all endpoint properties
                    if 'endpoint1_x' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint1_x']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(x1)
                            editor.updating = False
                    if 'endpoint1_y' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint1_y']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(y1)
                            editor.updating = False
                    if 'endpoint2_x' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint2_x']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(x2)
                            editor.updating = False
                    if 'endpoint2_y' in self.properties_panel.property_editors:
                        editor = self.properties_panel.property_editors['endpoint2_y']
                        if hasattr(editor, 'spin_box'):
                            editor.updating = True
                            editor.spin_box.setValue(y2)
                            editor.updating = False
            else:
                # For other object types, update all property editors
                for prop_name, editor in self.properties_panel.property_editors.items():
                    if hasattr(editor, 'update_widget'):
                        editor.update_widget()
                        logger.debug(f"Updated property editor for {prop_name}")

        logger.debug(f"Object modified: {obj.__class__.__name__} {obj.id}")

    def _on_property_changed(self, object_id: str, property_name: str, new_value: object) -> None:
        """Handle property changed event.

        Args:
            object_id: ID of the object that changed
            property_name: Name of the property that changed
            new_value: New value of the property
        """
        # Find object by ID
        obj = None
        if self.canvas:
            for o in self.canvas.objects:
                if o.id == object_id:
                    obj = o
                    break

        if obj:
            # Modify object using command system
            self.modify_object(obj, property_name, new_value)
            logger.debug(f"Property changed: {obj.__class__.__name__} {object_id}.{property_name} = {new_value}")
        else:
            logger.warning(f"Object with ID {object_id} not found")

    def _on_construction_modified(self) -> None:
        """Handle construction modified signal."""
        self.modified = True

        # Update window title to show modified state
        title = "Sacred Geometry Explorer"
        if self.current_file_path:
            title += f" - {self.current_file_path}"
        if self.modified:
            title += " *"

        self.setWindowTitle(title)

        # Update undo/redo actions
        self._update_undo_redo_actions()

    def _on_undo(self) -> None:
        """Handle undo action."""
        if self.undo():
            # Update undo/redo actions
            self._update_undo_redo_actions()

            # Update status bar
            self.status_bar.showMessage("Undone: " + self.command_history.get_undo_name())
        else:
            self.status_bar.showMessage("Nothing to undo")

    def _on_redo(self) -> None:
        """Handle redo action."""
        if self.redo():
            # Update undo/redo actions
            self._update_undo_redo_actions()

            # Update status bar
            self.status_bar.showMessage("Redone: " + self.command_history.get_redo_name())
        else:
            self.status_bar.showMessage("Nothing to redo")

    def _update_undo_redo_actions(self) -> None:
        """Update the undo/redo actions."""
        # Update undo action
        can_undo = self.command_history.can_undo()
        self.undo_action.setEnabled(can_undo)
        if can_undo:
            self.undo_action.setText(f"Undo {self.command_history.get_undo_name()}")
        else:
            self.undo_action.setText("Undo")

        # Update redo action
        can_redo = self.command_history.can_redo()
        self.redo_action.setEnabled(can_redo)
        if can_redo:
            self.redo_action.setText(f"Redo {self.command_history.get_redo_name()}")
        else:
            self.redo_action.setText("Redo")

    def _new_construction(self) -> None:
        """Create a new construction."""
        # Check if current construction is modified
        if self.modified:
            # Ask user if they want to save
            result = QMessageBox.question(
                self,
                "Save Changes",
                "The current construction has been modified. Do you want to save your changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if result == QMessageBox.StandardButton.Save:
                # Save current construction
                if not self._save_construction():
                    # Save failed or was cancelled
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                # Cancel new construction
                return

        # Clear canvas
        if self.canvas:
            self.canvas.clear_objects()

        # Reset state
        self.modified = False
        self.current_file_path = None
        self.command_history.clear()

        # Update window title
        self.setWindowTitle("Sacred Geometry Explorer")

        # Update undo/redo actions
        self._update_undo_redo_actions()

        logger.debug("Created new construction")

    def _open_construction(self) -> None:
        """Open an existing construction."""
        # Check if current construction is modified
        if self.modified:
            # Ask user if they want to save
            result = QMessageBox.question(
                self,
                "Save Changes",
                "The current construction has been modified. Do you want to save your changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if result == QMessageBox.StandardButton.Save:
                # Save current construction
                if not self._save_construction():
                    # Save failed or was cancelled
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                # Cancel open operation
                return

        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Construction",
            "",
            f"Sacred Geometry Files (*{self.default_file_extension});;All Files (*)"
        )

        if not file_path:
            # User cancelled
            return

        # Load construction
        objects = load_construction(file_path)
        if objects is None:
            # Loading failed
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load construction from {file_path}"
            )
            return

        # Clear current construction
        if self.canvas:
            self.canvas.clear_objects()

        # Add objects to canvas
        if self.canvas:
            self.canvas.add_objects(objects)

        # Update current file path
        self.current_file_path = file_path

        # Reset modified flag
        self.modified = False

        # Clear command history
        self.command_history.clear()

        # Update window title
        self.setWindowTitle(f"Sacred Geometry Explorer - {self.current_file_path}")

        # Update undo/redo actions
        self._update_undo_redo_actions()

        logger.debug(f"Opened construction from {file_path}")

    def _save_construction(self) -> bool:
        """Save the current construction.

        Returns:
            True if the construction was saved successfully, False otherwise
        """
        # If no file path, show save as dialog
        if not self.current_file_path:
            return self._save_construction_as()

        # Save construction
        if self.canvas:
            success = save_construction(self.current_file_path, self.canvas.objects)
            if success:
                # Reset modified flag
                self.modified = False

                # Update window title
                self.setWindowTitle(f"Sacred Geometry Explorer - {self.current_file_path}")

                logger.debug(f"Saved construction to {self.current_file_path}")
                return True
            else:
                # Saving failed
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save construction to {self.current_file_path}"
                )
                return False

        return False

    def _save_construction_as(self) -> bool:
        """Save the current construction with a new file name.

        Returns:
            True if the construction was saved successfully, False otherwise
        """
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Construction As",
            "",
            f"Sacred Geometry Files (*{self.default_file_extension});;All Files (*)"
        )

        if not file_path:
            # User cancelled
            return False

        # Add default extension if not present
        if not file_path.endswith(self.default_file_extension):
            file_path += self.default_file_extension

        # Update current file path
        self.current_file_path = file_path

        # Save construction
        return self._save_construction()

    def _undo(self) -> None:
        """Undo the last action."""
        if self.command_history.can_undo():
            self.command_history.undo()
            self.construction_modified.emit()

            logger.debug("Undid last action")

    def _redo(self) -> None:
        """Redo the last undone action."""
        if self.command_history.can_redo():
            self.command_history.redo()
            self.construction_modified.emit()

            logger.debug("Redid last action")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.

        Args:
            event: Close event
        """
        # Check if construction is modified
        if self.modified:
            # Ask user if they want to save
            pass

        # Accept the close event
        event.accept()

        logger.debug("Sacred Geometry Explorer closed")

    def _on_text_mode_changed(self, mode: int) -> None:
        """Handle text mode change.

        Args:
            mode: Mode index (0 = free text, 1 = label object)
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_mode(mode)

    def _on_text_font_family_changed(self, family: str) -> None:
        """Handle text font family change.

        Args:
            family: Font family name
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_font_family(family)

    def _on_text_font_size_changed(self, size: float) -> None:
        """Handle text font size change.

        Args:
            size: Font size
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_font_size(size)

    def _on_text_font_style_changed(self, style: int) -> None:
        """Handle text font style change.

        Args:
            style: Font style (0 = normal, 1 = bold, 2 = italic, 3 = bold+italic)
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_font_style(style)

    def _on_text_color_changed(self, color: QColor) -> None:
        """Handle text color change.

        Args:
            color: Text color
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_text_color(color)

    def _on_text_auto_position_changed(self, auto_position: bool) -> None:
        """Handle text auto-position change.

        Args:
            auto_position: Whether to automatically position text
        """
        if self.active_tool and isinstance(self.active_tool["tool"], TextTool):
            self.active_tool["tool"].set_auto_position(auto_position)