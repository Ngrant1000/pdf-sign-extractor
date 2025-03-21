#!/usr/bin/env python
"""
Extract a Bill of Materials from the plans document.

This script runs the table extraction on the existing extracted data
to generate a Bill of Materials for sign specifications.
"""

import os
import sys
from ocr.advanced.table_extractor import extract_sign_specs_from_plans

def main():
    # Path to extracted data directory
    extracted_data_dir = "extracted_data"
    
    # Check if extracted_data directory exists
    if not os.path.exists(extracted_data_dir) or not os.path.exists(os.path.join(extracted_data_dir, "texts")):
        print(f"Error: The extracted_data directory with text files is required.")
        print("Please run the OCR process on the plans document first.")
        return 1
    
    # Path to output file
    output_file = "sign_specifications_bom.csv"
    
    print(f"Extracting Bill of Materials from plans document...")
    bom = extract_sign_specs_from_plans(extracted_data_dir, output_file)
    
    if bom is None or len(bom) == 0:
        print("No sign specifications could be extracted from the plans document.")
        return 1
    
    # Print summary
    print("\nBill of Materials Summary:")
    print(f"- Total items: {len(bom)}")
    print(f"- Total quantity: {bom['Quantity'].sum()}")
    print(f"- Item types: {len(bom['Item'].unique())}")
    
    # Display the Bill of Materials
    print("\nBill of Materials:")
    print(bom.to_string(index=False))
    
    print(f"\nFull Bill of Materials saved to {output_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 