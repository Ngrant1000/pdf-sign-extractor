# PDF Sign Extractor

A specialized Python-based OCR tool for extracting and analyzing sign information from PDF plans and engineering documents. This tool uses optical character recognition to extract text from scanned PDFs and then performs targeted analysis to identify, categorize, and generate reports on sign specifications.

## Project Structure

- **ocr_package/** - Core OCR functionality organized as a Python package
- **outputs/** - Organized analysis results for specific projects
  - **SR-81_Plans/** - Example analysis of signs from SR-81 highway plans

## Features

- PDF text extraction using PyMuPDF and Tesseract OCR
- Sign specification identification and classification
- Bill of Materials (BOM) generation for signs
- Data visualization of sign types, sizes, and actions
- Organized reporting with detailed analysis

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/NicholasGrant/pdf-sign-extractor.git
cd pdf-sign-extractor

# Install the package and dependencies
cd ocr_package
pip install -e .
```

### Usage

For basic OCR processing:
```bash
python ocr_cli.py path/to/your/document.pdf
```

For sign extraction:
```bash
python extract_detailed_signs.py path/to/your/plans.pdf
```

See the README.md in the `ocr_package` directory for more detailed usage instructions.

## Example Output

The `outputs/SR-81_Plans` directory contains an example of extracting sign information from highway plans, including:

- Detailed sign schedules with locations and specifications
- Visual charts showing sign distribution by type, size, and action
- Comprehensive analysis reports in markdown and text formats

## License

MIT License 