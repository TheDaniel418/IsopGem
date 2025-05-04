"""
@file test_search_indexing_and_search.py
@description Comprehensive unit tests for Note Manager indexing and search, including Unicode, large docs, query types, and integration.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies unittest, tempfile, shutil, os, document_manager.note_manager.services.search_service, document_manager.note_manager.services.index_update_worker, document_manager.note_manager.services.search_api
"""

import unittest
import tempfile
import shutil
import os
from document_manager.note_manager.services.search_service import SearchService
from document_manager.note_manager.services.search_api import SearchAPI
import document_manager.note_manager.services.search_api as search_api_mod
from types import SimpleNamespace

class TestSearchIndexingAndSearch(unittest.TestCase):
    def setUp(self):
        # Use a temp directory for Whoosh index
        self.tempdir = tempfile.mkdtemp()
        os.environ['WHOOSH_INDEX_DIR'] = self.tempdir
        # Use a temp file for disk cache
        search_api_mod.DISK_CACHE_FILE = os.path.join(self.tempdir, 'diskcache.json')
        self.search_service = SearchService()
        self.api = SearchAPI()
        self.worker = self.api.index_worker  # Use the worker from SearchAPI

    def tearDown(self):
        self.worker.stop()
        shutil.rmtree(self.tempdir)
        if 'WHOOSH_INDEX_DIR' in os.environ:
            del os.environ['WHOOSH_INDEX_DIR']

    def test_index_unicode_content(self):
        # Greek and Hebrew content
        note1 = SimpleNamespace(id='1', name='Greek', content='Αλφάβητο βήτα γάμμα', tags=['greek'], created='2024-06-10', modified='2024-06-10')
        note2 = SimpleNamespace(id='2', name='Hebrew', content='אבגדהוז חטיכלמ', tags=['hebrew'], created='2024-06-10', modified='2024-06-10')
        self.api.add_or_update_note(note1)
        self.api.add_or_update_note(note2)
        self.worker.task_queue.join()
        res_greek = self.api.search_notes('Αλφάβητο')
        res_hebrew = self.api.search_notes('אבגדהוז')
        self.assertTrue(any('Greek' in n['name'] for n in res_greek['results']))
        self.assertTrue(any('Hebrew' in n['name'] for n in res_hebrew['results']))

    def test_index_large_document(self):
        large_content = 'lorem ipsum ' * 10000  # Large doc
        note = SimpleNamespace(id='3', name='Large', content=large_content, tags=['large'], created='2024-06-10', modified='2024-06-10')
        self.api.add_or_update_note(note)
        self.worker.task_queue.join()
        res = self.api.search_notes('lorem')
        self.assertTrue(any('Large' in n['name'] for n in res['results']))

    def test_search_various_query_types(self):
        note = SimpleNamespace(id='4', name='Boolean', content='alchemy emerald tablet', tags=['alchemy'], created='2024-06-10', modified='2024-06-10')
        self.api.add_or_update_note(note)
        self.worker.task_queue.join()
        # Simple
        res1 = self.api.search_notes('alchemy')
        # Field
        res2 = self.api.search_notes('name:Boolean')
        # Boolean
        res3 = self.api.search_notes('alchemy AND emerald')
        # Phrase
        res4 = self.api.search_notes('"emerald tablet"')
        # Wildcard
        res5 = self.api.search_notes('alch*')
        self.assertTrue(res1['total'] > 0)
        self.assertTrue(res2['total'] > 0)
        self.assertTrue(res3['total'] > 0)
        self.assertTrue(res4['total'] > 0)
        self.assertTrue(res5['total'] > 0)

    def test_search_unicode_queries(self):
        note = SimpleNamespace(id='5', name='Unicode', content='שלום עולם', tags=['hebrew'], created='2024-06-10', modified='2024-06-10')
        self.api.add_or_update_note(note)
        self.worker.task_queue.join()
        res = self.api.search_notes('שלום')
        self.assertTrue(res['total'] > 0)

    def test_performance_large_index(self):
        # Index 1000 notes
        for i in range(1000):
            note = SimpleNamespace(id=str(1000+i), name=f'Note{i}', content=f'content {i}', tags=['bulk'], created='2024-06-10', modified='2024-06-10')
            self.api.add_or_update_note(note)
        self.worker.task_queue.join()
        import time
        start = time.time()
        res = self.api.search_notes('content')
        elapsed = time.time() - start
        self.assertTrue(res['total'] >= 1000)
        self.assertLess(elapsed, 2.0)  # Should be fast

    def test_integration_with_worker_and_api(self):
        note = SimpleNamespace(id='6', name='Integration', content='integration test', tags=['integration'], created='2024-06-10', modified='2024-06-10')
        self.api.add_or_update_note(note)
        self.worker.task_queue.join()
        res = self.api.search_notes('integration')
        self.assertTrue(res['total'] > 0)

if __name__ == '__main__':
    unittest.main() 