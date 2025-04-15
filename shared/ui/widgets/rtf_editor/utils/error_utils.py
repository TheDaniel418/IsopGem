"""
Error handling utilities for the RTF editor.

This module provides a consistent approach to error handling across all RTF editor components.
"""

from PyQt6.QtWidgets import QMessageBox

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)


def handle_error(
    parent, error_message, exception=None, show_dialog=True, log_level="error"
):
    """
    Centralized error handling for the RTF editor.

    This function provides a consistent way to handle errors across all components:
    1. Logs the error with appropriate level and context
    2. Optionally shows a dialog to the user
    3. Emits an error signal if the parent has one

    Args:
        parent: Parent widget or object (should have error_occurred signal if available)
        error_message (str): User-friendly error message
        exception (Exception, optional): Exception object if available
        show_dialog (bool): Whether to show a dialog to the user
        log_level (str): Logging level to use ('error', 'warning', 'info', etc.)

    Returns:
        bool: Always returns False to make it easy to use in return statements
    """
    # Log the error with appropriate level
    log_func = getattr(logger, log_level, logger.error)

    if exception:
        log_func(f"{error_message}: {str(exception)}", exc_info=True)
    else:
        log_func(error_message)

    # Show dialog if requested
    if show_dialog and parent:
        QMessageBox.critical(parent, "Error", error_message)

    # Emit signal if parent has one
    if hasattr(parent, "error_occurred") and callable(
        getattr(parent, "error_occurred", None)
    ):
        parent.error_occurred.emit(error_message)

    # Always return False to make it easy to use in return statements
    return False


def handle_warning(parent, warning_message, show_dialog=True):
    """
    Centralized warning handling for the RTF editor.

    Similar to handle_error but for warnings.

    Args:
        parent: Parent widget or object
        warning_message (str): User-friendly warning message
        show_dialog (bool): Whether to show a dialog to the user

    Returns:
        bool: Always returns True to make it easy to use in conditional statements
    """
    # Log the warning
    logger.warning(warning_message)

    # Show dialog if requested
    if show_dialog and parent:
        QMessageBox.warning(parent, "Warning", warning_message)

    # Emit signal if parent has one
    if hasattr(parent, "status_updated") and callable(
        getattr(parent, "status_updated", None)
    ):
        parent.status_updated.emit(warning_message)

    # Return True to allow execution to continue
    return True
