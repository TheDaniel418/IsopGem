from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QTextListFormat, QAction
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFontComboBox,
    QSpinBox,
    QToolBar,
    QToolButton,
)


class FormatToolBar(QToolBar):
    """Advanced formatting toolbar for RTF editor.

    This class provides a comprehensive formatting toolbar for the RTF editor, including:
    - Font family and size selection
    - Bold, italic, underline, and strikethrough formatting
    - Text color and background color
    - Text alignment (left, center, right, justify)
    - Bullet and numbered lists
    - Indentation controls

    The toolbar monitors the current text selection and updates its controls to reflect
    the formatting of the selected text. It also emits signals when formatting is changed
    through the toolbar controls.

    Attributes:
        format_changed (pyqtSignal): Signal emitted when text format is changed
        alignment_changed (pyqtSignal): Signal emitted when text alignment is changed

    Signals:
        format_changed(QTextCharFormat): Emitted with the new format when changed
        alignment_changed(Qt.AlignmentFlag): Emitted with the new alignment when changed
    """

    # Signals for format changes
    format_changed = pyqtSignal(QTextCharFormat)
    alignment_changed = pyqtSignal(Qt.AlignmentFlag)

    def __init__(self, parent=None):
        """Initialize the formatting toolbar.

        Creates a toolbar with all formatting controls and connects their signals
        to appropriate slots. Sets up a timer for throttling rapid updates.

        Args:
            parent (QWidget, optional): Parent widget for this toolbar

        Returns:
            None
        """
        super().__init__(parent)
        
        # Configure toolbar for proper overflow handling
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setMovable(False)  # Prevent moving to avoid layout issues
        
        # Enable overflow menu - this is crucial for the arrow to work
        self.setFloatable(False)
        
        # Set a reasonable icon size
        self.setIconSize(self.iconSize())

        # Setup timer for throttling updates - disabled by default
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300)  # 300 ms throttle
        self.update_timer.timeout.connect(self._do_update_toolbar_state)

        # Flag to control automatic updates (disabled to prevent segfaults)
        self.auto_updates_enabled = False  # Disabled due to persistent segfaults

        self.setup_font_controls()
        self.setup_paragraph_controls()
        self.setup_list_controls()
        self.setup_alignment_controls()
        self.setup_spacing_controls()

        # Connect to text editor signals if possible
        self.connect_to_editor_signals()

    def queue_update_toolbar_state(self):
        """Queue a toolbar update with throttling to prevent rapid updates."""
        # Completely disabled to prevent segfaults
        return

        # Original implementation (disabled)
        # # Skip if auto-updates are disabled
        # if not self.auto_updates_enabled:
        #     return
        #
        # if not self.update_timer.isActive():
        #     self.update_timer.start()

    def _do_update_toolbar_state(self):
        """Actually perform the toolbar state update after throttling.

        This method is completely disabled to prevent segfaults.
        """
        # Completely disabled to prevent segfaults
        return

        # Original implementation (disabled)
        # """Actually perform the toolbar state update after throttling.
        #
        # This method updates the toolbar controls to reflect the formatting
        # at the current cursor position. It includes comprehensive error handling
        # to prevent segfaults that were previously occurring.
        # """
        # # Outer try block to catch any unexpected errors
        # try:
        #     # Try to get the text_edit from parent
        #     parent = self.parent()
        #     if not parent:
        #         return
        #
        #     # Check if parent has text_edit attribute
        #     editor = getattr(parent, "text_edit", None)
        #     if not editor:
        #         return
        #
        #     # Check if editor is valid and visible
        #     if not editor.isVisible() or not editor.isEnabled():
        #         return
        #
        #     # Get cursor with error handling
        #     try:
        #         cursor = editor.textCursor()
        #         if not cursor:
        #             return
        #         # Note: QTextCursor doesn't have isValid() method in PyQt6
        #     except Exception as e:
        #         print(f"Error getting text cursor: {e}")
        #         return
        #
        #     # Check if document is valid
        #     try:
        #         document = editor.document()
        #         if not document:
        #             return
        #     except Exception as e:
        #         print(f"Error accessing document: {e}")
        #         return
        #
        #     # Get the character format at cursor with error handling
        #     try:
        #         char_format = cursor.charFormat()
        #         # Note: QTextCharFormat doesn't have isValid() method in PyQt6
        #     except Exception as e:
        #         print(f"Error getting character format: {e}")
        #         return
        #
        #     # Update font family button
        #     try:
        #         font_family = char_format.fontFamily()
        #         if font_family:
        #             index = self.font_family.findText(font_family)
        #             if index >= 0:
        #                 self.font_family.setCurrentIndex(index)
        #     except Exception as e:
        #         print(f"Error updating font family: {e}")

        #     # Update font size
        #     try:
        #         font_size = char_format.fontPointSize()
        #         if font_size > 0:
        #             self.font_size.setCurrentText(str(int(font_size)))
        #     except Exception as e:
        #         print(f"Error updating font size: {e}")
        #
        #     # Update style buttons
        #     try:
        #         self.bold_btn.setChecked(char_format.fontWeight() >= QFont.Weight.Bold)
        #         self.italic_btn.setChecked(char_format.fontItalic())
        #         self.underline_btn.setChecked(char_format.fontUnderline())
        #     except Exception as e:
        #         print(f"Error updating style buttons: {e}")
        #
        #     # Update indentation and spacing
        #     try:
        #         block_format = cursor.blockFormat()
        #
        #         indent = block_format.leftMargin()
        #         if indent >= 0 and indent <= 100:  # Make sure it's within range
        #             self.indent_spin.blockSignals(True)
        #             self.indent_spin.setValue(indent)
        #             self.indent_spin.blockSignals(False)
        #
        #         spacing = block_format.bottomMargin()
        #         if spacing >= 0 and spacing <= 100:  # Make sure it's within range
        #             self.spacing_spin.blockSignals(True)
        #             self.spacing_spin.setValue(spacing)
        #             self.spacing_spin.blockSignals(False)
        #     except Exception as e:
        #         print(f"Error updating indentation/spacing: {e}")
        #
        #     # Update list buttons
        #     try:
        #         current_list = cursor.currentList()
        #         if current_list:
        #             fmt = current_list.format()
        #             style = fmt.style()
        #
        #             # Set the correct list button state
        #             self.bullet_btn.blockSignals(True)
        #             self.number_btn.blockSignals(True)
        #
        #             self.bullet_btn.setChecked(style == QTextListFormat.Style.ListDisc)
        #             self.number_btn.setChecked(
        #                 style == QTextListFormat.Style.ListDecimal
        #             )
        #
        #             self.bullet_btn.blockSignals(False)
        #             self.number_btn.blockSignals(False)
        #         else:
        #             self.bullet_btn.blockSignals(True)
        #             self.number_btn.blockSignals(True)
        #
        #             self.bullet_btn.setChecked(False)
        #             self.number_btn.setChecked(False)
        #
        #             self.bullet_btn.blockSignals(False)
        #             self.number_btn.blockSignals(False)
        #     except Exception as e:
        #         print(f"Error updating list buttons: {e}")
        # except Exception as e:
        #     print(f"Error updating toolbar state: {e}")

    def connect_to_editor_signals(self):
        """Safely connect to text editor signals.

        This method is completely disabled to prevent segfaults.

        Returns:
            bool: Always returns False as connections are disabled
        """
        # Completely disabled to prevent segfaults
        return False

        # Original implementation (disabled)
        # try:
        #     # Only connect if auto-updates are enabled
        #     if not self.auto_updates_enabled:
        #         return False
        #
        #     # Try to get the parent and text_edit
        #     parent = self.parent()
        #     if not parent or not hasattr(parent, "text_edit"):
        #         return False
        #
        #     text_edit = parent.text_edit
        #
        #     # Disconnect any existing connections first to prevent duplicates
        #     try:
        #         text_edit.cursorPositionChanged.disconnect(self.queue_update_toolbar_state)
        #     except:
        #         pass  # Ignore if not connected
        #
        #     try:
        #         text_edit.selectionChanged.disconnect(self.queue_update_toolbar_state)
        #     except:
        #         pass  # Ignore if not connected
        #
        #     # Connect signals with error handling
        #     text_edit.cursorPositionChanged.connect(self.queue_update_toolbar_state)
        #     text_edit.selectionChanged.connect(self.queue_update_toolbar_state)
        #
        #     return True
        # except Exception as e:
        #     print(f"Error connecting to editor signals: {e}")
        #     return False

    # Legacy method for compatibility
    def update_toolbar_state(self):
        """Disabled to prevent segfaults."""
        # Completely disabled to prevent segfaults
        return

        # Original implementation (disabled)
        # self.queue_update_toolbar_state()

    def setup_font_controls(self):
        """Set up basic font formatting controls."""
        # Font family
        self.font_family = QFontComboBox()
        self.font_family.setToolTip("Font Family")
        self.font_family.setMaximumWidth(200)  # Prevent it from taking too much space
        self.font_family.currentFontChanged.connect(self.font_family_changed)
        
        # Create action for font family to enable overflow handling
        font_family_action = QAction("Font Family", self)
        font_family_action.setToolTip("Font Family")
        self.addAction(font_family_action)
        self.widgetForAction(font_family_action).hide()  # Hide the default widget
        self.addWidget(self.font_family)

        # Font size
        self.font_size = QComboBox()
        self.font_size.setToolTip("Font Size")
        self.font_size.setEditable(True)
        self.font_size.setMinimumWidth(50)
        self.font_size.setMaximumWidth(80)  # Prevent it from taking too much space
        self.font_size.addItems(
            [
                str(size)
                for size in [
                    8,
                    9,
                    10,
                    11,
                    12,
                    14,
                    16,
                    18,
                    20,
                    22,
                    24,
                    26,
                    28,
                    36,
                    48,
                    72,
                ]
            ]
        )
        self.font_size.currentTextChanged.connect(self.font_size_changed)
        
        # Create action for font size to enable overflow handling
        font_size_action = QAction("Font Size", self)
        font_size_action.setToolTip("Font Size")
        self.addAction(font_size_action)
        self.widgetForAction(font_size_action).hide()  # Hide the default widget
        self.addWidget(self.font_size)

        self.addSeparator()

        # Bold - use QAction for proper overflow support
        self.bold_action = QAction("Bold", self)
        self.bold_action.setToolTip("Bold (Ctrl+B)")
        self.bold_action.setCheckable(True)
        # Make shortcut context-specific to avoid conflicts between multiple RTF editors
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.addAction(self.bold_action)
        
        # Get the button and style it
        self.bold_btn = self.widgetForAction(self.bold_action)
        if isinstance(self.bold_btn, QToolButton):
            self.bold_btn.setText("B")
            font = QFont()
            font.setBold(True)
            self.bold_btn.setFont(font)

        # Italic - use QAction for proper overflow support
        self.italic_action = QAction("Italic", self)
        self.italic_action.setToolTip("Italic (Ctrl+I)")
        self.italic_action.setCheckable(True)
        # Make shortcut context-specific to avoid conflicts between multiple RTF editors
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.addAction(self.italic_action)
        
        # Get the button and style it
        self.italic_btn = self.widgetForAction(self.italic_action)
        if isinstance(self.italic_btn, QToolButton):
            self.italic_btn.setText("I")
            font = QFont()
            font.setItalic(True)
            self.italic_btn.setFont(font)

        # Underline - use QAction for proper overflow support
        self.underline_action = QAction("Underline", self)
        self.underline_action.setToolTip("Underline (Ctrl+U)")
        self.underline_action.setCheckable(True)
        # Make shortcut context-specific to avoid conflicts between multiple RTF editors
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.underline_action.triggered.connect(self.toggle_underline)
        self.addAction(self.underline_action)
        
        # Get the button and style it
        self.underline_btn = self.widgetForAction(self.underline_action)
        if isinstance(self.underline_btn, QToolButton):
            self.underline_btn.setText("U")
            font = QFont()
            font.setUnderline(True)
            self.underline_btn.setFont(font)

        self.addSeparator()

        # Text color - use QAction for proper overflow support
        self.color_action = QAction("Text Color", self)
        self.color_action.setToolTip("Text Color")
        self.color_action.triggered.connect(self.show_color_dialog)
        self.addAction(self.color_action)
        
        # Get the button and style it
        self.color_btn = self.widgetForAction(self.color_action)
        if isinstance(self.color_btn, QToolButton):
            self.color_btn.setText("A")
            self.color_btn.setStyleSheet("color: red;")

        self.addSeparator()

    def font_family_changed(self, font):
        """Handle font family changes."""
        format = QTextCharFormat()
        format.setFontFamily(font.family())
        self.format_changed.emit(format)

    def font_size_changed(self, size):
        """Handle font size changes."""
        format = QTextCharFormat()
        try:
            format.setFontPointSize(float(size))
            self.format_changed.emit(format)
        except ValueError:
            pass

    def toggle_bold(self, checked):
        """Toggle bold formatting."""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
        self.format_changed.emit(format)

    def toggle_italic(self, checked):
        """Toggle italic formatting."""
        format = QTextCharFormat()
        format.setFontItalic(checked)
        self.format_changed.emit(format)

    def toggle_underline(self, checked):
        """Toggle underline formatting."""
        format = QTextCharFormat()
        format.setFontUnderline(checked)
        self.format_changed.emit(format)

    def show_color_dialog(self):
        """Show color picker dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            format = QTextCharFormat()
            format.setForeground(color)
            self.format_changed.emit(format)

    def setup_paragraph_controls(self):
        """Set up paragraph formatting controls."""
        # Paragraph style dropdown
        self.style_combo = QComboBox()
        self.style_combo.setToolTip("Paragraph Style")
        self.style_combo.setMaximumWidth(120)  # Prevent it from taking too much space
        self.style_combo.addItems(["Normal", "Heading 1", "Heading 2", "Heading 3"])
        self.style_combo.currentTextChanged.connect(self.style_changed)
        
        # Create action for style combo to enable overflow handling
        style_action = QAction("Paragraph Style", self)
        style_action.setToolTip("Paragraph Style")
        self.addAction(style_action)
        self.widgetForAction(style_action).hide()  # Hide the default widget
        self.addWidget(self.style_combo)

        self.addSeparator()

        # Line spacing
        self.line_spacing = QComboBox()
        self.line_spacing.setToolTip("Line Spacing")
        self.line_spacing.setMaximumWidth(80)  # Prevent it from taking too much space
        self.line_spacing.addItems(["1.0", "1.15", "1.5", "2.0"])
        self.line_spacing.currentTextChanged.connect(self.line_spacing_changed)
        
        # Create action for line spacing to enable overflow handling
        spacing_action = QAction("Line Spacing", self)
        spacing_action.setToolTip("Line Spacing")
        self.addAction(spacing_action)
        self.widgetForAction(spacing_action).hide()  # Hide the default widget
        self.addWidget(self.line_spacing)

    def setup_list_controls(self):
        """Set up list formatting controls."""
        self.addSeparator()

        # Bullet list - use QAction for proper overflow support
        self.bullet_action = QAction("Bullet List", self)
        self.bullet_action.setToolTip("Bullet List")
        self.bullet_action.setCheckable(True)
        self.bullet_action.triggered.connect(self.toggle_bullet_list)
        self.addAction(self.bullet_action)
        
        # Get the button and style it
        self.bullet_btn = self.widgetForAction(self.bullet_action)
        if isinstance(self.bullet_btn, QToolButton):
            self.bullet_btn.setText("•")

        # Numbered list - use QAction for proper overflow support
        self.number_action = QAction("Numbered List", self)
        self.number_action.setToolTip("Numbered List")
        self.number_action.setCheckable(True)
        self.number_action.triggered.connect(self.toggle_numbered_list)
        self.addAction(self.number_action)
        
        # Get the button and style it
        self.number_btn = self.widgetForAction(self.number_action)
        if isinstance(self.number_btn, QToolButton):
            self.number_btn.setText("1.")

    def setup_alignment_controls(self):
        """Set up text alignment controls."""
        self.addSeparator()

        # Left align - use QAction for proper overflow support
        self.align_left_action = QAction("Align Left", self)
        self.align_left_action.setToolTip("Align Left")
        self.align_left_action.triggered.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft)
        )
        self.addAction(self.align_left_action)
        
        # Get the button and style it
        self.align_left = self.widgetForAction(self.align_left_action)
        if isinstance(self.align_left, QToolButton):
            self.align_left.setText("⫷")

        # Center align - use QAction for proper overflow support
        self.align_center_action = QAction("Align Center", self)
        self.align_center_action.setToolTip("Align Center")
        self.align_center_action.triggered.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter)
        )
        self.addAction(self.align_center_action)
        
        # Get the button and style it
        self.align_center = self.widgetForAction(self.align_center_action)
        if isinstance(self.align_center, QToolButton):
            self.align_center.setText("⫼")

        # Right align - use QAction for proper overflow support
        self.align_right_action = QAction("Align Right", self)
        self.align_right_action.setToolTip("Align Right")
        self.align_right_action.triggered.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight)
        )
        self.addAction(self.align_right_action)
        
        # Get the button and style it
        self.align_right = self.widgetForAction(self.align_right_action)
        if isinstance(self.align_right, QToolButton):
            self.align_right.setText("⫸")

        # Justify - use QAction for proper overflow support
        self.justify_action = QAction("Justify", self)
        self.justify_action.setToolTip("Justify")
        self.justify_action.triggered.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignJustify)
        )
        self.addAction(self.justify_action)
        
        # Get the button and style it
        self.justify = self.widgetForAction(self.justify_action)
        if isinstance(self.justify, QToolButton):
            self.justify.setText("⫿")

    def setup_spacing_controls(self):
        """Set up paragraph spacing controls."""
        self.addSeparator()

        # Indent controls
        self.indent_spin = QSpinBox()
        self.indent_spin.setToolTip("Paragraph Indent")
        self.indent_spin.setRange(0, 100)
        self.indent_spin.setSuffix(" px")
        self.indent_spin.setMaximumWidth(80)  # Prevent it from taking too much space
        self.indent_spin.valueChanged.connect(self.indent_changed)
        
        # Create action for indent spin to enable overflow handling
        indent_action = QAction("Paragraph Indent", self)
        indent_action.setToolTip("Paragraph Indent")
        self.addAction(indent_action)
        self.widgetForAction(indent_action).hide()  # Hide the default widget
        self.addWidget(self.indent_spin)

        # Spacing controls
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setToolTip("Paragraph Spacing")
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setSuffix(" px")
        self.spacing_spin.setMaximumWidth(80)  # Prevent it from taking too much space
        self.spacing_spin.valueChanged.connect(self.spacing_changed)
        
        # Create action for spacing spin to enable overflow handling
        spacing_action = QAction("Paragraph Spacing", self)
        spacing_action.setToolTip("Paragraph Spacing")
        self.addAction(spacing_action)
        self.widgetForAction(spacing_action).hide()  # Hide the default widget
        self.addWidget(self.spacing_spin)

    def style_changed(self, style):
        """Handle paragraph style changes."""
        format = QTextCharFormat()
        if style == "Normal":
            format.setFontPointSize(12)
            format.setFontWeight(QFont.Weight.Normal)
        elif style == "Heading 1":
            format.setFontPointSize(24)
            format.setFontWeight(QFont.Weight.Bold)
        elif style == "Heading 2":
            format.setFontPointSize(18)
            format.setFontWeight(QFont.Weight.Bold)
        elif style == "Heading 3":
            format.setFontPointSize(14)
            format.setFontWeight(QFont.Weight.Bold)
        self.format_changed.emit(format)

    def line_spacing_changed(self, spacing):
        """Change the line spacing for the current paragraph."""
        # Get the text editor from parent
        parent = self.parent()
        if not parent:
            return

        editor = getattr(parent, "text_edit", None)
        if not editor:
            return

        cursor = editor.textCursor()

        try:
            # Get the current block format
            block_fmt = cursor.blockFormat()

            # Set line spacing - this is the correct way to do it
            line_spacing_value = float(spacing)
            block_fmt.setLineHeight(
                line_spacing_value * 100, 1
            )  # 1 = ProportionalHeight

            # Apply the updated block format
            cursor.setBlockFormat(block_fmt)

            # Update the editor with the modified cursor
            editor.setTextCursor(cursor)

            # Still emit a format change signal for consistency
            format = QTextCharFormat()
            self.format_changed.emit(format)
        except Exception as e:
            print(f"Error setting line spacing: {e}")

    def toggle_bullet_list(self, checked):
        """Toggle bullet list formatting for the current paragraph."""
        # Get the text editor from parent
        parent = self.parent()
        if not parent:
            return

        editor = getattr(parent, "text_edit", None)
        if not editor:
            return

        cursor = editor.textCursor()

        try:
            # Safer implementation - just emit signal and let the editor handle it
            format = QTextCharFormat()
            self.format_changed.emit(format)

            # Let the text editor handle the list formatting directly
            doc = editor.document()

            # Use the built-in list creation mechanism
            if checked:
                cursor.createList(QTextListFormat.Style.ListDisc)
            else:
                # Get the current list
                current_list = cursor.currentList()
                if current_list:
                    # Just indent the block as a simple text
                    block_fmt = cursor.blockFormat()
                    # Remove list formatting
                    cursor.beginEditBlock()
                    block_fmt.setIndent(0)
                    cursor.setBlockFormat(block_fmt)
                    cursor.endEditBlock()

            # Update cursor
            editor.setTextCursor(cursor)

        except Exception as e:
            print(f"Error in bullet list: {e}")

    def toggle_numbered_list(self, checked):
        """Toggle numbered list formatting for the current paragraph."""
        # Get the text editor from parent
        parent = self.parent()
        if not parent:
            return

        editor = getattr(parent, "text_edit", None)
        if not editor:
            return

        cursor = editor.textCursor()

        try:
            # Safer implementation - just emit signal and let the editor handle it
            format = QTextCharFormat()
            self.format_changed.emit(format)

            # Let the text editor handle the list formatting directly
            doc = editor.document()

            # Use the built-in list creation mechanism
            if checked:
                cursor.createList(QTextListFormat.Style.ListDecimal)
            else:
                # Get the current list
                current_list = cursor.currentList()
                if current_list:
                    # Just indent the block as a simple text
                    block_fmt = cursor.blockFormat()
                    # Remove list formatting
                    cursor.beginEditBlock()
                    block_fmt.setIndent(0)
                    cursor.setBlockFormat(block_fmt)
                    cursor.endEditBlock()

            # Update cursor
            editor.setTextCursor(cursor)

        except Exception as e:
            print(f"Error in numbered list: {e}")

    def set_alignment(self, alignment):
        """Set text alignment."""
        self.alignment_changed.emit(alignment)

    def indent_changed(self, value):
        """Handle paragraph indentation changes."""
        parent = self.parent()
        if not parent:
            return

        editor = getattr(parent, "text_edit", None)
        if not editor:
            return

        cursor = editor.textCursor()

        # Get the current block format
        block_fmt = cursor.blockFormat()

        # Set the left margin (indentation)
        block_fmt.setLeftMargin(value)

        # Apply the updated block format
        cursor.setBlockFormat(block_fmt)

        # Update the editor with the modified cursor
        editor.setTextCursor(cursor)

        # Also emit a format change signal (empty as we directly changed the editor)
        format = QTextCharFormat()
        self.format_changed.emit(format)

    def spacing_changed(self, value):
        """Change paragraph spacing."""
        # Get the text editor from parent
        parent = self.parent()
        if not parent:
            return

        editor = getattr(parent, "text_edit", None)
        if not editor:
            return

        cursor = editor.textCursor()

        try:
            # Get the current block format
            block_fmt = cursor.blockFormat()

            # Set bottom margin (spacing after paragraph)
            block_fmt.setBottomMargin(value)

            # Apply the updated block format
            cursor.setBlockFormat(block_fmt)

            # Update the editor with the modified cursor
            editor.setTextCursor(cursor)

            # Also emit a format change signal (empty as we directly changed the editor)
            format = QTextCharFormat()
            self.format_changed.emit(format)
        except Exception as e:
            print(f"Error setting paragraph spacing: {e}")
