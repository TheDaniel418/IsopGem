"""Geometry tab implementation.

This module provides the main tab for the Geometry pillar.
"""

import math
import random

from loguru import logger
from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import TabManager, WindowManager


class SimpleShape:
    """A simple geometric shape that can transform between different forms."""

    def __init__(self):
        # Position (as percentage of width/height) - use full tab space
        self.x = random.uniform(5, 95)
        self.y = random.uniform(5, 95)
        self.size = random.uniform(40, 120)  # More varied sizes

        # Movement - increased movement speed for faster animation
        self.dx = random.uniform(-0.4, 0.4)
        self.dy = random.uniform(-0.4, 0.4)

        # Shape type (0: circle, 1: square, 2: triangle, 3: hexagon, 4: star, 5: infinity)
        self.shape_type = random.randint(0, 5)
        self.target_shape = (
            self.shape_type + random.randint(1, 5)
        ) % 6  # More randomness in target shape
        self.morph_progress = random.uniform(
            0, 0.5
        )  # Start with some shapes already morphing

        # Color - use 0-1 range for HSV values
        self.hue = random.random()  # 0.0-1.0 instead of 0-360
        self.saturation = random.uniform(0.7, 1.0)  # More saturation variation
        self.value = random.uniform(0.7, 1.0)  # More brightness variation
        self.alpha = random.uniform(0.6, 0.9)  # More transparency variation

        # Target color
        self.target_hue = (
            self.hue + random.uniform(0.3, 0.7)
        ) % 1.0  # More random color changes
        self.color_progress = random.uniform(
            0, 0.5
        )  # Start with some colors already transitioning

        # Animation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-1.0, 1.0)  # Faster rotation
        self.transform_speed = random.uniform(0.005, 0.01)  # Even faster transformation
        self.color_speed = random.uniform(0.005, 0.01)  # Even faster color changes


