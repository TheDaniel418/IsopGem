"""
Unit tests for page number removal functionality in DocumentService.
"""

import unittest
from document_manager.services.document_service import DocumentService


class TestPageNumberRemoval(unittest.TestCase):
    """Test the page number removal functionality."""

    def setUp(self):
        """Set up the test environment."""
        self.document_service = DocumentService()

    def test_remove_standalone_page_numbers(self):
        """Test removing standalone page numbers."""
        text_with_numbers = """This is some text on page one.

1

This is text on page two.

2

This is text on page three.

3
"""
        expected_text = """This is some text on page one.

This is text on page two.

This is text on page three.
"""
        result = self.document_service._remove_page_numbers(text_with_numbers)
        self.assertEqual(result, expected_text)

    def test_remove_page_prefix_numbers(self):
        """Test removing page numbers with 'Page' prefix."""
        text_with_numbers = """This is some text on page one.

Page 1

This is text on page two.

Page 2 of 10

This is text on page three.

PAGE 3
"""
        expected_text = """This is some text on page one.

This is text on page two.

This is text on page three.
"""
        result = self.document_service._remove_page_numbers(text_with_numbers)
        self.assertEqual(result, expected_text)

    def test_remove_roman_numerals(self):
        """Test removing Roman numerals."""
        text_with_numbers = """This is some text on page one.

i

This is text on page two.

ii

This is text on page three.

iii
"""
        expected_text = """This is some text on page one.

This is text on page two.

This is text on page three.
"""
        result = self.document_service._remove_page_numbers(text_with_numbers)
        self.assertEqual(result, expected_text)

    def test_mixed_page_number_formats(self):
        """Test removing mixed page number formats."""
        text_with_numbers = """This is some text on page one.

i

This is text on page two.

Page 2

This is text on page three.

3
"""
        expected_text = """This is some text on page one.


This is text on page two.


This is text on page three.

"""
        result = self.document_service._remove_page_numbers(text_with_numbers)
        self.assertEqual(result, expected_text)

    def test_preserve_normal_content(self):
        """Test that normal content is preserved."""
        normal_text = """This is a paragraph with numbers like 123 and 456 embedded in it.
This is another paragraph that mentions Page 42 as part of a sentence.
Roman numerals like iv and viii should be preserved when they're part of sentences.
"""
        result = self.document_service._remove_page_numbers(normal_text)
        self.assertEqual(result, normal_text)

    def test_cleanup_multiple_newlines(self):
        """Test that multiple consecutive newlines are cleaned up."""
        text_with_extra_newlines = """This is page one.

1



This is page two.
"""
        expected_text = """This is page one.


This is page two.
"""
        result = self.document_service._remove_page_numbers(text_with_extra_newlines)
        self.assertEqual(result, expected_text)


if __name__ == "__main__":
    unittest.main()
