import os
import unittest
from ocr.core.processor import preprocess_image
from ocr.core.utils import ensure_dir, get_output_path
from PIL import Image
import numpy as np

class TestCoreUtils(unittest.TestCase):
    
    def test_ensure_dir(self):
        """Test directory creation"""
        test_dir = "test_output_dir"
        ensure_dir(test_dir)
        self.assertTrue(os.path.exists(test_dir))
        
        # Clean up
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
    
    def test_get_output_path(self):
        """Test output path generation"""
        pdf_path = "test.pdf"
        
        # Default path
        default_path = get_output_path(pdf_path)
        self.assertEqual(default_path, "test.txt")
        
        # With custom output path
        custom_path = get_output_path(pdf_path, output_path="custom.txt")
        self.assertEqual(custom_path, "custom.txt")
        
        # With output directory
        dir_path = get_output_path(pdf_path, output_dir="output_dir")
        self.assertEqual(dir_path, os.path.join("output_dir", "test.txt"))
        
        # Clean up
        if os.path.exists("output_dir"):
            os.rmdir("output_dir")

class TestImageProcessing(unittest.TestCase):
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create a simple test image
        test_img = Image.new("RGB", (100, 100), color="white")
        
        # Draw some text
        from PIL import ImageDraw
        draw = ImageDraw.Draw(test_img)
        draw.text((10, 40), "Test", fill="black")
        
        # Process the image
        processed = preprocess_image(test_img)
        
        # Check that we got back a PIL Image
        self.assertIsInstance(processed, Image.Image)
        
        # Check dimensions are preserved
        self.assertEqual(processed.size, test_img.size)

if __name__ == "__main__":
    unittest.main() 