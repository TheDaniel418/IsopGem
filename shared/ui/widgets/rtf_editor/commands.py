"""
Purpose: Implements the Command pattern for comprehensive undo/redo functionality in RTF editor

This file is part of the shared UI widgets and serves as a utility component.
It provides a robust command framework to track all document changes and enable proper
undo/redo operations for text edits, formatting changes, image operations, and table
modifications.

Key components:
- Command: Base class for all commands
- CommandHistory: Tracks command execution and provides undo/redo functionality
- Various concrete command classes for specific operations

Dependencies:
- PyQt6: For UI operations and event handling
"""

import uuid
from datetime import datetime
from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import (
    QTextCharFormat,
    QTextCursor,
    QTextImageFormat,
)
from PyQt6.QtWidgets import QTextEdit


class Command:
    """Base command class for all undo/redo operations.

    This abstract base class defines the interface for all commands
    in the Command pattern. Each concrete command must implement execute(),
    undo(), and can_merge() methods.

    Attributes:
        timestamp (datetime): When the command was created
        id (str): Unique identifier for the command
    """

    def __init__(self):
        """Initialize the command with a timestamp and unique ID."""
        self.timestamp = datetime.now()
        self.id = str(uuid.uuid4())

    def execute(self):
        """Execute the command.

        This method must be implemented by concrete command classes.
        It performs the actual operation on the document.

        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def undo(self):
        """Undo the command.

        This method must be implemented by concrete command classes.
        It reverses the operation performed by execute().

        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement undo()")

    def can_merge(self, other):
        """Check if this command can be merged with another command.

        This method determines if two consecutive commands can be combined
        into a single command for undo/redo purposes.

        Args:
            other (Command): The command to potentially merge with

        Returns:
            bool: True if commands can be merged, False otherwise
        """
        return False

    def merge(self, other):
        """Merge this command with another command.

        This method combines two commands into a single command
        for undo/redo purposes.

        Args:
            other (Command): The command to merge with

        Returns:
            bool: True if successfully merged, False otherwise
        """
        return False


class TextCommand(Command):
    """Base class for text-related commands.

    This class serves as a base for commands that modify text content.

    Attributes:
        editor (QTextEdit): The text editor widget
        cursor_position (int): Position of the cursor when the command was created
        selection_start (int): Selection start position, if applicable
        selection_end (int): Selection end position, if applicable
    """

    def __init__(self, editor: QTextEdit):
        """Initialize with text editor reference and cursor state.

        Args:
            editor (QTextEdit): The text editor widget
        """
        super().__init__()
        self.editor = editor
        cursor = editor.textCursor()
        self.cursor_position = cursor.position()
        self.selection_start = cursor.selectionStart()
        self.selection_end = cursor.selectionEnd()

    def restore_cursor(self):
        """Restore the cursor to its original position or selection.

        Returns:
            None
        """
        cursor = self.editor.textCursor()
        if self.selection_start != self.selection_end:
            cursor.setPosition(self.selection_start)
            cursor.setPosition(self.selection_end, QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.setPosition(self.cursor_position)
        self.editor.setTextCursor(cursor)


class InsertTextCommand(TextCommand):
    """Command for inserting text.

    This command handles text insertion operations including
    typing, pasting, or programmatic insertion.

    Attributes:
        text (str): The text that was inserted
        position (int): The position where text was inserted
    """

    def __init__(self, editor: QTextEdit, text: str, position: Optional[int] = None):
        """Initialize with text editor, inserted text, and position.

        Args:
            editor (QTextEdit): The text editor widget
            text (str): The text being inserted
            position (int, optional): The position where text was inserted.
                If None, the current cursor position is used.
        """
        super().__init__(editor)
        self.text = text
        self.position = position if position is not None else self.cursor_position
        self.length = len(text)

    def execute(self):
        """Execute the text insertion.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.insertText(self.text)
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error executing InsertTextCommand: {e}")
            return False

    def undo(self):
        """Undo the text insertion by deleting the inserted text.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                self.length,
            )
            cursor.removeSelectedText()
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error undoing InsertTextCommand: {e}")
            return False

    def can_merge(self, other):
        """Check if this command can be merged with another command.

        Merging is possible if:
        1. The other command is also an InsertTextCommand
        2. The other command's position is right after this command's last character
        3. The commands were executed within a short time of each other
        4. The other command's text is a single character (typing) or both are longer (paste operations)

        Args:
            other (Command): The command to potentially merge with

        Returns:
            bool: True if commands can be merged, False otherwise
        """
        if not isinstance(other, InsertTextCommand):
            return False

        # Check if positions are adjacent
        if other.position != self.position + self.length:
            return False

        # Check if timestamps are close (within 2 seconds)
        time_diff = (other.timestamp - self.timestamp).total_seconds()
        if time_diff > 2.0:
            return False

        # Check if both are single character insertions (typing)
        # or both are longer strings (paste operations)
        if (len(self.text) == 1 and len(other.text) == 1) or (
            len(self.text) > 1 and len(other.text) > 1
        ):
            return True

        return False

    def merge(self, other):
        """Merge this command with another InsertTextCommand.

        Args:
            other (InsertTextCommand): The command to merge with

        Returns:
            bool: True if successfully merged, False otherwise
        """
        if not self.can_merge(other):
            return False

        self.text += other.text
        self.length = len(self.text)
        return True


