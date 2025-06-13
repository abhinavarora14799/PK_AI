#!/usr/bin/env python3
"""
Check the structured manufacturing parts output
"""

import pandas as pd
import os

def check_structured_output():
    """Check the structured Excel output"""
    try:
        excel_path = "output_excel/manufacturing_parts_structured.xlsx"
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        df = pd.read_excel(excel_path)
        print('Structured Manufacturing Parts Data:')
        print('=' * 60)
        print(f'Shape: {df.shape} (rows, columns)')
        print(f'Columns: {list(df.columns)}')
        print()
        print(df.to_string(index=False))
        print()
        print('Data types:')
        print(df.dtypes)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_structured_output() 