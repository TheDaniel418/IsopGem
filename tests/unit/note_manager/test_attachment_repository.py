"""
@file test_attachment_repository.py
@description Unit tests for the AttachmentRepository in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, os, document_manager.note_manager.repositories.attachment_repository, document_manager.note_manager.models.attachment
"""

import pytest
import os
from document_manager.note_manager.repositories.attachment_repository import AttachmentRepository
from document_manager.note_manager.models.attachment import Attachment
from document_manager.note_manager.utils.constants import DEFAULT_ATTACHMENT_STORAGE

GREEK_FILENAME = "σημείωση.txt"
HEBREW_FILENAME = "הערה.txt"


def test_crud_operations(tmp_path):
    repo = AttachmentRepository()
    att = Attachment(filename="file.txt", path=os.path.join(DEFAULT_ATTACHMENT_STORAGE, "file.txt"))
    content = b"test content"
    repo.add(att, file_content=content)
    assert repo.get(att.id) == att
    assert repo.file_exists(att.id)
    att.filename = "file2.txt"
    repo.update(att.id, att)
    assert repo.get(att.id).filename == "file2.txt"
    repo.remove(att.id)
    assert repo.get(att.id) is None
    assert not repo.file_exists(att.id)


def test_unicode_support(tmp_path):
    repo = AttachmentRepository()
    att = Attachment(filename=GREEK_FILENAME, path=os.path.join(DEFAULT_ATTACHMENT_STORAGE, GREEK_FILENAME))
    repo.add(att, file_content=b"abc")
    assert repo.get(att.id).filename == GREEK_FILENAME
    att2 = Attachment(filename=HEBREW_FILENAME, path=os.path.join(DEFAULT_ATTACHMENT_STORAGE, HEBREW_FILENAME))
    repo.add(att2, file_content=b"def")
    assert repo.get(att2.id).filename == HEBREW_FILENAME
    repo.remove(att.id)
    repo.remove(att2.id) 