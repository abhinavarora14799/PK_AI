#!/usr/bin/env python3
"""
OCR processor using EasyOCR instead of PaddleOCR for better stability on macOS.
"""

import os
import gc
import logging
import traceback
import easyocr
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional

from config import OCR_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        self.reader = None
        self._initialize_ocr()

    def _initialize_ocr(self):
        """Initialize EasyOCR with error handling"""
        try:
            print("[*] Initializing EasyOCR...")
            # Initialize EasyOCR reader
            # EasyOCR supports many languages, 'en' for English
            self.reader = easyocr.Reader(['en'], gpu=OCR_CONFIG.get("use_gpu", False))
            print("[*] EasyOCR initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize EasyOCR: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise

    def process_image(self, image_path: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Performs text recognition on a given image using EasyOCR.
        
        Note: EasyOCR doesn't have built-in table detection like PaddleOCR,
        so we'll focus on text extraction and return empty table results.

        Args:
            image_path (str): The path to the input image file.

        Returns:
            Tuple[List[Dict], List[Dict]]: A tuple containing:
                - List of text detection/recognition results (each dict has 'bbox' and 'text').
                - List of table detection/structure results (empty for EasyOCR).
        """
        print(f"[*] Processing image for OCR: {os.path.basename(image_path)}")
        
        # Validate input
        if not os.path.exists(image_path):
            print(f"[ERROR] Image file not found: {image_path}")
            return [], []
        
        text_results = []
        table_results = []  # EasyOCR doesn't do table structure recognition
        
        try:
            # Process text OCR with error handling
            text_results = self._process_text_ocr(image_path)
            
            # Force garbage collection to free memory
            gc.collect()
            
        except Exception as e:
            print(f"[ERROR] OCR processing failed for {image_path}: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            # Return empty results instead of crashing
            return [], []

        print(f"    - Found {len(text_results)} text elements.")
        print(f"    - Found {len(table_results)} tables (table detection not supported by EasyOCR).")
        return text_results, table_results

    def _process_text_ocr(self, image_path: str) -> List[Dict]:
        """Process text OCR with EasyOCR"""
        text_results = []
        try:
            print(f"    - Running text OCR with EasyOCR...")
            
            # Read text from image
            results = self.reader.readtext(image_path)
            
            # Convert EasyOCR results to our format
            for result in results:
                try:
                    if len(result) >= 3:
                        # EasyOCR returns: (bbox, text, confidence)
                        bbox_coords = result[0]  # List of 4 coordinate pairs
                        text = result[1]
                        confidence = result[2]
                        
                        # Convert bbox format to match our expected format
                        # EasyOCR bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        bbox = [
                            [int(coord) for coord in bbox_coords[0]],  # top-left
                            [int(coord) for coord in bbox_coords[1]],  # top-right
                            [int(coord) for coord in bbox_coords[2]],  # bottom-right
                            [int(coord) for coord in bbox_coords[3]]   # bottom-left
                        ]
                        
                        text_results.append({
                            "bbox": bbox,
                            "text": text,
                            "confidence": confidence
                        })
                        
                except Exception as e:
                    print(f"    [WARNING] Failed to process text result: {e}")
                    continue
                    
        except Exception as e:
            print(f"    [ERROR] Text OCR failed: {e}")
            
        return text_results

    def __del__(self):
        """Cleanup method to ensure proper resource deallocation"""
        try:
            if hasattr(self, 'reader'):
                del self.reader
            gc.collect()
        except:
            pass

def test_easyocr():
    """Test function for EasyOCR"""
    print("Testing EasyOCR setup...")
    
    try:
        ocr_processor = OCRProcessor()
        
        # Check if we have an image to test with
        image_path = "temp_images/page_1.png"
        if not os.path.exists(image_path):
            print(f"Test image not found: {image_path}")
            return False
            
        print(f"Testing OCR on: {image_path}")
        
        # Run OCR
        text_results, table_results = ocr_processor.process_image(image_path)
        
        if text_results:
            print(f"OCR successful! Found {len(text_results)} text elements.")
            
            # Print first few results
            for i, result in enumerate(text_results[:5]):  # Show first 5 results
                text = result.get('text', '')
                confidence = result.get('confidence', 0)
                print(f"  {i+1}. Text: '{text}' (Confidence: {confidence:.3f})")
            
            return True
        else:
            print("OCR completed but no text found.")
            return False
            
    except Exception as e:
        print(f"Error during OCR test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_easyocr()
    if success:
        print("\n✅ EasyOCR test passed!")
        sys.exit(0)
    else:
        print("\n❌ EasyOCR test failed!")
        sys.exit(1) 