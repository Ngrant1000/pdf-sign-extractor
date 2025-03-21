"""
PDF OCR Tool - A Python package for extracting text from scanned PDF documents.
"""

from .core.processor import preprocess_image, extract_text_from_pdf, save_text_to_file
from .core.utils import ensure_dir, get_output_path

__version__ = "0.1.0"
__author__ = "Original Author"

# Allow direct imports from ocr package
__all__ = [
    'preprocess_image',
    'extract_text_from_pdf',
    'save_text_to_file',
    'ensure_dir',
    'get_output_path',
] 