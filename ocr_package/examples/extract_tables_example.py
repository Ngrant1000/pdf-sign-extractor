#!/usr/bin/env python
"""
Example script to demonstrate extracting tables from PDF documents.
"""

import os
import sys
import time
from ocr.core.processor import extract_text_from_pdf, save_text_to_file
from ocr.advanced.document_processor import process_document
from ocr.advanced.table_extractor import PlanSpecificationsExtractor

def extract_table_example(pdf_path):
    """Demonstrate how to extract tables from a PDF document."""
    print("\n=== Table Extraction Example ===")
    start_time = time.time()
    
    # Process the PDF using the advanced document processor first
    print(f"Processing: {pdf_path}")
    json_output_path = "document_structure.json"
    document = process_document(pdf_path, output_path=json_output_path)
    
    if not document:
        print("Failed to process document.")
        return
    
    # Create output directories
    extracted_data_dir = "extracted_table_data"
    os.makedirs(os.path.join(extracted_data_dir, "texts"), exist_ok=True)
    
    # Extract text with positions
    for i, element in enumerate(document.elements):
        if element.element_type == "page":
            # Save the page text with position information
            text_with_positions = []
            
            # Assuming the text has position information in the metadata
            if "text_positions" in element.metadata:
                for pos in element.metadata["text_positions"]:
                    text_with_positions.append(
                        f"Text: {pos['text']}, Position: ({pos['x']}, {pos['y']}), "
                        f"Size: {pos['width']}x{pos['height']}, Confidence: {pos['confidence']}"
                    )
            else:
                # If no positions in metadata, create a simplified format for demonstration
                text_with_positions.append(
                    f"Text: {element.text}, Position: (0, {i*100}), Size: 500x50, Confidence: 90"
                )
            
            # Save position information to file
            position_file = os.path.join(extracted_data_dir, "texts", f"page_{i+1}_text_positions.txt")
            with open(position_file, "w", encoding="utf-8") as f:
                f.write("\n".join(text_with_positions))
                
            # Also save the raw text
            text_file = os.path.join(extracted_data_dir, "texts", f"page_{i+1}_text.txt")
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(element.text)
    
    # Use the table extractor to generate a BOM
    extractor = PlanSpecificationsExtractor(extracted_data_dir)
    
    # Extract and print ATM specifications if available
    atm_specs = extractor.extract_atm_specifications()
    if atm_specs is not None:
        print("\nATM Specifications:")
        print(atm_specs.head().to_string(index=False))
    else:
        print("\nNo ATM specifications found.")
    
    # Extract and print panel schedule if available
    panel_schedule = extractor.extract_panel_schedule()
    if panel_schedule is not None:
        print("\nPanel Schedule:")
        print(panel_schedule.head().to_string(index=False))
    else:
        print("\nNo panel schedule found.")
    
    # Generate and print BOM
    bom = extractor.generate_bom()
    if bom is not None:
        print("\nBill of Materials:")
        print(bom.to_string(index=False))
        
        # Save BOM to CSV
        bom_file = os.path.join(extracted_data_dir, "bom.csv")
        bom.to_csv(bom_file, index=False)
        print(f"\nBill of Materials saved to {bom_file}")
    else:
        print("\nNo Bill of Materials could be generated.")
    
    elapsed = time.time() - start_time
    print(f"\nTable extraction completed in {elapsed:.2f} seconds.")

def main():
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: File not found - {pdf_path}")
            return
            
        # Run the table extraction example
        extract_table_example(pdf_path)
    else:
        print("Please provide a PDF file path as argument")
        print("Example: python extract_tables_example.py sample.pdf")

if __name__ == "__main__":
    main() 