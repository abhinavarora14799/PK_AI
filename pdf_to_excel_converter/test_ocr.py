#!/usr/bin/env python3
"""
Simple test script to verify PaddleOCR is working correctly.
"""

import os
import sys
from paddleocr import PaddleOCR

def test_ocr():
    """Test OCR functionality with a simple setup"""
    print("Testing PaddleOCR setup...")
    
    try:
        # Initialize with minimal configuration
        print("Initializing PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("PaddleOCR initialized successfully!")
        
        # Check if we have an image to test with
        image_path = "temp_images/page_1.png"
        if not os.path.exists(image_path):
            print(f"Test image not found: {image_path}")
            return False
            
        print(f"Testing OCR on: {image_path}")
        
        # Run OCR
        result = ocr.ocr(image_path)
        
        if result and len(result) > 0 and result[0]:
            print(f"OCR successful! Found {len(result[0])} text elements.")
            
            # Print first few results
            for i, line in enumerate(result[0][:5]):  # Show first 5 results
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                    confidence = line[1][1] if isinstance(line[1], (list, tuple)) and len(line[1]) > 1 else "N/A"
                    print(f"  {i+1}. Text: '{text}' (Confidence: {confidence})")
            
            return True
        else:
            print("OCR completed but no text found.")
            return False
            
    except Exception as e:
        print(f"Error during OCR test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ocr()
    if success:
        print("\n✅ OCR test passed!")
        sys.exit(0)
    else:
        print("\n❌ OCR test failed!")
        sys.exit(1) 