#!/usr/bin/env python3
"""
Debug script to see all extracted OCR text with positions
"""

import pandas as pd
import os

def debug_ocr_results():
    """Show all OCR results to understand the table structure"""
    try:
        excel_path = "output_excel/extracted_data.xlsx"
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        df = pd.read_excel(excel_path)
        print(f"Total extracted text elements: {len(df)}")
        print("\nAll extracted text:")
        print("=" * 50)
        
        for i, row in df.iterrows():
            text = row['Text']
            confidence = row['Confidence']
            print(f"{i+1:2d}. '{text}' (conf: {confidence:.3f})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ocr_results() 