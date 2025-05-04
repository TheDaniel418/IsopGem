"""
@file test_attachment_service.py
@description Unit tests for the AttachmentService class.
@author Daniel
@created 2024-06-15
@lastModified 2024-06-15
@dependencies unittest, os, tempfile, shutil, document_manager.note_manager.services.attachment_service, document_manager.note_manager.repositories.attachment_repository
"""

import unittest
import os
import tempfile
import shutil
import uuid
from unittest.mock import MagicMock
from document_manager.note_manager.services.attachment_service import AttachmentService
from document_manager.note_manager.repositories.attachment_repository import AttachmentRepository

class TestAttachmentService(unittest.TestCase):
    """
    @class TestAttachmentService
    @description Unit tests for the AttachmentService class.
    """

    def setUp(self):
        """
        @function setUp
        @description Set up the test environment.
        """
        # Create a temporary directory for attachments
        self.temp_dir = tempfile.mkdtemp()

        # Create a test file
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("Test content")

        # Create a test note ID
        self.note_id = str(uuid.uuid4())

        # Create a mock repository
        self.repo = MagicMock(spec=AttachmentRepository)

        # Set up mock behavior
        self.attachments = {}

        def mock_add(entity, _file_content=None):
            self.attachments[entity.id] = entity
            return None

        def mock_get(id):
            return self.attachments.get(id)

        def mock_update(id, entity):
            if id in self.attachments:
                self.attachments[id] = entity
            return None

        def mock_remove(id):
            if id in self.attachments:
                del self.attachments[id]
            return None

        def mock_list():
            return list(self.attachments.values())

        def mock_find_by_note_id(note_id):
            return [att for att in self.attachments.values() if att.note_id == note_id]

        def mock_file_exists(id):
            return id in self.attachments

        def mock_move_attachment(id, new_note_id):
            if id in self.attachments:
                self.attachments[id].note_id = new_note_id
                return True
            return False

        # Configure mock
        self.repo.add.side_effect = mock_add
        self.repo.get.side_effect = mock_get
        self.repo.update.side_effect = mock_update
        self.repo.remove.side_effect = mock_remove
        self.repo.list.side_effect = mock_list
        self.repo.find_by_note_id.side_effect = mock_find_by_note_id
        self.repo.file_exists.side_effect = mock_file_exists
        self.repo.move_attachment.side_effect = mock_move_attachment
        self.repo.get_file_path.return_value = self.test_file_path

        # Create service with mock repository
        self.service = AttachmentService(self.repo)

    def tearDown(self):
        """
        @function tearDown
        @description Clean up the test environment.
        """
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_create_attachment(self):
        """
        @function test_create_attachment
        @description Test creating an attachment.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Check that the attachment was created
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.filename, "test_file.txt")
        self.assertEqual(attachment.note_id, self.note_id)

        # Check that the file exists
        self.assertTrue(self.service.file_exists(attachment.id))

    def test_get_attachment(self):
        """
        @function test_get_attachment
        @description Test retrieving an attachment.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Get the attachment
        retrieved = self.service.get_attachment(attachment.id)

        # Check that the attachment was retrieved
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, attachment.id)
        self.assertEqual(retrieved.filename, attachment.filename)
        self.assertEqual(retrieved.note_id, attachment.note_id)

    def test_update_attachment(self):
        """
        @function test_update_attachment
        @description Test updating an attachment.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Update the attachment
        self.service.update_attachment(attachment.id, {"filename": "new_name.txt"})

        # Get the updated attachment
        updated = self.service.get_attachment(attachment.id)

        # Check that the attachment was updated
        self.assertEqual(updated.filename, "new_name.txt")

    def test_delete_attachment(self):
        """
        @function test_delete_attachment
        @description Test deleting an attachment.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Delete the attachment
        self.service.delete_attachment(attachment.id)

        # Check that the attachment was deleted
        self.assertIsNone(self.service.get_attachment(attachment.id))
        self.assertFalse(self.service.file_exists(attachment.id))

    def test_list_attachments(self):
        """
        @function test_list_attachments
        @description Test listing attachments.
        """
        # Create multiple attachments
        attachment1 = self.service.create_attachment(
            self.note_id, "test_file1.txt", self.test_file_path
        )
        attachment2 = self.service.create_attachment(
            self.note_id, "test_file2.txt", self.test_file_path
        )

        # List attachments
        attachments = self.service.list_attachments(self.note_id)

        # Check that the attachments were listed
        self.assertEqual(len(attachments), 2)
        self.assertIn(attachment1.id, [a.id for a in attachments])
        self.assertIn(attachment2.id, [a.id for a in attachments])

    def test_unicode_filename(self):
        """
        @function test_unicode_filename
        @description Test creating an attachment with a Unicode filename.
        """
        # Create an attachment with a Unicode filename
        unicode_filename = "测试文件.txt"
        attachment = self.service.create_attachment(
            self.note_id, unicode_filename, self.test_file_path
        )

        # Check that the attachment was created
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.filename, unicode_filename)

        # Check that the file exists
        self.assertTrue(self.service.file_exists(attachment.id))

    def test_add_file_from_path(self):
        """
        @function test_add_file_from_path
        @description Test adding a file from a path.
        """
        # Add a file from a path
        attachment = self.service.add_file_from_path(self.note_id, self.test_file_path)

        # Check that the attachment was created
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.filename, "test_file.txt")
        self.assertEqual(attachment.note_id, self.note_id)

        # Check that the file exists
        self.assertTrue(self.service.file_exists(attachment.id))

    def test_move_attachment(self):
        """
        @function test_move_attachment
        @description Test moving an attachment to a different note.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Create a new note ID
        new_note_id = str(uuid.uuid4())

        # Move the attachment
        success = self.service.move_attachment(attachment.id, new_note_id)

        # Check that the attachment was moved
        self.assertTrue(success)

        # Get the updated attachment
        moved = self.service.get_attachment(attachment.id)

        # Check that the attachment was updated
        self.assertEqual(moved.note_id, new_note_id)

        # Check that the file exists
        self.assertTrue(self.service.file_exists(attachment.id))

    def test_export_attachment(self):
        """
        @function test_export_attachment
        @description Test exporting an attachment.
        """
        # Create an attachment
        attachment = self.service.create_attachment(
            self.note_id, "test_file.txt", self.test_file_path
        )

        # Create an export path
        export_path = os.path.join(self.temp_dir, "exported.txt")

        # Mock the export method
        def mock_export(_id, path):
            # Copy the test file to the export path
            shutil.copy2(self.test_file_path, path)
            return True

        # Configure mock
        self.service.export_attachment = MagicMock(side_effect=mock_export)

        # Export the attachment
        success = self.service.export_attachment(attachment.id, export_path)

        # Check that the attachment was exported
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))

        # Check the content
        with open(export_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")

if __name__ == "__main__":
    unittest.main()
