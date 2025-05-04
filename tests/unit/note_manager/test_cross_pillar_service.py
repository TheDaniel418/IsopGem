"""
@file test_cross_pillar_service.py
@description Unit tests for CrossPillarService covering message sending/receiving, event subscription, UUID-based referencing, and data transformation.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.services.cross_pillar_service, document_manager.note_manager.models.note
"""

import pytest
from document_manager.note_manager.services.cross_pillar_service import CrossPillarService
from document_manager.note_manager.models.note import Note

@pytest.fixture
def service():
    return CrossPillarService()

def test_send_and_receive_message(service):
    service.send_message("test", {"msg": "hello"})
    messages = service.receive_messages("test")
    assert any(m["msg"] == "hello" for m in messages)

def test_event_subscription(service):
    received = []
    def callback(msg):
        received.append(msg)
    service.subscribe("events", callback)
    service.send_message("events", {"event": "fired"})
    assert any(m["event"] == "fired" for m in received)

def test_reference_note_by_uuid(service):
    note = Note(name="Ref Note", content="Ref me")
    service.register_note(note)
    ref = service.reference_note_by_uuid(note.id)
    assert ref.id == note.id

def test_transform_data_for_pillar(service):
    data = {"foo": "bar"}
    transformed = service.transform_data_for_pillar(data, "geometry")
    assert transformed["pillar"] == "geometry" 