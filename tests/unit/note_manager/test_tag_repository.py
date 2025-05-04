"""
@file test_tag_repository.py
@description Unit tests for the TagRepository in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.repositories.tag_repository, document_manager.note_manager.models.tag
"""

import pytest
from document_manager.note_manager.repositories.tag_repository import TagRepository
from document_manager.note_manager.models.tag import Tag

GREEK_TEXT = "Ετικέτα"
HEBREW_TEXT = "תגית"

def test_crud_operations():
    repo = TagRepository()
    tag = Tag(name="Test Tag", color="#ff0000")
    repo.add(tag)
    assert repo.get(tag.id) == tag
    tag.color = "#00ff00"
    repo.update(tag.id, tag)
    assert repo.get(tag.id).color == "#00ff00"
    repo.remove(tag.id)
    assert repo.get(tag.id) is None

def test_relationship_management():
    repo = TagRepository()
    tag = Tag(name="Tag1")
    repo.add(tag)
    note_id = "note-uuid"
    repo.add_note_to_tag(tag.id, note_id)
    assert note_id in repo.get(tag.id).notes
    repo.remove_note_from_tag(tag.id, note_id)
    assert note_id not in repo.get(tag.id).notes

def test_unicode_support():
    repo = TagRepository()
    tag = Tag(name=GREEK_TEXT)
    repo.add(tag)
    fetched = repo.get(tag.id)
    assert fetched.name == GREEK_TEXT
    tag2 = Tag(name=HEBREW_TEXT)
    repo.add(tag2)
    fetched2 = repo.get(tag2.id)
    assert fetched2.name == HEBREW_TEXT 