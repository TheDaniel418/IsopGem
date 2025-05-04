"""
@file test_tag_service.py
@description Unit tests for TagService covering business logic, validation, error handling, analytics, suggestions, merging, and Unicode support.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.services.tag_service, document_manager.note_manager.models.tag
"""

import pytest
from document_manager.note_manager.services.tag_service import TagService
from document_manager.note_manager.models.tag import Tag

@pytest.fixture
def service():
    return TagService()

def test_create_tag_valid(service):
    tag = service.create_tag({"name": "Important", "color": "#ff0000"})
    assert isinstance(tag, Tag)
    assert tag.name == "Important"

def test_create_tag_unicode(service):
    tag = service.create_tag({"name": "Σημαντικό", "color": "#00ff00"})
    assert "Σημαντικό" in tag.name

def test_create_tag_invalid(service):
    with pytest.raises(ValueError):
        service.create_tag({"name": "", "color": "#000000"})

def test_get_tag(service):
    tag = service.create_tag({"name": "FindMe", "color": "#123456"})
    fetched = service.get_tag(tag.id)
    assert fetched.id == tag.id

def test_update_tag(service):
    tag = service.create_tag({"name": "Old", "color": "#111111"})
    service.update_tag(tag.id, {"name": "New"})
    updated = service.get_tag(tag.id)
    assert updated.name == "New"

def test_delete_tag(service):
    tag = service.create_tag({"name": "DeleteMe", "color": "#222222"})
    service.delete_tag(tag.id)
    assert service.get_tag(tag.id) is None

def test_list_tags(service):
    service.create_tag({"name": "A", "color": "#333333"})
    service.create_tag({"name": "B", "color": "#444444"})
    tags = service.list_tags()
    assert len(tags) >= 2

def test_merge_tags(service):
    t1 = service.create_tag({"name": "T1", "color": "#555555", "notes": ["n1"]})
    t2 = service.create_tag({"name": "T2", "color": "#666666", "notes": ["n2"]})
    service.merge_tags(t1.id, t2.id)
    merged = service.get_tag(t1.id)
    assert "n2" in merged.notes
    assert service.get_tag(t2.id) is None

def test_tag_analytics(service):
    service.create_tag({"name": "Analytics", "color": "#777777", "notes": ["n1", "n2"]})
    analytics = service.tag_analytics()
    assert "usage" in analytics and "Analytics" in analytics["usage"]

def test_suggest_tags(service):
    service.create_tag({"name": "Alpha", "color": "#888888"})
    suggestions = service.suggest_tags("Alp")
    assert any("Alpha" == tag.name for tag in suggestions) 