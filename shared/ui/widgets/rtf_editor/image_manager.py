import os

from PIL import Image  # Import Pillow
from PyQt6.QtCore import QBuffer, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QImage, QTextImageFormat
from PyQt6.QtWidgets import (  # Added QInputDialog
    QFileDialog,
    QInputDialog,
    QMenu,
    QMessageBox,
)

# Import DEFAULT_DIR from document_manager (consider a better place later)
try:
    from .document_manager import DEFAULT_DIR
except ImportError:
    # Fallback if run standalone or structure changes
    DEFAULT_DIR = os.path.join(os.getcwd(), "document_folder")


class ImageManager(QObject):
    """Manages image operations for the RTF editor."""

    # Signal to indicate text change is needed
    content_changed = pyqtSignal()

    def __init__(self, editor, parent_window):
        super().__init__()
        self.editor = editor
        self.parent_window = parent_window

    def add_menu_actions(self, menubar):
        """Add image-related actions to the main menubar."""
        insert_menu = menubar.findChild(QMenu, "&Insert")
        if not insert_menu:
            insert_menu = menubar.addMenu("&Insert")

        self.insert_image_action = insert_menu.addAction("&Image...")
        self.insert_image_action.triggered.connect(self.insert_image)
        # Add other image actions here in the future

    def insert_image(self):
        """Open file dialog, allow resizing, setup format, and insert the image using data URI."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Insert Image",
            DEFAULT_DIR,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )

        if not file_path:
            return

        try:
            # Load with Pillow only to get original dimensions for the dialog
            pillow_image = Image.open(file_path)
            original_width, original_height = pillow_image.size

            # Ask user for desired width
            new_width, ok = QInputDialog.getInt(
                self.parent_window,
                "Resize Image",
                f"Enter desired width (original: {original_width}px):",
                original_width,
                10,
                8000,
                10,
            )

            insert_width = original_width
            insert_height = original_height

            if ok and new_width != original_width:
                # Calculate new height maintaining aspect ratio
                aspect_ratio = (
                    original_height / original_width if original_width > 0 else 1
                )
                new_height = int(new_width * aspect_ratio)
                insert_width = new_width
                insert_height = new_height
                print(
                    f"Image will be inserted with size: {insert_width}x{insert_height}"
                )

            # --- Create a data URI from the image ---
            try:
                # Load the image using Qt
                qimage = QImage(file_path)
                if qimage.isNull():
                    print("Failed to load image with QImage, trying fallback method")
                    # Fallback to raw bytes if QImage fails
                    with open(file_path, "rb") as img_file:
                        img_data = img_file.read()

                    # Determine mime type
                    mime_type = "image/png"  # Default
                    if file_path.lower().endswith(".jpg") or file_path.lower().endswith(
                        ".jpeg"
                    ):
                        mime_type = "image/jpeg"
                    elif file_path.lower().endswith(".gif"):
                        mime_type = "image/gif"

                    # Encode as base64
                    import base64

                    img_base64 = base64.b64encode(img_data).decode("utf-8")
                    data_uri = f"data:{mime_type};base64,{img_base64}"
                else:
                    # Convert QImage to base64 data URI
                    import base64
                    import io

                    buffer = io.BytesIO()
                    qimage = qimage.scaled(
                        insert_width,
                        insert_height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                    # Determine format for saving
                    save_format = "PNG"
                    if file_path.lower().endswith(".jpg") or file_path.lower().endswith(
                        ".jpeg"
                    ):
                        save_format = "JPEG"
                        mime_type = "image/jpeg"
                    elif file_path.lower().endswith(".gif"):
                        save_format = "GIF"
                        mime_type = "image/gif"
                    else:
                        mime_type = "image/png"

                    # Save to buffer
                    qbuffer = QBuffer()
                    qbuffer.open(QBuffer.OpenModeFlag.WriteOnly)
                    qimage.save(qbuffer, save_format)
                    img_data = qbuffer.data().data()

                    # Encode as base64
                    img_base64 = base64.b64encode(img_data).decode("utf-8")
                    data_uri = f"data:{mime_type};base64,{img_base64}"

                    print(f"Created data URI for image (length: {len(data_uri)})")
            except Exception as e:
                print(f"Error creating data URI: {e}, falling back to file path")
                data_uri = file_path  # Fallback to file path if conversion fails

            # --- Insert the image format with data URI ---
            cursor = self.editor.textCursor()
            image_format = QTextImageFormat()
            image_format.setName(data_uri)  # Use data URI instead of file path
            image_format.setWidth(insert_width)
            image_format.setHeight(insert_height)

            # Store the original path as a custom property for reference
            property_id = 1001  # Custom property ID
            image_format.setProperty(property_id, file_path)

            cursor.insertImage(image_format)
            # ---------------------------------------------

            self.content_changed.emit()  # Signal that content changed
        except Exception as e:
            print(f"Error inserting image: {e}")
            QMessageBox.critical(
                self.parent_window, "Error", f"Could not insert image: {str(e)}"
            )
