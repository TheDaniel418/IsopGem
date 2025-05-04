"""
@file test_rtf_note_editor.py
@description Unit tests for the RTF Note Editor integration.
@author Daniel
@created 2024-06-15
@lastModified 2024-06-15
@dependencies unittest, PyQt6, document_manager.note_manager.ui.components.rtf_note_editor
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from document_manager.note_manager.ui.components.rtf_note_editor import RTFNoteEditor
from document_manager.note_manager.services.factory import ServiceFactory
from document_manager.note_manager.models.note import Note


class TestRTFNoteEditor(unittest.TestCase):
    """
    @class TestRTFNoteEditor
    @description Unit tests for the RTF Note Editor integration.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        @function setUpClass
        @description Set up the test environment.
        """
        # Create a QApplication instance if one doesn't exist
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """
        @function setUp
        @description Set up the test environment for each test.
        """
        # Create a mock ServiceFactory
        self.services = MagicMock(spec=ServiceFactory)
        
        # Create mock services
        self.note_service = MagicMock()
        self.attachment_service = MagicMock()
        
        # Configure the mock ServiceFactory
        self.services.get_note_service.return_value = self.note_service
        self.services.get_attachment_service.return_value = self.attachment_service
        
        # Create a test note
        self.test_note = Note(
            id="test-note-id",
            title="Test Note",
            content="<html><body><p>Test content</p></body></html>",
            tags=["test"]
        )
        
        # Configure the mock NoteService
        self.note_service.get_note.return_value = self.test_note
        
        # Create the RTF Note Editor
        self.editor = RTFNoteEditor(self.services)
    
    def tearDown(self):
        """
        @function tearDown
        @description Clean up after each test.
        """
        self.editor.cleanup()
        self.editor = None
    
    def test_set_note(self):
        """
        @function test_set_note
        @description Test setting a note in the editor.
        """
        # Set the note
        self.editor.set_note("test-note-id")
        
        # Check that the note service was called
        self.note_service.get_note.assert_called_once_with("test-note-id")
        
        # Check that the note was set
        self.assertEqual(self.editor.current_note_id, "test-note-id")
        self.assertEqual(self.editor.current_note, self.test_note)
    
    def test_save_note(self):
        """
        @function test_save_note
        @description Test saving a note from the editor.
        """
        # Set the note
        self.editor.set_note("test-note-id")
        
        # Save the note
        self.editor.save()
        
        # Check that the note service was called
        self.note_service.update_note.assert_called_with("test-note-id", self.test_note)
    
    def test_auto_save(self):
        """
        @function test_auto_save
        @description Test auto-saving a note.
        """
        # Set the note
        self.editor.set_note("test-note-id")
        
        # Trigger auto-save
        self.editor._auto_save()
        
        # Check that the note service was called
        self.note_service.update_note.assert_called_with("test-note-id", self.test_note)
    
    def test_insert_attachment(self):
        """
        @function test_insert_attachment
        @description Test inserting an attachment into the note.
        """
        # Create a mock attachment
        mock_attachment = MagicMock()
        mock_attachment.id = "test-attachment-id"
        mock_attachment.filename = "test.jpg"
        
        # Configure the mock AttachmentService
        self.attachment_service.get_attachment.return_value = mock_attachment
        self.attachment_service.get_file_path.return_value = "/path/to/test.jpg"
        self.attachment_service.get_mime_type.return_value = "image/jpeg"
        
        # Set the note
        self.editor.set_note("test-note-id")
        
        # Mock the image manager
        self.editor.rtf_editor.image_manager = MagicMock()
        
        # Insert the attachment
        self.editor.insert_attachment("test-attachment-id")
        
        # Check that the attachment service was called
        self.attachment_service.get_attachment.assert_called_once_with("test-attachment-id")
        self.attachment_service.get_file_path.assert_called_once_with("test-attachment-id")
        self.attachment_service.get_mime_type.assert_called_once_with("test-attachment-id")
        
        # Check that the image manager was called
        self.editor.rtf_editor.image_manager.insert_image_at_cursor.assert_called_once()


if __name__ == "__main__":
    unittest.main()
