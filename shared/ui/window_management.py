"""Window management system for IsopGem.

Implements a robust tab manager, panel/window manager, and auxiliary window manager
following principles of modular development. All panels are non-modal,
free-floating, resizable, focusable, themeable, with min/max/close controls.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Callable, cast

from PyQt6.QtCore import Qt, QPoint, QSize, QSettings, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon, QAction, QCloseEvent, QColor, QPainter, QPen, QBrush
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QDockWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QToolBar,
    QLabel,
    QSizePolicy,
    QFrame,
    QMenu,
    QApplication,
    QTabBar,
    QStyleOptionTab,
    QStyle,
)

from loguru import logger
from shared.utils.config import get_config


class ColoredTabBar(QTabBar):
    """Custom tab bar with colored tabs."""
    
    def __init__(self, parent=None):
        """Initialize the tab bar."""
        super().__init__(parent)
        self.tab_colors = {}  # Maps tab indices to colors
        
    def set_tab_color(self, index, color):
        """Set the color for a specific tab.
        
        Args:
            index: Tab index
            color: Color for the tab (hex string)
        """
        self.tab_colors[index] = color
        self.update()
        
    def paintEvent(self, event):
        """Override paint event to add custom tab colors."""
        painter = QPainter(self)
        option = QStyleOptionTab()
        
        for i in range(self.count()):
            self.initStyleOption(option, i)
            
            # Get tab rectangle area
            rect = self.tabRect(i)
            
            if i in self.tab_colors:
                color = self.tab_colors[i]
                
                # Draw differently depending on selected state
                if self.currentIndex() == i:
                    # Selected tab - full color
                    painter.save()
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(QColor(color)))
                    painter.drawRoundedRect(rect, 4, 4)
                    painter.restore()
                    
                    # Draw text in white
                    painter.save()
                    painter.setPen(QPen(QColor("white")))
                    # Center text
                    text_rect = rect.adjusted(8, 4, -8, -4)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(i))
                    painter.restore()
                else:
                    # Unselected tab - lighter version with color bar on top
                    painter.save()
                    # Light background
                    light_color = self._lighten_color(color, 0.85)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(QColor(light_color)))
                    painter.drawRoundedRect(rect, 4, 4)
                    
                    # Color bar on top
                    top_bar_rect = rect.adjusted(0, 0, 0, -rect.height() + 3)
                    painter.setBrush(QBrush(QColor(color)))
                    painter.drawRect(top_bar_rect)
                    painter.restore()
                    
                    # Black text
                    painter.save()
                    painter.setPen(QPen(QColor("black")))
                    # Center text
                    text_rect = rect.adjusted(8, 4, -8, -4)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(i))
                    painter.restore()
            else:
                # Default tab rendering for tabs without color
                self.style().drawControl(QStyle.ControlElement.CE_TabBarTab, option, painter, self)
                
    def _lighten_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Lighten a color by the given factor.
        
        Args:
            hex_color: Hex color code (e.g. #RRGGBB)
            factor: Factor to lighten by (0-1)
            
        Returns:
            Lightened hex color
        """
        # Remove the '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"


