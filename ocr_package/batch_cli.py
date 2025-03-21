#!/usr/bin/env python
"""
Command line interface for batch PDF processing.
"""

import os
import sys
import argparse
import glob
from ocr.batch.processors import batch_process, process_directory

def main():
    parser = argparse.ArgumentParser(description="Batch process multiple PDF files with OCR")
    parser.add_argument("files", nargs='+', help="PDF files to process (wildcards supported)")
    parser.add_argument("--output-dir", "-o", help="Directory to save extracted text files")
    parser.add_argument("--dpi", "-d", type=int, default=200, help="DPI for rendering (lower = faster)")
    parser.add_argument("--save-images", "-i", action="store_true", help="Save processed images")
    parser.add_argument("--workers", "-w", type=int, help="Number of worker processes")
    parser.add_argument("--page-range", "-p", help="Page range to process (e.g., '0-5' or '10')")
    parser.add_argument("--process-dir", action="store_true", help="Process directories instead of files")
    
    args = parser.parse_args()
    
    if args.process_dir:
        # Process directories
        for directory in args.files:
            if os.path.isdir(directory):
                print(f"\nProcessing directory: {directory}")
                process_directory(
                    directory,
                    output_dir=args.output_dir,
                    dpi=args.dpi,
                    save_images=args.save_images,
                    max_workers=args.workers,
                    page_range=args.page_range
                )
            else:
                print(f"Skipping {directory} - not a directory")
    else:
        # Expand any wildcards in file paths
        file_list = []
        for path in args.files:
            if '*' in path:
                file_list.extend(glob.glob(path))
            else:
                file_list.append(path)
        
        # Filter to only include PDF files
        file_list = [f for f in file_list if f.lower().endswith('.pdf') and os.path.isfile(f)]
        
        if not file_list:
            print("No PDF files found")
            return
        
        # Process files
        batch_process(
            file_list,
            output_dir=args.output_dir,
            dpi=args.dpi,
            save_images=args.save_images,
            max_workers=args.workers,
            page_range=args.page_range
        )

if __name__ == "__main__":
    main() 