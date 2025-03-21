#!/usr/bin/env python
"""
Process plans PDF and extract Bill of Materials (BOM).

This script processes a plans PDF document and extracts 
sign specifications to generate a Bill of Materials.
"""

import os
import sys
import pandas as pd
import re
import glob
from ocr.core.processor import extract_text_from_pdf, save_text_to_file

def extract_sign_specs_from_text(text):
    """Extract sign specifications from text."""
    # Create a list to store BOM items
    bom_items = []
    
    # Count ATM signs by type
    atm_type1_count = len(re.findall(r'ATM\s+TYPE\s+1\s+SIGN', text))
    atm_type2_count = len(re.findall(r'ATM\s+TYPE\s+2\s+SIGN', text))
    atm_type3_count = len(re.findall(r'ATM\s+TYPE\s+3', text))
    
    if atm_type1_count > 0:
        bom_items.append({
            'Item': 'ATM Sign Type 1',
            'Quantity': atm_type1_count,
            'Description': 'Active Traffic Management Sign (Type 1)'
        })
    
    if atm_type2_count > 0:
        bom_items.append({
            'Item': 'ATM Sign Type 2',
            'Quantity': atm_type2_count,
            'Description': 'Active Traffic Management Sign (Type 2)'
        })
    
    if atm_type3_count > 0:
        bom_items.append({
            'Item': 'ATM Sign Type 3',
            'Quantity': atm_type3_count,
            'Description': 'Active Traffic Management Sign (Type 3)'
        })
    
    # Count other ITS equipment
    if 'ITS POLE (80 FEET)' in text:
        bom_items.append({
            'Item': 'ITS Pole',
            'Quantity': text.count('ITS POLE (80 FEET)'),
            'Description': 'ITS Pole (80 Feet)'
        })
    
    if 'CCTV CAMERA (PTZ)' in text:
        bom_items.append({
            'Item': 'CCTV Camera (PTZ)',
            'Quantity': text.count('CCTV CAMERA (PTZ)'),
            'Description': 'CCTV Camera with Pan/Tilt/Zoom Capability'
        })
    
    if 'CCTV CAMERA (FIXED)' in text:
        bom_items.append({
            'Item': 'CCTV Camera (Fixed)',
            'Quantity': text.count('CCTV CAMERA (FIXED)'),
            'Description': 'Fixed CCTV Camera'
        })
    
    if 'RADAR DETECTOR SYSTEM' in text:
        bom_items.append({
            'Item': 'Radar Detector System',
            'Quantity': text.count('RADAR DETECTOR SYSTEM'),
            'Description': 'Radar Detector System'
        })
        
    if 'COMMUNICATION CABINET' in text:
        bom_items.append({
            'Item': 'Communication Cabinet',
            'Quantity': text.count('COMMUNICATION CABINET'),
            'Description': 'Communication Cabinet for ITS Equipment'
        })
    
    # Look for panel information
    panel_match = re.search(r'PROJECT\s+ATCMTD\s+PANEL\s+SCHEDULE(.*?)PROJECT', text, re.DOTALL)
    if panel_match:
        panel_count = len(re.findall(r'PNL-\d+', panel_match.group(1)))
        if panel_count > 0:
            bom_items.append({
                'Item': 'Panel Board',
                'Quantity': panel_count,
                'Description': 'Electrical Panel Board for ATM Signs'
            })
    
    return pd.DataFrame(bom_items)

def get_plans_text():
    """Get text from either a provided PDF or existing extracted text files."""
    # Check if a PDF file is provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File not found - {pdf_path}")
            return None
        
        # Extract text from PDF
        print(f"Processing PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            print("Failed to extract text from PDF.")
            return None
        
        # Save extracted text
        text_output = "plans_extracted.txt"
        save_text_to_file(text, text_output)
        print(f"Extracted text saved to {text_output}")
        
        return text
    
    # No PDF provided, try to use existing extracted text
    print("No PDF file provided. Looking for existing extracted text files...")
    
    # Look in the extracted_data/texts directory
    extracted_texts_dir = "../extracted_data/texts"
    if os.path.exists(extracted_texts_dir):
        plans_files = glob.glob(os.path.join(extracted_texts_dir, "plans_*.txt"))
        if plans_files:
            # Use the first plans text file found
            plans_file = plans_files[0]
            print(f"Using existing text file: {plans_file}")
            with open(plans_file, 'r', encoding='utf-8') as f:
                return f.read()
    
    # Also check the current directory
    plans_files = glob.glob("plans_*.txt")
    if plans_files:
        # Use the first plans text file found
        plans_file = plans_files[0]
        print(f"Using existing text file: {plans_file}")
        with open(plans_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    print("Error: No PDF file provided and no existing plans text files found.")
    return None

def main():
    # Get text from PDF or existing files
    text = get_plans_text()
    
    if not text:
        print("Usage: python process_plans_for_bom.py [pdf_file]")
        print("If pdf_file is not provided, the script will try to use existing extracted text files.")
        return 1
    
    # Extract sign specifications
    print("Extracting sign specifications...")
    bom = extract_sign_specs_from_text(text)
    
    if bom.empty:
        print("No sign specifications found in the document.")
        return 1
    
    # Save BOM to CSV
    bom_output = "sign_specifications_bom.csv"
    bom.to_csv(bom_output, index=False)
    
    # Print summary
    print("\nBill of Materials Summary:")
    print(f"- Total items: {len(bom)}")
    print(f"- Total quantity: {bom['Quantity'].sum()}")
    
    # Display the Bill of Materials
    print("\nBill of Materials:")
    print(bom.to_string(index=False))
    
    print(f"\nBill of Materials saved to {bom_output}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 