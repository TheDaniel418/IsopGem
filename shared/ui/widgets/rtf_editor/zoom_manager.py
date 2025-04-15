from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QToolButton, QWidget

from shared.ui.widgets.rtf_editor.utils.error_utils import handle_error, handle_warning
from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)


class ZoomManager(QWidget):
    """Manages zoom functionality for the RTF editor.

    This class provides a complete zoom management system for a QTextEdit-based editor,
    including a UI with zoom controls and the ability to scale both text and embedded images.

    Attributes:
        zoom_changed (pyqtSignal): Signal emitted when zoom level changes, with the new zoom factor
        ZOOM_LEVELS (list): Predefined zoom levels as percentages
        DEFAULT_ZOOM (int): Default zoom level (100%)

    Signals:
        zoom_changed(float): Emitted when zoom level changes, with zoom factor (1.0 = 100%)
    """

    # Signal emitted when zoom level changes
    zoom_changed = pyqtSignal(float)

    # Predefined zoom levels as percentages
    ZOOM_LEVELS = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500]
    DEFAULT_ZOOM = 100

    def __init__(self, editor, parent=None):
        """Initialize the ZoomManager.

        Creates a zoom management widget with controls for zooming in, out, and selecting
        specific zoom levels. Applies the default zoom level to the editor on initialization.

        Args:
            editor (QTextEdit): The text editor to apply zoom to
            parent (QWidget, optional): Parent widget for this control

        Raises:
            TypeError: If editor is not a QTextEdit or compatible object
        """
        super().__init__(parent)
        self.editor = editor
        self.current_zoom = self.DEFAULT_ZOOM

        # Setup UI
        self.setup_ui()

        # Apply initial zoom
        self.apply_zoom(self.current_zoom)

    def setup_ui(self):
        """Set up the zoom controls UI.

        Creates and configures the UI components for the zoom manager:
        - Zoom out button (-)
        - Zoom level combo box with predefined and custom levels
        - Zoom in button (+)
        - Reset zoom button (100%)

        All components are connected to their respective handlers.

        Returns:
            None
        """
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

        Called when the user selects a predefined zoom level from the combo box.
        Retrieves the zoom level from the combo box's item data and applies it.

        Args:
            index (int): Index of the selected item in the combo box

        Returns:
            None

        Note:
            This method is connected to the combo box's currentIndexChanged signal.
        """
        if index >= 0:
            zoom_level = self.zoom_combo.itemData(index)
            if zoom_level:
                self.apply_zoom(zoom_level)

    def on_edit_text_changed(self, text):
        """Handle manual entry of a zoom level.

        Called when the user manually types a zoom level in the combo box.
        Extracts numeric values from the text, validates them, and applies
        the zoom if the input is valid and complete (ends with % or newline).

        Args:
            text (str): The text entered in the combobox

        Returns:
            None

        Raises:
            ValueError: Handled internally when text cannot be converted to a valid zoom level

        Note:
            This method is connected to the combo box's editTextChanged signal.
        """
        # Input validation and extraction of numbers from text
        try:
            # Validate input is not empty
            if not text:
                return

            # Remove non-digit characters and convert to int
            zoom_text = "".join(filter(str.isdigit, text))
            if not zoom_text:
                logger.warning(f"Invalid zoom text entered: {text}")
                return

            # Convert to integer with validation
            try:
                zoom_level = int(zoom_text)
            except ValueError:
                logger.warning(f"Could not convert zoom text to integer: {zoom_text}")
                return

            # Validate zoom level is within acceptable range
            if zoom_level < 10 or zoom_level > 500:
                logger.warning(f"Zoom level out of range: {zoom_level}")

            # Limit zoom level to a reasonable range
            zoom_level = max(10, min(zoom_level, 500))

            # Log the validated zoom level
            logger.debug(f"Validated zoom level: {zoom_level}%")

            # Only apply if enter is pressed or focus is lost
            # Otherwise wait for user to finish typing
            if text.endswith("%") or text.endswith("\n"):
                self.apply_zoom(zoom_level)
        except ValueError:
            # Handle invalid input
            handle_warning(
                self, "Invalid zoom value, using current zoom level", show_dialog=False
            )
            # Reset to current zoom if input is invalid
            self.update_display()

    def zoom_in(self):
        """Increase the zoom level.

        Finds the next predefined zoom level higher than the current level
        and applies it. If already at the highest predefined level, increases
        by 50% increments.

        Returns:
            None

        Note:
            This method is connected to the zoom in button's clicked signal.
        """
        # Find the next zoom level higher than current
        for level in self.ZOOM_LEVELS:
            if level > self.current_zoom:
                self.apply_zoom(level)
                return

        # If we're already at the highest predefined level, increase by 50%
        self.apply_zoom(self.current_zoom + 50)

    def zoom_out(self):
        """Decrease the zoom level.

        Finds the next predefined zoom level lower than the current level
        and applies it. If already at the lowest predefined level, decreases
        by 50% increments but never goes below 10%.

        Returns:
            None

        Note:
            This method is connected to the zoom out button's clicked signal.
        """
        # Find the next zoom level lower than current
        for level in reversed(self.ZOOM_LEVELS):
            if level < self.current_zoom:
                self.apply_zoom(level)
                return

        # If we're already at the lowest predefined level, decrease by 50%
        # but don't go below 10%
        self.apply_zoom(max(10, self.current_zoom - 50))

    def reset_zoom(self):
        """Reset zoom to the default level (100%).

        Resets the zoom level to the default (100%), regardless of the current level.

        Returns:
            None

        Note:
            This method is connected to the reset zoom button's clicked signal.
        """
        self.apply_zoom(self.DEFAULT_ZOOM)

    def set_zoom(self, level):
        """Set zoom to a specific level.

        Sets the zoom to an exact level specified as a percentage.
        The level will be constrained to the range 10-500%.

        Args:
            level (int): Zoom level as a percentage (e.g., 100 for 100%)

        Returns:
            None

        Note:
            This method can be called programmatically or connected to UI elements.
        """
        self.apply_zoom(level)

    def scale_images(self, document, scale_factor):
        """Scale all images in the document by the given factor.

        Attempts to scale all images in the document using two different methods:
        1. Selection-based scaling: Iterates through the document character by character
        2. Fragment-based scaling: Iterates through document fragments

        Both methods are used for redundancy to ensure images are properly scaled.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by (e.g., 1.25 for 125%)

        Returns:
            None

        Raises:
            Exception: Handled internally for any errors during scaling

        Note:
            This is an internal method called by apply_zoom.
        """
        try:
            logger.debug(f"Scaling images with factor: {scale_factor}")

            # Try different methods to scale images
            self._scale_images_by_selection(document, scale_factor)

            # Try another approach if the first one didn't work
            self._scale_images_by_fragment(document, scale_factor)

            # Force layout update
            document.markContentsDirty(0, document.characterCount())
            document.setModified(True)

        except Exception as e:
            error_msg = f"Error scaling images: {str(e)}"
            handle_error(self, error_msg, e, show_dialog=False)

    def _scale_images_by_selection(self, document, scale_factor):
        """Scale images by selecting characters in document.

        First method for scaling images: iterates through the document character by character,
        checking each character for image formats. When an image is found, it's scaled
        by the given factor.

        This method uses QTextCursor to select and modify each character.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by

        Returns:
            None

        Raises:
            Exception: Handled internally for any errors during scaling

        Note:
            This is a private method called by scale_images.
        """
        try:
            from PyQt6.QtGui import QTextCursor, QTextImageFormat

            logger.debug("Trying to scale images by selection method")

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

                    logger.debug(
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

                        logger.debug(f"Scaled image to {new_width}x{new_height}")

                        # Mark as processed
                        processed.add(pos)

                # Move to next character
                if not cursor.movePosition(QTextCursor.MoveOperation.Right):
                    break

            # Restore original position
            cursor.setPosition(original_pos)

            logger.info(f"Found and processed {count} images")

        except Exception as e:
            error_msg = f"Error in selection-based image scaling: {str(e)}"
            handle_error(self, error_msg, e, show_dialog=False)

    def _scale_images_by_fragment(self, document, scale_factor):
        """Alternative approach to scale images using document fragments.

        Second method for scaling images: iterates through document blocks and fragments,
        checking each fragment for image formats. When an image is found, it's scaled
        by the given factor.

        This method uses document block and fragment iteration which may catch images
        that the selection method misses.

        Args:
            document (QTextDocument): The document containing images
            scale_factor (float): The factor to scale images by

        Returns:
            None

        Raises:
            Exception: Handled internally for any errors during scaling

        Note:
            This is a private method called by scale_images as a backup to _scale_images_by_selection.
        """
        try:
            from PyQt6.QtGui import QTextCursor, QTextImageFormat

            logger.debug("Trying to scale images by fragment method")

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

                        logger.debug(
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

                            logger.debug(
                                f"Scaled fragment image to {new_width}x{new_height}"
                            )

                    # Move to next fragment
                    it += 1

                # Move to next block
                block = block.next()

            logger.info(f"Found and processed {image_count} images by fragment")

        except Exception as e:
            error_msg = f"Error in fragment-based image scaling: {str(e)}"
            handle_error(self, error_msg, e, show_dialog=False)

    def apply_zoom(self, level):
        """Apply the zoom level to the editor.

        Core method that implements the zoom functionality. It:
        1. Validates and constrains the zoom level
        2. Calculates the relative zoom factor from the previous level
        3. Adjusts the document's default font size
        4. Scales all embedded images
        5. Preserves cursor position and scroll position
        6. Updates the UI to reflect the new zoom level
        7. Emits the zoom_changed signal

        Args:
            level (int): Zoom level as a percentage (e.g., 100 for 100%)

        Returns:
            None

        Note:
            This is the main implementation method called by all other zoom methods.
        """
        try:
            # Input validation
            if not isinstance(level, (int, float)):
                logger.warning(f"Invalid zoom level type: {type(level)}")
                level = self.current_zoom  # Use current zoom if invalid type

            # Convert to int if it's a float
            if isinstance(level, float):
                level = int(level)

            # Validate zoom level range
            if level < 10 or level > 500:
                logger.warning(
                    f"Zoom level out of range: {level}%, constraining to 10-500%"
                )

            # Constrain zoom level to reasonable limits
            level = max(10, min(level, 500))  # Limit zoom to 10%-500%

            logger.debug(f"Applying zoom level: {level}%")
        except Exception as e:
            logger.error(f"Error validating zoom level: {e}")
            level = self.current_zoom  # Use current zoom if validation fails
            handle_warning(
                self, f"Invalid zoom level, using {level}%", show_dialog=False
            )

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
        """Update the zoom combo box to reflect the current zoom level.

        Updates the UI to show the current zoom level. If the current level
        is one of the predefined levels, selects it in the combo box.
        Otherwise, sets a custom text value.

        Returns:
            None
        """
        # Check if current zoom is in predefined levels
        if self.current_zoom in self.ZOOM_LEVELS:
            index = self.ZOOM_LEVELS.index(self.current_zoom)
            self.zoom_combo.setCurrentIndex(index)
        else:
            # Custom zoom level - add it to the combobox
            self.zoom_combo.setEditText(f"{self.current_zoom}%")

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming.

        Implements Ctrl+Wheel zooming functionality. When the user holds Ctrl
        and scrolls the mouse wheel, the zoom level is increased or decreased.

        Args:
            event (QWheelEvent): The wheel event containing scroll information

        Returns:
            None

        Note:
            This method overrides QWidget.wheelEvent.
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
