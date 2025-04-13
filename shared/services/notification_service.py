"""
Purpose: Provides notification services for the application.

This file is part of the shared services and provides a centralized way
to display notifications to the user.

Key components:
- NotificationService: Service for showing notifications

Dependencies:
- PyQt6: For UI components
- loguru: For logging
"""

from enum import Enum, auto
from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel, QWidget


class NotificationType(Enum):
    """Types of notifications."""
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()


class NotificationService:
    """Service for showing notifications to the user."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the notification service."""
        if self._initialized:
            return
            
        self._initialized = True
        self._parent = None
        self._notification_label = None
        self._timer = None
        
        logger.debug("NotificationService initialized")
    
    def set_parent(self, parent: QWidget) -> None:
        """Set the parent widget for notifications.
        
        Args:
            parent: Parent widget
        """
        self._parent = parent
        
    def _get_color_for_type(self, notification_type: NotificationType) -> str:
        """Get the color for a notification type.
        
        Args:
            notification_type: Type of notification
            
        Returns:
            Color as CSS string
        """
        if notification_type == NotificationType.INFO:
            return "rgba(0, 120, 215, 0.9)"  # Blue
        elif notification_type == NotificationType.SUCCESS:
            return "rgba(16, 124, 16, 0.9)"  # Green
        elif notification_type == NotificationType.WARNING:
            return "rgba(240, 163, 10, 0.9)"  # Orange
        elif notification_type == NotificationType.ERROR:
            return "rgba(232, 17, 35, 0.9)"  # Red
        else:
            return "rgba(0, 0, 0, 0.9)"  # Black
    
    def show_notification(self, message: str, notification_type: NotificationType, 
                         duration: int = 3000) -> None:
        """Show a notification.
        
        Args:
            message: Notification message
            notification_type: Type of notification
            duration: Duration in milliseconds
        """
        if not self._parent:
            logger.warning("No parent set for notification service")
            return
            
        # Ensure duration is an integer
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            logger.warning(f"Invalid duration value: {duration}, using default")
            duration = 3000
            
        # If there's already a notification, remove it
        self._hide_notification()
        
        # Create notification label
        self._notification_label = QLabel(message, self._parent)
        self._notification_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._notification_label.setWordWrap(True)
        self._notification_label.setStyleSheet(f"""
            background-color: {self._get_color_for_type(notification_type)};
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        """)
        
        # Position at bottom of parent - make sure to use integer values
        width = int(self._parent.width() * 0.8)
        height = 50
        self._notification_label.resize(width, height)
        self._notification_label.move(
            int(self._parent.width() * 0.1),
            self._parent.height() - 70
        )
        
        # Show notification
        self._notification_label.show()
        
        # Create timer to hide notification
        self._timer = QTimer(self._parent)
        self._timer.timeout.connect(self._hide_notification)
        self._timer.setSingleShot(True)
        self._timer.start(duration)
        
        # Log notification
        logger.info(f"Notification ({notification_type.name}): {message}")
    
    def _hide_notification(self) -> None:
        """Hide the current notification."""
        if self._notification_label:
            self._notification_label.deleteLater()
            self._notification_label = None
        
        if self._timer:
            self._timer.stop()
            self._timer = None
    
    def show_info(self, message: str, duration: int = 3000) -> None:
        """Show an info notification.
        
        Args:
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(message, NotificationType.INFO, duration)
    
    def show_success(self, message: str, duration: int = 3000) -> None:
        """Show a success notification.
        
        Args:
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(message, NotificationType.SUCCESS, duration)
    
    def show_warning(self, message: str, duration: int = 3000) -> None:
        """Show a warning notification.
        
        Args:
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(message, NotificationType.WARNING, duration)
    
    def show_error(self, message: str, duration: int = 5000) -> None:
        """Show an error notification.
        
        Args:
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(message, NotificationType.ERROR, duration) 