#!/usr/bin/env python
"""
Command line interface for advanced document processing.
"""

import os
import sys
import argparse
from ocr.advanced.document_processor import process_document

def main():
    parser = argparse.ArgumentParser(description="Process PDF documents with advanced OCR")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--dpi", "-d", type=int, default=200, help="DPI for rendering (higher = better quality, lower = faster)")
    parser.add_argument("--workers", "-w", type=int, help="Number of worker processes (default: CPU count - 1)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found - {args.pdf_path}")
        return
    
    # Set output path
    if not args.output:
        base_name = os.path.basename(args.pdf_path)
        output_path = os.path.splitext(base_name)[0] + ".json"
    else:
        output_path = args.output
    
    print(f"Starting advanced document processing on {args.pdf_path}")
    print(f"DPI: {args.dpi}, Workers: {args.workers or 'Auto'}")
    
    document = process_document(
        args.pdf_path,
        output_path=output_path,
        dpi=args.dpi,
        num_workers=args.workers
    )
    
    if document:
        print(f"Document processing completed successfully. Results saved to {output_path}")
        
        # Print a summary
        print(f"\nDocument Summary:")
        print(f"- Pages: {document.metadata.get('page_count', 'Unknown')}")
        print(f"- Elements: {len(document.elements)}")
        print(f"- Title: {document.metadata.get('title', 'Unknown')}")
        print(f"- Author: {document.metadata.get('author', 'Unknown')}")
    else:
        print("Document processing failed.")

if __name__ == "__main__":
    main() 