class ShapeCanvas(QWidget):
    """A canvas widget for drawing shapes on top of other content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shapes = []
        self.num_shapes = 20  # More shapes for better visual effect

        # Initialize shapes
        for _ in range(self.num_shapes):
            self.shapes.append(SimpleShape())

        # Make transparent but explicitly set size policy
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Debug info
        logger.debug(f"ShapeCanvas initialized with {self.num_shapes} shapes")

    def showEvent(self, event):
        """Called when the widget is shown."""
        super().showEvent(event)
        logger.debug(
            f"ShapeCanvas shown - size: {self.width()}x{self.height()}, visible: {self.isVisible()}"
        )

    def resizeEvent(self, event):
        """Called when the widget is resized."""
        super().resizeEvent(event)
        logger.debug(f"ShapeCanvas resized to {self.width()}x{self.height()}")

    def update_animation(self):
        """Update all shape animations."""
        for shape in self.shapes:
            # Update shape properties
            shape.x += shape.dx
            shape.y += shape.dy

            # Bounce off edges
            if shape.x < 5 or shape.x > 95:
                shape.dx = -shape.dx
            if shape.y < 5 or shape.y > 95:
                shape.dy = -shape.dy

            # Rotate shape
            shape.rotation += shape.rotation_speed
            if shape.rotation > 360:
                shape.rotation -= 360

            # Update morph progress
            shape.morph_progress += shape.transform_speed
            shape.color_progress += shape.color_speed

            # Handle shape transformation completion
            if shape.morph_progress >= 1.0:
                shape.shape_type = shape.target_shape
                shape.target_shape = (shape.target_shape + 1) % 6
                shape.morph_progress = 0.0

            # Handle color transition completion
            if shape.color_progress >= 1.0:
                shape.hue = shape.target_hue
                shape.target_hue = (shape.target_hue + 0.5) % 1.0
                shape.color_progress = 0.0

        # Remove debug logging to reduce console spam
        # (previously logged animation updates every 60 frames)

        # Trigger repaint
        self.update()

    def _create_shape_path(self, shape_type, half_size):
        """Create a path for a specific shape type.

        Args:
            shape_type: The type of shape (0-5)
            half_size: Half the size of the shape

        Returns:
            QPainterPath: The path for the shape
        """
        path = QPainterPath()

        if shape_type == 0:  # Circle
            path.addEllipse(
                QRectF(-half_size, -half_size, half_size * 2, half_size * 2)
            )
        elif shape_type == 1:  # Square
            path.addRect(QRectF(-half_size, -half_size, half_size * 2, half_size * 2))
        elif shape_type == 2:  # Triangle
            path.moveTo(0, -half_size)
            path.lineTo(-half_size, half_size)
            path.lineTo(half_size, half_size)
            path.closeSubpath()
        elif shape_type == 3:  # Hexagon
            for i in range(6):
                angle = math.radians(60 * i)
                x_point = half_size * math.cos(angle)
                y_point = half_size * math.sin(angle)
                if i == 0:
                    path.moveTo(x_point, y_point)
                else:
                    path.lineTo(x_point, y_point)
            path.closeSubpath()
        elif shape_type == 4:  # Star
            for i in range(5):
                # Outer points
                angle_outer = math.radians(72 * i - 90)
                x_outer = half_size * math.cos(angle_outer)
                y_outer = half_size * math.sin(angle_outer)

                # Inner points
                angle_inner = math.radians(72 * i - 90 + 36)
                x_inner = (half_size * 0.4) * math.cos(angle_inner)
                y_inner = (half_size * 0.4) * math.sin(angle_inner)

                if i == 0:
                    path.moveTo(x_outer, y_outer)
                else:
                    path.lineTo(x_outer, y_outer)

                path.lineTo(x_inner, y_inner)
            path.closeSubpath()
        elif shape_type == 5:  # Infinity
            # Left loop
            path.addEllipse(QRectF(-half_size, -half_size / 2, half_size, half_size))
            # Right loop
            path.addEllipse(QRectF(0, -half_size / 2, half_size, half_size))

        return path

    def paintEvent(self, event):
        """Paint the geometric shapes."""
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Draw each shape
        for shape in self.shapes:
            # Calculate actual position and size
            x = self.width() * shape.x / 100.0
            y = self.height() * shape.y / 100.0
            size = shape.size

            # Interpolate between current and target hue for smoother transitions
            current_hue = shape.hue
            target_hue = shape.target_hue
            # Ensure we take the shortest path around the color wheel
            if abs(target_hue - current_hue) > 0.5:
                if target_hue > current_hue:
                    current_hue += 1.0
                else:
                    target_hue += 1.0

            interpolated_hue = current_hue + shape.color_progress * (
                target_hue - current_hue
            )
            interpolated_hue %= 1.0  # Keep in 0-1 range

            # Set color with proper HSV values (0-1 range)
            color = QColor()
            color.setHsvF(
                interpolated_hue,  # Hue: 0-1
                shape.saturation,  # Saturation: 0-1
                shape.value,  # Value: 0-1
                shape.alpha,  # Alpha: 0-1
            )

            # Prepare painter
            painter.save()
            painter.translate(x, y)
            painter.rotate(shape.rotation)

            # No fill, only thin borders
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(color, 1.5))  # Skinnier borders

            # Calculate half-size for drawing
            half_size = size / 2

            # Create paths for current and target shapes
            current_path = self._create_shape_path(shape.shape_type, half_size)
            target_path = self._create_shape_path(shape.target_shape, half_size)

            if shape.morph_progress > 0 and shape.morph_progress < 1:
                # Draw morphing shape - use QPainterPath directly for morphing effect
                # This is a simplified approach - a more advanced approach would use
                # proper path interpolation for complex shapes

                # Just crossfade between the two shapes
                painter.setOpacity(1.0 - shape.morph_progress)
                painter.drawPath(current_path)

                painter.setOpacity(shape.morph_progress)
                painter.drawPath(target_path)

                painter.setOpacity(1.0)  # Reset opacity
            else:
                # Draw normal shape with no morphing
                painter.drawPath(current_path)

            painter.restore()


class GeometryTab(QWidget):
    """Main tab for the Geometry pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Geometry tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager

        # We need to set a layout first
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Initialize canvas first so it's available for resize events
        self.shape_canvas = ShapeCanvas(self)

        # Now initialize the UI
        self._init_ui()

        # Debug widget visibility after everything is set up
        QTimer.singleShot(500, self._debug_widget_visibility)

        logger.debug("GeometryTab initialized")

    def _debug_widget_visibility(self) -> None:
        """Debug the visibility of widgets in the stacked layout."""
        # Get the stacked layout
        stack_layout = self.layout()
        if isinstance(stack_layout, QStackedLayout):
            # Log information about the stacked layout
            logger.debug(f"GeometryTab stacked layout - count: {stack_layout.count()}")
            logger.debug(
                f"GeometryTab stacked layout - current index: {stack_layout.currentIndex()}"
            )
            logger.debug(
                f"GeometryTab stacked layout - stacking mode: {stack_layout.stackingMode()}"
            )

            # Log information about each widget in the stacked layout
            for i in range(stack_layout.count()):
                widget = stack_layout.widget(i)
                logger.debug(
                    f"  Widget {i}: {widget.__class__.__name__} - visible: {widget.isVisible()}, "
                    f"size: {widget.width()}x{widget.height()}"
                )
                if widget == self.shape_canvas:
                    # Force canvas to be raised
                    logger.debug("  Raising ShapeCanvas to the top using raise_()")
                    widget.raise_()

    def showEvent(self, event) -> None:
        """Called when the tab is shown."""
        super().showEvent(event)
        logger.debug(
            f"GeometryTab shown - size: {self.width()}x{self.height()}, visible: {self.isVisible()}"
        )

        # Debug widget visibility when the tab is shown
        QTimer.singleShot(100, self._debug_widget_visibility)

        # Make sure the canvas is visible and on top
        QTimer.singleShot(200, self._ensure_canvas_on_top)

    def _ensure_canvas_on_top(self) -> None:
        """Make sure the shape canvas is visible and on top."""
        logger.debug("Ensuring ShapeCanvas is on top")

        # Make sure the canvas is visible
        self.shape_canvas.setVisible(True)

        # Raise the canvas to the top
        self.shape_canvas.raise_()

        # Update the tab to make sure changes take effect
        self.update()

    def resizeEvent(self, event) -> None:
        """Called when the tab is resized."""
        super().resizeEvent(event)
        logger.debug(f"GeometryTab resized to {self.width()}x{self.height()}")

        # Ensure the shape canvas covers the entire widget area when resized
        if hasattr(self, "shape_canvas") and hasattr(self, "stacked_widget"):
            self.shape_canvas.resize(self.stacked_widget.size())
            self.shape_canvas.raise_()  # Make sure it's on top when resized

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Create a stacked widget to hold both content and canvas
        self.stacked_widget = QWidget(self)
        self.layout().addWidget(self.stacked_widget)

        # Use QHBoxLayout for the stacked_widget to ensure it fills the parent completely
        stack_layout = QHBoxLayout(self.stacked_widget)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)

        # Content container with background styling
        content_container = QWidget()
        content_container.setObjectName("geometry_content")
        content_container.setStyleSheet(
            """
            QWidget#geometry_content {
                background-color: #f0f8ff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #f0f8ff, stop:1 #e0f0fd);
            }
        """
        )
        content_layout = QVBoxLayout(content_container)

        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        # Sacred Geometry button
        sacred_geometry_btn = QPushButton("Sacred Geometry")
        sacred_geometry_btn.setToolTip("Open Sacred Geometry Explorer")
        sacred_geometry_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #009688;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
        """
        )
        sacred_geometry_btn.clicked.connect(self._open_sacred_geometry)
        button_layout.addWidget(sacred_geometry_btn)

        # Regular Polygon Calculator button
        regular_polygon_btn = QPushButton("Regular Polygon")
        regular_polygon_btn.setToolTip("Open Regular Polygon Calculator")
        regular_polygon_btn.clicked.connect(self._open_regular_polygon)
        button_layout.addWidget(regular_polygon_btn)

        # Golden Ratio button
        golden_ratio_btn = QPushButton("Golden Ratio")
        golden_ratio_btn.setToolTip("Open Golden Ratio Calculator")
        # golden_ratio_btn.clicked.connect(lambda: self._open_golden_ratio())
        button_layout.addWidget(golden_ratio_btn)

        # Platonic Solids button
        platonic_btn = QPushButton("Platonic Solids")
        platonic_btn.setToolTip("Open Platonic Solids Calculator")
        platonic_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #673AB7;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5E35B1;
            }
            """
        )
        platonic_btn.clicked.connect(self._open_platonic_solids)
        button_layout.addWidget(platonic_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show Geometry help")
        help_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        # help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        # Add button bar to content layout
        content_layout.addWidget(button_bar)

        # Create card for welcome content
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet(
            """
            #welcomeCard {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 20px 40px;
                min-width: 500px;
                max-width: 800px;
                min-height: 200px;
            }
        """
        )
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(15, 15, 15, 15)
        welcome_layout.setSpacing(10)

        # Title and welcome message with enhanced styling
        title = QLabel("Geometry")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #009688;")

        welcome = QLabel(
            "Welcome to the Geometry pillar. Here you can explore sacred geometry, "
            "mathematical ratios, and visual patterns found throughout nature."
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("font-size: 14px; color: #555;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description with more details
        description = QLabel(
            "Sacred geometry is the geometry used in the planning and construction of "
            "religious structures, sacred spaces, and significant art. It ascribes symbolic and "
            "sacred meanings to certain geometric shapes and proportions."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #777; margin-top: 10px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add content to welcome card
        welcome_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(description)

        # Add welcome card to content layout
        content_layout.addWidget(welcome_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add Harmonia image below welcome card
        harmonia_container = QFrame()
        harmonia_container.setObjectName("harmoniaImageContainer")
        harmonia_container.setStyleSheet(
            """
            #harmoniaImageContainer {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 8px;
                margin: 10px 40px 20px 40px;
                padding: 10px;
            }
        """
        )
        harmonia_layout = QVBoxLayout(harmonia_container)

        # Create image label
        harmonia_image_label = QLabel()
        harmonia_pixmap = QPixmap("assets/tab_images/harmonia.png")

        if not harmonia_pixmap.isNull():
            # Scale the image to a reasonable size while maintaining aspect ratio
            scaled_pixmap = harmonia_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            harmonia_image_label.setPixmap(scaled_pixmap)
            harmonia_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add caption
            caption = QLabel(
                "Harmonia - Greek goddess of harmony, concord and geometric proportion"
            )
            caption.setStyleSheet(
                "font-size: 12px; color: #009688; font-style: italic;"
            )
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

            harmonia_layout.addWidget(
                harmonia_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            harmonia_layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add the image container to the content layout
            content_layout.addWidget(
                harmonia_container, alignment=Qt.AlignmentFlag.AlignCenter
            )
        else:
            logger.error(
                "Failed to load Harmonia image from assets/tab_images/harmonia.png"
            )

        content_layout.addStretch()

        # Add content container to stacked layout
        stack_layout.addWidget(content_container)

        # Add the shape canvas to the stacked widget
        self.shape_canvas.setParent(self.stacked_widget)
        self.shape_canvas.resize(self.stacked_widget.size())

        # Stack the canvas above the content
        self.shape_canvas.stackUnder(content_container)

        # Set attributes for shape canvas
        self.shape_canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        logger.debug(
            "ShapeCanvas created with visibility: " + str(self.shape_canvas.isVisible())
        )

        # Debug the layout
        logger.debug("Using regular layout with overlay canvas")

        # Raise the canvas to be on top of everything else after a delay
        QTimer.singleShot(1000, self._ensure_canvas_on_top)

    def _open_sacred_geometry(self) -> None:
        """Open the Sacred Geometry Explorer window."""
        logger.debug("Opening Sacred Geometry Explorer")

        # Import here to avoid circular imports
        # Generate a unique instance ID for multi-window support
        import uuid

        from geometry.ui.sacred_geometry import SacredGeometryExplorer
        from geometry.ui.sacred_geometry.tool_system.selection_tool import SelectionTool

        instance_id = f"sacred_geometry_{uuid.uuid4().hex[:8]}"

        # Create a new Sacred Geometry Explorer instance
        explorer = SacredGeometryExplorer(self.window_manager, instance_id)

        # Add tools
        explorer.add_tool(SelectionTool())

        # Register the window with the window manager
        self.window_manager._auxiliary_windows[instance_id] = explorer

        # Configure and show the window
        self.window_manager.configure_window(explorer)

        # Activate the selection tool by default
        explorer.set_active_tool("Selection")

        logger.debug(f"Opened Sacred Geometry Explorer with instance ID: {instance_id}")

    def _open_regular_polygon(self) -> None:
        """Open the Regular Polygon Calculator window."""
        logger.debug("Opening Regular Polygon Calculator")

        # Import here to avoid circular imports
        import uuid

        from geometry.ui.panels.regular_polygon_panel import RegularPolygonPanel

        # Generate a unique instance ID for multi-window support
        instance_id = f"regular_polygon_{uuid.uuid4().hex[:8]}"

        # Create a window for the calculator
        window = self.window_manager.create_auxiliary_window(
            instance_id, "Regular Polygon Calculator"
        )

        # Create the calculator panel
        calculator_panel = RegularPolygonPanel()

        # Set the panel as the window content
        window.set_content(calculator_panel)

        # Configure and show the window
        window.setMinimumSize(900, 600)
        window.show()

        logger.debug(
            f"Opened Regular Polygon Calculator with instance ID: {instance_id}"
        )

    def _open_platonic_solids(self) -> None:
        """Open the Platonic Solids Calculator window."""
        logger.debug("Opening Platonic Solids Calculator")

        # Import here to avoid circular imports
        import uuid

        from geometry.ui.windows.platonic_solid_window import PlatonicSolidWindow

        # Generate a unique instance ID for multi-window support
        instance_id = f"platonic_solid_{uuid.uuid4().hex[:8]}"

        # Create the Platonic Solids window
        window = PlatonicSolidWindow(instance_id, self)

        # Register the window with the window manager
        self.window_manager._auxiliary_windows[instance_id] = window

        # Configure and show the window
        self.window_manager.configure_window(window)
        window.setMinimumSize(900, 600)
        window.show()

        logger.debug(
            f"Opened Platonic Solids Calculator with instance ID: {instance_id}"
        )