class WindowType(Enum):
    """Type of window in the application."""

    MAIN = auto()  # Main application window
    PANEL = auto()  # Dockable panel
    AUXILIARY = auto()  # Secondary window
    DIALOG = auto()  # Dialog window (potentially modal)
    TOOL = auto()  # Tool window


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
        self.setMovable(False)  # Tabs order is fixed
        self.setDocumentMode(True)  # Cleaner look
        
        # Replace the default tab bar with our custom one
        self.colored_tab_bar = ColoredTabBar(self)
        self.setTabBar(self.colored_tab_bar)

        # Map of tab IDs to indices
        self._tab_map: Dict[str, int] = {}
        # Map of tab button IDs to buttons
        self._button_map: Dict[str, Dict[str, QPushButton]] = {}
        
        # Pillar colors map
        self.pillar_colors = {
            "Gematria": "#673AB7",     # Deep purple
            "Geometry": "#009688",     # Teal
            "Document Manager": "#FFC107",  # Amber
            "Astrology": "#1565C0",    # Deep blue
            "TQ": "#43A047"            # Rich green
        }

        # Apply theme
        self._apply_theme()
        
        # Connect signals for tab color updates
        self.currentChanged.connect(self._update_tab_colors)

    def _apply_theme(self) -> None:
        """Apply theme to the tab widget."""
        config = get_config()
        colors = config.ui.theme_colors

        # Apply basic styling for the tab widget and buttons
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border-top: 1px solid #cccccc;
                background-color: {colors.background};
            }}
            
            QPushButton {{
                background-color: {colors.background};
                color: {colors.text};
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: normal;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: #f5f5f5;
                border: 1px solid {colors.primary};
                color: {colors.primary};
            }}
            
            QPushButton:pressed {{
                background-color: #e0e0e0;
                border: 1px solid {colors.primary};
                padding-top: 7px;
                padding-left: 13px;
                padding-bottom: 5px;
                padding-right: 11px;
            }}
            
            QPushButton:focus {{
                border: 2px solid {colors.primary};
                outline: none;
            }}
        """)
        
        # Wait for tabs to be created before applying colors
        QTimer.singleShot(100, self._update_tab_colors)

    def _update_tab_colors(self) -> None:
        """Update tab colors based on pillar names."""
        # Apply colors to each tab
        for i in range(self.count()):
            tab_text = self.tabText(i)
            if tab_text in self.pillar_colors:
                color = self.pillar_colors[tab_text]
                self.colored_tab_bar.set_tab_color(i, color)
                
                # Also apply matching styles to the buttons in this tab
                tab_id = f"tab_{i}"
                if tab_id in self._button_map:
                    container = self.widget(i)
                    if container:
                        # Apply pillar-specific button styles
                        container.setStyleSheet(f"""
                            QPushButton:hover {{
                                border-color: {color};
                                color: {color};
                            }}
                            
                            QPushButton:pressed {{
                                background-color: {self._lighten_color(color, 0.9)};
                            }}
                            
                            QPushButton:focus {{
                                border: 2px solid {color};
                            }}
                        """)

    def _lighten_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Lighten a color by the given factor.
        
        Args:
            hex_color: Hex color code (e.g. #RRGGBB)
            factor: Factor to lighten by (0-1)
            
        Returns:
            Lightened hex color
        """
        # Remove the '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

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

        # Create an ID and set object names for styling
        tab_id = f"tab_{index}"
        container.setObjectName(tab_id)
        button_bar.setObjectName(f"{tab_id}_button_bar")
        
        # Store tab info
        self._tab_map[tab_id] = index
        self._button_map[tab_id] = {}
        
        # Apply color to the tab if it matches a pillar
        if title in self.pillar_colors:
            color = self.pillar_colors[title]
            self.colored_tab_bar.set_tab_color(index, color)
            
            # Apply matching styles to the buttons container
            container.setStyleSheet(f"""
                QPushButton:hover {{
                    border-color: {color};
                    color: {color};
                }}
                
                QPushButton:pressed {{
                    background-color: {self._lighten_color(color, 0.9)};
                }}
                
                QPushButton:focus {{
                    border: 2px solid {color};
                }}
            """)

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
        
        # Create an id and set object name for CSS styling
        button_id = f"panel_{text.lower().replace(' ', '_')}"
        button.setObjectName(f"{tab_id}_{button_id}")

        # Connect the button click to the callback
        button.clicked.connect(callback)

        # Add button to layout before the stretch
        stretch_index = button_layout.count() - 1
        button_layout.insertWidget(stretch_index, button)

        # Store the button
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
        
        # Create an id and set object name for CSS styling
        button_id = f"window_{text.lower().replace(' ', '_')}"
        button.setObjectName(f"{tab_id}_{button_id}")

        # Connect the button click to the callback
        button.clicked.connect(callback)

        # Add button to layout before the stretch
        stretch_index = button_layout.count() - 1
        button_layout.insertWidget(stretch_index, button)

        # Store the button
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
        return int(super().indexOf(widget))


