"""
@file test_backup_export_service.py
@description Unit tests for BackupExportService covering export, import, validation, conflict resolution, progress reporting, and error handling.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.services.backup_export_service, document_manager.note_manager.models.note, document_manager.note_manager.models.tag, document_manager.note_manager.models.attachment
"""

import pytest
from document_manager.note_manager.services.backup_export_service import BackupExportService
from document_manager.note_manager.models.note import Note
from document_manager.note_manager.models.tag import Tag
from document_manager.note_manager.models.attachment import Attachment
import json

@pytest.fixture
def service():
    return BackupExportService()

def test_export_and_import_all(service):
    # Add some data
    note = Note(name="Exported Note", content="Exported note")
    tag = Tag(name="Exported tag")
    att = Attachment(filename="file.txt", path="/tmp/file.txt", note_id=note.id)
    service._note_repo.add(note)
    service._tag_repo.add(tag)
    service._attachment_repo.add(att)
    exported = service.export_all()
    assert "Exported note" in exported and "Exported tag" in exported
    # Import into a new service
    new_service = BackupExportService()
    summary = new_service.import_all(exported)
    assert summary["success"] > 0

def test_validate_imported_data(service):
    valid = json.dumps({"notes": [], "tags": [], "attachments": []})
    invalid = json.dumps({"notes": {}, "tags": [], "attachments": []})
    assert service.validate_imported_data(valid)
    assert not service.validate_imported_data(invalid)

def test_import_conflict(service):
    note = Note(name="Conflict Note", content="Conflict note")
    service._note_repo.add(note)
    exported = service.export_all()
    # Import again, should cause conflict
    summary = service.import_all(exported)
    assert any(c["type"] == "note" for c in summary["conflicts"])

def test_import_error_handling(service):
    # Malformed JSON
    summary = service.import_all("not a json string")
    assert any("Fatal error" in e for e in summary["errors"])

def test_import_progress_reporting(service):
    note = Note(name="Progress Note", content="Progress note")
    service._note_repo.add(note)
    exported = service.export_all()
    progress = []
    def on_progress(entity, count, total):
        progress.append((entity, count, total))
    new_service = BackupExportService()
    new_service.import_all(exported, on_progress=on_progress)
    assert any(p[0] == "note" for p in progress) 