#!/usr/bin/env python
"""
Command line interface for basic OCR processing.
"""

import os
import sys
import argparse
from ocr.core.processor import extract_text_from_pdf, save_text_to_file
from ocr.core.utils import get_output_path

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF using OCR")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output text file path")
    parser.add_argument("--start-page", "-s", type=int, default=1, help="Starting page number")
    parser.add_argument("--end-page", "-e", type=int, help="Ending page number")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found - {args.pdf_path}")
        return
    
    # Set output path
    output_path = args.output or get_output_path(args.pdf_path)
    
    print(f"Starting OCR on {args.pdf_path}")
    print(f"Processing pages {args.start_page} to {args.end_page or 'end'}")
    
    text = extract_text_from_pdf(args.pdf_path, args.start_page, args.end_page)
    
    if text:
        save_text_to_file(text, output_path)
        print(f"OCR completed successfully. Text saved to {output_path}")
        
        # Print a preview of the text
        preview_length = min(500, len(text))
        print(f"\nText preview:\n{text[:preview_length]}...")
    else:
        print("OCR failed.")

if __name__ == "__main__":
    main() 