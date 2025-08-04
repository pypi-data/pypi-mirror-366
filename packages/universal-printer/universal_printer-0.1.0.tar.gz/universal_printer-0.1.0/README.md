# Universal Printer

A dependency-free Python library for cross-platform document printing with PDF fallback. Works on Windows, macOS, and Linux using only the Python standard library.

## Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Dependency-free**: Uses only Python standard library
- **PDF fallback**: Generates minimal PDFs when printing fails
- **Simple API**: Easy to use with just a few lines of code
- **Flexible input**: Print strings, file paths, or any text content

## Installation

```bash
pip install universal-printer
```

## Quick Start

```python
from universal_printer import DocumentPrinter

# Create a printer instance
printer = DocumentPrinter()

# Print a simple string
success, message, pdf_path = printer.print_document("Hello, World!")

if success:
    print("Document printed successfully!")
else:
    print(f"Printing failed: {message}")
    if pdf_path:
        print(f"PDF fallback saved to: {pdf_path}")
```

## Usage Examples

### Print text content

```python
from universal_printer import DocumentPrinter

printer = DocumentPrinter()

# Print simple text
text = """
This is a sample document.
It contains multiple lines.
Perfect for testing the printer!
"""

success, message, pdf_path = printer.print_document(text)
```

### Print an existing file

```python
# Print an existing text file
success, message, pdf_path = printer.print_document("/path/to/your/file.txt")
```

### Specify a printer

```python
# Print to a specific printer
success, message, pdf_path = printer.print_document(
    "Hello, World!", 
    printer_name="Your Printer Name"
)
```

### Print to PDF directly

```python
# Print to PDF (useful for "Microsoft Print to PDF" on Windows)
success, message, pdf_path = printer.print_document(
    "Hello, World!", 
    printer_name="Microsoft Print to PDF",
    pdf_filename="my_document.pdf"
)
```

### Disable PDF fallback

```python
# Disable PDF fallback if printing fails
success, message, pdf_path = printer.print_document(
    "Hello, World!", 
    fallback_to_pdf=False
)
```

## API Reference

### DocumentPrinter

The main class for printing documents.

#### Methods

##### `print_document(content, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`

Print the given content.

**Parameters:**
- `content` (str): Text content to print, or path to an existing file
- `printer_name` (str, optional): Name of the printer to use
- `fallback_to_pdf` (bool): Whether to create a PDF if printing fails (default: True)
- `pdf_filename` (str, optional): Custom filename for PDF fallback

**Returns:**
- `tuple`: (success: bool, message: str, pdf_path: str or None)

## Platform-Specific Behavior

### Windows
- Uses `rundll32.exe` with shell32.dll for printing
- Supports "Microsoft Print to PDF" printer
- Falls back to Notepad for .txt files if needed

### macOS/Linux
- Uses the `lp` command (CUPS)
- Supports print-to-file for PDF generation
- Requires CUPS to be installed and configured

### PDF Fallback
- Generates minimal but valid PDF files
- Uses Helvetica font at 12pt
- Places text starting at coordinates (50, 750)
- Handles basic text escaping for PDF format

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0
- Initial release
- Cross-platform printing support
- PDF fallback functionality
- Standard library only implementation