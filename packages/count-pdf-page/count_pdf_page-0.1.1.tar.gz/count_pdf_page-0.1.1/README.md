# Count PDF Page

A Python package for counting pages in PDF files and generating detailed markdown reports.

## Features

- 📄 Count pages in individual PDF files or entire directories
- 📊 Generate comprehensive markdown reports with statistics
- 🖥️ Command-line interface for easy usage
- 🐍 Python API for programmatic use
- 📈 Detailed statistics including average, largest, and smallest files

## Installation

### From PyPI (when published)

```bash
pip install count-pdf-page
```

### From Source

```bash
git clone https://github.com/yourusername/count-pdf-page.git
cd count-pdf-page
pip install -e .
```

## Usage

### Command Line Interface

Count PDF pages in the current directory:

```bash
count-pdf-page
```

Count PDF pages in a specific directory:

```bash
count-pdf-page /path/to/pdf/directory
```

Specify custom output file:

```bash
count-pdf-page --output my_report.md
```

Enable verbose output:

```bash
count-pdf-page --verbose
```

### Python API

```python
from count_pdf_page import count_pdf_pages, process_directory, generate_markdown_report

# Count pages in a single PDF
page_count = count_pdf_pages("document.pdf")
print(f"Pages: {page_count}")

# Process entire directory
results, total_pages = process_directory("/path/to/pdfs")

# Generate markdown report
report = generate_markdown_report(results, total_pages)
print(report)
```

## Requirements

- Python 3.7+
- PyPDF2

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/count-pdf-page.git
cd count-pdf-page
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
```

### Type Checking

```bash
mypy src
```

## Output Example

The generated markdown report includes:

- Summary with total files and pages
- Detailed table of all PDF files and their page counts
- Statistics including average pages, largest file, and smallest file
- Timestamp of report generation

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0
- Initial release
- Basic PDF page counting functionality
- Command-line interface
- Markdown report generation
- Python API
