#!/usr/bin/env python
"""
Simple Bill of Materials extractor for sign specifications.

This script extracts sign specifications from the plans document
to create a Bill of Materials.
"""

import os
import sys
import pandas as pd
import re
import glob

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

def main():
    # Look for plans text file in extracted_data directory
    extracted_texts_dir = "../extracted_data/texts"
    plans_text = ""
    
    if os.path.exists(extracted_texts_dir):
        # Check for plans text files
        plans_files = glob.glob(os.path.join(extracted_texts_dir, "plans_*.txt"))
        
        # If no plans files are found, try all txt files
        if not plans_files:
            plans_files = glob.glob(os.path.join(extracted_texts_dir, "*.txt"))
        
        # Process each found file
        for file_path in plans_files:
            print(f"Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    plans_text += f.read() + "\n\n"
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    # If no files found or no text extracted, exit
    if not plans_text:
        print("Error: No text files found or unable to read files.")
        print("Please ensure that the extracted_data/texts directory exists and contains text files.")
        return 1
    
    # Extract sign specifications
    print("Extracting sign specifications...")
    bom = extract_sign_specs_from_text(plans_text)
    
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