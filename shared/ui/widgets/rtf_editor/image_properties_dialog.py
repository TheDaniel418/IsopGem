# src/ui/components/rtf_editor/image_properties_dialog.py
import sys
import os
import base64
import re
import io
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QCheckBox,
)
from PyQt6.QtGui import QTextImageFormat, QPixmap, QImage
from PyQt6.QtCore import Qt, QSize, QByteArray
from PIL import Image  # Use Pillow to get original dimensions accurately


class ImagePropertiesDialog(QDialog):
    """Dialog for viewing and editing image properties."""

    def __init__(self, image_format, parent=None):
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
        """Load original dimensions using Pillow, handling both file paths and data URIs."""
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
                    print("Failed to parse data URI")
                    self.original_width = int(self.image_format.width())
                    self.original_height = int(self.image_format.height())
            except Exception as e:
                print(f"Error loading image dimensions from data URI: {e}")
                self.original_width = int(self.image_format.width())
                self.original_height = int(self.image_format.height())
        elif path and os.path.exists(path):
            # Regular file path
            try:
                with Image.open(path) as img:
                    self.original_width, self.original_height = img.size
                    if self.original_width > 0 and self.original_height > 0:
                        self.aspect_ratio = self.original_height / self.original_width

                # Also store the image data for preview
                with open(path, "rb") as f:
                    self.image_data = f.read()
            except Exception as e:
                print(f"Error loading original image dimensions: {e}")
                self.original_width = int(self.image_format.width())
                self.original_height = int(self.image_format.height())
        else:
            # Fallback if path invalid or not stored
            print(f"Image path invalid or not found: {path}")
            self.original_width = int(self.image_format.width())
            self.original_height = int(self.image_format.height())

        if self.original_width <= 0:
            self.original_width = 100  # Avoid division by zero
        if self.original_height <= 0:
            self.original_height = 100
        self.aspect_ratio = self.original_height / self.original_width

    def setup_ui(self):
        """Set up the dialog UI elements."""
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

        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 8000)
        self.width_spin.setSuffix(" px")
        self.width_spin.valueChanged.connect(self.width_changed)
        dims_layout.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 8000)
        self.height_spin.setSuffix(" px")
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
        """Load settings from the current image format into the UI."""
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
        """Handle width change, potentially updating height."""
        if not self._ignore_spin_changes and self.keep_aspect_checkbox.isChecked():
            self._ignore_spin_changes = True
            new_height = int(new_width * self.aspect_ratio)
            self.height_spin.setValue(new_height)
            self._ignore_spin_changes = False

    def height_changed(self, new_height):
        """Handle height change, potentially updating width."""
        if not self._ignore_spin_changes and self.keep_aspect_checkbox.isChecked():
            self._ignore_spin_changes = True
            new_width = int(new_height / self.aspect_ratio)
            self.width_spin.setValue(new_width)
            self._ignore_spin_changes = False

    def aspect_ratio_lock_changed(self):
        """Recalculate based on width if lock is enabled."""
        if self.keep_aspect_checkbox.isChecked():
            self.width_changed(
                self.width_spin.value()
            )  # Trigger height update from width

    def get_new_dimensions(self):
        """Return the chosen width and height."""
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
    test_path = "dummy_image.png"
    if not os.path.exists(test_path):
        try:
            from PIL import Image

            Image.new("RGB", (300, 250), color="red").save(test_path)
            dummy_fmt.setName(test_path)  # Use the created dummy path
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
    if os.path.exists(test_path):
        os.remove(test_path)

    sys.exit()