class DeleteTextCommand(TextCommand):
    """Command for deleting text.

    This command handles text deletion operations including
    backspace, delete, or programmatic removal.

    Attributes:
        text (str): The text that was deleted
        position (int): The position where text was deleted
    """

    def __init__(self, editor: QTextEdit, position: int, length: int):
        """Initialize with text editor, position, and length of deleted text.

        Args:
            editor (QTextEdit): The text editor widget
            position (int): The position where text was deleted
            length (int): The length of the deleted text
        """
        super().__init__(editor)
        self.position = position
        self.length = length

        # Store the text that will be deleted for undo operations
        cursor = editor.textCursor()
        cursor.setPosition(position)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, length
        )
        self.text = cursor.selectedText()

    def execute(self):
        """Execute the text deletion.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                self.length,
            )
            cursor.removeSelectedText()
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error executing DeleteTextCommand: {e}")
            return False

    def undo(self):
        """Undo the text deletion by inserting the deleted text.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.insertText(self.text)
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error undoing DeleteTextCommand: {e}")
            return False

    def can_merge(self, other):
        """Check if this command can be merged with another command.

        Merging is possible if:
        1. The other command is also a DeleteTextCommand
        2. The deletions are adjacent (either forward or backward)
        3. The commands were executed within a short time of each other

        Args:
            other (Command): The command to potentially merge with

        Returns:
            bool: True if commands can be merged, False otherwise
        """
        if not isinstance(other, DeleteTextCommand):
            return False

        # Check if timestamps are close (within 2 seconds)
        time_diff = (other.timestamp - self.timestamp).total_seconds()
        if time_diff > 2.0:
            return False

        # Check if deletions are adjacent
        # Forward delete: this.position == other.position
        # Backward delete: other.position + other.length == this.position
        if other.position == self.position:
            # Forward deletions
            return True
        elif other.position + other.length == self.position:
            # Backward deletions
            return True

        return False

    def merge(self, other):
        """Merge this command with another DeleteTextCommand.

        Args:
            other (DeleteTextCommand): The command to merge with

        Returns:
            bool: True if successfully merged, False otherwise
        """
        if not self.can_merge(other):
            return False

        if other.position == self.position:
            # Forward deletions - append text
            self.text = self.text + other.text
            self.length += other.length
        elif other.position + other.length == self.position:
            # Backward deletions - prepend text
            self.text = other.text + self.text
            self.position = other.position
            self.length += other.length

        return True


class FormatCommand(TextCommand):
    """Command for applying text formatting.

    This command handles character formatting operations such as
    bold, italic, underline, font family, font size, etc.

    Attributes:
        format (QTextCharFormat): The format to apply
        old_format (QTextCharFormat): The previous format
    """

    def __init__(self, editor: QTextEdit, format: QTextCharFormat):
        """Initialize with text editor and format to apply.

        Args:
            editor (QTextEdit): The text editor widget
            format (QTextCharFormat): The format to apply
        """
        super().__init__(editor)
        self.format = format

        # Store the current format for undo operations
        cursor = editor.textCursor()
        self.old_format = cursor.charFormat()

    def execute(self):
        """Execute the format change.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.mergeCharFormat(self.format)
            self.editor.mergeCurrentCharFormat(self.format)
            return True
        except Exception as e:
            logger.error(f"Error executing FormatCommand: {e}")
            return False

    def undo(self):
        """Undo the format change by applying the old format.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.selection_start)
            cursor.setPosition(self.selection_end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(self.old_format)
            self.editor.mergeCurrentCharFormat(self.old_format)
            return True
        except Exception as e:
            logger.error(f"Error undoing FormatCommand: {e}")
            return False


class AlignmentCommand(TextCommand):
    """Command for changing text alignment.

    This command handles paragraph alignment operations such as
    left, right, center, and justify.

    Attributes:
        alignment (Qt.AlignmentFlag): The alignment to apply
        old_alignment (Qt.AlignmentFlag): The previous alignment
    """

    def __init__(self, editor: QTextEdit, alignment: Qt.AlignmentFlag):
        """Initialize with text editor and alignment to apply.

        Args:
            editor (QTextEdit): The text editor widget
            alignment (Qt.AlignmentFlag): The alignment to apply
        """
        super().__init__(editor)
        self.alignment = alignment

        # Store the current alignment for undo operations
        cursor = editor.textCursor()
        block_format = cursor.blockFormat()
        self.old_alignment = block_format.alignment()

    def execute(self):
        """Execute the alignment change.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.editor.setAlignment(self.alignment)
            return True
        except Exception as e:
            logger.error(f"Error executing AlignmentCommand: {e}")
            return False

    def undo(self):
        """Undo the alignment change by setting the previous alignment.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.selection_start)
            cursor.setPosition(self.selection_end, QTextCursor.MoveMode.KeepAnchor)
            self.editor.setTextCursor(cursor)
            self.editor.setAlignment(self.old_alignment)
            return True
        except Exception as e:
            logger.error(f"Error undoing AlignmentCommand: {e}")
            return False


