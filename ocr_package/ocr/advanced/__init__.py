"""
Advanced OCR functionality for more sophisticated document processing.
"""

from .document_processor import (
    BoundingBox, TableCell, Table, DocumentElement, StructuredDocument,
    preprocess_image_for_ocr, process_document, process_page, extract_elements_from_page
)

__all__ = [
    'BoundingBox',
    'TableCell',
    'Table',
    'DocumentElement',
    'StructuredDocument',
    'preprocess_image_for_ocr',
    'process_document',
    'process_page',
    'extract_elements_from_page',
] 