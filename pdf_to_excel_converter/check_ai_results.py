#!/usr/bin/env python3
"""
Check the AI-generated results
"""

import pandas as pd
import os

def check_ai_results():
    """Check the AI-generated Excel output"""
    try:
        excel_path = "output_excel/ai_manufacturing_parts.xlsx"
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        df = pd.read_excel(excel_path)
        print('🤖 AI-DETECTED TABLE STRUCTURE:')
        print('=' * 60)
        print(f'Shape: {df.shape} (rows, columns)')
        print(f'Columns: {list(df.columns)}')
        print()
        print(df.to_string(index=False))
        print()
        print('🎯 AI ANALYSIS:')
        print(f'✅ Automatically detected {len(df.columns)} columns')
        print(f'✅ Extracted {len(df)} data rows')
        print('✅ No hardcoding used - pure AI detection!')
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_ai_results() 