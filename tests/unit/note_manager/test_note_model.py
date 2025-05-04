"""
@file test_note_model.py
@description Unit tests for the Note model in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.models.note
"""

import pytest
from document_manager.note_manager.models.note import Note
from datetime import datetime

GREEK_TEXT = "Καλημέρα"
HEBREW_TEXT = "שלום"


def test_unicode_support():
    note = Note(name=GREEK_TEXT, content=HEBREW_TEXT)
    assert note.name == GREEK_TEXT
    assert note.content == HEBREW_TEXT


def test_serialization_deserialization():
    note = Note(name="Test Note", content="Test Content")
    data = note.to_dict()
    note2 = Note.from_dict(data)
    assert note == note2
    assert note2.name == "Test Note"
    assert note2.content == "Test Content"


def test_validation():
    note = Note(name="Valid Note")
    assert note.validate()
    note_invalid = Note(name="", note_id="not-a-uuid")
    assert not note_invalid.validate() 