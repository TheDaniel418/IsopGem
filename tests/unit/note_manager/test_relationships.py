"""
@file test_relationships.py
@description Unit tests for model relationships and cascading operations in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.models.note, document_manager.note_manager.models.tag, document_manager.note_manager.models.attachment, document_manager.note_manager.models.relationships
"""

import pytest
from document_manager.note_manager.models.note import Note
from document_manager.note_manager.models.tag import Tag
from document_manager.note_manager.models.attachment import Attachment
from document_manager.note_manager.models.relationships import (
    link_note_tag, unlink_note_tag, add_attachment_to_note, remove_attachment_from_note, delete_note_cascade
)

def test_link_unlink_note_tag():
    note = Note(name="Test Note")
    tag = Tag(name="Test Tag")
    link_note_tag(note, tag)
    assert tag.id in note.tags
    assert note.id in tag.notes
    unlink_note_tag(note, tag)
    assert tag.id not in note.tags
    assert note.id not in tag.notes

def test_add_remove_attachment():
    note = Note(name="Test Note")
    attachment = Attachment(filename="file.txt", path="data/attachments/file.txt")
    add_attachment_to_note(note, attachment)
    assert attachment.id in note.attachments
    assert attachment.note_id == note.id
    remove_attachment_from_note(note, attachment)
    assert attachment.id not in note.attachments
    assert attachment.note_id is None

def test_delete_note_cascade():
    note = Note(name="Test Note")
    att1 = Attachment(filename="a.txt", path="data/attachments/a.txt")
    att2 = Attachment(filename="b.txt", path="data/attachments/b.txt")
    add_attachment_to_note(note, att1)
    add_attachment_to_note(note, att2)
    attachments = [att1, att2]
    delete_note_cascade(note, attachments)
    assert len(note.attachments) == 0
    assert att1 not in attachments
    assert att2 not in attachments 