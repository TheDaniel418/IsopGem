#!/usr/bin/env python3
"""
Test script for encoding detection and conversion functionality.
"""

import tempfile
import os
from pathlib import Path
from document_manager.services.document_service import DocumentService

def create_test_files():
    """Create test files with different encodings."""
    test_dir = Path(tempfile.mkdtemp(prefix="encoding_test_"))
    print(f"📁 Creating test files in: {test_dir}")
    
    # Test content with characters that exist in Windows-1252
    test_content = """This is a test file with special characters:
    
Windows "smart quotes" and em-dashes like this.
Some accented characters: cafe, naive, resume
Currency symbols: 100 pounds, 50 euros, 1000 yen
Mathematical symbols: plus/minus 5, less than 10, greater than 20
    
This content should test various encoding issues."""
    
    # More challenging content for Windows-1252
    win1252_content = """This file tests Windows-1252 encoding:
    
Smart quotes: "Hello" and 'world'
Em dash — and en dash –
Copyright © and trademark ™
Accented letters: café résumé naïve
Curly apostrophe: don't
    
This should work with Windows-1252 encoding."""
    
    # Create files with different encodings
    test_files = []
    
    # UTF-8 file (should work fine)
    utf8_file = test_dir / "utf8_test.txt"
    with open(utf8_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    test_files.append(("UTF-8", utf8_file))
    
    # Windows-1252 file (common Word export encoding)
    win1252_file = test_dir / "windows1252_test.txt"
    with open(win1252_file, 'w', encoding='windows-1252') as f:
        f.write(win1252_content)
    test_files.append(("Windows-1252", win1252_file))
    
    # ISO-8859-1 file (Latin-1) - use simpler content
    iso_content = """This file tests ISO-8859-1 encoding:
    
Basic accented characters: cafe, resume, naive
Some symbols: copyright and trademark
Simple punctuation and quotes.
    
This should work with ISO-8859-1 encoding."""
    
    iso_file = test_dir / "iso8859_test.txt"
    with open(iso_file, 'w', encoding='iso-8859-1') as f:
        f.write(iso_content)
    test_files.append(("ISO-8859-1", iso_file))
    
    return test_dir, test_files

def test_encoding_detection():
    """Test the encoding detection functionality."""
    print("🔍 Testing encoding detection...")
    
    test_dir, test_files = create_test_files()
    document_service = DocumentService()
    
    try:
        for encoding_name, file_path in test_files:
            print(f"\n📄 Testing file: {file_path.name} (created as {encoding_name})")
            
            # Test encoding detection
            detected_encoding = document_service._detect_file_encoding(file_path)
            print(f"   Detected encoding: {detected_encoding}")
            
            # Test reading with detected encoding
            try:
                with open(file_path, 'r', encoding=detected_encoding) as f:
                    content = f.read()
                print(f"   ✅ Successfully read with detected encoding")
                print(f"   📝 Content length: {len(content)} characters")
            except Exception as e:
                print(f"   ❌ Failed to read with detected encoding: {e}")
                
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")

def test_bulk_conversion():
    """Test the bulk conversion functionality."""
    print("\n🔄 Testing bulk conversion...")
    
    test_dir, test_files = create_test_files()
    document_service = DocumentService()
    
    try:
        # Run bulk conversion
        results = document_service.bulk_convert_text_files_to_utf8(
            test_dir,
            file_patterns=['*.txt'],
            recursive=False
        )
        
        print(f"\n📊 Conversion Results:")
        print(f"   Total files: {results['total_files']}")
        print(f"   Converted: {results['converted_files']}")
        print(f"   Already UTF-8: {results['already_utf8']}")
        print(f"   Failed: {results['failed_conversions']}")
        
        if results['errors']:
            print(f"   Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"     - {error}")
        
        print(f"\n📋 File Details:")
        for detail in results['conversion_details']:
            file_name = Path(detail['file_path']).name
            status = detail['status']
            original_encoding = detail['original_encoding']
            print(f"   {file_name}: {status} (was {original_encoding})")
            
        # Verify all files can now be read as UTF-8
        print(f"\n✅ Verification - Reading all files as UTF-8:")
        for _, file_path in test_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   ✅ {file_path.name}: Successfully read as UTF-8")
            except Exception as e:
                print(f"   ❌ {file_path.name}: Failed to read as UTF-8: {e}")
                
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    print("🧪 Testing Encoding Detection and Conversion System")
    print("=" * 60)
    
    try:
        test_encoding_detection()
        test_bulk_conversion()
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 