class InsertImageCommand(TextCommand):
    """Command for inserting images.

    This command handles image insertion operations.

    Attributes:
        image_format (QTextImageFormat): The image format to insert
        position (int): The position where the image was inserted
    """

    def __init__(
        self,
        editor: QTextEdit,
        image_format: QTextImageFormat,
        position: Optional[int] = None,
    ):
        """Initialize with text editor, image format, and position.

        Args:
            editor (QTextEdit): The text editor widget
            image_format (QTextImageFormat): The image format to insert
            position (int, optional): The position where the image was inserted.
                If None, the current cursor position is used.
        """
        super().__init__(editor)
        self.image_format = image_format
        self.position = position if position is not None else self.cursor_position

    def execute(self):
        """Execute the image insertion.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.insertImage(self.image_format)
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error executing InsertImageCommand: {e}")
            return False

    def undo(self):
        """Undo the image insertion by removing the image.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.position)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                1,  # Images count as a single character
            )
            cursor.removeSelectedText()
            self.editor.setTextCursor(cursor)
            return True
        except Exception as e:
            logger.error(f"Error undoing InsertImageCommand: {e}")
            return False


class CommandHistory(QObject):
    """Manages undo/redo history using the Command pattern.

    This class maintains two stacks: one for undo and one for redo.
    It handles the execution, undoing, and redoing of commands,
    as well as command merging for efficiency.

    Attributes:
        history_changed (pyqtSignal): Signal emitted when history changes
        undo_available (pyqtSignal): Signal emitted when undo state changes
        redo_available (pyqtSignal): Signal emitted when redo state changes

    Signals:
        history_changed(): Emitted when the command history changes
        undo_available(bool): Emitted with the current undo availability
        redo_available(bool): Emitted with the current redo availability
    """

    history_changed = pyqtSignal()
    undo_available = pyqtSignal(bool)
    redo_available = pyqtSignal(bool)

    def __init__(self, max_history: int = 100):
        """Initialize with maximum history size.

        Args:
            max_history (int, optional): Maximum number of commands to store.
                Defaults to 100.
        """
        super().__init__()
        self.max_history = max_history
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []

    def clear(self):
        """Clear all command history.

        Returns:
            None
        """
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._emit_signals()

    def push(self, command: Command):
        """Push a new command onto the undo stack and execute it.

        Args:
            command (Command): The command to execute and push

        Returns:
            bool: True if the command was executed successfully, False otherwise
        """
        # Clear the redo stack when a new command is pushed
        self.redo_stack.clear()

        # Try to merge with the last command if possible
        merged = False
        if self.undo_stack:
            last_command = self.undo_stack[-1]
            if last_command.can_merge(command):
                merged = last_command.merge(command)

        if not merged:
            # Execute the command
            if command.execute():
                # Check if we need to trim the history
                if len(self.undo_stack) >= self.max_history:
                    self.undo_stack.pop(0)

                # Add to the undo stack
                self.undo_stack.append(command)

                # Emit signals
                self._emit_signals()
                return True
            else:
                return False
        else:
            # Command was merged, emit signals in case the merge affected undo/redo state
            self._emit_signals()
            return True

    def undo(self):
        """Undo the last command on the undo stack.

        Returns:
            bool: True if a command was undone, False otherwise
        """
        if not self.undo_stack:
            return False

        command = self.undo_stack.pop()
        if command.undo():
            self.redo_stack.append(command)
            self._emit_signals()
            return True
        else:
            # If undo failed, put the command back on the undo stack
            self.undo_stack.append(command)
            return False

    def redo(self):
        """Redo the last undone command.

        Returns:
            bool: True if a command was redone, False otherwise
        """
        if not self.redo_stack:
            return False

        command = self.redo_stack.pop()
        if command.execute():
            self.undo_stack.append(command)
            self._emit_signals()
            return True
        else:
            # If redo failed, put the command back on the redo stack
            self.redo_stack.append(command)
            return False

    def can_undo(self):
        """Check if there are commands that can be undone.

        Returns:
            bool: True if there are commands on the undo stack, False otherwise
        """
        return len(self.undo_stack) > 0

    def can_redo(self):
        """Check if there are commands that can be redone.

        Returns:
            bool: True if there are commands on the redo stack, False otherwise
        """
        return len(self.redo_stack) > 0

    def _emit_signals(self):
        """Emit signals indicating changes in the command history.

        Returns:
            None
        """
        self.history_changed.emit()
        self.undo_available.emit(self.can_undo())
        self.redo_available.emit(self.can_redo())
