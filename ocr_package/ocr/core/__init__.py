"""
Core OCR functionality for basic PDF text extraction.
"""

from .processor import preprocess_image, extract_text_from_pdf, save_text_to_file
from .utils import ensure_dir, get_output_path

__all__ = [
    'preprocess_image',
    'extract_text_from_pdf',
    'save_text_to_file',
    'ensure_dir',
    'get_output_path',
] 