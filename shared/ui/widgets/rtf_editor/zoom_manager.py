from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QToolButton,
    QWidget,
)


class ZoomManager(QWidget):
    """Manages zoom functionality for the RTF editor."""

    # Signal emitted when zoom level changes
    zoom_changed = pyqtSignal(float)

    # Predefined zoom levels as percentages
    ZOOM_LEVELS = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500]
    DEFAULT_ZOOM = 100

    def __init__(self, editor, parent=None):
        """Initialize the ZoomManager.

        Args:
            editor (QTextEdit): The text editor to apply zoom to
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.editor = editor
        self.current_zoom = self.DEFAULT_ZOOM

        # Setup UI
        self.setup_ui()

        # Apply initial zoom
        self.apply_zoom(self.current_zoom)

    def setup_ui(self):
        """Set up the zoom controls UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Zoom out button
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setText("-")
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        layout.addWidget(self.zoom_out_btn)

        # Zoom selector combobox
        self.zoom_combo = QComboBox()
        self.zoom_combo.setEditable(True)
        self.zoom_combo.setMinimumWidth(70)
        self.zoom_combo.setMaximumWidth(100)

        # Add zoom levels to combobox
        for level in self.ZOOM_LEVELS:
            self.zoom_combo.addItem(f"{level}%", level)

        # Set default zoom level
        default_index = self.ZOOM_LEVELS.index(self.DEFAULT_ZOOM)
        self.zoom_combo.setCurrentIndex(default_index)

        # Connect signals
        self.zoom_combo.currentIndexChanged.connect(self.on_combo_index_changed)
        self.zoom_combo.editTextChanged.connect(self.on_edit_text_changed)
        layout.addWidget(self.zoom_combo)

        # Zoom in button
        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setText("+")
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        layout.addWidget(self.zoom_in_btn)

        # Reset zoom button
        self.zoom_reset_btn = QToolButton()
        self.zoom_reset_btn.setText("100%")
        self.zoom_reset_btn.setToolTip("Reset Zoom")
        self.zoom_reset_btn.clicked.connect(self.reset_zoom)
        layout.addWidget(self.zoom_reset_btn)

        # Set layout
        self.setLayout(layout)

    def on_combo_index_changed(self, index):
        """Handle selection of a zoom level from the dropdown.

        Args:
            index (int): Index of the selected item
        """
        if index >= 0:
            zoom_level = self.zoom_combo.itemData(index)
            if zoom_level:
                self.apply_zoom(zoom_level)

    def on_edit_text_changed(self, text):
        """Handle manual entry of a zoom level.

        Args:
            text (str): The text entered in the combobox
        """
        # Extract numbers from text
        try:
            # Remove non-digit characters and convert to int
            zoom_text = "".join(filter(str.isdigit, text))
            if zoom_text:
                zoom_level = int(zoom_text)
                # Limit zoom level to a reasonable range
                zoom_level = max(10, min(zoom_level, 500))

                # Only apply if enter is pressed or focus is lost
                # Otherwise wait for user to finish typing
                if text.endswith("%") or text.endswith("\n"):
                    self.apply_zoom(zoom_level)
        except ValueError:
            # Reset to current zoom if input is invalid
            self.update_display()

    def zoom_in(self):
        """Increase the zoom level."""
        # Find the next zoom level higher than current
        for level in self.ZOOM_LEVELS:
            if level > self.current_zoom:
                self.apply_zoom(level)
                return

        # If we're already at the highest predefined level, increase by 50%
        self.apply_zoom(self.current_zoom + 50)

    def zoom_out(self):
        """Decrease the zoom level."""
        # Find the next zoom level lower than current
        for level in reversed(self.ZOOM_LEVELS):
            if level < self.current_zoom:
                self.apply_zoom(level)
                return

        # If we're already at the lowest predefined level, decrease by 50%
        # but don't go below 10%
        self.apply_zoom(max(10, self.current_zoom - 50))

    def reset_zoom(self):
        """Reset zoom to the default level (100%)."""
        self.apply_zoom(self.DEFAULT_ZOOM)

    def set_zoom(self, level):
        """Set zoom to a specific level.

        Args:
            level (int): Zoom level as a percentage (e.g., 100 for 100%)
        """
        self.apply_zoom(level)

    def scale_images(self, document, scale_factor):
        """Scale all images in the document by the given factor.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by
        """
        try:
            print("Scaling images with factor:", scale_factor)

            # Try different methods to scale images
            self._scale_images_by_selection(document, scale_factor)

            # Try another approach if the first one didn't work
            self._scale_images_by_fragment(document, scale_factor)

            # Force layout update
            document.markContentsDirty(0, document.characterCount())
            document.setModified(True)

        except Exception as e:
            print(f"Error in scale_images: {str(e)}")

    def _scale_images_by_selection(self, document, scale_factor):
        """Scale images by selecting characters in document.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by
        """
        try:
            from PyQt6.QtGui import QTextCursor, QTextImageFormat

            print("Trying to scale images by selection method")

            # Save the current selection
            cursor = QTextCursor(document)
            original_pos = cursor.position()

            # Start from the beginning of the document
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # Track processed positions to avoid duplicates
            processed = set()

            # Loop through the document
            count = 0
            while not cursor.atEnd():
                position = cursor.position()

                # Skip if already processed
                if position in processed:
                    cursor.movePosition(QTextCursor.MoveOperation.Right)
                    continue

                # Get the current character format
                fmt = cursor.charFormat()

                # Check if it's an image format
                if fmt.isImageFormat():
                    count += 1
                    img_fmt = fmt.toImageFormat()
                    name = img_fmt.name()
                    width = img_fmt.width()
                    height = img_fmt.height()

                    print(
                        f"Found image {count}: name={name}, width={width}, height={height}"
                    )

                    if width > 0 and height > 0:
                        # Calculate new dimensions
                        new_width = max(5, int(width * scale_factor))
                        new_height = max(5, int(height * scale_factor))

                        # Create a new format
                        new_fmt = QTextImageFormat()

                        # Copy all properties
                        for prop in img_fmt.properties():
                            new_fmt.setProperty(prop, img_fmt.property(prop))

                        # Update width and height
                        new_fmt.setWidth(new_width)
                        new_fmt.setHeight(new_height)

                        # Select the character containing the image
                        pos = cursor.position()
                        cursor.movePosition(
                            QTextCursor.MoveOperation.Right,
                            QTextCursor.MoveMode.KeepAnchor,
                        )

                        # Apply the new format
                        cursor.setCharFormat(new_fmt)

                        # Clear selection and restore position
                        cursor.clearSelection()
                        cursor.setPosition(pos)

                        print(f"Scaled image to {new_width}x{new_height}")

                        # Mark as processed
                        processed.add(pos)

                # Move to next character
                if not cursor.movePosition(QTextCursor.MoveOperation.Right):
                    break

            # Restore original position
            cursor.setPosition(original_pos)

            print(f"Found and processed {count} images")

        except Exception as e:
            print(f"Error in _scale_images_by_selection: {str(e)}")

    def _scale_images_by_fragment(self, document, scale_factor):
        """Alternative approach to scale images using document fragments.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by
        """
        try:
            from PyQt6.QtGui import (
                QTextCursor,
                QTextImageFormat,
            )

            print("Trying to scale images by fragment method")

            # Iterate through all blocks in the document
            block = document.begin()
            image_count = 0

            while block.isValid():
                # Get the block's iterator
                it = block.begin()

                # Iterate through all fragments in the block
                while not it.atEnd():
                    fragment = it.fragment()

                    # Check if the fragment contains an image
                    fmt = fragment.charFormat()
                    if fmt.isImageFormat():
                        image_count += 1
                        img_fmt = fmt.toImageFormat()
                        name = img_fmt.name()
                        width = img_fmt.width()
                        height = img_fmt.height()

                        print(
                            f"Found image by fragment {image_count}: name={name}, width={width}, height={height}"
                        )

                        if width > 0 and height > 0:
                            # Calculate new dimensions
                            new_width = max(5, int(width * scale_factor))
                            new_height = max(5, int(height * scale_factor))

                            # Create cursor at the fragment position
                            cursor = QTextCursor(document)
                            cursor.setPosition(fragment.position())
                            cursor.movePosition(
                                QTextCursor.MoveOperation.Right,
                                QTextCursor.MoveMode.KeepAnchor,
                                fragment.length(),
                            )

                            # Create new format
                            new_fmt = QTextImageFormat()

                            # Copy all properties
                            for prop in img_fmt.properties():
                                new_fmt.setProperty(prop, img_fmt.property(prop))

                            # Update dimensions
                            new_fmt.setWidth(new_width)
                            new_fmt.setHeight(new_height)

                            # Apply the format
                            cursor.setCharFormat(new_fmt)

                            print(f"Scaled fragment image to {new_width}x{new_height}")

                    # Move to next fragment
                    it += 1

                # Move to next block
                block = block.next()

            print(f"Found and processed {image_count} images by fragment")

        except Exception as e:
            print(f"Error in _scale_images_by_fragment: {str(e)}")

    def apply_zoom(self, level):
        """Apply the zoom level to the editor.

        Args:
            level (int): Zoom level as a percentage (e.g., 100 for 100%)
        """
        # Validate zoom level
        level = max(10, min(level, 500))  # Limit zoom to 10%-500%

        # Calculate zoom factor relative to previous zoom
        relative_factor = level / self.current_zoom

        # Store current zoom level
        old_zoom = self.current_zoom
        self.current_zoom = level

        # Calculate absolute zoom factor (1.0 = 100%)
        zoom_factor = level / 100.0

        # QTextEdit doesn't have a setZoomFactor method, so we'll resize the font
        document = self.editor.document()
        default_font = document.defaultFont()

        # Store the default font size on first zoom if not set
        if not hasattr(self, "default_font_size"):
            self.default_font_size = default_font.pointSizeF()
            if self.default_font_size <= 0:  # If point size not set, use pixel size
                self.default_font_size = (
                    default_font.pixelSize() / 1.33
                )  # Convert pixel to approx point
            if self.default_font_size <= 0:  # Fallback if both are not set
                self.default_font_size = 12.0

        # Calculate the new font size
        new_size = self.default_font_size * zoom_factor

        # Apply the new font size to the document
        default_font.setPointSizeF(new_size)
        document.setDefaultFont(default_font)

        # Store cursor position and scroll position
        cursor_pos = self.editor.textCursor().position()
        scroll_pos = (
            self.editor.verticalScrollBar().value()
            if hasattr(self.editor, "verticalScrollBar")
            else 0
        )

        # Scale embedded images
        self.scale_images(document, relative_factor)

        # Restore cursor and scroll position
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor_pos)
        self.editor.setTextCursor(cursor)
        if hasattr(self.editor, "verticalScrollBar"):
            # Scale the scroll position by the zoom factor to maintain view position
            self.editor.verticalScrollBar().setValue(int(scroll_pos * relative_factor))

        # Update the display
        self.update_display()

        # Emit signal for other components
        self.zoom_changed.emit(zoom_factor)

    def update_display(self):
        """Update the zoom combo box to reflect the current zoom level."""
        # Check if current zoom is in predefined levels
        if self.current_zoom in self.ZOOM_LEVELS:
            index = self.ZOOM_LEVELS.index(self.current_zoom)
            self.zoom_combo.setCurrentIndex(index)
        else:
            # Custom zoom level - add it to the combobox
            self.zoom_combo.setEditText(f"{self.current_zoom}%")

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming.

        Args:
            event (QWheelEvent): The wheel event
        """
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom in/out with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Pass event to parent for normal scrolling
            super().wheelEvent(event)
