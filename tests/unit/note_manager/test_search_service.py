"""
@file test_search_service.py
@description Unit tests for SearchService covering business logic, query processing, Unicode support, tag filtering, and combined search.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.services.search_service, document_manager.note_manager.models.note, document_manager.note_manager.models.tag
"""

import pytest
from document_manager.note_manager.services.search_service import SearchService
from document_manager.note_manager.models.note import Note
from document_manager.note_manager.models.tag import Tag

@pytest.fixture
def service():
    return SearchService()

def test_create_index_and_index_document(service):
    service.create_index()
    note = Note(name="Searchable Note", content="Searchable content", tags=["tag1"])
    service.index_document(note)
    results = service.search("Searchable")
    assert any(r["id"] == note.id for r in results)

def test_index_tag_and_search(service):
    tag = Tag(name="SpecialTag")
    service.index_tag(tag)
    results = service.search("SpecialTag")
    assert any(r["id"] == tag.id for r in results)

def test_unicode_search(service):
    note = Note(name="Unicode Note", content="Γειά σου Κόσμε!", tags=["unicode"])
    service.index_document(note)
    results = service.search("Κόσμε")
    assert any("Κόσμε" in r["content"] for r in results)

def test_tag_filtering(service):
    note1 = Note(name="Alpha Note", content="Alpha", tags=["t1"])
    note2 = Note(name="Beta Note", content="Beta", tags=["t2"])
    service.index_document(note1)
    service.index_document(note2)
    results = service.search("", tags=["t2"])
    assert all("t2" in r["tags"] for r in results)

def test_combined_search(service):
    note = Note(name="Combo Note", content="Combo", tags=["combo"])
    service.index_document(note)
    results = service.combined_search("Combo", tags=["combo"])
    assert any(r["id"] == note.id for r in results)

def test_sorting(service):
    note1 = Note(name="A Note", content="A", tags=[])
    note2 = Note(name="B Note", content="B", tags=[])
    service.index_document(note1)
    service.index_document(note2)
    results = service.search("", sort_by="content")
    assert results[0]["content"] <= results[1]["content"] 