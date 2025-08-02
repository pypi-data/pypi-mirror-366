"""
Tests for core functionality.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from count_pdf_page.core import (
    count_pdf_pages,
    generate_markdown_report,
    process_directory,
)


class TestCoreFunctionality(unittest.TestCase):
    """Test cases for core PDF processing functions."""

    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        results = [
            ("test1.pdf", 10),
            ("test2.pdf", 20),
            ("test3.pdf", "Error"),
        ]
        total_pages = 30

        report = generate_markdown_report(results, total_pages)

        # Check if report contains expected elements
        self.assertIn("# PDF Page Count Report", report)
        self.assertIn("Total PDF files:** 3", report)
        self.assertIn("Total pages:** 30", report)
        self.assertIn("test1.pdf", report)
        self.assertIn("test2.pdf", report)
        self.assertIn("test3.pdf", report)
        self.assertIn("Average pages per file:", report)

    def test_generate_markdown_report_empty(self):
        """Test markdown report generation with empty results."""
        results = []
        total_pages = 0

        report = generate_markdown_report(results, total_pages)

        self.assertIn("Total PDF files:** 0", report)
        self.assertIn("Total pages:** 0", report)
        self.assertIn("Average pages per file:** N/A", report)

    @patch("count_pdf_page.core.PyPDF2.PdfReader")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_count_pdf_pages_success(self, mock_exists, mock_file, mock_reader):
        """Test successful PDF page counting."""
        mock_exists.return_value = True
        mock_reader.return_value.pages = [1, 2, 3]  # 3 pages

        result = count_pdf_pages("test.pdf")

        self.assertEqual(result, 3)
        mock_exists.assert_called_once_with("test.pdf")
        mock_file.assert_called_once_with("test.pdf", "rb")

    @patch("os.path.exists")
    def test_count_pdf_pages_file_not_found(self, mock_exists):
        """Test PDF page counting when file doesn't exist."""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            count_pdf_pages("nonexistent.pdf")

    @patch("count_pdf_page.core.PyPDF2.PdfReader")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_count_pdf_pages_error(self, mock_exists, mock_file, mock_reader):
        """Test PDF page counting when an error occurs."""
        mock_exists.return_value = True
        mock_reader.side_effect = Exception("PDF parsing error")

        result = count_pdf_pages("corrupt.pdf")

        self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main()
