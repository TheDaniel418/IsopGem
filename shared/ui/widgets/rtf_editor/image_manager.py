import gc
import mimetypes
import os
import uuid
from pathlib import Path

from PIL import Image  # Import Pillow
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QTextImageFormat
from PyQt6.QtWidgets import (  # Added QInputDialog
    QFileDialog,
    QInputDialog,
    QMenu,
    QMessageBox,
)

from shared.ui.widgets.rtf_editor.utils.error_utils import handle_error
from shared.ui.widgets.rtf_editor.utils.image_storage import (
    cleanup_unused_images,
    data_uri_to_image_file,
    save_image_to_storage,
)
from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger
from shared.ui.widgets.rtf_editor.utils.recovery_utils import (
    create_error_report,
)

# Initialize logger
logger = get_logger(__name__)

# Import DEFAULT_DIR from document_manager (consider a better place later)
try:
    from .document_manager import DEFAULT_DIR
except ImportError:
    # Fallback if run standalone or structure changes
    logger.warning("Could not import DEFAULT_DIR from document_manager, using fallback")
    DEFAULT_DIR = Path.cwd() / "document_folder"


class ImageManager(QObject):
    """Manages image operations for the RTF editor.

    This class handles all image-related functionality for the RTF editor, including:
    - Inserting images from files
    - Converting images to data URIs for embedding
    - Resizing images
    - Managing image properties

    It provides menu actions for image operations and handles the technical details
    of embedding images in Qt's rich text format.

    Attributes:
        content_changed (pyqtSignal): Signal emitted when content changes due to image operations

    Signals:
        content_changed(): Emitted when an image operation changes the document content
    """

    # Signal to indicate text change is needed
    content_changed = pyqtSignal()

    def __init__(self, editor, parent_window, document_id=None):
        """Initialize the ImageManager.

        Sets up the image manager with references to the editor and parent window.

        Args:
            editor (QTextEdit): The text editor where images will be inserted
            parent_window (QWidget): The parent window for dialogs and messages
            document_id (str, optional): Unique identifier for the document

        Returns:
            None
        """
        super().__init__()
        self.editor = editor
        self.parent_window = parent_window

        # Set document ID (generate one if not provided)
        self.document_id = document_id or f"doc_{uuid.uuid4().hex[:8]}"
        logger.debug(f"ImageManager initialized with document_id: {self.document_id}")

    def add_menu_actions(self, menubar):
        """Add image-related actions to the main menubar.

        Finds or creates an Insert menu in the menubar and adds image-related
        actions to it.

        Args:
            menubar (QMenuBar): The main menu bar of the application

        Returns:
            None
        """
        insert_menu = menubar.findChild(QMenu, "&Insert")
        if not insert_menu:
            insert_menu = menubar.addMenu("&Insert")

        self.insert_image_action = insert_menu.addAction("&Image...")
        self.insert_image_action.triggered.connect(self.insert_image)
        # Add other image actions here in the future

    def insert_image(self):
        """Insert an image into the document.

        Opens a file dialog for the user to select an image file, then:
        1. Prompts for desired image width (maintaining aspect ratio)
        2. Converts the image to a data URI for embedding
        3. Creates a QTextImageFormat with the image data
        4. Uses the Command pattern to insert the image at the current cursor position

        The image is embedded directly in the document using a data URI,
        which makes the document self-contained without external dependencies.

        Returns:
            None

        Raises:
            Exception: Handled internally for image loading and insertion errors
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Insert Image",
            str(DEFAULT_DIR),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )

        if not file_path:
            return

        try:
            # Verify that the file exists and is accessible
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"Image file not found: {file_path}")

            # Determine the MIME type for the image
            mime_type = get_mime_type(file_path)
            if not mime_type.startswith("image/"):
                raise ValueError(f"Not a valid image file: {file_path}")

            # Try to open the image to verify it's valid and get dimensions
            image = QImage(file_path)
            if image.isNull():
                raise ValueError(f"Could not load image: {file_path}")

            # Get original dimensions
            orig_width = image.width()
            orig_height = image.height()

            # Calculate aspect ratio
            aspect_ratio = orig_width / orig_height if orig_height > 0 else 1.0

            # Set a reasonable default size (70% of original, capped at 600px width)
            default_width = min(int(orig_width * 0.7), 600)
            default_height = int(default_width / aspect_ratio)

            # Prompt user for desired width
            width, ok = QInputDialog.getInt(
                self.parent_window,
                "Image Width",
                "Enter desired image width in pixels:",
                default_width,
                10,
                2000,
            )

            if not ok:
                return  # User canceled

            # Calculate height based on aspect ratio
            height = int(width / aspect_ratio)

            # Save the image to storage
            try:
                storage_path, actual_width, actual_height = save_image_to_storage(
                    file_path,
                    document_id=self.document_id,
                    max_width=width,
                    max_height=height,
                )

                # Use the actual dimensions returned by the storage function
                width = actual_width
                height = actual_height

                logger.debug(f"Image saved to storage: {storage_path}")
            except Exception as e:
                logger.warning(
                    f"Error saving to storage, using original path: {str(e)}"
                )
                storage_path = file_path  # Fallback to original path

            # Create the image format
            image_format = QTextImageFormat()
            image_format.setName(storage_path)
            image_format.setWidth(width)
            image_format.setHeight(height)

            # Store the original path as a custom property for reference
            property_id = 1001  # Custom property ID
            image_format.setProperty(property_id, str(path_obj))

            # Store document ID as a custom property for reference
            property_id_doc = 1002  # Custom property ID for document
            image_format.setProperty(property_id_doc, self.document_id)

            # Get the current cursor position
            cursor = self.editor.textCursor()
            position = cursor.position()

            # Use the command pattern to insert the image
            if hasattr(self.parent_window, "image_manager_insert_image"):
                # Use the command pattern
                success = self.parent_window.image_manager_insert_image(
                    image_format, position
                )
                if not success:
                    raise RuntimeError("Failed to insert image using command pattern")
            else:
                # Fallback to direct insertion if command pattern not available
                cursor.insertImage(image_format)
                self.content_changed.emit()  # Signal that content changed

        except Exception as e:
            error_msg = f"Could not insert image: {str(e)}"
            handle_error(self.parent_window, error_msg, e)

    def _load_image_with_downsampling(self, path_obj):
        """Load an image with progressive downsampling to handle memory errors.

        This method attempts to load a large image by progressively reducing its
        resolution until it can be loaded without memory errors.

        Args:
            path_obj (Path): Path to the image file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Force garbage collection first
            gc.collect()

            # Try different scaling factors until one works
            for scale_factor in [0.5, 0.25, 0.1, 0.05]:
                try:
                    # Create a temporary file for the downsampled image
                    temp_dir = Path(os.path.expanduser("~")) / ".isopgem" / "temp"
                    temp_dir.mkdir(parents=True, exist_ok=True)

                    temp_file = temp_dir / f"downsampled_{path_obj.name}"

                    # Open the image with PIL's thumbnail function which is memory efficient
                    with Image.open(path_obj) as img:
                        # Get original size
                        original_width, original_height = img.size

                        # Calculate new size
                        new_width = int(original_width * scale_factor)
                        new_height = int(original_height * scale_factor)

                        # Create a new image with thumbnail (memory efficient)
                        img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

                        # Save to temporary file
                        img.save(temp_file)

                        logger.info(
                            f"Successfully downsampled image to {new_width}x{new_height}"
                        )

                        # Show success message
                        QMessageBox.information(
                            self.parent_window,
                            "Image Downsampled",
                            f"The image was too large to load at full resolution.\n\n"
                            f"It has been automatically downsampled to {new_width}x{new_height} pixels.",
                        )

                        # Now insert the downsampled image
                        self.insert_image_at_cursor(
                            str(temp_file), new_width, new_height
                        )
                        return True

                except MemoryError:
                    # If this scale factor still causes memory error, try a smaller one
                    logger.warning(
                        f"Downsampling to {scale_factor} still caused memory error, trying smaller scale"
                    )
                    continue

            # If we get here, all scale factors failed
            QMessageBox.critical(
                self.parent_window,
                "Image Too Large",
                "The image is too large to load even after downsampling.\n\n"
                "Please use a smaller image or an image editor to reduce its size.",
            )
            return False

        except Exception as e:
            logger.error(f"Error in downsampling: {str(e)}", exc_info=True)

            # Create error report
            error_report = create_error_report(e, "image downsampling error")

            QMessageBox.critical(
                self.parent_window,
                "Downsampling Failed",
                f"Could not downsample the image: {str(e)}\n\n"
                "Please try a different image.",
            )
            return False

    def insert_image_at_cursor(self, image_path, width, height):
        """Insert an image at the current cursor position.

        A simplified version of insert_image that doesn't prompt the user
        and uses the provided dimensions.

        Args:
            image_path (str): Path to the image file
            width (int): Width to display the image
            height (int): Height to display the image

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Save the image to storage
            try:
                storage_path, actual_width, actual_height = save_image_to_storage(
                    image_path,
                    document_id=self.document_id,
                    max_width=width,
                    max_height=height,
                )

                # Use the actual dimensions returned by the storage function
                width = actual_width
                height = actual_height

                logger.debug(f"Image saved to storage: {storage_path}")
            except Exception as e:
                logger.warning(
                    f"Error saving to storage, using original path: {str(e)}"
                )
                storage_path = image_path  # Fallback to original path

            # Create the image format
            image_format = QTextImageFormat()
            image_format.setName(storage_path)
            image_format.setWidth(width)
            image_format.setHeight(height)

            # Store the original path as a custom property for reference
            property_id = 1001  # Custom property ID
            image_format.setProperty(property_id, image_path)

            # Store document ID as a custom property for reference
            property_id_doc = 1002  # Custom property ID for document
            image_format.setProperty(property_id_doc, self.document_id)

            # Get the current cursor position
            cursor = self.editor.textCursor()
            position = cursor.position()

            # Use the command pattern to insert the image
            if hasattr(self.parent_window, "image_manager_insert_image"):
                # Use the command pattern
                success = self.parent_window.image_manager_insert_image(
                    image_format, position
                )
                if not success:
                    raise RuntimeError("Failed to insert image using command pattern")
            else:
                # Fallback to direct insertion if command pattern not available
                cursor.insertImage(image_format)
                self.content_changed.emit()  # Signal that content changed

            return True

        except Exception as e:
            logger.error(f"Error inserting image at cursor: {e}")
            return False

    def convert_data_uris_to_files(self):
        """Convert all data URI images in the document to file-based images.

        Scans the document for data URI images and converts them to file-based
        images stored in the image storage directory.

        Returns:
            int: Number of images converted
        """
        try:
            # Get the document
            document = self.editor.document()

            # Find all images in the document
            converted_count = 0
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)

            # Iterate through the document
            while not cursor.atEnd():
                # Check if current position has an image
                char_format = cursor.charFormat()
                if char_format.isImageFormat():
                    # Get the image format
                    image_format = char_format.toImageFormat()

                    # Get the image source
                    image_source = image_format.name()

                    # Check if it's a data URI
                    if image_source.startswith("data:image/"):
                        try:
                            # Convert data URI to file
                            storage_path, width, height = data_uri_to_image_file(
                                image_source, document_id=self.document_id
                            )

                            # Update the image format
                            image_format.setName(storage_path)

                            # Store document ID as a custom property
                            property_id_doc = 1002  # Custom property ID for document
                            image_format.setProperty(property_id_doc, self.document_id)

                            # Replace the image at the current position
                            cursor.deleteChar()  # Remove the old image
                            cursor.insertImage(image_format)  # Insert the new one

                            converted_count += 1
                            logger.debug(f"Converted data URI to file: {storage_path}")

                            # Continue from current position
                            continue
                        except Exception as e:
                            logger.error(
                                f"Error converting data URI: {str(e)}", exc_info=True
                            )

                # Move to next character
                cursor.movePosition(cursor.MoveOperation.Right)

            if converted_count > 0:
                self.content_changed.emit()  # Signal that content changed
                logger.info(f"Converted {converted_count} data URI images to files")

            return converted_count

        except Exception as e:
            logger.error(
                f"Error converting data URIs to files: {str(e)}", exc_info=True
            )
            return 0

    def cleanup_unused_images(self):
        """Clean up unused images for the current document.

        Scans the document to find all used images, then removes any
        images in the storage directory that are no longer referenced.

        Returns:
            int: Number of images removed
        """
        try:
            # Get the document
            document = self.editor.document()

            # Find all images in the document
            used_images = []
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)

            # Iterate through the document
            while not cursor.atEnd():
                # Check if current position has an image
                char_format = cursor.charFormat()
                if char_format.isImageFormat():
                    # Get the image format
                    image_format = char_format.toImageFormat()

                    # Get the image source
                    image_source = image_format.name()

                    # Add to used images if it's a file path (not a data URI)
                    if not image_source.startswith("data:"):
                        used_images.append(image_source)

                # Move to next character
                cursor.movePosition(cursor.MoveOperation.Right)

            # Clean up unused images
            removed_count = cleanup_unused_images(self.document_id, used_images)

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} unused images")

            return removed_count

        except Exception as e:
            logger.error(f"Error cleaning up unused images: {str(e)}", exc_info=True)
            return 0


def get_mime_type(file_path):
    """Get the MIME type of a file.

    Args:
        file_path (str): Path to the file

    Returns:
        str: MIME type of the file
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"
