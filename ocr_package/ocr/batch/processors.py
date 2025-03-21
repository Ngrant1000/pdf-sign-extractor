import os
import sys
import time
import glob
from ..core.processor import extract_text_from_pdf, save_text_to_file
from ..core.utils import ensure_dir, get_output_path

def process_pdf_with_progress(pdf_path, output_path=None, start_page=0, end_page=None, 
                            dpi=200, save_images=False, workers=None):
    """Process a PDF with progress tracking"""
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    # Determine output path
    if output_path is None:
        output_path = get_output_path(pdf_path)
    
    # Create output directory for images if needed
    output_dir = None
    if save_images:
        output_dir = f"images_{os.path.splitext(os.path.basename(pdf_path))[0]}"
        ensure_dir(output_dir)
    
    # Extract text with optimized settings
    start_time = time.time()
    text = extract_text_from_pdf(
        pdf_path, 
        start_page=start_page, 
        end_page=end_page
    )
    processing_time = time.time() - start_time
    
    if text:
        # Save the text
        save_text_to_file(text, output_path)
        
        # Report statistics
        print(f"\nResults for {os.path.basename(pdf_path)}:")
        print(f"- Text saved to: {output_path}")
        print(f"- Processing time: {processing_time:.2f} seconds")
        if save_images:
            print(f"- Images saved to: {output_dir}")
        
        return True
    else:
        print(f"\nFailed to process {os.path.basename(pdf_path)}")
        return False

def batch_process(file_list, output_dir=None, dpi=200, save_images=False, 
                max_workers=None, page_range=None):
    """Process multiple PDF files in batch"""
    if not file_list:
        print("No files to process")
        return
    
    # Create output directory if specified
    if output_dir:
        ensure_dir(output_dir)
    
    # Parse page range if provided
    start_page, end_page = 0, None
    if page_range:
        parts = page_range.split('-')
        if len(parts) == 2:
            start_page = int(parts[0]) if parts[0] else 0
            end_page = int(parts[1]) if parts[1] else None
        elif len(parts) == 1:
            start_page = int(parts[0])
            end_page = start_page
    
    # Process each file
    successful = 0
    failed = 0
    total_time = 0
    
    print(f"\nBatch processing {len(file_list)} files")
    print(f"DPI: {dpi}, Workers: {max_workers or 'Auto'}, Save images: {save_images}")
    if page_range:
        print(f"Page range: {page_range}")
    
    start_batch_time = time.time()
    
    for i, pdf_path in enumerate(file_list, 1):
        print(f"\nFile {i} of {len(file_list)}")
        
        # Set output path
        if output_dir:
            output_path = get_output_path(pdf_path, output_dir=output_dir)
        else:
            output_path = None
        
        # Process file
        file_start_time = time.time()
        result = process_pdf_with_progress(
            pdf_path, 
            output_path, 
            start_page, 
            end_page, 
            dpi, 
            save_images, 
            max_workers
        )
        file_time = time.time() - file_start_time
        total_time += file_time
        
        if result:
            successful += 1
        else:
            failed += 1
    
    # Summary
    batch_time = time.time() - start_batch_time
    print(f"\n{'='*80}")
    print(f"Batch processing complete")
    print(f"{'='*80}")
    print(f"Files processed: {successful + failed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Total time including overhead: {batch_time:.2f} seconds")

def process_directory(directory_path, output_dir=None, pattern="*.pdf", **kwargs):
    """Process all PDF files in a directory"""
    # Find all PDF files in the directory
    search_path = os.path.join(directory_path, pattern)
    file_list = glob.glob(search_path)
    
    if not file_list:
        print(f"No files matching {pattern} found in {directory_path}")
        return False
    
    print(f"Found {len(file_list)} files matching {pattern} in {directory_path}")
    
    # Process the files
    batch_process(file_list, output_dir=output_dir, **kwargs)
    return True 