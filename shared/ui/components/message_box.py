"""
Purpose: Provides a standardized message box component.

This file is part of the shared UI components and serves as a utility.
It wraps PyQt6's QMessageBox for consistent usage throughout the application.

Key components:
- MessageBox: Class providing static methods for different types of message boxes

Dependencies:
- PyQt6: For UI components
"""

from PyQt6.QtWidgets import QMessageBox, QWidget


class MessageBox:
    """Wrapper for QMessageBox providing standardized message dialogs."""
    
    @staticmethod
    def information(parent: QWidget, title: str, message: str) -> None:
        """Show an information message box.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
        """
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def warning(parent: QWidget, title: str, message: str) -> None:
        """Show a warning message box.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
        """
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def error(parent: QWidget, title: str, message: str) -> None:
        """Show an error message box.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
        """
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def question(parent: QWidget, title: str, message: str) -> bool:
        """Show a question message box.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        result: QMessageBox.StandardButton = QMessageBox.question(
            parent, 
            title, 
            message, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return result == QMessageBox.StandardButton.Yes
    
    @staticmethod
    def confirmation(parent: QWidget, title: str, message: str) -> bool:
        """Show a confirmation message box.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
            
        Returns:
            True if user confirmed, False otherwise
        """
        result: QMessageBox.StandardButton = QMessageBox.question(
            parent, 
            title, 
            message, 
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        return result == QMessageBox.StandardButton.Ok 