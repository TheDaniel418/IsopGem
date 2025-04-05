"""Window management system for IsopGem.

Implements a robust tab manager, panel/window manager, and auxiliary window manager
following principles of modular development. All panels are non-modal,
free-floating, resizable, focusable, themeable, with min/max/close controls.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Callable, cast

from PyQt6.QtCore import Qt, QPoint, QSize, QSettings, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction, QCloseEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QDockWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QToolBar, QLabel, QSizePolicy,
    QFrame, QMenu, QApplication
)

from loguru import logger
from shared.utils.config import get_config


class WindowType(Enum):
    """Type of window in the application."""
    MAIN = auto()           # Main application window
    PANEL = auto()          # Dockable panel
    AUXILIARY = auto()      # Secondary window
    DIALOG = auto()         # Dialog window (potentially modal)
    TOOL = auto()           # Tool window


class TabManager(QTabWidget):
    """Tab manager widget that handles permanent tabs.
    
    Tabs are not closeable and serve as containers for launching
    panels and windows rather than for content directly.
    """
    
    tab_button_clicked = pyqtSignal(str, str)  # (tab_id, button_id)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the tab manager.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Configure tab appearance
        self.setTabsClosable(False)  # Tabs are permanent
        self.setMovable(False)       # Tabs order is fixed
        self.setDocumentMode(True)   # Cleaner look
        
        # Map of tab IDs to indices
        self._tab_map: Dict[str, int] = {}
        # Map of tab button IDs to buttons
        self._button_map: Dict[str, Dict[str, QPushButton]] = {}
        
        # Apply theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply theme to the tab widget."""
        config = get_config()
        colors = config.ui.theme_colors
        
        # Set tab bar styling
        self.setStyleSheet(f"""
            QTabBar::tab {{
                background-color: {colors.background};
                color: {colors.text};
                padding: 8px 20px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            
            QTabWidget::pane {{
                border-top: 1px solid #cccccc;
                background-color: {colors.background};
            }}
        """)
    
    def add_tab(self, title: str) -> str:
        """Add a new tab for launching panels and windows.
        
        Args:
            title: Title of the tab
            
        Returns:
            ID of the created tab
        """
        # Create the tab container with a layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a bar for buttons
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 0)
        button_layout.setSpacing(5)
        
        # Add a stretch to push buttons to the left
        button_layout.addStretch()
        
        # Add the content widget to layout
        layout.addWidget(button_bar)
        
        # Add the tab and store its reference
        index = self.addTab(container, title)
        
        # Store the button layout for reference
        tab_id = f"tab_{index}"
        self._tab_map[tab_id] = index
        self._button_map[tab_id] = {}
        
        return tab_id
    
    def add_panel_button(
        self, tab_id: str, text: str, tooltip: str, callback: Callable
    ) -> QPushButton:
        """Add a button to open a panel.
        
        Args:
            tab_id: ID of the tab to add the button to
            text: Button text
            tooltip: Tooltip for the button
            callback: Function to call when the button is clicked
            
        Returns:
            The created button
        """
        if tab_id not in self._tab_map:
            raise ValueError(f"Tab with ID '{tab_id}' not found")
        
        # Get the tab container
        index = self._tab_map[tab_id]
        container = self.widget(index)
        
        # Get the button bar (first child of the container's layout)
        button_bar = container.layout().itemAt(0).widget()
        button_layout = cast(QHBoxLayout, button_bar.layout())
        
        # Create the button
        button = QPushButton(text)
        button.setToolTip(tooltip)
        
        # Connect the button click to the callback
        button.clicked.connect(callback)
        
        # Add button to layout before the stretch
        stretch_index = button_layout.count() - 1
        button_layout.insertWidget(stretch_index, button)
        
        # Store the button
        button_id = f"panel_{text.lower().replace(' ', '_')}"
        self._button_map[tab_id][button_id] = button
        
        return button
    
    def add_window_button(
        self, tab_id: str, text: str, tooltip: str, callback: Callable
    ) -> QPushButton:
        """Add a button to open a window.
        
        Args:
            tab_id: ID of the tab to add the button to
            text: Button text
            tooltip: Tooltip for the button
            callback: Function to call when the button is clicked
            
        Returns:
            The created button
        """
        if tab_id not in self._tab_map:
            raise ValueError(f"Tab with ID '{tab_id}' not found")
        
        # Get the tab container
        index = self._tab_map[tab_id]
        container = self.widget(index)
        
        # Get the button bar (first child of the container's layout)
        button_bar = container.layout().itemAt(0).widget()
        button_layout = cast(QHBoxLayout, button_bar.layout())
        
        # Create the button
        button = QPushButton(text)
        button.setToolTip(tooltip)
        
        # Connect the button click to the callback
        button.clicked.connect(callback)
        
        # Add button to layout before the stretch
        stretch_index = button_layout.count() - 1
        button_layout.insertWidget(stretch_index, button)
        
        # Store the button
        button_id = f"window_{text.lower().replace(' ', '_')}"
        self._button_map[tab_id][button_id] = button
        
        return button
    
    def get_tab_id(self, index: int) -> Optional[str]:
        """Get the tab ID for the given index.
        
        Args:
            index: Tab index
            
        Returns:
            Tab ID or None if not found
        """
        for tab_id, tab_index in self._tab_map.items():
            if tab_index == index:
                return tab_id
        
        # If no match found, create a new tab ID
        tab_id = f"tab_{index}"
        self._tab_map[tab_id] = index
        self._button_map[tab_id] = {}
        return tab_id
    
    def get_tab_index(self, tab_id: str) -> Optional[int]:
        """Get the tab index for the given ID.
        
        Args:
            tab_id: Tab ID
            
        Returns:
            Tab index or None if not found
        """
        return self._tab_map.get(tab_id)
    
    def get_button(self, tab_id: str, button_id: str) -> Optional[QPushButton]:
        """Get a tab button.
        
        Args:
            tab_id: ID of the tab
            button_id: ID of the button
            
        Returns:
            Button or None if not found
        """
        if tab_id in self._button_map and button_id in self._button_map[tab_id]:
            return self._button_map[tab_id][button_id]
        return None
    
    def indexOf(self, widget: QWidget) -> int:
        """Get the index of the given widget.
        
        This is a wrapper around the QTabWidget.indexOf method.
        
        Args:
            widget: Widget to find the index for
            
        Returns:
            Index of the widget in the tab widget, or -1 if not found
        """
        return super().indexOf(widget)


