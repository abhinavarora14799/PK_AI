# Functions for OCR processing # ocr_processor.py
import os
import gc
import logging
import traceback
from paddleocr import PaddleOCR
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional

from config import OCR_CONFIG

# Set up a specific logger for PaddleOCR to control its output
# This prevents it from flooding the console with info-level messages
# You can adjust the level (e.g., logging.DEBUG) and log file path as needed
logging.getLogger("ppocr").setLevel(logging.ERROR)
# To save to a file instead, you could use:
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s: %(message)s',
#     filename='paddleocr.log',
#     filemode='a'
# )

class OCRProcessor:
    def __init__(self):
        self.ocr_text = None
        self.ocr_table = None
        self._initialize_ocr()

    def _initialize_ocr(self):
        """Initialize OCR models with error handling"""
        try:
            print("[*] Initializing OCR models...")
            # Initialize PaddleOCR for text detection and recognition
            self.ocr_text = PaddleOCR(
                lang=OCR_CONFIG["lang"],
                use_angle_cls=OCR_CONFIG["use_angle_cls"],
            )
            print("[*] Text OCR model initialized successfully")
            
            # Initialize PaddleOCR for table recognition (structure only)
            # The new API is more streamlined. We specify the table pipeline
            # through other configurations, not these boolean flags.
            self.ocr_table = PaddleOCR(
                lang=OCR_CONFIG["lang"],
            )
            print("[*] Table OCR model initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize OCR models: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise

    def process_image(self, image_path: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Performs text and table recognition on a given image with robust error handling.

        Args:
            image_path (str): The path to the input image file.

        Returns:
            Tuple[List[Dict], List[Dict]]: A tuple containing:
                - List of text detection/recognition results (each dict has 'bbox' and 'text').
                - List of table detection/structure results (each dict has 'bbox' and 'rec_res' (HTML)).
        """
        print(f"[*] Processing image for OCR: {os.path.basename(image_path)}")
        
        # Validate input
        if not os.path.exists(image_path):
            print(f"[ERROR] Image file not found: {image_path}")
            return [], []
        
        text_results = []
        table_results = []
        
        try:
            # Process text OCR with error handling
            text_results = self._process_text_ocr(image_path)
            
            # Force garbage collection to free memory
            gc.collect()
            
            # Process table OCR with error handling
            table_results = self._process_table_ocr(image_path)
            
            # Force garbage collection again
            gc.collect()
            
        except Exception as e:
            print(f"[ERROR] OCR processing failed for {image_path}: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            # Return empty results instead of crashing
            return [], []

        print(f"    - Found {len(text_results)} text lines.")
        print(f"    - Found {len(table_results)} tables.")
        return text_results, table_results

    def _process_text_ocr(self, image_path: str) -> List[Dict]:
        """Process text OCR with error handling"""
        text_results = []
        try:
            print(f"    - Running text OCR...")
            # Perform general text OCR (detection and recognition)
            text_results_raw = self.ocr_text.ocr(image_path)
            
            # Flatten the result structure
            if text_results_raw and len(text_results_raw) > 0 and text_results_raw[0]:
                for line in text_results_raw[0]:
                    try:
                        if line and len(line) >= 2:
                            # Extract bounding box coordinates
                            bbox_coords = line[0]
                            if len(bbox_coords) >= 4:
                                bbox = [
                                    [int(p) for p in bbox_coords[0]],
                                    [int(p) for p in bbox_coords[1]],
                                    [int(p) for p in bbox_coords[2]],
                                    [int(p) for p in bbox_coords[3]]
                                ]
                                
                                # Extract text and confidence
                                text_info = line[1]
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text = text_info[0]
                                    confidence = text_info[1]
                                    text_results.append({
                                        "bbox": bbox, 
                                        "text": text, 
                                        "confidence": confidence
                                    })
                    except Exception as e:
                        print(f"    [WARNING] Failed to process text line: {e}")
                        continue
                        
        except Exception as e:
            print(f"    [ERROR] Text OCR failed: {e}")
            
        return text_results

    def _process_table_ocr(self, image_path: str) -> List[Dict]:
        """Process table OCR with error handling"""
        table_results = []
        try:
            print(f"    - Running table OCR...")
            # Perform table recognition
            table_results_raw = self.ocr_table.ocr(image_path)
            
            # Flatten the result structure for tables
            if table_results_raw and len(table_results_raw) > 0 and table_results_raw[0]:
                for item in table_results_raw[0]:
                    try:
                        # PaddleOCR table results can have different formats.
                        # We're interested in the 'rec_res' which contains the HTML table structure.
                        if isinstance(item, dict) and 'rec_res' in item:
                            if isinstance(item['rec_res'], str) and '<table>' in item['rec_res']:
                                # Extract table bounding box
                                if 'box' in item and len(item['box']) >= 4:
                                    table_bbox = [
                                        [int(p) for p in item['box'][0]],
                                        [int(p) for p in item['box'][1]],
                                        [int(p) for p in item['box'][2]],
                                        [int(p) for p in item['box'][3]]
                                    ]
                                    table_html = item['rec_res']
                                    table_results.append({
                                        "bbox": table_bbox, 
                                        "html": table_html
                                    })
                    except Exception as e:
                        print(f"    [WARNING] Failed to process table item: {e}")
                        continue
                        
        except Exception as e:
            print(f"    [ERROR] Table OCR failed: {e}")
            
        return table_results

    def __del__(self):
        """Cleanup method to ensure proper resource deallocation"""
        try:
            if hasattr(self, 'ocr_text'):
                del self.ocr_text
            if hasattr(self, 'ocr_table'):
                del self.ocr_table
            gc.collect()
        except:
            pass

if __name__ == '__main__':
    # Example usage
    # You need a sample image with handwritten text and a table for good testing.
    # For a quick test, you can use a blank image or an image from pdf_processor.py output.
    # Ensure you have an image file named 'temp_images/page_1.png'
    # if not os.path.exists(TEMP_IMAGE_DIR):
    #     os.makedirs(TEMP_IMAGE_DIR)
    # Image.new('RGB', (800, 600), color = 'white').save(os.path.join(TEMP_IMAGE_DIR, 'test_image.png'))

    # ocr_proc = OCRProcessor()
    # text_res, table_res = ocr_proc.process_image(os.path.join(TEMP_IMAGE_DIR, 'test_image.png'))
    # print("\nText Results (first 3):")
    # for t in text_res[:3]:
    #     print(t)
    # print("\nTable Results (first 1):")
    # for t in table_res[:1]:
    #     print(t['html'][:200] + '...' if len(t['html']) > 200 else t['html'])
    pass