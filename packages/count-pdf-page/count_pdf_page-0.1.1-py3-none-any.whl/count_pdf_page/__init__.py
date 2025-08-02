"""
Count PDF Page - A Python package for counting pages in PDF files.

This package provides utilities to count pages in PDF files and generate
markdown reports with detailed statistics.
"""

__version__ = "0.1.1"
__author__ = "Chih-Hung Hsu"
__email__ = "aaronhsu@mail.ntou.edu.tw"

from .core import count_pdf_pages, generate_markdown_report
from .cli import main

__all__ = ["count_pdf_pages", "generate_markdown_report", "main"]
