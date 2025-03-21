# PDF OCR Tool

A Python package for extracting text from scanned PDF documents with various levels of processing complexity.

## Features

- Basic OCR processing for simple PDFs
- Advanced document structure extraction with table detection
- Batch processing for multiple documents
- Parallel processing for improved performance
- Command-line interfaces for all functionality
- Table extraction and Bill of Materials generation

## Requirements

- Python 3.6+
- Tesseract OCR engine (must be installed separately)
- Poppler (for pdf2image) - only needed for the basic OCR functionality

## Installation

1. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

2. Install Poppler (for basic OCR functionality):
   - Windows: Download and install from https://github.com/oschwartz10612/poppler-windows/releases/
   - Linux: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

3. Install the package:
   ```
   pip install -e .
   ```

   For advanced features (optional):
   ```
   pip install -e ".[advanced]"
   ```

## Package Structure

```
ocr_package/
├── ocr/                # Main package
│   ├── core/           # Core functionality
│   │   ├── processor.py  # Basic OCR processing
│   │   └── utils.py      # Utility functions
│   ├── advanced/       # Advanced processing
│   │   └── document_processor.py  # Document structure extraction
│   └── batch/          # Batch processing
│       └── processors.py  # Multi-file processing
├── ocr_cli.py          # Basic OCR CLI
├── advanced_cli.py     # Advanced processing CLI
├── batch_cli.py        # Batch processing CLI
├── setup.py            # Package setup
└── requirements.txt    # Required dependencies
```

## Usage

### Basic OCR

```python
from ocr.core.processor import extract_text_from_pdf, save_text_to_file

text = extract_text_from_pdf("input.pdf")
save_text_to_file(text, "output.txt")
```

From command line:
```
ocr input.pdf --output output.txt
```

### Advanced Document Processing

```python
from ocr.advanced.document_processor import process_document

document = process_document("input.pdf", "output.json")
```

From command line:
```
ocr-advanced input.pdf --output output.json --dpi 300
```

### Batch Processing

```python
from ocr.batch.processors import batch_process
import glob

files = glob.glob("*.pdf")
batch_process(files, output_dir="extracted_texts")
```

From command line:
```
ocr-batch "*.pdf" --output-dir extracted_texts
```

### Table Extraction and Bill of Materials

```python
from ocr.advanced.table_extractor import extract_sign_specs_from_plans

# Extract Bill of Materials from plans document
bom = extract_sign_specs_from_plans("extracted_data", "bom.csv")
print(bom.head())
```

From command line:
```
python extract_bom.py --data-dir extracted_data --output bom.csv
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 