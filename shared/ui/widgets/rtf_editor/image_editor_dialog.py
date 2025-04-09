from dataclasses import dataclass
from typing import Optional, Callable, Union, Any, cast

# These imports are used dynamically in the code
# import base64
# import io
# import os
# import re
import numpy as np
from PIL import (
    Image,
    ImageFilter,
    ImageEnhance,
    ImageOps,
    ImageDraw,
    ImageFont,
    ImageChops,
)
from PIL.Image import Resampling
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QPainter,
    QMouseEvent,
    QWheelEvent,
    QPaintEvent,
    QResizeEvent,
    QColor,
    QBrush,
    QPen,
    QIcon,
    QPalette,
)
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QCheckBox,
    QPushButton,
    QComboBox,
    QSlider,
    QTabWidget,
    QWidget,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QGridLayout,
    QInputDialog,
)


@dataclass
class ImageDimensions:
    width: int
    height: int
    aspect_ratio: float


class ImagePreviewWidget(QWidget):
    """Widget to display an image with zoom and pan capability."""

    crop_changed = pyqtSignal(QRect)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 1px solid #CCCCCC;")

        # Image properties
        self.original_pixmap: Optional[QPixmap] = None
        self.working_pixmap: Optional[QPixmap] = None
        self.crop_rect: Optional[QRect] = None
        self.image_rect: Optional[QRect] = None

        # State flags
        self.dragging: bool = False
        self.drag_start: Optional[QPoint] = None
        self.crop_mode: bool = False
        self.panning: bool = False
        self.color_picking: bool = False

        # Transform properties
        self.zoom_factor: float = 1.0
        self.pan_start_pos: QPoint = QPoint()
        self.scroll_offset: QPoint = QPoint()

        # Color picking properties
        self.original_image: Optional[Image.Image] = None
        self.color_callback: Optional[Callable[[QColor], None]] = None

        self.setMouseTracking(True)

    def set_image(self, pixmap: QPixmap) -> None:
        """Set the image and reset crop."""
        self.original_pixmap = pixmap
        self.working_pixmap = (
            self.original_pixmap.copy() if self.original_pixmap else None
        )
        self.crop_rect = None
        self.update_display()

    def update_display(self) -> None:
        """Update the display with the working pixmap and crop overlay."""
        if not self.working_pixmap:
            self.update()
            return

        # Calculate the actual area where the image is drawn in the label
        self.image_rect = self.get_image_rect(self.working_pixmap.size())

        # Don't need to create and assign a display pixmap anymore since we're drawing
        # directly in paintEvent
        self.update()

    def get_image_rect(self, image_size: QSize) -> QRect:
        """Calculate the rect where the image is displayed in the label."""
        widget_size = self.size()

        # Calculate the scaled size while maintaining aspect ratio
        scaled_size = image_size.scaled(widget_size, Qt.AspectRatioMode.KeepAspectRatio)

        # Calculate the position to center the image in the label
        pos_x = (widget_size.width() - scaled_size.width()) // 2
        pos_y = (widget_size.height() - scaled_size.height()) // 2

        return QRect(pos_x, pos_y, scaled_size.width(), scaled_size.height())

    def map_to_image_coords(
        self, widget_pos: Union[QPoint, QPointF]
    ) -> Optional[QPoint]:
        """Map coordinates from widget space to image space."""
        if not self.working_pixmap:
            return None

        # Calculate the scaled size
        scaled_width = int(self.working_pixmap.width() * self.zoom_factor)
        scaled_height = int(self.working_pixmap.height() * self.zoom_factor)

        # Calculate the centered position
        x = max(0, (self.width() - scaled_width) // 2) + self.scroll_offset.x()
        y = max(0, (self.height() - scaled_height) // 2) + self.scroll_offset.y()

        # Define the image rect
        img_rect = QRect(x, y, scaled_width, scaled_height)

        # Convert QPointF to QPoint if needed
        if isinstance(widget_pos, QPointF):
            widget_pos = QPoint(int(widget_pos.x()), int(widget_pos.y()))

        # Check if the position is inside the image
        if not img_rect.contains(widget_pos):
            return None

        # Convert to image coordinates
        img_x = int((widget_pos.x() - x) / self.zoom_factor)
        img_y = int((widget_pos.y() - y) / self.zoom_factor)

        return QPoint(img_x, img_y)

    def set_crop_mode(self, enabled: bool) -> None:
        """Enable or disable crop mode."""
        self.crop_mode = enabled
        if not enabled:
            self.crop_rect = None
        self.update_display()

    def mousePressEvent(self, event: Optional[QMouseEvent] = None) -> None:
        """Handle mouse press events."""
        if event is None:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if (
                self.color_picking
                and self.original_pixmap
                and hasattr(self, "original_image")
            ):
                # Calculate the position in the original image
                image_pos = self.image_pos_from_widget_pos(event.position())
                if image_pos is not None and self.original_image:
                    img_x, img_y = image_pos.x(), image_pos.y()
                    if (
                        0 <= img_x < self.original_image.width
                        and 0 <= img_y < self.original_image.height
                    ):
                        # Get the pixel color at that position
                        try:
                            pixel = self.original_image.getpixel((img_x, img_y))
                            if isinstance(pixel, tuple) and len(pixel) >= 3:
                                r, g, b = pixel[0:3]
                                color = QColor(r, g, b)
                                # Call the callback
                                if self.color_callback:
                                    self.color_callback(color)
                        except Exception as e:
                            print(f"Error picking color: {e}")
            elif self.crop_mode and self.working_pixmap:
                # Handle crop mode selection
                img_pos = self.map_to_image_coords(event.position())
                if img_pos is not None:
                    self.dragging = True
                    self.drag_start = img_pos
                    self.crop_rect = QRect(img_pos, QSize(1, 1))
                    self.update()
            else:
                # Start panning
                self.panning = True
                self.pan_start_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: Optional[QMouseEvent] = None) -> None:
        """Handle mouse move events."""
        if event is None:
            return

        if self.dragging and self.crop_mode and self.working_pixmap:
            img_pos = self.map_to_image_coords(event.position())
            if img_pos is not None and self.drag_start is not None:
                self.crop_rect = QRect(self.drag_start, img_pos).normalized()
                self.update()
        elif self.panning and event.buttons() & Qt.MouseButton.LeftButton:
            # Calculate the distance moved
            current_pos = event.position().toPoint()
            delta = QPoint(
                current_pos.x() - self.pan_start_pos.x(),
                current_pos.y() - self.pan_start_pos.y(),
            )

            # Update the scroll offset
            self.scroll_offset += delta

            # Update the start position for the next move
            self.pan_start_pos = current_pos

            # Update the display
            self.update()

    def mouseReleaseEvent(self, event: Optional[QMouseEvent] = None) -> None:
        """Handle mouse release events."""
        if event is None:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging and self.crop_mode:
                self.dragging = False
                if (
                    self.crop_rect is not None
                    and self.crop_rect.width() > 10
                    and self.crop_rect.height() > 10
                ):
                    self.crop_changed.emit(self.crop_rect)
                else:
                    self.crop_rect = None
                    self.update()
            self.panning = False

    def resizeEvent(self, event: Optional[QResizeEvent] = None) -> None:
        """Handle resize events to update image display."""
        if event is not None:
            super().resizeEvent(event)
        self.update()

    def get_current_crop(self) -> Optional[QRect]:
        """Get the current crop rectangle."""
        return self.crop_rect

    def reset_image(self) -> None:
        """Reset to original image."""
        if self.original_pixmap:
            self.working_pixmap = self.original_pixmap.copy()
            self.crop_rect = None
            self.update()

    def set_zoom(self, factor: float) -> None:
        """Set the zoom factor for the image."""
        self.zoom_factor = factor
        self.update_display()

    def enable_color_picking(
        self, pil_image: Image.Image, callback: Callable[[QColor], None]
    ) -> None:
        """Enable color picking mode."""
        self.color_picking = True
        self.original_image = pil_image
        self.color_callback = callback
        self.setCursor(Qt.CursorShape.CrossCursor)

    def disable_color_picking(self) -> None:
        """Disable color picking mode."""
        self.color_picking = False
        self.original_image = None
        self.color_callback = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def paintEvent(self, event: Optional[QPaintEvent] = None) -> None:
        """Paint the widget with the image."""
        # event parameter is required by Qt but not used
        painter = QPainter(self)

        # Fill with a checkered background to indicate transparency
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        if not self.original_pixmap:
            return

        # Calculate the scaled size
        scaled_width = int(self.original_pixmap.width() * self.zoom_factor)
        scaled_height = int(self.original_pixmap.height() * self.zoom_factor)

        # Calculate the centered position
        x = max(0, (self.width() - scaled_width) // 2) + self.scroll_offset.x()
        y = max(0, (self.height() - scaled_height) // 2) + self.scroll_offset.y()

        # Draw the scaled image
        target_rect = QRect(x, y, scaled_width, scaled_height)
        painter.drawPixmap(target_rect, self.original_pixmap)

        # Draw crop rectangle if in crop mode
        if (
            self.crop_mode
            and self.crop_rect is not None
            and self.working_pixmap is not None
        ):
            # First, calculate where the crop rect would be in widget coordinates
            img_to_widget_x_ratio = target_rect.width() / self.working_pixmap.width()
            img_to_widget_y_ratio = target_rect.height() / self.working_pixmap.height()

            widget_crop_rect = QRect(
                int(self.crop_rect.x() * img_to_widget_x_ratio) + target_rect.x(),
                int(self.crop_rect.y() * img_to_widget_y_ratio) + target_rect.y(),
                int(self.crop_rect.width() * img_to_widget_x_ratio),
                int(self.crop_rect.height() * img_to_widget_y_ratio),
            )

            # Semi-transparent overlay for non-cropped area
            overlay = QColor(0, 0, 0, 100)
            pen = QPen(Qt.GlobalColor.red)
            pen.setWidth(2)

            # Draw the semi-transparent overlay around the crop area
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(overlay))

            # Draw four rectangles around the crop area
            painter.drawRect(
                target_rect.x(),
                target_rect.y(),
                target_rect.width(),
                widget_crop_rect.top() - target_rect.y(),
            )  # Top
            painter.drawRect(
                target_rect.x(),
                widget_crop_rect.bottom(),
                target_rect.width(),
                target_rect.bottom() - widget_crop_rect.bottom(),
            )  # Bottom
            painter.drawRect(
                target_rect.x(),
                widget_crop_rect.top(),
                widget_crop_rect.left() - target_rect.x(),
                widget_crop_rect.height(),
            )  # Left
            painter.drawRect(
                widget_crop_rect.right(),
                widget_crop_rect.top(),
                target_rect.right() - widget_crop_rect.right(),
                widget_crop_rect.height(),
            )  # Right

            # Draw the crop rectangle outline
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(widget_crop_rect)

        # Draw zoom information
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(10, 20, f"Zoom: {int(self.zoom_factor * 100)}%")

    def image_pos_from_widget_pos(self, widget_pos: Union[QPoint, QPointF]) -> QPoint:
        """Convert a position in the widget to a position in the image."""
        if not self.original_pixmap:
            return QPoint(0, 0)

        # Convert QPointF to QPoint if needed
        if isinstance(widget_pos, QPointF):
            widget_pos = QPoint(int(widget_pos.x()), int(widget_pos.y()))

        # Calculate the scaled size
        scaled_width = int(self.original_pixmap.width() * self.zoom_factor)
        scaled_height = int(self.original_pixmap.height() * self.zoom_factor)

        # Calculate the centered position
        x = max(0, (self.width() - scaled_width) // 2) + self.scroll_offset.x()
        y = max(0, (self.height() - scaled_height) // 2) + self.scroll_offset.y()

        # Calculate the position in the original image
        image_x = int((widget_pos.x() - x) / self.zoom_factor)
        image_y = int((widget_pos.y() - y) / self.zoom_factor)

        return QPoint(image_x, image_y)

    def wheelEvent(self, event: Optional[QWheelEvent] = None) -> None:
        """Handle mouse wheel events for zooming."""
        if event is None:
            return

        zoom_in = event.angleDelta().y() > 0

        # Calculate new zoom factor
        new_zoom = self.zoom_factor * 1.2 if zoom_in else self.zoom_factor / 1.2
        new_zoom = max(0.1, min(5.0, new_zoom))  # Limit zoom range

        # Apply the new zoom factor
        self.set_zoom(new_zoom)


class ImageEditorDialog(QDialog):
    """Dialog for editing images with filters, cropping, and other enhancements."""

    def __init__(self, image_format, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Editor")
        self.setMinimumSize(800, 600)

        self.image_format = image_format
        self.original_image = None  # PIL Image
        self.working_image = None  # Current PIL Image with edits
        self.original_width = 0
        self.original_height = 0
        self.aspect_ratio = 1.0
        self.final_width = 0
        self.final_height = 0

        # Initialize aspect ratio settings
        self.current_aspect_ratio = "Free Form"
        self.custom_aspect_ratio = 1.0  # Default to 1:1

        # Initialize preview-related attributes
        self.preview2 = None
        self.compare_checkbox = None
        self.color_display = None
        self.color_hex = None
        self.original_image_copy = None

        # Result storage
        self.result_image = None  # Final PIL Image
        self.result_pixmap = None  # Final QPixmap

        # Try to load the image
        self.load_image()

        # Set up the UI
        self.setup_ui()

    def load_image(self):
        """Load the image from the image format, handling both file paths and data URIs."""
        path = self.image_format.name()

        # Check if this is a data URI
        if path and path.startswith("data:"):
            try:
                # Extract the base64 data
                import re, base64, io

                data_uri_pattern = r"data:(.*?);base64,(.*)"
                match = re.match(data_uri_pattern, path)

                if match:
                    content_type, b64data = match.groups()
                    # Decode the base64 data
                    img_data = base64.b64decode(b64data)

                    # Use BytesIO to create a file-like object
                    buffer = io.BytesIO(img_data)

                    # Load with PIL
                    self.original_image = Image.open(buffer)
                    self.original_image.load()  # Ensure the image is fully loaded
                    self.working_image = self.original_image.copy()

                    # Get dimensions
                    self.original_width, self.original_height = self.original_image.size
                    if self.original_width > 0 and self.original_height > 0:
                        self.aspect_ratio = self.original_height / self.original_width

                    # Set final dimensions from format or from original
                    format_width = int(self.image_format.width())
                    format_height = int(self.image_format.height())

                    self.final_width = (
                        format_width if format_width > 0 else self.original_width
                    )
                    self.final_height = (
                        format_height if format_height > 0 else self.original_height
                    )

                    # Create a temporary file to enable editing and saving
                    import tempfile, os

                    temp_dir = tempfile.gettempdir()

                    # Determine file extension from content type
                    ext = "png"  # Default
                    if content_type == "image/jpeg":
                        ext = "jpg"
                    elif content_type == "image/gif":
                        ext = "gif"

                    # Create a unique temp filename
                    import uuid

                    temp_filename = f"temp_img_{uuid.uuid4().hex}.{ext}"
                    temp_path = os.path.join(temp_dir, temp_filename)

                    # Save to temp file
                    self.original_image.save(temp_path)
                    print(f"Saved embedded image to temporary file: {temp_path}")

                    # Store temp path for later use
                    self._temp_file_path = temp_path

                    return True
                else:
                    print(f"Failed to parse data URI: {path[:50]}...")
                    return False

            except Exception as e:
                print(f"Error loading image from data URI: {e}")
                return False

        # Regular file path handling
        elif path:
            try:
                import os

                if os.path.isfile(path):
                    # Load with PIL
                    self.original_image = Image.open(path)
                    self.working_image = self.original_image.copy()
                else:
                    print(f"File not found: {path}")
                    return False

                # Get dimensions
                self.original_width, self.original_height = self.original_image.size
                if self.original_width > 0 and self.original_height > 0:
                    self.aspect_ratio = self.original_height / self.original_width

                # Set final dimensions from format or from original
                format_width = int(self.image_format.width())
                format_height = int(self.image_format.height())

                self.final_width = (
                    format_width if format_width > 0 else self.original_width
                )
                self.final_height = (
                    format_height if format_height > 0 else self.original_height
                )

                return True
            except Exception as e:
                print(f"Error loading image file: {e}")

        else:
            print(f"Image path invalid or not found: {path}")

        return False

    def setup_ui(self):
        """Set up the dialog UI elements."""
        main_layout = QVBoxLayout(self)

        # Create a tab widget for different editing functions
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Add tabs - change order so preview tab (with comparison toggle) is set up before main tab
        self.setup_preview_tab()
        self.setup_main_tab()
        self.setup_filters_tab()
        self.setup_adjustments_tab()
        self.setup_crop_tab()

        # Add a button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add save as button
        save_as_button = QPushButton("Save As...")
        button_box.addButton(save_as_button, QDialogButtonBox.ButtonRole.ActionRole)
        save_as_button.clicked.connect(self.save_image_as)

        main_layout.addWidget(button_box)

    def setup_main_tab(self):
        """Set up the main tab with preview and basic info."""
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)

        # Preview area
        self.preview = ImagePreviewWidget()
        self.update_preview()

        # Information group
        info_group = QGroupBox("Image Information")
        info_layout = QFormLayout()

        # File path
        self.path_label = QLabel(self.image_format.name())
        self.path_label.setWordWrap(True)
        info_layout.addRow("Path:", self.path_label)

        # Dimensions
        dims_label = QLabel(f"{self.original_width} x {self.original_height} pixels")
        info_layout.addRow("Original Size:", dims_label)

        # Reset button
        reset_button = QPushButton("Reset to Original")
        reset_button.clicked.connect(self.reset_image)

        info_group.setLayout(info_layout)

        # Add components to layout
        layout.addWidget(self.preview, 1)  # 1 = stretch factor
        layout.addWidget(info_group)
        layout.addWidget(reset_button)

        self.tab_widget.addTab(main_tab, "Preview")

    def setup_filters_tab(self):
        """Set up the filters tab."""
        filters_tab = QWidget()
        layout = QVBoxLayout(filters_tab)

        # Add a preview area at the top of the filters tab
        self.filter_preview = ImagePreviewWidget()
        self.filter_preview.setMinimumHeight(200)
        if self.working_image:
            self.filter_preview.set_image(self.pil_to_pixmap(self.working_image))
        layout.addWidget(self.filter_preview)

        # Filter selection
        filter_group = QGroupBox("Apply Filter")
        filter_layout = QVBoxLayout()

        # Filter combobox
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                "None",
                "Blur",
                "Sharpen",
                "Contour",
                "Detail",
                "Smooth",
                "Emboss",
                "Edge Enhance",
                "Find Edges",
                "Grayscale",
                "Sepia",
                "Negative",
                "Posterize",
                "Solarize",
                "Vignette",
                "Vintage",
                "Cold",
                "Warm",
                "Dramatic",
                "Noise Reduction",
            ]
        )
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)

        # Intensity slider for some filters
        intensity_widget = QWidget()
        intensity_layout = QFormLayout(intensity_widget)
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.apply_filter)
        intensity_layout.addRow("Intensity:", self.intensity_slider)
        filter_layout.addWidget(intensity_widget)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Apply button
        apply_filter_button = QPushButton("Apply Filter")
        apply_filter_button.clicked.connect(self.apply_selected_filter)
        layout.addWidget(apply_filter_button)

        # Add stretch to push everything to the top
        layout.addStretch()

        self.tab_widget.addTab(filters_tab, "Filters")

    def on_filter_changed(self, filter_name):
        """Enable or disable intensity slider based on filter type."""
        # Enable intensity slider only for filters that can use it
        intensity_filters = [
            "Blur",
            "Sharpen",
            "Edge Enhance",
            "Smooth",
            "Sepia",
            "Vignette",
            "Vintage",
            "Cold",
            "Warm",
            "Dramatic",
            "Noise Reduction",
        ]

        if hasattr(self, "intensity_slider") and self.intensity_slider is not None:
            self.intensity_slider.setEnabled(filter_name in intensity_filters)

        # Apply the filter with current intensity
        self.apply_filter()

    def apply_filter(self):
        """Preview a filter on the image."""
        if not self.working_image:
            return

        # Get the selected filter
        filter_name = self.filter_combo.currentText()

        # Create a temporary image for preview
        temp_image = self.working_image.copy()

        # Get intensity value (0-100 to 0.0-3.0 range)
        intensity = self.intensity_slider.value() / 100.0 * 3.0

        try:
            # Apply the selected filter
            if filter_name == "None":
                pass  # No filter to apply
            elif filter_name == "Blur":
                # Use intensity for blur radius (0.5 to 5)
                blur_radius = max(0.5, intensity * 2.5)
                temp_image = temp_image.filter(
                    ImageFilter.GaussianBlur(radius=blur_radius)
                )
            elif filter_name == "Sharpen":
                # Apply sharpen multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    temp_image = temp_image.filter(ImageFilter.SHARPEN)
            elif filter_name == "Contour":
                temp_image = temp_image.filter(ImageFilter.CONTOUR)
            elif filter_name == "Detail":
                temp_image = temp_image.filter(ImageFilter.DETAIL)
            elif filter_name == "Smooth":
                # Apply smooth multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    temp_image = temp_image.filter(ImageFilter.SMOOTH)
            elif filter_name == "Emboss":
                temp_image = temp_image.filter(ImageFilter.EMBOSS)
            elif filter_name == "Edge Enhance":
                # Apply edge enhance multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    temp_image = temp_image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_name == "Find Edges":
                temp_image = temp_image.filter(ImageFilter.FIND_EDGES)
            elif filter_name == "Grayscale":
                temp_image = ImageOps.grayscale(temp_image)
                # Convert back to RGB mode for consistent handling
                temp_image = Image.merge("RGB", [temp_image, temp_image, temp_image])
            elif filter_name == "Sepia":
                temp_image = self.apply_sepia(temp_image, intensity)
            elif filter_name == "Negative":
                # Convert to RGB for invert operation if in RGBA mode
                if temp_image.mode == "RGBA":
                    # Save the alpha channel
                    r, g, b, a = temp_image.split()
                    rgb_image = Image.merge("RGB", (r, g, b))
                    # Invert the RGB channels
                    inverted_rgb = ImageOps.invert(rgb_image)
                    # Merge back with original alpha channel
                    r, g, b = inverted_rgb.split()
                    temp_image = Image.merge("RGBA", (r, g, b, a))
                else:
                    temp_image = ImageOps.invert(temp_image.convert("RGB"))
            elif filter_name == "Posterize":
                # Use intensity to determine levels (2-8)
                levels = max(2, min(8, int(intensity * 6 / 3.0) + 2))

                # Posterize doesn't support RGBA mode, so handle alpha channel separately
                if temp_image.mode == "RGBA":
                    # Split the image into channels
                    r, g, b, a = temp_image.split()
                    # Merge RGB channels
                    rgb_image = Image.merge("RGB", (r, g, b))
                    # Apply posterize to RGB image
                    posterized = ImageOps.posterize(rgb_image, levels)
                    # Split the posterized image
                    r2, g2, b2 = posterized.split()
                    # Merge with original alpha channel
                    temp_image = Image.merge("RGBA", (r2, g2, b2, a))
                else:
                    # If not RGBA, just convert to RGB and apply
                    temp_image = ImageOps.posterize(temp_image.convert("RGB"), levels)
            elif filter_name == "Solarize":
                # Solarize inverts all pixel values above a threshold
                threshold = int(
                    128 * (1 - intensity / 3.0)
                )  # Higher intensity means more solarization

                # Handle alpha channel separately if needed
                if temp_image.mode == "RGBA":
                    r, g, b, a = temp_image.split()
                    rgb_image = Image.merge("RGB", (r, g, b))
                    solarized = ImageOps.solarize(rgb_image, threshold)
                    r2, g2, b2 = solarized.split()
                    temp_image = Image.merge("RGBA", (r2, g2, b2, a))
                else:
                    temp_image = ImageOps.solarize(temp_image.convert("RGB"), threshold)
            elif filter_name == "Vignette":
                temp_image = self.apply_vignette(temp_image, intensity)
            elif filter_name == "Vintage":
                temp_image = self.apply_vintage_effect(temp_image, intensity)
            elif filter_name == "Cold":
                temp_image = self.apply_color_temperature(
                    temp_image, -intensity
                )  # Negative for cold
            elif filter_name == "Warm":
                temp_image = self.apply_color_temperature(temp_image, intensity)
            elif filter_name == "Dramatic":
                temp_image = self.apply_dramatic(temp_image, intensity)
            elif filter_name == "Noise Reduction":
                # More intensity = more noise reduction
                radius = max(0.5, intensity * 0.5)
                temp_image = temp_image.filter(
                    ImageFilter.MedianFilter(size=int(radius * 2) + 1)
                )

            # Update the preview with the filtered image
            pixmap = self.pil_to_pixmap(temp_image)
            self.preview.set_image(pixmap)

            # Update the filter tab preview
            if hasattr(self, "filter_preview"):
                self.filter_preview.set_image(pixmap)

        except Exception as e:
            print(f"Error applying filter {filter_name}: {e}")

    def apply_vignette(self, image, intensity=1.0):
        """Apply a vignette effect to the image."""
        # Create an oval shaped mask
        img_width, img_height = image.size
        mask = Image.new("L", image.size, 255)
        draw = ImageDraw.Draw(mask)

        # Calculate dimensions for the ellipse
        width_offset = int(img_width * 0.15 * intensity)
        height_offset = int(img_height * 0.15 * intensity)

        # Draw ellipse
        draw.ellipse(
            (
                width_offset,
                height_offset,
                img_width - width_offset,
                img_height - height_offset,
            ),
            fill=255,
        )

        # Apply a gaussian blur to the mask
        blur_radius = max(30, int(min(img_width, img_height) * 0.05 * intensity))
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Convert the image to RGBA if it's not already
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Create a semi-transparent black layer
        black_layer = Image.new("RGBA", image.size, (0, 0, 0, int(150 * intensity)))

        # Apply the mask to the black layer
        black_layer.putalpha(ImageOps.invert(mask))

        # Composite the images
        return Image.alpha_composite(image, black_layer)

    def apply_sepia(self, image, intensity=1.0):
        """Apply a sepia filter to the image."""
        # Convert to grayscale
        gray = ImageOps.grayscale(image)

        # Create a sepia palette
        sepia = Image.new("RGB", image.size, (112, 66, 20))

        # Blend the grayscale with the sepia color
        blend_amount = min(0.8, intensity * 0.3)  # Cap at 0.8 for best results
        return Image.blend(gray.convert("RGB"), sepia, blend_amount)

    def apply_vintage_effect(self, image, intensity=1.0):
        """Apply a vintage/retro effect to the image."""
        # Make a copy to avoid modifying the original
        vintage_img = image.copy()

        # Convert to RGB
        if vintage_img.mode != "RGB":
            alpha = None
            if vintage_img.mode == "RGBA":
                alpha = vintage_img.split()[3]
            vintage_img = vintage_img.convert("RGB")

        # 1. Increase contrast slightly
        enhancer = ImageEnhance.Contrast(vintage_img)
        vintage_img = enhancer.enhance(1.1 + 0.1 * intensity)

        # 2. Add warmth
        vintage_img = self.apply_color_temperature(vintage_img, intensity * 0.7)

        # 3. Add a slight vignette
        vintage_img = self.apply_vignette(vintage_img, intensity * 0.5)

        # 4. Reduce saturation slightly
        enhancer = cast(Any, ImageEnhance.Color(vintage_img))
        vintage_img = enhancer.enhance(0.85)

        # 5. Add slight noise texture - using a safer approach than effect_noise
        if intensity > 0.5:
            try:
                # Create a noise layer using numpy instead of effect_noise
                from PIL import Image

                # Create random noise array
                width, height = vintage_img.size
                noise_array = np.random.randint(
                    0, 255, (height, width, 3), dtype=np.uint8
                )

                # Convert to image
                noise = Image.fromarray(noise_array, mode="RGB")

                # Make sure modes match
                if noise.mode != vintage_img.mode:
                    noise = noise.convert(vintage_img.mode)

                # Blend with very low alpha to add subtle noise
                vintage_img = Image.blend(
                    vintage_img, noise, min(0.05 * intensity, 0.1)
                )
            except Exception as e:
                # Fail gracefully if noise can't be added
                print(f"Warning: Couldn't add noise to vintage effect: {e}")
                # Continue without adding noise

        # Restore alpha channel if it was present
        if alpha:
            r, g, b = vintage_img.split()
            vintage_img = Image.merge("RGBA", (r, g, b, alpha))

        return vintage_img

    def apply_color_temperature(self, image, temperature):
        """
        Apply color temperature adjustment to an image.
        Positive values for warm (yellow/orange), negative for cool (blue).
        """
        # The intensity range is 0-3, scale appropriately
        temp_shifted = abs(temperature) * 0.15  # Max ±0.45

        # Handle alpha channel
        has_alpha = image.mode == "RGBA"
        alpha = None
        if has_alpha:
            alpha = image.split()[3]
            image = image.convert("RGB")

        # Split image into RGB
        r, g, b = image.split()

        # Adjust levels based on temperature direction
        if temperature > 0:  # Warm (increase red/green, decrease blue)
            r = ImageEnhance.Brightness(r).enhance(1 + temp_shifted)
            g = ImageEnhance.Brightness(g).enhance(1 + temp_shifted * 0.5)
            b = ImageEnhance.Brightness(b).enhance(1 - temp_shifted * 0.5)
        else:  # Cool (increase blue, decrease red/green)
            r = ImageEnhance.Brightness(r).enhance(1 - temp_shifted * 0.5)
            g = ImageEnhance.Brightness(g).enhance(1 - temp_shifted * 0.3)
            b = ImageEnhance.Brightness(b).enhance(1 + temp_shifted)

        # Merge back
        result = Image.merge("RGB", (r, g, b))

        # Restore alpha if needed
        if has_alpha and alpha is not None:
            r, g, b = result.split()
            result = Image.merge("RGBA", (r, g, b, alpha))

        return result

    def apply_dramatic(self, image, intensity=1.0):
        """Apply a dramatic high-contrast look to the image."""
        # Make a copy and preserve mode
        original_mode = image.mode
        dramatic = image.copy()

        # Convert to RGB for processing
        if original_mode == "RGBA":
            # Save the alpha channel
            alpha = dramatic.split()[3]
            dramatic = dramatic.convert("RGB")
        else:
            alpha = None
            dramatic = dramatic.convert("RGB")

        # 1. Increase contrast significantly
        enhancer = cast(Any, ImageEnhance.Contrast(dramatic))
        dramatic = enhancer.enhance(1.5 + intensity * 0.5)

        # 2. Increase brightness slightly for a lifted shadows look
        enhancer = cast(Any, ImageEnhance.Brightness(dramatic))
        dramatic = enhancer.enhance(1.1)

        # 3. Reduce saturation for a more cinematic look
        enhancer = cast(Any, ImageEnhance.Color(dramatic))
        dramatic = enhancer.enhance(0.8 - intensity * 0.2)

        # 4. Create a vignette manually instead of using apply_vignette
        # to avoid mode conversion issues
        img_width, img_height = dramatic.size

        # Create an oval mask for vignette
        mask = Image.new("L", dramatic.size, 255)
        draw = ImageDraw.Draw(mask)

        # Draw oval
        width_offset = int(img_width * 0.15 * intensity * 0.7)
        height_offset = int(img_height * 0.15 * intensity * 0.7)
        draw.ellipse(
            (
                width_offset,
                height_offset,
                img_width - width_offset,
                img_height - height_offset,
            ),
            fill=255,
        )

        # Blur the mask
        blur_radius = max(20, int(min(img_width, img_height) * 0.03 * intensity * 0.7))
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Invert and adjust the mask intensity
        mask = ImageOps.invert(mask)
        mask = Image.eval(mask, lambda x: int(x * 0.6))  # Adjust vignette intensity

        # Apply the mask to create the vignette effect
        r, g, b = dramatic.split()
        r = ImageChops.multiply(r, ImageOps.invert(mask))
        g = ImageChops.multiply(g, ImageOps.invert(mask))
        b = ImageChops.multiply(b, ImageOps.invert(mask))
        dramatic = Image.merge("RGB", (r, g, b))

        # Restore alpha channel if original image was RGBA
        if original_mode == "RGBA" and alpha is not None:
            dramatic = dramatic.convert("RGBA")
            r, g, b, _ = dramatic.split()
            dramatic = Image.merge("RGBA", (r, g, b, alpha))

        return dramatic

    def setup_adjustments_tab(self):
        """Set up the adjustments tab."""
        adjustments_tab = QWidget()
        layout = QVBoxLayout(adjustments_tab)

        # Add a preview area at the top of the adjustments tab
        self.adjustment_preview = ImagePreviewWidget()
        self.adjustment_preview.setMinimumHeight(200)
        if self.working_image:
            self.adjustment_preview.set_image(self.pil_to_pixmap(self.working_image))
        layout.addWidget(self.adjustment_preview)

        # Adjustments group
        adjustments_group = QGroupBox("Adjustments")
        adjustments_layout = QFormLayout()

        # Brightness
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(
            lambda: self.preview_adjustment("brightness")
        )
        adjustments_layout.addRow("Brightness:", self.brightness_slider)

        # Contrast
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(
            lambda: self.preview_adjustment("contrast")
        )
        adjustments_layout.addRow("Contrast:", self.contrast_slider)

        # Saturation
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(
            lambda: self.preview_adjustment("saturation")
        )
        adjustments_layout.addRow("Saturation:", self.saturation_slider)

        # Sharpness
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setRange(-100, 100)
        self.sharpness_slider.setValue(0)
        self.sharpness_slider.valueChanged.connect(
            lambda: self.preview_adjustment("sharpness")
        )
        adjustments_layout.addRow("Sharpness:", self.sharpness_slider)

        adjustments_group.setLayout(adjustments_layout)
        layout.addWidget(adjustments_group)

        # Apply button
        apply_adjustments_button = QPushButton("Apply Adjustments")
        apply_adjustments_button.clicked.connect(self.apply_adjustments)
        layout.addWidget(apply_adjustments_button)

        # Reset adjustments button
        reset_button = QPushButton("Reset Adjustments")
        reset_button.clicked.connect(self.reset_adjustments)
        layout.addWidget(reset_button)

        # Add stretch to push everything to the top
        layout.addStretch()

        self.tab_widget.addTab(adjustments_tab, "Adjustments")

    def setup_crop_tab(self):
        """Set up the crop tab."""
        crop_tab = QWidget()
        layout = QVBoxLayout(crop_tab)

        # Crop preview area
        self.crop_preview = ImagePreviewWidget()
        self.crop_preview.setMinimumHeight(200)
        if self.working_image:
            self.crop_preview.set_image(self.pil_to_pixmap(self.working_image))
        layout.addWidget(self.crop_preview)

        # Crop controls
        crop_group = QGroupBox("Crop Settings")
        crop_layout = QGridLayout()

        # Aspect ratio selection
        aspect_label = QLabel("Aspect Ratio:")
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(
            [
                "Free Form",
                "Original",
                "Square (1:1)",
                "16:9",
                "4:3",
                "3:2",
                "2:1",
                "Custom...",
            ]
        )
        self.aspect_combo.currentTextChanged.connect(self.on_aspect_ratio_changed)
        crop_layout.addWidget(aspect_label, 0, 0)
        crop_layout.addWidget(self.aspect_combo, 0, 1)

        # X position
        x_label = QLabel("X:")
        self.crop_x = QSpinBox()
        self.crop_x.setRange(0, 9999)
        self.crop_x.valueChanged.connect(self.update_crop_preview)
        crop_layout.addWidget(x_label, 1, 0)
        crop_layout.addWidget(self.crop_x, 1, 1)

        # Y position
        y_label = QLabel("Y:")
        self.crop_y = QSpinBox()
        self.crop_y.setRange(0, 9999)
        self.crop_y.valueChanged.connect(self.update_crop_preview)
        crop_layout.addWidget(y_label, 2, 0)
        crop_layout.addWidget(self.crop_y, 2, 1)

        # Width
        width_label = QLabel("Width:")
        self.crop_width = QSpinBox()
        self.crop_width.setRange(1, 9999)
        self.crop_width.valueChanged.connect(self.on_crop_width_changed)
        crop_layout.addWidget(width_label, 3, 0)
        crop_layout.addWidget(self.crop_width, 3, 1)

        # Height
        height_label = QLabel("Height:")
        self.crop_height = QSpinBox()
        self.crop_height.setRange(1, 9999)
        self.crop_height.valueChanged.connect(self.on_crop_height_changed)
        crop_layout.addWidget(height_label, 4, 0)
        crop_layout.addWidget(self.crop_height, 4, 1)

        # Set values if image exists
        if self.working_image:
            width, height = self.working_image.size
            self.crop_width.setValue(width)
            self.crop_height.setValue(height)

            # Set maximum ranges based on image dimensions
            self.crop_x.setRange(0, width - 1)
            self.crop_y.setRange(0, height - 1)
            self.crop_width.setRange(1, width)
            self.crop_height.setRange(1, height)

        crop_group.setLayout(crop_layout)
        layout.addWidget(crop_group)

        # Apply crop button
        apply_crop_button = QPushButton("Apply Crop")
        apply_crop_button.clicked.connect(self.apply_crop)
        layout.addWidget(apply_crop_button)

        # Add stretch to push everything to the top
        layout.addStretch()

        self.tab_widget.addTab(crop_tab, "Crop")

        # Store the current aspect ratio mode
        self.current_aspect_ratio = "Free Form"
        self.custom_aspect_ratio = 1.0  # Default to 1:1

    def on_aspect_ratio_changed(self, ratio_text):
        """Handle change of aspect ratio selection."""
        self.current_aspect_ratio = ratio_text

        if (
            ratio_text == "Custom..."
            and hasattr(self, "aspect_combo")
            and self.aspect_combo is not None
        ):
            # Prompt for custom ratio
            custom_ratio, ok = QInputDialog.getText(
                self,
                "Custom Aspect Ratio",
                "Enter aspect ratio (width:height):",
                QLineEdit.EchoMode.Normal,
                "16:9",
            )

            if ok and custom_ratio:
                try:
                    # Parse the ratio
                    width_part, height_part = custom_ratio.split(":")
                    width_value = float(width_part.strip())
                    height_value = float(height_part.strip())

                    if width_value <= 0 or height_value <= 0:
                        raise ValueError("Values must be positive")

                    self.custom_aspect_ratio = width_value / height_value
                    self.current_aspect_ratio = f"Custom ({custom_ratio})"

                    # Update combo box text
                    index = self.aspect_combo.findText("Custom...")
                    if index >= 0:
                        self.aspect_combo.setItemText(index, self.current_aspect_ratio)

                except (ValueError, ZeroDivisionError):
                    QMessageBox.warning(
                        self,
                        "Invalid Ratio",
                        "Please enter a valid ratio in the format width:height",
                    )
                    # Reset to free form
                    if self.aspect_combo is not None:
                        self.aspect_combo.setCurrentText("Free Form")
                    self.current_aspect_ratio = "Free Form"
                    return
            else:
                # User cancelled, reset to free form
                if self.aspect_combo is not None:
                    self.aspect_combo.setCurrentText("Free Form")
                self.current_aspect_ratio = "Free Form"
                return

        # Apply the aspect ratio constraint
        self.apply_aspect_ratio_constraint()

    def apply_aspect_ratio_constraint(self):
        """Apply the current aspect ratio constraint to the crop dimensions."""
        if not self.working_image:
            return

        # Get current crop values
        x = self.crop_x.value()
        y = self.crop_y.value()
        width = self.crop_width.value()
        height = self.crop_height.value()

        # Calculate new dimensions based on aspect ratio
        if self.current_aspect_ratio == "Free Form":
            # No constraint, keep current values
            pass
        elif self.current_aspect_ratio == "Original":
            # Use original image aspect ratio
            orig_width, orig_height = self.working_image.size
            aspect = orig_width / orig_height
            height = int(width / aspect)
        elif self.current_aspect_ratio == "Square (1:1)":
            # Make height equal to width
            height = width
        elif self.current_aspect_ratio == "16:9":
            height = int(width * 9 / 16)
        elif self.current_aspect_ratio == "4:3":
            height = int(width * 3 / 4)
        elif self.current_aspect_ratio == "3:2":
            height = int(width * 2 / 3)
        elif self.current_aspect_ratio == "2:1":
            height = int(width / 2)
        elif self.current_aspect_ratio.startswith("Custom"):
            # Use custom aspect ratio
            height = int(width / self.custom_aspect_ratio)

        # Ensure dimensions are within image bounds
        img_width, img_height = self.working_image.size

        # Adjust width and height to fit within image bounds
        if x + width > img_width:
            width = img_width - x
        if y + height > img_height:
            height = img_height - y

            # If height was adjusted, recalculate width based on aspect ratio
            if self.current_aspect_ratio != "Free Form":
                if self.current_aspect_ratio == "Square (1:1)":
                    width = height
                elif self.current_aspect_ratio == "16:9":
                    width = int(height * 16 / 9)
                elif self.current_aspect_ratio == "4:3":
                    width = int(height * 4 / 3)
                elif self.current_aspect_ratio == "3:2":
                    width = int(height * 3 / 2)
                elif self.current_aspect_ratio == "2:1":
                    width = int(height * 2)
                elif self.current_aspect_ratio == "Original":
                    orig_width, orig_height = self.working_image.size
                    width = int(height * orig_width / orig_height)
                elif self.current_aspect_ratio.startswith("Custom"):
                    width = int(height * self.custom_aspect_ratio)

        # Update the spin boxes without triggering recursive updates
        self.crop_width.blockSignals(True)
        self.crop_height.blockSignals(True)

        self.crop_width.setValue(width)
        self.crop_height.setValue(height)

        self.crop_width.blockSignals(False)
        self.crop_height.blockSignals(False)

        # Update the preview
        self.update_crop_preview()

    def on_crop_width_changed(self, new_width):
        """Handle change of crop width value."""
        # new_width parameter is required by Qt signal but not used directly
        if self.current_aspect_ratio != "Free Form":
            # Adjust height based on aspect ratio
            self.apply_aspect_ratio_constraint()
        else:
            self.update_crop_preview()

    def on_crop_height_changed(self, new_height):
        """Handle change of crop height value."""
        if self.current_aspect_ratio != "Free Form":
            # Adjust width based on aspect ratio
            self.crop_width.blockSignals(True)

            if self.current_aspect_ratio == "Square (1:1)":
                self.crop_width.setValue(new_height)
            elif self.current_aspect_ratio == "16:9":
                self.crop_width.setValue(int(new_height * 16 / 9))
            elif self.current_aspect_ratio == "4:3":
                self.crop_width.setValue(int(new_height * 4 / 3))
            elif self.current_aspect_ratio == "3:2":
                self.crop_width.setValue(int(new_height * 3 / 2))
            elif self.current_aspect_ratio == "2:1":
                self.crop_width.setValue(int(new_height * 2))
            elif (
                self.current_aspect_ratio == "Original"
                and self.working_image is not None
            ):
                orig_width, orig_height = self.working_image.size
                self.crop_width.setValue(int(new_height * orig_width / orig_height))
            elif self.current_aspect_ratio.startswith("Custom"):
                self.crop_width.setValue(int(new_height * self.custom_aspect_ratio))

            self.crop_width.blockSignals(False)

        self.update_crop_preview()

    def update_crop_preview(self):
        """Update the crop preview with the current working image."""
        if (
            not self.working_image
            or not hasattr(self, "crop_preview")
            or self.crop_preview is None
        ):
            return

        # Convert PIL Image to QImage
        data = self.working_image.convert("RGBA").tobytes("raw", "RGBA")
        qimg = QImage(
            data,
            self.working_image.width,
            self.working_image.height,
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(qimg)
        self.crop_preview.set_image(pixmap)

    def update_preview(self):
        """Update the main preview with the current working image."""
        if not self.working_image:
            return

        # Reset comparison mode - add null check before accessing attribute
        if (
            hasattr(self, "compare_checkbox")
            and self.compare_checkbox is not None
            and self.compare_checkbox.isChecked()
        ):
            self.compare_checkbox.setChecked(False)

        # Update the preview
        pixmap = self.pil_to_pixmap(self.working_image)
        self.preview.set_image(pixmap)

        # Update transform preview if it exists - already has null check
        self.update_transform_preview()

        # Also update adjustment preview if it exists
        if hasattr(self, "adjustment_preview") and self.adjustment_preview is not None:
            self.adjustment_preview.set_image(pixmap)

    def update_filter_preview(self):
        """Update the filter tab preview."""
        if not self.working_image:
            return

        if not hasattr(self, "filter_preview") or self.filter_preview is None:
            return

        pixmap = self.pil_to_pixmap(self.working_image)
        self.filter_preview.set_image(pixmap)

        # Apply current filter if selected
        if hasattr(self, "filter_combo") and self.filter_combo is not None:
            filter_name = self.filter_combo.currentText()
            if filter_name != "None":
                self.apply_filter()

    def reset_image(self):
        """Reset to the original image."""
        if self.original_image:
            self.working_image = self.original_image.copy()
            self.update_preview()
            self.update_crop_preview()
            self.reset_adjustments()

    def reset_adjustments(self):
        """Reset all adjustment sliders."""
        if hasattr(self, "brightness_slider") and self.brightness_slider is not None:
            self.brightness_slider.setValue(0)
        if hasattr(self, "contrast_slider") and self.contrast_slider is not None:
            self.contrast_slider.setValue(0)
        if hasattr(self, "saturation_slider") and self.saturation_slider is not None:
            self.saturation_slider.setValue(0)
        if hasattr(self, "sharpness_slider") and self.sharpness_slider is not None:
            self.sharpness_slider.setValue(0)
        if hasattr(self, "filter_combo") and self.filter_combo is not None:
            self.filter_combo.setCurrentText("None")

    def reset_crop(self):
        """Reset the crop selection."""
        self.crop_preview.reset_image()
        self.update_crop_preview()

    def apply_selected_filter(self):
        """Apply the selected filter permanently to the working image."""
        filter_name = self.filter_combo.currentText()

        if filter_name == "None":
            return  # No filter to apply

        if not self.working_image:
            return

        try:
            # Get intensity value (0-100 to 0.0-3.0 range)
            intensity = self.intensity_slider.value() / 100.0 * 3.0

            # Apply the filter permanently
            if filter_name == "Blur":
                # Use intensity for blur radius
                blur_radius = max(0.5, intensity * 2.5)
                self.working_image = self.working_image.filter(
                    ImageFilter.GaussianBlur(radius=blur_radius)
                )
            elif filter_name == "Sharpen":
                # Apply sharpen multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    self.working_image = self.working_image.filter(ImageFilter.SHARPEN)
            elif filter_name == "Contour":
                self.working_image = self.working_image.filter(ImageFilter.CONTOUR)
            elif filter_name == "Detail":
                self.working_image = self.working_image.filter(ImageFilter.DETAIL)
            elif filter_name == "Smooth":
                # Apply smooth multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    self.working_image = self.working_image.filter(ImageFilter.SMOOTH)
            elif filter_name == "Emboss":
                self.working_image = self.working_image.filter(ImageFilter.EMBOSS)
            elif filter_name == "Edge Enhance":
                # Apply edge enhance multiple times based on intensity
                repeat = int(intensity * 2) + 1
                for _ in range(repeat):
                    self.working_image = self.working_image.filter(
                        ImageFilter.EDGE_ENHANCE
                    )
            elif filter_name == "Find Edges":
                self.working_image = self.working_image.filter(ImageFilter.FIND_EDGES)
            elif filter_name == "Grayscale":
                self.working_image = ImageOps.grayscale(self.working_image)
                # Convert back to RGB mode for consistent handling
                self.working_image = Image.merge(
                    "RGB", [self.working_image, self.working_image, self.working_image]
                )
            elif filter_name == "Sepia":
                self.working_image = self.apply_sepia(self.working_image, intensity)
            elif filter_name == "Negative":
                # Convert to RGB for invert operation if in RGBA mode
                if self.working_image.mode == "RGBA":
                    # Save the alpha channel
                    r, g, b, a = self.working_image.split()
                    rgb_image = Image.merge("RGB", (r, g, b))
                    # Invert the RGB channels
                    inverted_rgb = ImageOps.invert(rgb_image)
                    # Merge back with original alpha channel
                    r, g, b = inverted_rgb.split()
                    self.working_image = Image.merge("RGBA", (r, g, b, a))
                else:
                    self.working_image = ImageOps.invert(
                        self.working_image.convert("RGB")
                    )
            elif filter_name == "Posterize":
                # Use intensity to determine levels (2-8)
                levels = max(2, min(8, int(intensity * 6 / 3.0) + 2))

                # Posterize doesn't support RGBA mode, so handle alpha channel separately
                if self.working_image.mode == "RGBA":
                    # Split the image into channels
                    r, g, b, a = self.working_image.split()
                    # Merge RGB channels
                    rgb_image = Image.merge("RGB", (r, g, b))
                    # Apply posterize to RGB image
                    posterized = ImageOps.posterize(rgb_image, levels)
                    # Split the posterized image
                    r2, g2, b2 = posterized.split()
                    # Merge with original alpha channel
                    self.working_image = Image.merge("RGBA", (r2, g2, b2, a))
                else:
                    # If not RGBA, just convert to RGB and apply
                    self.working_image = ImageOps.posterize(
                        self.working_image.convert("RGB"), levels
                    )
            elif filter_name == "Solarize":
                # Solarize inverts all pixel values above a threshold
                threshold = int(
                    128 * (1 - intensity / 3.0)
                )  # Higher intensity means more solarization

                # Handle alpha channel separately if needed
                if self.working_image.mode == "RGBA":
                    r, g, b, a = self.working_image.split()
                    rgb_image = Image.merge("RGB", (r, g, b))
                    solarized = ImageOps.solarize(rgb_image, threshold)
                    r2, g2, b2 = solarized.split()
                    self.working_image = Image.merge("RGBA", (r2, g2, b2, a))
                else:
                    self.working_image = ImageOps.solarize(
                        self.working_image.convert("RGB"), threshold
                    )
            elif filter_name == "Vignette":
                self.working_image = self.apply_vignette(self.working_image, intensity)
            elif filter_name == "Vintage":
                self.working_image = self.apply_vintage_effect(
                    self.working_image, intensity
                )
            elif filter_name == "Cold":
                self.working_image = self.apply_color_temperature(
                    self.working_image, -intensity
                )  # Negative for cold
            elif filter_name == "Warm":
                self.working_image = self.apply_color_temperature(
                    self.working_image, intensity
                )
            elif filter_name == "Dramatic":
                self.working_image = self.apply_dramatic(self.working_image, intensity)
            elif filter_name == "Noise Reduction":
                # More intensity = more noise reduction
                radius = max(0.5, intensity * 0.5)
                self.working_image = self.working_image.filter(
                    ImageFilter.MedianFilter(size=int(radius * 2) + 1)
                )

            # Reset filter selection
            self.filter_combo.setCurrentText("None")

            # Update all previews
            self.update_preview()
            self.update_crop_preview()

        except Exception as e:
            print(f"Error applying filter {filter_name} permanently: {e}")

    def preview_adjustment(self, adjustment_type):
        """Preview an adjustment on the image."""
        if not self.working_image:
            return

        # Create a temporary image for preview
        temp_image = self.working_image.copy()

        # Apply the adjustments
        try:
            if adjustment_type == "brightness" and hasattr(self, "brightness_slider"):
                value = 1.0 + (self.brightness_slider.value() / 100.0)
                enhancer = cast(Any, ImageEnhance.Brightness(temp_image))
                temp_image = enhancer.enhance(value)
            elif adjustment_type == "contrast" and hasattr(self, "contrast_slider"):
                value = 1.0 + (self.contrast_slider.value() / 100.0)
                enhancer = cast(Any, ImageEnhance.Contrast(temp_image))
                temp_image = enhancer.enhance(value)
            elif adjustment_type == "saturation" and hasattr(self, "saturation_slider"):
                value = 1.0 + (self.saturation_slider.value() / 100.0)
                enhancer = cast(Any, ImageEnhance.Color(temp_image))
                temp_image = enhancer.enhance(value)
            elif adjustment_type == "sharpness" and hasattr(self, "sharpness_slider"):
                value = 1.0 + (self.sharpness_slider.value() / 100.0)
                enhancer = cast(Any, ImageEnhance.Sharpness(temp_image))
                temp_image = enhancer.enhance(value)
        except Exception as e:
            print(f"Error applying adjustment {adjustment_type}: {e}")
            return

        # Update the preview with the adjusted image
        pixmap = self.pil_to_pixmap(temp_image)

        if hasattr(self, "preview") and self.preview is not None:
            self.preview.set_image(pixmap)

        # Update the adjustment tab preview
        if hasattr(self, "adjustment_preview") and self.adjustment_preview is not None:
            self.adjustment_preview.set_image(pixmap)

    def apply_adjustments(self):
        """Apply all adjustments permanently to the working image."""
        if not self.working_image:
            return

        try:
            # Apply the adjustments in sequence

            # Brightness
            if (
                hasattr(self, "brightness_slider")
                and self.brightness_slider is not None
            ):
                value = 1.0 + (self.brightness_slider.value() / 100.0)
                if value != 1.0:
                    enhancer = cast(Any, ImageEnhance.Brightness(self.working_image))
                    self.working_image = enhancer.enhance(value)

            # Contrast
            if hasattr(self, "contrast_slider") and self.contrast_slider is not None:
                value = 1.0 + (self.contrast_slider.value() / 100.0)
                if value != 1.0:
                    enhancer = cast(Any, ImageEnhance.Contrast(self.working_image))
                    self.working_image = enhancer.enhance(value)

            # Saturation
            if (
                hasattr(self, "saturation_slider")
                and self.saturation_slider is not None
            ):
                value = 1.0 + (self.saturation_slider.value() / 100.0)
                if value != 1.0:
                    enhancer = cast(Any, ImageEnhance.Color(self.working_image))
                    self.working_image = enhancer.enhance(value)

            # Sharpness
            if hasattr(self, "sharpness_slider") and self.sharpness_slider is not None:
                value = 1.0 + (self.sharpness_slider.value() / 100.0)
                if value != 1.0:
                    enhancer = cast(Any, ImageEnhance.Sharpness(self.working_image))
                    self.working_image = enhancer.enhance(value)

            # Reset sliders
            self.reset_adjustments()

            # Update all previews
            self.update_preview()
            self.update_crop_preview()
        except Exception as e:
            print(f"Error applying adjustments: {e}")

    def apply_crop(self):
        """Apply the crop to the working image."""
        if not self.working_image:
            return

        crop_rect = self.crop_preview.get_current_crop()
        if crop_rect is None or crop_rect.width() <= 10 or crop_rect.height() <= 10:
            return

        # Apply the crop
        self.working_image = self.working_image.crop(
            (
                crop_rect.x(),
                crop_rect.y(),
                crop_rect.x() + crop_rect.width(),
                crop_rect.y() + crop_rect.height(),
            )
        )

        # Update all previews
        self.update_preview()
        self.update_crop_preview()

        # Reset crop info
        self.update_crop_preview()

    def save_image_as(self):
        """Save the edited image to a file."""
        if not self.working_image:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        # Add extension if not present
        if not any(
            file_path.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".bmp")
        ):
            file_path += ".png"

        try:
            self.working_image.save(file_path)
            self.path_label.setText(file_path)
            self.image_format.setName(file_path)
        except Exception as e:
            print(f"Error saving image: {e}")

    def pil_to_pixmap(self, pil_image):
        """Convert a PIL Image to a QPixmap."""
        if not pil_image:
            return QPixmap()

        # Convert PIL Image to QImage
        data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
        qimg = QImage(
            data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888
        )

        return QPixmap.fromImage(qimg)

    def accept(self):
        """Handle dialog acceptance and prepare the edited image for embedding."""
        if not self.working_image:
            super().accept()
            return

        # Store final results
        self.result_image = self.working_image.copy()

        # Resize to final dimensions if needed
        if (
            self.result_image.width != self.final_width
            or self.result_image.height != self.final_height
        ):
            self.result_image = self.result_image.resize(
                (self.final_width, self.final_height), Resampling.LANCZOS
            )

        # Convert to QPixmap
        self.result_pixmap = self.pil_to_pixmap(self.result_image)

        # Create a data URI directly from the edited image
        try:
            # Determine the format (keep original when possible)
            save_format = "PNG"  # Default
            mime_type = "image/png"

            orig_path = self.image_format.name()
            if orig_path.startswith("data:"):
                # Try to extract mime type from original data URI
                import re

                match = re.match(r"data:(.*?);base64,", orig_path)
                if match:
                    mime_type = match.group(1)
                    if "jpeg" in mime_type:
                        save_format = "JPEG"
                    elif "gif" in mime_type:
                        save_format = "GIF"
            else:
                # Try to determine from file extension
                if orig_path.lower().endswith((".jpg", ".jpeg")):
                    save_format = "JPEG"
                    mime_type = "image/jpeg"
                elif orig_path.lower().endswith(".gif"):
                    save_format = "GIF"
                    mime_type = "image/gif"

            # Save to a byte buffer
            import io, base64

            buffer = io.BytesIO()
            self.result_image.save(buffer, format=save_format)
            img_data = buffer.getvalue()

            # Create data URI
            img_base64 = base64.b64encode(img_data).decode("utf-8")
            data_uri = f"data:{mime_type};base64,{img_base64}"

            # Store the data URI as the result path
            self._result_path = data_uri
            print(f"Created data URI from edited image (length: {len(data_uri)})")

        except Exception as e:
            print(f"Error creating data URI from edited image: {e}")

            # Fallback method - save to a temporary file
            try:
                # Get the original path
                orig_path = self.image_format.name()
                if orig_path.startswith("data:"):
                    # For data URIs, create a temp directory
                    import tempfile, os, uuid

                    temp_dir = tempfile.gettempdir()
                    edit_dir = os.path.join(temp_dir, "edited_images")
                else:
                    # For file paths, use the original directory
                    import os

                    dir_path = os.path.dirname(orig_path)
                    edit_dir = os.path.join(dir_path, "edited_images")

                # Create a directory for edited images if it doesn't exist
                os.makedirs(edit_dir, exist_ok=True)

                # Generate a unique filename
                file_ext = ".png"  # Default
                if orig_path.lower().endswith((".jpg", ".jpeg")):
                    file_ext = ".jpg"
                elif orig_path.lower().endswith(".gif"):
                    file_ext = ".gif"

                unique_name = f"edited_image_{uuid.uuid4().hex[:8]}{file_ext}"
                save_path = os.path.join(edit_dir, unique_name)

                # Save the edited image
                print(f"Saving edited image to {save_path}")
                self.result_image.save(save_path)

                # Update the result path for retrieval by the editor window
                self._result_path = save_path

                # Log success
                print(f"Image edited successfully and saved to {save_path}")
            except Exception as inner_e:
                print(f"Error in fallback save method: {inner_e}")
                # If all else fails, just return the original path
                self._result_path = self.image_format.name()

        # Call parent class accept to close the dialog
        super().accept()

    def get_result_image(self):
        """Get the resulting PIL Image."""
        return self.result_image

    def get_result_pixmap(self):
        """Get the resulting QPixmap."""
        return self.result_pixmap

    def get_result_path(self):
        """Get the path of the edited image."""
        # Return the path where we saved the edited image
        if hasattr(self, "_result_path"):
            return self._result_path
        return self.image_format.name()

    def get_new_dimensions(self):
        """Get the dimensions of the edited image."""
        if self.result_image:
            return self.result_image.width, self.result_image.height
        return self.final_width, self.final_height

    def setup_preview_tab(self):
        """Set up the preview tab with rotation and flipping tools."""
        preview_tab = QWidget()
        layout = QVBoxLayout(preview_tab)

        # Preview area
        self.preview2 = ImagePreviewWidget()
        self.preview2.setMinimumHeight(300)
        if self.working_image:
            self.preview2.set_image(self.pil_to_pixmap(self.working_image))
        layout.addWidget(self.preview2)

        # Add transformation tools
        transform_group = QGroupBox("Transform")
        transform_layout = QHBoxLayout()

        # Rotation buttons
        rotate_left_btn = QPushButton("Rotate Left")
        rotate_left_btn.setIcon(QIcon.fromTheme("object-rotate-left", QIcon()))
        rotate_left_btn.clicked.connect(lambda: self.rotate_image(-90))

        rotate_right_btn = QPushButton("Rotate Right")
        rotate_right_btn.setIcon(QIcon.fromTheme("object-rotate-right", QIcon()))
        rotate_right_btn.clicked.connect(lambda: self.rotate_image(90))

        rotate_180_btn = QPushButton("Rotate 180°")
        rotate_180_btn.clicked.connect(lambda: self.rotate_image(180))

        # Flip buttons
        flip_h_btn = QPushButton("Flip Horizontal")
        flip_h_btn.clicked.connect(lambda: self.flip_image("horizontal"))

        flip_v_btn = QPushButton("Flip Vertical")
        flip_v_btn.clicked.connect(lambda: self.flip_image("vertical"))

        # Add buttons to layout
        transform_layout.addWidget(rotate_left_btn)
        transform_layout.addWidget(rotate_right_btn)
        transform_layout.addWidget(rotate_180_btn)
        transform_layout.addWidget(flip_h_btn)
        transform_layout.addWidget(flip_v_btn)

        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)

        # Add zoom controls
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QHBoxLayout()

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.setIcon(QIcon.fromTheme("zoom-out", QIcon()))
        zoom_out_btn.clicked.connect(
            lambda: self.preview2
            and self.preview2.set_zoom(self.preview2.zoom_factor - 0.1)
        )

        zoom_reset_btn = QPushButton("Reset (100%)")
        zoom_reset_btn.clicked.connect(
            lambda: self.preview2 and self.preview2.set_zoom(1.0)
        )

        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.setIcon(QIcon.fromTheme("zoom-in", QIcon()))
        zoom_in_btn.clicked.connect(
            lambda: self.preview2
            and self.preview2.set_zoom(self.preview2.zoom_factor + 0.1)
        )

        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(zoom_reset_btn)
        zoom_layout.addWidget(zoom_in_btn)

        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)

        # Add comparison toggle
        compare_layout = QHBoxLayout()
        self.compare_checkbox = QCheckBox("Show Before/After Comparison")
        self.compare_checkbox.toggled.connect(self.toggle_comparison)
        compare_layout.addWidget(self.compare_checkbox)

        # Add color picker button
        color_picker_btn = QPushButton("Color Picker")
        color_picker_btn.clicked.connect(self.pick_color)
        compare_layout.addWidget(color_picker_btn)

        self.color_display = QLabel()
        self.color_display.setFixedSize(30, 20)
        self.color_display.setAutoFillBackground(True)
        self.color_display.setStyleSheet(
            "background-color: none; border: 1px solid black;"
        )
        compare_layout.addWidget(self.color_display)

        self.color_hex = QLineEdit()
        self.color_hex.setFixedWidth(80)
        self.color_hex.setReadOnly(True)
        self.color_hex.setPlaceholderText("#RRGGBB")
        compare_layout.addWidget(self.color_hex)

        layout.addLayout(compare_layout)

        layout.addStretch()
        self.tab_widget.addTab(preview_tab, "Transform")

        # Store original image for comparison
        if self.working_image:
            self.original_image_copy = self.working_image.copy()

    def rotate_image(self, degrees):
        """Rotate the working image by the specified degrees."""
        if not self.working_image:
            return

        try:
            # Rotate the image
            self.working_image = self.working_image.rotate(
                degrees, expand=True, resample=Resampling.BICUBIC
            )

            # Update all previews
            self.update_preview()
            self.update_filter_preview()
            self.update_crop_preview()
            self.update_transform_preview()
        except Exception as e:
            print(f"Error rotating image: {e}")

    def flip_image(self, direction):
        """Flip the working image horizontally or vertically."""
        if not self.working_image:
            return

        try:
            if direction == "horizontal":
                self.working_image = ImageOps.mirror(self.working_image)
            elif direction == "vertical":
                self.working_image = ImageOps.flip(self.working_image)

            # Update all previews
            self.update_preview()
            self.update_filter_preview()
            self.update_crop_preview()
            self.update_transform_preview()
        except Exception as e:
            print(f"Error flipping image: {e}")

    def toggle_comparison(self, checked):
        """Toggle between showing the current image and a side-by-side comparison."""
        if (
            not hasattr(self, "original_image_copy")
            or self.original_image_copy is None
            or not self.working_image
        ):
            return

        if not hasattr(self, "preview2") or self.preview2 is None:
            return

        if checked:
            # Create a side-by-side comparison image
            width = self.original_image_copy.width * 2
            height = max(self.original_image_copy.height, self.working_image.height)

            comparison = Image.new("RGBA", (width, height), (255, 255, 255, 255))

            # Paste original on left
            comparison.paste(self.original_image_copy, (0, 0))

            # Paste working image on right
            comparison.paste(self.working_image, (self.original_image_copy.width, 0))

            # Draw a separator line
            draw = ImageDraw.Draw(comparison)
            draw.line(
                [
                    (self.original_image_copy.width, 0),
                    (self.original_image_copy.width, height),
                ],
                fill=(0, 0, 0),
                width=2,
            )

            # Add "Before" and "After" labels
            font = None
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                pass

            draw.text((10, 10), "Before", fill=(0, 0, 0), font=font)
            draw.text(
                (self.original_image_copy.width + 10, 10),
                "After",
                fill=(0, 0, 0),
                font=font,
            )

            # Show comparison
            self.preview2.set_image(self.pil_to_pixmap(comparison))
        else:
            # Show only the working image
            self.update_transform_preview()

    def pick_color(self):
        """Enable color picking mode on the preview image."""
        if (
            not self.working_image
            or not hasattr(self, "preview2")
            or self.preview2 is None
        ):
            return

        QMessageBox.information(
            self, "Color Picker", "Click anywhere on the image to pick a color."
        )

        # Enable click handling on the preview widget
        self.preview2.enable_color_picking(self.working_image, self.on_color_picked)

    def on_color_picked(self, color):
        """Handle when a color is picked from the image."""
        if not color:
            return

        if not hasattr(self, "color_display") or self.color_display is None:
            return

        if not hasattr(self, "color_hex") or self.color_hex is None:
            return

        # Update color display
        palette = self.color_display.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.color_display.setPalette(palette)

        # Update hex value
        self.color_hex.setText(color.name().upper())

        # Disable picking mode
        if hasattr(self, "preview2") and self.preview2 is not None:
            self.preview2.disable_color_picking()

    def update_transform_preview(self):
        """Update the transform tab preview."""
        if (
            not self.working_image
            or not hasattr(self, "preview2")
            or self.preview2 is None
        ):
            return

        pixmap = self.pil_to_pixmap(self.working_image)
        self.preview2.set_image(pixmap)
