#!/usr/bin/env python3
"""
Test script for KWIC Concordance functionality.

This script demonstrates the creation and usage of KWIC concordances
with sample text data.
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_manager.models.document import Document, DocumentType
from document_manager.models.kwic_concordance import ConcordanceSettings, ConcordanceExportFormat
from document_manager.repositories.concordance_repository import ConcordanceRepository
from document_manager.services.concordance_service import ConcordanceService
from document_manager.services.document_service import DocumentService


class MockDocumentService:
    """Mock document service for testing."""
    
    def __init__(self):
        """Initialize with sample documents."""
        self.documents = {
            "doc1": Document(
                id="doc1",
                name="sample1.txt",
                file_path=Path("sample1.txt"),
                file_type=DocumentType.TXT,
                size_bytes=500,
                content="""
                The quick brown fox jumps over the lazy dog. This is a classic pangram 
                that contains every letter of the alphabet. The fox is known for its 
                cunning and agility. Many stories feature foxes as clever characters.
                The dog, on the other hand, is often portrayed as loyal and faithful.
                """,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            "doc2": Document(
                id="doc2",
                name="sample2.txt",
                file_path=Path("sample2.txt"),
                file_type=DocumentType.TXT,
                size_bytes=600,
                content="""
                In the realm of natural language processing, concordances are powerful 
                tools for text analysis. A concordance shows every occurrence of a word 
                or phrase in its context. KWIC (Key Word In Context) concordances are 
                particularly useful for linguistic research and corpus analysis.
                The context window provides valuable information about word usage patterns.
                """,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            "doc3": Document(
                id="doc3",
                name="sample3.txt",
                file_path=Path("sample3.txt"),
                file_type=DocumentType.TXT,
                size_bytes=700,
                content="""
                Text analysis has evolved significantly with the advent of computational 
                linguistics. Modern tools can process vast amounts of text data quickly 
                and efficiently. Concordance analysis remains a fundamental technique 
                for understanding language patterns and word relationships in context.
                Researchers use these tools to study everything from literature to 
                social media posts.
                """,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        }
    
    def get_document(self, doc_id: str) -> Document:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def list_documents(self):
        """List all documents."""
        return list(self.documents.values())


def test_kwic_concordance():
    """Test the KWIC concordance functionality."""
    print("🔍 Testing KWIC Concordance Functionality")
    print("=" * 50)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Initialize services
        print("📚 Initializing services...")
        concordance_repo = ConcordanceRepository(db_path)
        document_service = MockDocumentService()
        concordance_service = ConcordanceService(concordance_repo, document_service)
        
        # Test 1: Create a basic concordance
        print("\n🎯 Test 1: Creating basic concordance...")
        keywords = ["fox", "dog", "text", "analysis"]
        document_ids = ["doc1", "doc2", "doc3"]
        
        settings = ConcordanceSettings(
            context_window=30,
            case_sensitive=False,
            whole_words_only=True,
            sort_by="keyword"
        )
        
        concordance_table = concordance_service.generate_concordance(
            name="Sample Concordance",
            keywords=keywords,
            document_ids=document_ids,
            settings=settings,
            description="A test concordance for demonstration",
            tags=["test", "demo"]
        )
        
        print(f"✅ Created concordance with {len(concordance_table.entries)} entries")
        
        # Save the concordance
        table_id = concordance_service.save_concordance(concordance_table)
        print(f"💾 Saved concordance with ID: {table_id}")
        
        # Test 2: Display concordance entries
        print("\n📋 Test 2: Displaying concordance entries...")
        print(f"{'Keyword':<12} {'Left Context':<25} {'Right Context':<25} {'Document':<15}")
        print("-" * 80)
        
        for entry in concordance_table.entries[:10]:  # Show first 10 entries
            left = entry.left_context[-25:] if len(entry.left_context) > 25 else entry.left_context
            right = entry.right_context[:25] if len(entry.right_context) > 25 else entry.right_context
            print(f"{entry.keyword:<12} {left:<25} {right:<25} {entry.document_name:<15}")
        
        if len(concordance_table.entries) > 10:
            print(f"... and {len(concordance_table.entries) - 10} more entries")
        
        # Test 3: Statistics
        print("\n📊 Test 3: Concordance statistics...")
        stats = concordance_table.get_statistics()
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Test 4: Keyword extraction
        print("\n🔤 Test 4: Automatic keyword extraction...")
        all_text = " ".join([doc.content for doc in document_service.documents.values()])
        extracted_keywords = concordance_service.extract_keywords_from_text(
            all_text,
            min_length=4,
            min_frequency=2,
            exclude_stop_words=True
        )
        
        print("Top extracted keywords:")
        for keyword, frequency in extracted_keywords[:10]:
            print(f"  {keyword}: {frequency} occurrences")
        
        # Test 5: Export functionality
        print("\n📤 Test 5: Export functionality...")
        
        # Export to CSV
        csv_format = ConcordanceExportFormat(
            format_type="csv",
            include_metadata=True,
            include_statistics=True
        )
        
        csv_data = concordance_service.export_concordance(table_id, csv_format)
        print(f"✅ CSV export: {len(csv_data)} characters")
        
        # Export to JSON
        json_format = ConcordanceExportFormat(
            format_type="json",
            include_metadata=True,
            include_statistics=True
        )
        
        json_data = concordance_service.export_concordance(table_id, json_format)
        print(f"✅ JSON export: {len(json_data)} characters")
        
        # Export to HTML
        html_format = ConcordanceExportFormat(
            format_type="html",
            include_metadata=True,
            include_statistics=True
        )
        
        html_data = concordance_service.export_concordance(table_id, html_format)
        print(f"✅ HTML export: {len(html_data)} characters")
        
        # Test 6: Search and filtering
        print("\n🔍 Test 6: Search and filtering...")
        
        # Search for specific keyword
        search_results = concordance_service.search_concordances(
            table_id=table_id
        )
        print(f"✅ Found {len(search_results.entries)} total entries")
        print(f"   Keywords found: {', '.join(search_results.keywords_found)}")
        print(f"   Documents found: {len(search_results.documents_found)}")
        print(f"   Search time: {search_results.search_time_ms:.2f}ms")
        
        # Test 7: List all concordances
        print("\n📝 Test 7: List all concordances...")
        all_concordances = concordance_service.list_concordances()
        print(f"✅ Found {len(all_concordances)} concordance tables")
        
        for concordance in all_concordances:
            print(f"  - {concordance['name']}: {concordance['entry_count']} entries")
        
        # Test 8: Retrieve saved concordance
        print("\n🔄 Test 8: Retrieve saved concordance...")
        retrieved_concordance = concordance_service.get_concordance(table_id)
        
        if retrieved_concordance:
            print(f"✅ Retrieved concordance: {retrieved_concordance.name}")
            print(f"   Entries: {len(retrieved_concordance.entries)}")
            print(f"   Keywords: {', '.join(retrieved_concordance.keywords)}")
            print(f"   Created: {retrieved_concordance.created_at}")
        else:
            print("❌ Failed to retrieve concordance")
        
        print("\n🎉 All tests completed successfully!")
        
        # Show sample export data
        print("\n📄 Sample CSV Export (first 500 characters):")
        print("-" * 50)
        print(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary database
        try:
            os.unlink(db_path)
            print(f"\n🧹 Cleaned up temporary database: {db_path}")
        except:
            pass


if __name__ == "__main__":
    test_kwic_concordance() 