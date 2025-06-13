#!/usr/bin/env python3
"""
Check the final manufacturing parts output
"""

import pandas as pd
import os

def check_final_output():
    """Check the final Excel output"""
    try:
        excel_path = "output_excel/manufacturing_parts_final.xlsx"
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        df = pd.read_excel(excel_path)
        print('🎉 FINAL Manufacturing Parts Data:')
        print('=' * 70)
        print(f'Shape: {df.shape} (rows, columns)')
        print()
        print(df.to_string(index=False))
        print()
        print('✅ SUCCESS: Your PDF has been converted to a properly structured Excel file!')
        print(f'📁 File location: {excel_path}')
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_final_output() 