class PanelWidget(QDockWidget):
    """Panel widget that can be docked, floated, or tabified.

    Panels are non-modal, free-floating, resizable windows that can
    be docked to the main window or other panels.
    """

    def __init__(
        self,
        title: str,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Widget,
    ) -> None:
        """Initialize the panel widget.

        Args:
            title: Title of the panel
            parent: Parent widget
            flags: Window flags
        """
        super().__init__(title, parent, flags)

        # Configure panel appearance and behavior
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
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
        self.setStyleSheet(
            f"""
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
        """
        )

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
    """Auxiliary window that can be created and managed by the WindowManager."""

    def __init__(
        self,
        title: str,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        """Initialize the auxiliary window.

        Args:
            title: Window title
            parent: Parent widget
            flags: Window flags
        """
        super().__init__(parent, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Store window ID for lookup during cleanup
        self.window_id = ""

        # Set window properties
        self.setWindowTitle(title)
        self.resize(800, 600)  # Default size

        # Create central widget with layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Apply theming
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply theming to the window."""
        # Add any theming or styling here
        pass

    def set_content(self, widget: QWidget) -> None:
        """Set the content of the window.

        Args:
            widget: Widget to set as content
        """
        # Clear existing layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                # Instead of setParent(None), use the proper removeWidget method
                self.main_layout.removeWidget(item.widget())
                # Then hide the widget
                item.widget().hide()

        # Ensure the widget has a minimum size for visibility
        if widget.minimumSize().width() == 0 and widget.minimumSize().height() == 0:
            widget.setMinimumSize(400, 300)

        # Add the widget to the layout
        self.main_layout.addWidget(widget)

        # Make sure the widget is visible
        widget.setVisible(True)

        # Update the layout
        self.central_widget.setLayout(self.main_layout)
        self.central_widget.update()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event by emitting signal.

        Args:
            event: Close event
        """
        # Let the parent handle cleanup
        super().closeEvent(event)


class WindowManager(QObject):
    """Manager for application windows, panels, and tabs.

    Handles creation, tracking, saving, and restoring window states.
    """

    # Signal emitted when a window is closed (window_id)
    window_closed = pyqtSignal(str)

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
        self,
        panel_id: str,
        title: str,
        area: Qt.DockWidgetArea = Qt.DockWidgetArea.RightDockWidgetArea,
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

    def create_auxiliary_window(self, window_id: str, title: str) -> AuxiliaryWindow:
        """Create a new auxiliary window.

        Args:
            window_id: Unique identifier for the window
            title: Title of the window

        Returns:
            The created window
        """
        if window_id in self._auxiliary_windows:
            # Check if the window is valid before returning it
            window = self._auxiliary_windows[window_id]
            if window.isVisible():
                # If the window already exists, return it and bring it to front
                window.show()
                window.raise_()
                return window
            else:
                # Window reference exists but window might be invalid - remove it
                self._auxiliary_windows.pop(window_id, None)

        # Create a new window
        window = AuxiliaryWindow(title, self._main_window)

        # Store the window ID in the window for reference
        window.window_id = window_id

        # Connect to the destroyed signal to clean up the reference
        window.destroyed.connect(
            lambda obj=None, wid=window_id: self._on_window_destroyed(wid)
        )

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

        # Save panel states - only for valid panels
        for panel_id, panel in list(self._panels.items()):
            # Check if panel is still valid
            if not panel.isVisible() or panel.parent() is None:
                self._panels.pop(panel_id, None)
                continue

            try:
                settings.setValue(f"panels/{panel_id}/geometry", panel.saveGeometry())
                settings.setValue(f"panels/{panel_id}/visible", panel.isVisible())
                settings.setValue(f"panels/{panel_id}/floating", panel.isFloating())
            except RuntimeError:
                # Panel might have been deleted, remove from tracking
                logger.warning(
                    f"Error saving panel {panel_id} state, removing reference"
                )
                self._panels.pop(panel_id, None)

        # Save auxiliary window states - only for valid windows
        for window_id, window in list(self._auxiliary_windows.items()):
            # Check if window is still valid
            if not window.isVisible():
                self._auxiliary_windows.pop(window_id, None)
                continue

            try:
                settings.setValue(
                    f"auxiliaryWindows/{window_id}/geometry", window.saveGeometry()
                )
                settings.setValue(
                    f"auxiliaryWindows/{window_id}/visible", window.isVisible()
                )
            except RuntimeError:
                # Window might have been deleted, remove from tracking
                logger.warning(
                    f"Error saving window {window_id} state, removing reference"
                )
                self._auxiliary_windows.pop(window_id, None)

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
            visible = settings.value(
                f"auxiliaryWindows/{window_id}/visible", False, type=bool
            )

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

    def open_window(
        self, window_id: str, widget: QWidget, title: str, size=None
    ) -> AuxiliaryWindow:
        """Open or create a window and set its content.

        Args:
            window_id: Unique identifier for the window
            widget: Widget to use as the window content
            title: Title of the window
            size: Optional tuple of (width, height) for window size

        Returns:
            The window widget
        """
        # Get or create the window
        window = self.create_auxiliary_window(window_id, title)

        # Set its content
        window.set_content(widget)

        # Set window size if specified
        if size is not None:
            window.resize(size[0], size[1])

        # Show and raise the window
        window.show()
        window.raise_()

        return window

    def _on_window_destroyed(self, window_id: str) -> None:
        """Handle window destruction.

        Args:
            window_id: ID of the destroyed window
        """
        # Log the event
        logger.debug(f"Window {window_id} was destroyed, removing reference")

        # Remove the window from our registry
        if window_id in self._panels:
            del self._panels[window_id]
        elif window_id in self._auxiliary_windows:
            del self._auxiliary_windows[window_id]

        # Emit signal that window was closed
        self.window_closed.emit(window_id)
