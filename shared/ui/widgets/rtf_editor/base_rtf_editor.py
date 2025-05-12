"""
@file base_rtf_editor.py
@description Base interface for rich text editors
@created 2024-05-05
@dependencies PyQt6

Defines the interface contract for rich text editors in the system.
Both lightweight and full-featured editors should implement this interface.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseRTFEditor(Protocol):
    """Protocol defining the interface for rich text editors.

    This class defines the minimum functionality that all rich text editors
    must implement, regardless of whether they're lightweight embedded widgets
    or full-featured standalone editors.

    Unlike ABC, Protocol is compatible with PyQt's metaclass system.
    """

    def set_html(self, html: str) -> None:
        """Set the content of the editor as HTML.

        Args:
            html: HTML content to set
        """
        ...

    def get_html(self) -> str:
        """Get the content of the editor as HTML.

        Returns:
            HTML content as string
        """
        ...

    def set_plain_text(self, text: str) -> None:
        """Set the content of the editor as plain text.

        Args:
            text: Plain text content to set
        """
        ...

    def get_plain_text(self) -> str:
        """Get the content of the editor as plain text.

        Returns:
            Plain text content as string
        """
        ...

    def is_modified(self) -> bool:
        """Check if the content has been modified since last save.

        Returns:
            True if modified, False otherwise
        """
        ...

    def set_modified(self, modified: bool = True) -> None:
        """Set the modified state.

        Args:
            modified: True to mark as modified, False otherwise
        """
        ...

    def get_text_edit(self):
        """Get the QTextEdit widget.

        This method allows access to the underlying QTextEdit widget for
        operations that require direct access.

        Returns:
            QTextEdit widget
        """
        ...
