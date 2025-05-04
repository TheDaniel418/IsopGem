"""
@file test_attachment_model.py
@description Unit tests for the Attachment model in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.models.attachment
"""

import pytest
from document_manager.note_manager.models.attachment import Attachment
from datetime import datetime

GREEK_FILENAME = "σημείωση.txt"
HEBREW_FILENAME = "הערה.txt"


def test_unicode_support():
    attachment = Attachment(filename=GREEK_FILENAME, path="data/attachments/σημείωση.txt")
    assert attachment.filename == GREEK_FILENAME
    attachment2 = Attachment(filename=HEBREW_FILENAME, path="data/attachments/הערה.txt")
    assert attachment2.filename == HEBREW_FILENAME


def test_serialization_deserialization():
    attachment = Attachment(filename="file.txt", path="data/attachments/file.txt")
    data = attachment.to_dict()
    attachment2 = Attachment.from_dict(data)
    assert attachment == attachment2
    assert attachment2.filename == "file.txt"
    assert attachment2.path == "data/attachments/file.txt"


def test_validation():
    attachment = Attachment(filename="file.txt", path="data/attachments/file.txt")
    assert attachment.validate()
    attachment_invalid = Attachment(filename="", path="", attachment_id="not-a-uuid")
    assert not attachment_invalid.validate() 