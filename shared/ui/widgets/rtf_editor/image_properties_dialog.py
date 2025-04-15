# src/ui/components/rtf_editor/image_properties_dialog.py
import base64
import io
import os
import re
import sys
from pathlib import Path

from PIL import Image  # Use Pillow to get original dimensions accurately
from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QPixmap, QTextImageFormat
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)


class ImagePropertiesDialog(QDialog):
    """Dialog for viewing and editing image properties.

    This dialog allows users to view and modify properties of an image in the document,
    including:
    - Width and height
    - Aspect ratio (with option to maintain or break it)
    - Original dimensions
    - Preview of the image

    It works with both embedded images (data URIs) and linked images (file paths).

    Attributes:
        image_format (QTextImageFormat): The format of the image being edited
        original_width (int): The original width of the image
        original_height (int): The original height of the image
        aspect_ratio (float): The aspect ratio of the image (height/width)
    """

    def __init__(self, image_format, parent=None):
        """Initialize the image properties dialog.

        Creates a dialog for editing image properties based on the provided image format.
        Loads the original dimensions of the image and sets up the UI.

        Args:
            image_format (QTextImageFormat): The format of the image to edit
            parent (QWidget, optional): Parent widget for this dialog

        Returns:
            None
        """
        super().__init__(parent)
        self.setWindowTitle("Image Properties")
        self.image_format = image_format
        self.original_width = 0
        self.original_height = 0
        self.aspect_ratio = 1.0
        self._ignore_spin_changes = False  # Flag to prevent signal loops
        self.image_data = None  # Store actual image data

        self.load_original_dimensions()
        self.setup_ui()
        self.load_current_format()

    def load_original_dimensions(self):
        """Load original dimensions using Pillow, handling both file paths and data URIs.

        Attempts to load the original dimensions of the image from either:
        1. A data URI embedded in the document
        2. A file path stored in the image format

        Sets the original_width, original_height, and aspect_ratio properties.
        Falls back to the current format dimensions if the original can't be determined.

        Returns:
            None

        Raises:
            Exception: Handled internally for image loading errors
        """
        path = self.image_format.name()

        # Check if this is a data URI
        if path and path.startswith("data:"):
            try:
                # Extract the base64 data
                data_uri_pattern = r"data:(.*?);base64,(.*)"
                match = re.match(data_uri_pattern, path)
                if match:
                    content_type, b64data = match.groups()
                    # Decode the base64 data
                    img_data = base64.b64decode(b64data)
                    self.image_data = img_data  # Store for preview

                    # Use BytesIO to create a file-like object
                    buffer = io.BytesIO(img_data)
                    with Image.open(buffer) as img:
                        self.original_width, self.original_height = img.size
                        if self.original_width > 0 and self.original_height > 0:
                            self.aspect_ratio = (
                                self.original_height / self.original_width
                            )
                else:
                    logger.warning("Failed to parse data URI")
                    self.original_width = int(self.image_format.width())
                    self.original_height = int(self.image_format.height())
            except Exception as e:
                logger.error(
                    f"Error loading image dimensions from data URI: {e}", exc_info=True
                )
                self.original_width = int(self.image_format.width())
                self.original_height = int(self.image_format.height())
        elif path and Path(path).exists():
            # Regular file path
            try:
                # Input validation
                if not path or not isinstance(path, str):
                    raise ValueError("Invalid image path")

                path_obj = Path(path)

                # Validate file exists and is readable
                if not path_obj.is_file():
                    raise IsADirectoryError(f"Not a file: {path_obj}")
                if not os.access(str(path_obj), os.R_OK):
                    raise PermissionError(f"No read permission for file: {path_obj}")

                # Validate file is an image by checking extension
                valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
                if path_obj.suffix.lower() not in valid_extensions:
                    raise ValueError(f"Unsupported image format: {path_obj.suffix}")

                # Check file size to prevent loading extremely large images
                max_size_mb = 10  # Maximum file size in MB
                if path_obj.stat().st_size > max_size_mb * 1024 * 1024:
                    raise ValueError(f"Image too large (> {max_size_mb}MB): {path_obj}")

                # Load image and get dimensions
                with Image.open(path_obj) as img:
                    self.original_width, self.original_height = img.size

                    # Validate image dimensions
                    if self.original_width <= 0 or self.original_height <= 0:
                        raise ValueError(
                            f"Invalid image dimensions: {self.original_width}x{self.original_height}"
                        )

                    self.aspect_ratio = self.original_height / self.original_width

                # Also store the image data for preview
                with open(path_obj, "rb") as f:
                    self.image_data = f.read()
            except Exception as e:
                logger.error(
                    f"Error loading original image dimensions: {e}", exc_info=True
                )
                self.original_width = int(self.image_format.width())
                self.original_height = int(self.image_format.height())
        else:
            # Fallback if path invalid or not stored
            logger.warning(f"Image path invalid or not found: {path}")
            self.original_width = int(self.image_format.width())
            self.original_height = int(self.image_format.height())

        if self.original_width <= 0:
            self.original_width = 100  # Avoid division by zero
        if self.original_height <= 0:
            self.original_height = 100
        self.aspect_ratio = self.original_height / self.original_width

    def setup_ui(self):
        """Set up the dialog UI elements.

        Creates and configures all UI components for the dialog, including:
        - Image preview
        - Dimension controls (width and height)
        - Aspect ratio maintenance checkbox
        - Original dimensions display
        - OK and Cancel buttons

        Returns:
            None
        """
        layout = QVBoxLayout(self)

        # --- Preview ---
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(200, 150)
        self.preview_label.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;"
        )

        # Create preview pixmap from the data
        if self.image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(self.image_data))
            # Scale to fit the preview area
            pixmap = pixmap.scaled(
                300,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("No preview available")

        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # --- Info ---
        info_group = QGroupBox("Information")
        info_layout = QFormLayout()

        # Show abbreviated path if it's a data URI
        path_text = self.image_format.name()
        if path_text and path_text.startswith("data:"):
            path_text = f"Embedded image ({path_text[:30]}...)"

        self.path_label = QLabel(path_text)
        self.path_label.setWordWrap(True)
        info_layout.addRow("Path:", self.path_label)
        self.orig_dims_label = QLabel(
            f"{self.original_width} x {self.original_height} px"
        )
        info_layout.addRow("Original Size:", self.orig_dims_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # --- Dimensions ---
        dims_group = QGroupBox("Dimensions")
        dims_layout = QFormLayout()

        # Width spinbox with validation
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 8000)  # Set reasonable min/max values
        self.width_spin.setSuffix(" px")
        self.width_spin.setToolTip("Width must be between 10 and 8000 pixels")
        self.width_spin.valueChanged.connect(self.width_changed)
        dims_layout.addRow("Width:", self.width_spin)

        # Height spinbox with validation
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 8000)  # Set reasonable min/max values
        self.height_spin.setSuffix(" px")
        self.height_spin.setToolTip("Height must be between 10 and 8000 pixels")
        self.height_spin.valueChanged.connect(self.height_changed)
        dims_layout.addRow("Height:", self.height_spin)

        self.keep_aspect_checkbox = QCheckBox("Keep Aspect Ratio")
        self.keep_aspect_checkbox.setChecked(True)  # Default to keeping aspect ratio
        self.keep_aspect_checkbox.stateChanged.connect(self.aspect_ratio_lock_changed)
        dims_layout.addRow("", self.keep_aspect_checkbox)

        dims_group.setLayout(dims_layout)
        layout.addWidget(dims_group)

        # --- Buttons ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_current_format(self):
        """Load settings from the current image format into the UI.

        Retrieves the current width and height from the image format and
        updates the UI controls to reflect these values. Also updates
        the image preview.

        Returns:
            None
        """
        self._ignore_spin_changes = True
        current_width = int(self.image_format.width())
        current_height = int(self.image_format.height())

        # If format dimensions are 0, use original dimensions
        if current_width <= 0:
            current_width = self.original_width
        if current_height <= 0:
            current_height = self.original_height

        self.width_spin.setValue(current_width)
        self.height_spin.setValue(current_height)
        self._ignore_spin_changes = False

    def width_changed(self, new_width):
        """Handle width change, potentially updating height.

        When the width is changed and aspect ratio lock is enabled,
        automatically updates the height to maintain the aspect ratio.

        Args:
            new_width (int): The new width value

        Returns:
            None
        """
        if not self._ignore_spin_changes and self.keep_aspect_checkbox.isChecked():
            self._ignore_spin_changes = True
            new_height = int(new_width * self.aspect_ratio)
            self.height_spin.setValue(new_height)
            self._ignore_spin_changes = False

    def height_changed(self, new_height):
        """Handle height change, potentially updating width.

        When the height is changed and aspect ratio lock is enabled,
        automatically updates the width to maintain the aspect ratio.

        Args:
            new_height (int): The new height value

        Returns:
            None
        """
        if not self._ignore_spin_changes and self.keep_aspect_checkbox.isChecked():
            self._ignore_spin_changes = True
            new_width = int(new_height / self.aspect_ratio)
            self.width_spin.setValue(new_width)
            self._ignore_spin_changes = False

    def aspect_ratio_lock_changed(self):
        """Recalculate based on width if lock is enabled.

        When the aspect ratio lock is toggled on, updates the height
        based on the current width to restore the proper aspect ratio.

        Returns:
            None
        """
        if self.keep_aspect_checkbox.isChecked():
            self.width_changed(
                self.width_spin.value()
            )  # Trigger height update from width

    def get_new_dimensions(self):
        """Return the chosen width and height.

        Provides the final dimensions selected by the user in the dialog.

        Returns:
            tuple: A tuple containing (width, height) in pixels
        """
        return self.width_spin.value(), self.height_spin.value()


# Example Usage (for testing)
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Dummy format for testing
    dummy_fmt = QTextImageFormat()
    dummy_fmt.setName(
        "path/to/dummy/image.png"
    )  # Needs a valid path to test Pillow loading
    dummy_fmt.setWidth(200)
    dummy_fmt.setHeight(150)

    # Create a dummy image file if needed for testing load_original_dimensions
    test_path = Path("dummy_image.png")
    if not test_path.exists():
        try:
            from PIL import Image

            Image.new("RGB", (300, 250), color="red").save(test_path)
            dummy_fmt.setName(str(test_path))  # Use the created dummy path
        except ImportError:
            print("Pillow not installed, cannot create dummy image for full test.")
        except Exception as e:
            print(f"Error creating dummy image: {e}")

    dialog = ImagePropertiesDialog(dummy_fmt)
    if dialog.exec():
        new_w, new_h = dialog.get_new_dimensions()
        print(f"Dialog Accepted! New Dimensions: {new_w} x {new_h}")
    else:
        print("Dialog Cancelled.")

    # Clean up dummy file
    if test_path.exists():
        test_path.unlink()

    sys.exit()
