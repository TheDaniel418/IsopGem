"""
@file test_note_repository.py
@description Unit tests for the NoteRepository in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.repositories.note_repository, document_manager.note_manager.models.note
"""

import pytest
from document_manager.note_manager.repositories.note_repository import NoteRepository
from document_manager.note_manager.models.note import Note

GREEK_TEXT = "Καλημέρα"
HEBREW_TEXT = "שלום"

def test_crud_operations():
    repo = NoteRepository()
    note = Note(name="Test Note", content="Test Content")
    repo.add(note)
    assert repo.get(note.id) == note
    note.content = "Updated Content"
    repo.update(note.id, note)
    assert repo.get(note.id).content == "Updated Content"
    repo.remove(note.id)
    assert repo.get(note.id) is None

def test_relationship_management():
    repo = NoteRepository()
    note = Note(name="Note1")
    repo.add(note)
    tag_id = "tag-uuid"
    repo.add_tag_to_note(note.id, tag_id)
    assert tag_id in repo.get(note.id).tags
    repo.remove_tag_from_note(note.id, tag_id)
    assert tag_id not in repo.get(note.id).tags

def test_unicode_support():
    repo = NoteRepository()
    note = Note(name=GREEK_TEXT, content=HEBREW_TEXT)
    repo.add(note)
    fetched = repo.get(note.id)
    assert fetched.name == GREEK_TEXT
    assert fetched.content == HEBREW_TEXT 