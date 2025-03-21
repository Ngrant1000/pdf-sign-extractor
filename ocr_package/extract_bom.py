#!/usr/bin/env python
"""
Extract Bill of Materials (BOM) from plans document.

This script uses position information from OCR text extraction to detect
and parse tables in the document, identifying sign specifications and 
generating a Bill of Materials.
"""

import os
import sys
import argparse
from ocr.advanced.table_extractor import extract_sign_specs_from_plans

def main():
    parser = argparse.ArgumentParser(description="Extract Bill of Materials from plans document")
    parser.add_argument("--data-dir", "-d", default="extracted_data", 
                        help="Directory containing extracted text data (default: extracted_data)")
    parser.add_argument("--output", "-o", default="bom.csv",
                        help="Output CSV file for Bill of Materials (default: bom.csv)")
    
    args = parser.parse_args()
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' not found")
        return 1
        
    # Extract Bill of Materials
    print(f"Extracting Bill of Materials from documents in {args.data_dir}...")
    bom = extract_sign_specs_from_plans(args.data_dir, args.output)
    
    if bom is None or len(bom) == 0:
        print("No specifications could be extracted from the documents")
        return 1
    
    # Print summary
    print("\nBill of Materials Summary:")
    print(f"- Total items: {len(bom)}")
    print(f"- Total quantity: {bom['Quantity'].sum()}")
    print(f"- Item types: {len(bom['Item'].unique())}")
    
    # Display the first few rows
    print("\nTop items:")
    print(bom.head().to_string(index=False))
    
    print(f"\nFull Bill of Materials saved to {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 