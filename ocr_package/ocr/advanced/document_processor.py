import os
import sys
import time
import json
import io
import numpy as np
import cv2
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# Check if transformers is available, otherwise we'll use a simpler approach
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Optional: OpenAI API for advanced understanding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
USE_OPENAI = bool(OPENAI_API_KEY)

@dataclass
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int
    text: str = ""
    confidence: float = 0.0
    element_type: str = "unknown"

@dataclass
class TableCell:
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    text: str = ""
    bounding_box: Optional[BoundingBox] = None

@dataclass
class Table:
    cells: List[TableCell] = field(default_factory=list)
    rows: int = 0
    cols: int = 0
    position: Optional[BoundingBox] = None
    
    def to_markdown(self):
        """Convert table to markdown format"""
        if not self.cells or not self.rows or not self.cols:
            return ""
        
        # Initialize grid
        grid = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Fill in grid with cell data
        for cell in self.cells:
            if 0 <= cell.row < self.rows and 0 <= cell.col < self.cols:
                grid[cell.row][cell.col] = cell.text.strip()
        
        # Convert to markdown
        markdown = []
        if grid:
            # Header row
            markdown.append('| ' + ' | '.join(grid[0]) + ' |')
            # Separator
            markdown.append('| ' + ' | '.join(['---' for _ in range(self.cols)]) + ' |')
            # Data rows
            for row in grid[1:]:
                markdown.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(markdown)
    
    def to_dict(self):
        """Convert table to dictionary format"""
        result = []
        if not self.cells or not self.rows or not self.cols:
            return result
        
        # Initialize grid
        grid = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Fill in grid with cell data
        for cell in self.cells:
            if 0 <= cell.row < self.rows and 0 <= cell.col < self.cols:
                grid[cell.row][cell.col] = cell.text.strip()
        
        # Convert to array of objects
        if len(grid) > 1:  # Has header row
            headers = grid[0]
            for row in grid[1:]:
                row_dict = {}
                for i, cell in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = cell
                result.append(row_dict)
        
        return result

@dataclass
class DocumentElement:
    element_type: str  # heading, paragraph, table, list, image, etc.
    text: str = ""
    bounding_box: Optional[BoundingBox] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # For table elements
    table: Optional[Table] = None

@dataclass
class StructuredDocument:
    elements: List[DocumentElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        """Convert to dictionary format"""
        result = {
            "metadata": self.metadata,
            "elements": []
        }
        
        for elem in self.elements:
            element_dict = {
                "type": elem.element_type,
                "text": elem.text,
                "confidence": elem.confidence
            }
            
            if elem.element_type == "table" and elem.table:
                element_dict["table"] = elem.table.to_dict()
            
            # Include metadata
            if elem.metadata:
                element_dict["metadata"] = elem.metadata
            
            result["elements"].append(element_dict)
        
        return result
    
    def to_json(self, indent=2):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

def preprocess_image_for_ocr(img_np):
    """Optimize image for OCR text extraction"""
    # Convert to grayscale if not already
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_np
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Noise removal
    denoised = cv2.medianBlur(binary, 3)
    
    return denoised

def extract_text_with_positions(img_np):
    """
    Extract text from image with position information using Tesseract.
    
    Returns:
        tuple: (text, text_positions)
            text: Full extracted text
            text_positions: List of dictionaries with text position information
    """
    # Convert numpy array to PIL Image for tesseract
    pil_img = Image.fromarray(img_np)
    
    # Get word boxes using tesseract
    boxes = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
    
    # Extract full text
    text = pytesseract.image_to_string(pil_img)
    
    # Create position information for each word
    text_positions = []
    for i in range(len(boxes['text'])):
        # Skip empty text
        if not boxes['text'][i].strip():
            continue
            
        confidence = int(boxes['conf'][i]) if boxes['conf'][i] != '-1' else 0
        
        text_positions.append({
            'text': boxes['text'][i],
            'x': boxes['left'][i],
            'y': boxes['top'][i],
            'width': boxes['width'][i],
            'height': boxes['height'][i],
            'confidence': confidence
        })
    
    return text, text_positions

def process_document(pdf_path, output_path=None, dpi=200, num_workers=None):
    """Process a PDF document with advanced OCR and structure extraction"""
    try:
        # Determine the number of workers based on CPU cores
        if num_workers is None:
            num_workers = max(1, multiprocessing.cpu_count() - 1)
        
        print(f"Processing document: {pdf_path}")
        print(f"Using {num_workers} worker processes, DPI: {dpi}")
        
        # Open the PDF
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        print(f"Total pages: {num_pages}")
        
        # Extract metadata
        metadata = {
            "filename": os.path.basename(pdf_path),
            "page_count": num_pages,
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "producer": doc.metadata.get("producer", ""),
            "creator": doc.metadata.get("creator", "")
        }
        
        # Create structured document
        document = StructuredDocument(metadata=metadata)
        
        # Process pages in parallel
        task_args = [(pdf_path, i, dpi) for i in range(num_pages)]
        
        # Process using multiple workers
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(process_page, task_args))
        
        # Add pages to document in correct order
        for page_elements in results:
            if page_elements:
                document.elements.extend(page_elements)
        
        # Save to output file if specified
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(document.to_json())
            print(f"Document processed and saved to {output_path}")
        
        return document
        
    except Exception as e:
        print(f"Error processing document: {e}")
        return None

def process_page(args):
    """Process a single page of a PDF document"""
    pdf_path, page_num, dpi = args
    
    try:
        # Open the document and get the specific page
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # Render page to an image at specified DPI
        matrix = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to numpy array
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # Process the image
        processed_img = preprocess_image_for_ocr(img)
        
        # Extract elements
        page_elements = extract_elements_from_page(processed_img, page_num)
        
        doc.close()
        return page_elements
        
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        return []

def extract_elements_from_page(img_np, page_num):
    """Extract structured elements from a page image"""
    # Extract text with position information
    text, text_positions = extract_text_with_positions(img_np)
    
    # Create a document element with the page text and position metadata
    elements = [
        DocumentElement(
            element_type="page",
            text=text,
            metadata={
                "page_number": page_num,
                "text_positions": text_positions
            }
        )
    ]
    
    # TODO: Implement more sophisticated element detection (tables, headers, etc.)
    
    return elements 