"""
@file test_ui_components.py
@description Unit tests for Note Manager UI components: instantiation, event handling, Unicode support, and responsive layout.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, PyQt6, unittest.mock
"""

import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys

# Import UI components
from document_manager.note_manager.ui.components.tag_selector import TagSelector
from document_manager.note_manager.ui.components.files_list_panel import FilesListPanel
from document_manager.note_manager.ui.components.note_editor import NoteEditor
from document_manager.note_manager.services.factory import ServiceFactory

@pytest.fixture(scope="module")
def app():
    """Create QApplication for all UI tests."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.fixture
def mock_services():
    """Mocked ServiceFactory with stubbed services."""
    factory = MagicMock(spec=ServiceFactory)
    # Mock tag service
    tag_service = MagicMock()
    tag_service.list_tags.return_value = [MagicMock(id="1", name="TagA"), MagicMock(id="2", name="ТегБ")]  # Unicode
    factory.get_tag_service.return_value = tag_service
    # Mock note service
    note_service = MagicMock()
    note_service.list_notes.return_value = [MagicMock(id="n1", name="Note1", content="Hello"), MagicMock(id="n2", name="Заметка2", content="Привет")]  # Unicode
    note_service.get_note.side_effect = lambda nid: next((n for n in note_service.list_notes.return_value if n.id == nid), None)
    factory.get_note_service.return_value = note_service
    return factory

def test_tag_selector_instantiation(app, mock_services):
    panel = TagSelector(mock_services)
    assert panel is not None
    assert panel.list_widget.count() == 2  # TagA, ТегБ

def test_files_list_panel_instantiation(app, mock_services):
    panel = FilesListPanel(mock_services)
    assert panel is not None
    assert panel.list_widget.count() == 2  # Note1, Заметка2

def test_note_editor_unicode(app, mock_services):
    panel = NoteEditor(mock_services)
    panel.load_note("n2")
    assert "Привет" in panel.rtf_editor.text_edit.toPlainText()

def test_tag_selector_event_handling(app, mock_services):
    panel = TagSelector(mock_services)
    # Simulate selecting both tags
    panel.list_widget.item(0).setSelected(True)
    panel.list_widget.item(1).setSelected(True)
    selected = [item.text() for item in panel.list_widget.selectedItems()]
    assert "TagA" in selected and "ТегБ" in selected

def test_files_list_panel_context_menu(app, mock_services):
    panel = FilesListPanel(mock_services)
    # Simulate right-click context menu
    pos = panel.list_widget.visualItemRect(panel.list_widget.item(0)).center()
    panel._show_context_menu(pos)
    # No assertion: just ensure no crash

def test_responsive_layout(app, mock_services):
    panel = FilesListPanel(mock_services)
    panel.resize(300, 100)
    assert panel.width() == 300
    panel.resize(800, 600)
    assert panel.height() == 600 