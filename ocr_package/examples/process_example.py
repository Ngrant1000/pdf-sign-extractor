#!/usr/bin/env python
"""
Example script demonstrating basic usage of the OCR package.
"""

import os
import sys
import time
from ocr.core.processor import extract_text_from_pdf, save_text_to_file
from ocr.advanced.document_processor import process_document
from ocr.batch.processors import batch_process

def basic_ocr_example(pdf_path):
    """Demonstrate basic OCR processing"""
    print("\n=== Basic OCR Example ===")
    start_time = time.time()
    
    # Process the PDF
    print(f"Processing: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if text:
        # Save the extracted text
        output_path = "example_output.txt"
        save_text_to_file(text, output_path)
        
        # Print stats
        elapsed = time.time() - start_time
        print(f"Completed in {elapsed:.2f} seconds")
        print(f"Text saved to: {output_path}")
        
        # Print preview
        preview_length = min(300, len(text))
        print(f"\nText preview:\n{text[:preview_length]}...")
    else:
        print("OCR processing failed")

def advanced_ocr_example(pdf_path):
    """Demonstrate advanced document processing"""
    print("\n=== Advanced Document Processing Example ===")
    start_time = time.time()
    
    # Process the PDF
    print(f"Processing: {pdf_path}")
    output_path = "example_advanced.json"
    document = process_document(pdf_path, output_path=output_path)
    
    if document:
        # Print stats
        elapsed = time.time() - start_time
        print(f"Completed in {elapsed:.2f} seconds")
        print(f"JSON saved to: {output_path}")
        
        # Print document info
        print(f"\nDocument Information:")
        print(f"- Pages: {document.metadata.get('page_count', 'Unknown')}")
        print(f"- Elements: {len(document.elements)}")
        print(f"- Title: {document.metadata.get('title', 'Unknown')}")
        print(f"- Author: {document.metadata.get('author', 'Unknown')}")
    else:
        print("Advanced processing failed")

def batch_processing_example(pdf_directory):
    """Demonstrate batch processing"""
    print("\n=== Batch Processing Example ===")
    
    # Create output directory
    output_dir = "batch_results"
    
    # Process all PDFs in the directory
    from ocr.batch.processors import process_directory
    process_directory(
        pdf_directory,
        output_dir=output_dir,
        dpi=150,
        save_images=False
    )

def main():
    # Check for test PDF
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: File not found - {pdf_path}")
            return
            
        # Run examples
        basic_ocr_example(pdf_path)
        advanced_ocr_example(pdf_path)
        
        # For batch processing, use the directory of the PDF
        pdf_dir = os.path.dirname(pdf_path) or "."
        batch_processing_example(pdf_dir)
    else:
        print("Please provide a PDF file path as argument")
        print("Example: python process_example.py sample.pdf")

if __name__ == "__main__":
    main() 