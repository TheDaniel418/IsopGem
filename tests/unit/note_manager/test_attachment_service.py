"""
@file test_attachment_service.py
@description Unit tests for AttachmentService covering business logic, validation, error handling, file operations, and Unicode support.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.services.attachment_service, document_manager.note_manager.models.attachment
"""

import pytest
from document_manager.note_manager.services.attachment_service import AttachmentService
from document_manager.note_manager.models.attachment import Attachment

@pytest.fixture
def service():
    return AttachmentService()

def test_create_attachment_valid(service):
    att = service.create_attachment({"filename": "file.txt", "path": "/tmp/file.txt", "note_id": "n1"}, file_content=b"data")
    assert isinstance(att, Attachment)
    assert att.filename == "file.txt"

def test_create_attachment_unicode(service):
    att = service.create_attachment({"filename": "δοκιμή.txt", "path": "/tmp/δοκιμή.txt", "note_id": "n2"}, file_content=b"data")
    assert "δοκιμή" in att.filename

def test_create_attachment_invalid(service):
    with pytest.raises(ValueError):
        service.create_attachment({"filename": "", "path": "", "note_id": "n3"}, file_content=b"")

def test_get_attachment(service):
    att = service.create_attachment({"filename": "getme.txt", "path": "/tmp/getme.txt", "note_id": "n4"}, file_content=b"data")
    fetched = service.get_attachment(att.id)
    assert fetched.id == att.id

def test_update_attachment(service):
    att = service.create_attachment({"filename": "old.txt", "path": "/tmp/old.txt", "note_id": "n5"}, file_content=b"data")
    service.update_attachment(att.id, {"filename": "new.txt"})
    updated = service.get_attachment(att.id)
    assert updated.filename == "new.txt"

def test_delete_attachment(service):
    att = service.create_attachment({"filename": "del.txt", "path": "/tmp/del.txt", "note_id": "n6"}, file_content=b"data")
    service.delete_attachment(att.id)
    assert service.get_attachment(att.id) is None

def test_list_attachments(service):
    service.create_attachment({"filename": "a.txt", "path": "/tmp/a.txt", "note_id": "n7"}, file_content=b"data")
    service.create_attachment({"filename": "b.txt", "path": "/tmp/b.txt", "note_id": "n7"}, file_content=b"data")
    atts = service.list_attachments(note_id="n7")
    assert len(atts) >= 2

def test_save_and_check_file(service):
    att = service.create_attachment({"filename": "save.txt", "path": "/tmp/save.txt", "note_id": "n8"}, file_content=b"data")
    service.save_file(att.id, b"newdata")
    assert service.file_exists(att.id) 