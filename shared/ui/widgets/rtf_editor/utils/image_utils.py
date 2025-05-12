"""
@file image_utils.py
@description Utilities for image handling in rich text editors
@created 2024-05-05
@dependencies PyQt6

Provides utility functions for image processing, conversion, embedding and manipulation
in rich text editors.
"""

import base64
import mimetypes
from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QTextCursor, QTextImageFormat
from PyQt6.QtWidgets import QTextEdit


class ImageUtils:
    """Utility class for image handling operations."""

    @staticmethod
    def file_path_to_data_uri(file_path: str) -> str:
        """Convert a file path to a data URI.

        Args:
            file_path: Path to the image file

        Returns:
            Data URI string with embedded image data

        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the image format is not supported
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found at {file_path}")

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            # Try to infer from extension
            if file_path.lower().endswith(".jpg") or file_path.lower().endswith(
                ".jpeg"
            ):
                mime_type = "image/jpeg"
            elif file_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif file_path.lower().endswith(".gif"):
                mime_type = "image/gif"
            else:
                mime_type = "image/png"  # Default

        # Read image file and convert to base64
        with open(file_path, "rb") as img_file:
            img_data = img_file.read()

        img_base64 = base64.b64encode(img_data).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{img_base64}"

        return data_uri

    @staticmethod
    def is_data_uri(path_or_uri: str) -> bool:
        """Check if the given string is a data URI.

        Args:
            path_or_uri: Path or data URI to check

        Returns:
            True if it's a data URI, False otherwise
        """
        return path_or_uri.startswith("data:")

    @staticmethod
    def update_image_at_cursor(
        editor: QTextEdit, cursor_pos: int, image_path: str, width: int, height: int
    ) -> bool:
        """Update an image at the specified cursor position.

        This method removes the existing image at the cursor position and
        inserts a new image with the specified path and dimensions.

        Args:
            editor: The text edit widget
            cursor_pos: Position of the cursor where the image is located
            image_path: Path or data URI of the new image
            width: New width of the image
            height: New height of the image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure image_path is a data URI
            if not ImageUtils.is_data_uri(image_path):
                image_path = ImageUtils.file_path_to_data_uri(image_path)

            # Find and remove the existing image
            image_found = False
            cursor = QTextCursor(editor.document())
            cursor.setPosition(cursor_pos)

            # Check if we're already at an image position
            cursor_format = cursor.charFormat()
            if cursor_format.isImageFormat():
                # Create a selection of just this character
                selection_cursor = QTextCursor(cursor)
                selection_cursor.movePosition(
                    QTextCursor.MoveOperation.NextCharacter,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                selection_cursor.deleteChar()
                image_found = True
            else:
                # Search nearby positions (within ±3 characters)
                for offset in range(-1, 2):  # Check -1, 0, 1
                    pos = cursor_pos + offset
                    if pos < 0:
                        continue

                    check_cursor = QTextCursor(editor.document())
                    check_cursor.setPosition(pos)

                    # Check the current character
                    if check_cursor.charFormat().isImageFormat():
                        # Select and delete it
                        check_cursor.movePosition(
                            QTextCursor.MoveOperation.NextCharacter,
                            QTextCursor.MoveMode.KeepAnchor,
                        )
                        check_cursor.deleteChar()
                        cursor.setPosition(pos)
                        image_found = True
                        break

                # If still not found, try a slightly larger range
                if not image_found:
                    for offset in range(2, 4):  # Check ±2, ±3
                        for direction in [-1, 1]:
                            pos = cursor_pos + (offset * direction)
                            if pos < 0:
                                continue

                            check_cursor = QTextCursor(editor.document())
                            check_cursor.setPosition(pos)

                            if check_cursor.charFormat().isImageFormat():
                                check_cursor.movePosition(
                                    QTextCursor.MoveOperation.NextCharacter,
                                    QTextCursor.MoveMode.KeepAnchor,
                                )
                                check_cursor.deleteChar()
                                cursor.setPosition(pos)
                                image_found = True
                                break
                        if image_found:
                            break

            if not image_found:
                return False

            # Insert the new image
            new_format = QTextImageFormat()
            new_format.setName(image_path)
            new_format.setWidth(width)
            new_format.setHeight(height)
            cursor.insertImage(new_format)

            return True
        except Exception as e:
            print(f"Error updating image: {e}")
            return False

    @staticmethod
    def insert_image(
        editor: QTextEdit,
        image_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        position: Optional[int] = None,
    ) -> bool:
        """Insert an image at the current cursor position or specified position.

        Args:
            editor: The text edit widget
            image_path: Path or data URI of the image
            width: Width of the image (optional)
            height: Height of the image (optional)
            position: Position to insert the image at (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure image_path is a data URI
            if not ImageUtils.is_data_uri(image_path):
                image_path = ImageUtils.file_path_to_data_uri(image_path)

            # Create a new image format
            new_format = QTextImageFormat()
            new_format.setName(image_path)
            if width is not None:
                new_format.setWidth(width)
            if height is not None:
                new_format.setHeight(height)

            # Get cursor at current position or specified position
            cursor = QTextCursor(editor.document())
            if position is not None:
                cursor.setPosition(position)
            else:
                cursor = editor.textCursor()

            # Insert the image
            cursor.insertImage(new_format)

            # Update cursor in editor
            if position is not None:
                editor.setTextCursor(cursor)

            return True
        except Exception as e:
            print(f"Error inserting image: {e}")
            return False

    @staticmethod
    def resize_image(
        editor: QTextEdit, cursor_pos: int, new_width: int, new_height: int
    ) -> bool:
        """Resize an image at the specified cursor position.

        Args:
            editor: The text edit widget
            cursor_pos: Position of the cursor where the image is located
            new_width: New width of the image
            new_height: New height of the image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the image at or near the cursor position
            image_format = ImageUtils.find_image_at_position(editor, cursor_pos)
            if not image_format:
                return False

            # Get the image path
            image_path = image_format.name()

            # Update the image with new dimensions
            return ImageUtils.update_image_at_cursor(
                editor, cursor_pos, image_path, new_width, new_height
            )
        except Exception as e:
            print(f"Error resizing image: {e}")
            return False

    @staticmethod
    def find_image_at_position(
        editor: QTextEdit, position: int
    ) -> Optional[QTextImageFormat]:
        """Find an image at or near the specified position.

        Args:
            editor: The text edit widget
            position: Position to search for an image

        Returns:
            The image format if found, None otherwise
        """
        # Check the exact position
        cursor = QTextCursor(editor.document())
        cursor.setPosition(position)
        format = cursor.charFormat()
        if format.isImageFormat():
            return format.toImageFormat()

        # Check nearby positions (±3 characters)
        for offset in range(-3, 4):
            if offset == 0:
                continue

            pos = position + offset
            if pos < 0:
                continue

            cursor = QTextCursor(editor.document())
            cursor.setPosition(pos)
            format = cursor.charFormat()

            if format.isImageFormat():
                return format.toImageFormat()

        return None