class PanelWidget(QDockWidget):
    """Panel widget that can be docked, floated, or tabified.
    
    Panels are non-modal, free-floating, resizable windows that can
    be docked to the main window or other panels.
    """
    
    def __init__(
        self, title: str, parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Widget
    ) -> None:
        """Initialize the panel widget.
        
        Args:
            title: Title of the panel
            parent: Parent widget
            flags: Window flags
        """
        super().__init__(title, parent, flags)
        
        # Configure panel appearance and behavior
        self.setAllowedAreas(
            Qt.DockWidgetArea.AllDockWidgetAreas
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
        # Create a content widget
        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self.setWidget(self._content)
        
        # Apply theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply theme to the panel."""
        config = get_config()
        colors = config.ui.theme_colors
        
        # Set panel styling
        self.setStyleSheet(f"""
            QDockWidget {{
                border: 1px solid #cccccc;
                background-color: {colors.background};
            }}
            
            QDockWidget::title {{
                text-align: center;
                background-color: {colors.primary};
                color: white;
                padding: 6px;
            }}
            
            QDockWidget::close-button, QDockWidget::float-button {{
                background-color: {colors.background};
                border: none;
                padding: 0px;
            }}
        """)
    
    def set_content(self, widget: QWidget) -> None:
        """Set the content widget of the panel.
        
        Args:
            widget: Widget to use as the panel content
        """
        # Clear existing content
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add the new content
        self._layout.addWidget(widget)


class AuxiliaryWindow(QMainWindow):
    """Auxiliary window for secondary content.
    
    Auxiliary windows are non-modal, separate windows that can be
    created from panel interactions.
    """
    
    def __init__(
        self, title: str, parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window
    ) -> None:
        """Initialize the auxiliary window.
        
        Args:
            title: Title of the window
            parent: Parent widget
            flags: Window flags
        """
        super().__init__(parent, flags)
        
        # Configure window appearance and behavior
        self.setWindowTitle(title)
        self.resize(640, 480)
        
        # Create central widget and layout
        self._central = QWidget()
        self._layout = QVBoxLayout(self._central)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self.setCentralWidget(self._central)
        
        # Apply theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply theme to the window."""
        config = get_config()
        colors = config.ui.theme_colors
        
        # Set window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors.background};
                color: {colors.text};
            }}
            
            QToolBar {{
                background-color: {colors.background};
                border-bottom: 1px solid #cccccc;
                spacing: 4px;
                padding: 2px;
            }}
        """)
    
    def set_content(self, widget: QWidget) -> None:
        """Set the content widget of the window.
        
        Args:
            widget: Widget to use as the window content
        """
        # Clear existing content
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add the new content
        self._layout.addWidget(widget)


class WindowManager(QObject):
    """Manager for application windows, panels, and tabs.
    
    Handles creation, tracking, saving, and restoring window states.
    """
    
    def __init__(self, main_window: QMainWindow) -> None:
        """Initialize the window manager.
        
        Args:
            main_window: Main application window
        """
        super().__init__()
        
        self._main_window = main_window
        
        # Track all windows by ID
        self._panels: Dict[str, PanelWidget] = {}
        self._auxiliary_windows: Dict[str, AuxiliaryWindow] = {}
        
        # Tab manager
        self._tab_manager: Optional[TabManager] = None
        
        # Connect to tab button signals
        self._tab_handlers: Dict[Tuple[str, str], Callable] = {}
    
    def set_tab_manager(self, tab_manager: TabManager) -> None:
        """Set the tab manager.
        
        Args:
            tab_manager: Tab manager instance
        """
        self._tab_manager = tab_manager
        self._tab_manager.tab_button_clicked.connect(self._handle_tab_button_click)
    
    def _handle_tab_button_click(self, tab_id: str, button_id: str) -> None:
        """Handle a tab button click.
        
        Args:
            tab_id: ID of the tab
            button_id: ID of the button
        """
        handler_key = (tab_id, button_id)
        if handler_key in self._tab_handlers:
            self._tab_handlers[handler_key]()
    
    def register_tab_button_handler(
        self, tab_id: str, button_id: str, handler: Callable
    ) -> None:
        """Register a handler for a tab button click.
        
        Args:
            tab_id: ID of the tab
            button_id: ID of the button
            handler: Function to call when the button is clicked
        """
        self._tab_handlers[(tab_id, button_id)] = handler
    
    def create_panel(
        self, panel_id: str, title: str, area: Qt.DockWidgetArea = Qt.DockWidgetArea.RightDockWidgetArea
    ) -> PanelWidget:
        """Create a new panel.
        
        Args:
            panel_id: Unique identifier for the panel
            title: Title of the panel
            area: Dock area for the panel
            
        Returns:
            The created panel
        """
        if panel_id in self._panels:
            # If the panel already exists, return it and bring it to front
            panel = self._panels[panel_id]
            panel.show()
            panel.raise_()
            return panel
        
        # Create a new panel
        panel = PanelWidget(title, self._main_window)
        
        # Add it to the main window
        self._main_window.addDockWidget(area, panel)
        
        # Store it
        self._panels[panel_id] = panel
        
        return panel
    
    def create_auxiliary_window(
        self, window_id: str, title: str
    ) -> AuxiliaryWindow:
        """Create a new auxiliary window.
        
        Args:
            window_id: Unique identifier for the window
            title: Title of the window
            
        Returns:
            The created window
        """
        if window_id in self._auxiliary_windows:
            # If the window already exists, return it and bring it to front
            window = self._auxiliary_windows[window_id]
            window.show()
            window.raise_()
            return window
        
        # Create a new window
        window = AuxiliaryWindow(title, self._main_window)
        
        # Store it
        self._auxiliary_windows[window_id] = window
        
        return window
    
    def get_panel(self, panel_id: str) -> Optional[PanelWidget]:
        """Get a panel by ID.
        
        Args:
            panel_id: ID of the panel
            
        Returns:
            Panel or None if not found
        """
        return self._panels.get(panel_id)
    
    def get_auxiliary_window(self, window_id: str) -> Optional[AuxiliaryWindow]:
        """Get an auxiliary window by ID.
        
        Args:
            window_id: ID of the window
            
        Returns:
            Window or None if not found
        """
        return self._auxiliary_windows.get(window_id)
    
    def save_window_state(self) -> None:
        """Save the state of all windows."""
        settings = QSettings("IsopGem", "WindowState")
        
        # Save main window geometry and state
        settings.setValue("mainWindow/geometry", self._main_window.saveGeometry())
        settings.setValue("mainWindow/state", self._main_window.saveState())
        
        # Save panel states
        for panel_id, panel in self._panels.items():
            settings.setValue(f"panels/{panel_id}/geometry", panel.saveGeometry())
            settings.setValue(f"panels/{panel_id}/visible", panel.isVisible())
            settings.setValue(f"panels/{panel_id}/floating", panel.isFloating())
        
        # Save auxiliary window states
        for window_id, window in self._auxiliary_windows.items():
            settings.setValue(f"auxiliaryWindows/{window_id}/geometry", window.saveGeometry())
            settings.setValue(f"auxiliaryWindows/{window_id}/visible", window.isVisible())
    
    def restore_window_state(self) -> None:
        """Restore the state of all windows."""
        settings = QSettings("IsopGem", "WindowState")
        
        # Restore main window geometry and state
        geometry = settings.value("mainWindow/geometry")
        state = settings.value("mainWindow/state")
        
        if geometry:
            self._main_window.restoreGeometry(geometry)
        if state:
            self._main_window.restoreState(state)
        
        # Restore panel states
        for panel_id, panel in self._panels.items():
            geometry = settings.value(f"panels/{panel_id}/geometry")
            visible = settings.value(f"panels/{panel_id}/visible", True, type=bool)
            floating = settings.value(f"panels/{panel_id}/floating", False, type=bool)
            
            if geometry:
                panel.restoreGeometry(geometry)
            
            panel.setVisible(visible)
            panel.setFloating(floating)
        
        # Restore auxiliary window states
        for window_id, window in self._auxiliary_windows.items():
            geometry = settings.value(f"auxiliaryWindows/{window_id}/geometry")
            visible = settings.value(f"auxiliaryWindows/{window_id}/visible", False, type=bool)
            
            if geometry:
                window.restoreGeometry(geometry)
            
            window.setVisible(visible)
    
    def close_all_windows(self) -> None:
        """Close all panels and auxiliary windows."""
        # Close panels
        for panel in list(self._panels.values()):
            panel.close()
        
        # Close auxiliary windows
        for window in list(self._auxiliary_windows.values()):
            window.close()
        
        # Clear our maps
        self._panels.clear()
        self._auxiliary_windows.clear()
    
    def open_panel(self, panel_id: str, widget: QWidget, title: str) -> PanelWidget:
        """Open or create a panel and set its content.
        
        Args:
            panel_id: Unique identifier for the panel
            widget: Widget to use as the panel content
            title: Title of the panel
            
        Returns:
            The panel widget
        """
        # Get or create the panel
        panel = self.create_panel(panel_id, title)
        
        # Set its content
        panel.set_content(widget)
        
        # Show and raise the panel
        panel.show()
        panel.raise_()
        
        return panel
    
    def open_window(self, window_id: str, widget: QWidget, title: str) -> AuxiliaryWindow:
        """Open or create a window and set its content.
        
        Args:
            window_id: Unique identifier for the window
            widget: Widget to use as the window content
            title: Title of the window
            
        Returns:
            The window widget
        """
        # Get or create the window
        window = self.create_auxiliary_window(window_id, title)
        
        # Set its content
        window.set_content(widget)
        
        # Show and raise the window
        window.show()
        window.raise_()
        
        return window 