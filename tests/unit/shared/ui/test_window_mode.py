"""Test to verify that all windows are free-floating.

This test verifies that our implementation uses only AuxiliaryWindow 
instances (free-floating windows) and not PanelWidget instances (dockable panels).
"""

import pytest
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMainWindow

from shared.ui.window_management import WindowManager, AuxiliaryWindow, PanelWidget


class TestWindowMode:
    """Tests to verify window management is using only free-floating windows."""
    
    @pytest.fixture
    def window_manager(self, qtbot):
        """Create a window manager fixture for testing."""
        # Create main window for testing
        main_window = QMainWindow()
        main_window.setWindowTitle("Window Mode Test")
        main_window.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create window manager
        window_manager = WindowManager(main_window)
        
        # Track window for cleanup
        qtbot.addWidget(main_window)
        main_window.show()
        
        return window_manager
    
    def create_content_widget(self):
        """Create a simple content widget for testing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QPushButton("Test Button"))
        return widget
    
    def test_open_window_creates_auxiliary_window(self, window_manager, qtbot):
        """Test that open_window creates an AuxiliaryWindow and not a PanelWidget."""
        # Open a window
        window = window_manager.open_window(
            "test_window",
            self.create_content_widget(),
            "Test Window"
        )
        
        # Verify it's an AuxiliaryWindow
        assert isinstance(window, AuxiliaryWindow)
        assert "test_window" in window_manager._auxiliary_windows
        assert len(window_manager._panels) == 0
        
        # Clean up
        window.close()
    
    def test_no_panels_used(self, window_manager):
        """Test that no panels are used in our implementation."""
        # Open multiple windows
        for i in range(3):
            window_manager.open_window(
                f"test_window_{i}",
                self.create_content_widget(),
                f"Test Window {i}"
            )
        
        # Verify no panels are created
        assert len(window_manager._panels) == 0
        assert len(window_manager._auxiliary_windows) == 3
        
        # Clean up
        window_manager.close_all_windows()
    
    def test_create_panel_not_used(self, window_manager):
        """Verify that create_panel method is not used in our implementation."""
        # This is a negative test - we shouldn't be using create_panel at all
        # But we'll test that it works as expected if called directly
        
        panel = window_manager.create_panel(
            "test_panel", 
            "Test Panel"
        )
        
        # Verify it's a PanelWidget
        assert isinstance(panel, PanelWidget)
        
        # But our window count should still be 0
        assert len(window_manager._auxiliary_windows) == 0
        
        # And we should have one panel
        assert len(window_manager._panels) == 1
        
        # Clean up
        panel.close() 