"""
@file test_tag_model.py
@description Unit tests for the Tag model in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.models.tag
"""

import pytest
from document_manager.note_manager.models.tag import Tag

GREEK_TEXT = "Ετικέτα"
HEBREW_TEXT = "תגית"


def test_unicode_support():
    tag = Tag(name=GREEK_TEXT)
    assert tag.name == GREEK_TEXT
    tag2 = Tag(name=HEBREW_TEXT)
    assert tag2.name == HEBREW_TEXT


def test_serialization_deserialization():
    tag = Tag(name="Test Tag", color="#ff0000")
    data = tag.to_dict()
    tag2 = Tag.from_dict(data)
    assert tag == tag2
    assert tag2.name == "Test Tag"
    assert tag2.color == "#ff0000"


def test_validation():
    tag = Tag(name="Valid Tag")
    assert tag.validate()
    tag_invalid = Tag(name="", tag_id="not-a-uuid")
    assert not tag_invalid.validate() 