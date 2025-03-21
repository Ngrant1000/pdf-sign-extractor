import os
import sys
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

# Path to Poppler binaries
POPPLER_PATH = None  # Set this to your Poppler path if it's not in PATH

def preprocess_image(image):
    """Apply image preprocessing to improve OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Noise removal
    denoised = cv2.medianBlur(binary, 3)
    
    return Image.fromarray(denoised)

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """Extract text from PDF using OCR"""
    try:
        # Convert PDF to images
        print(f"Converting PDF to images: {pdf_path}")
        
        # Check if Poppler path is provided
        if POPPLER_PATH and os.path.exists(POPPLER_PATH):
            print(f"Using Poppler from: {POPPLER_PATH}")
            images = convert_from_path(
                pdf_path, 
                first_page=start_page, 
                last_page=end_page,
                poppler_path=POPPLER_PATH
            )
        else:
            print("Using Poppler from system PATH")
            images = convert_from_path(
                pdf_path, 
                first_page=start_page, 
                last_page=end_page
            )
        
        print(f"Total pages: {len(images)}")
        all_text = ""
        
        # Process each page
        for i, image in enumerate(images):
            print(f"Processing page {i + start_page}...")
            
            # Preprocess the image
            processed_image = preprocess_image(image)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image)
            all_text += f"\n\n--- PAGE {i + start_page} ---\n\n"
            all_text += text
            
        return all_text
    
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def save_text_to_file(text, output_path):
    """Save extracted text to a file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved to {output_path}") 