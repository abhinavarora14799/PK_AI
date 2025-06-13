#!/usr/bin/env python3
"""
Preview the contents of the generated Excel file.
"""

import pandas as pd
import os

def preview_excel(excel_path):
    """Preview the Excel file contents"""
    try:
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        print(f"Reading Excel file: {excel_path}")
        
        # Read all sheets
        excel_file = pd.ExcelFile(excel_path)
        print(f"Found {len(excel_file.sheet_names)} sheet(s): {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n=== Sheet: {sheet_name} ===")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"Shape: {df.shape} (rows, columns)")
            print(f"Columns: {list(df.columns)}")
            
            print("\nFirst 10 rows:")
            print(df.head(10).to_string(index=False))
            
            if len(df) > 10:
                print(f"\n... and {len(df) - 10} more rows")
                
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    excel_path = "output_excel/extracted_data.xlsx"
    preview_excel(excel_path) 