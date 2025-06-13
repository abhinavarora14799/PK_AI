# Functions for exporting data to Excel # excel_exporter.py
import os
import pandas as pd
from typing import List

from config import OUTPUT_DIR

def export_to_excel(dataframes: List[pd.DataFrame], output_filename: str):
    """
    Exports a list of Pandas DataFrames to a single Excel file, with each DataFrame
    as a separate sheet.

    Args:
        dataframes (List[pd.DataFrame]): A list of DataFrames to export.
        output_filename (str): The desired name for the output Excel file (e.g., "extracted_data.xlsx").
    """
    if not dataframes:
        print("[!] No data to export to Excel.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            sheet_name = f"Table_Page_{i+1}" # Or come up with a more descriptive name
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"[*] Successfully exported {len(dataframes)} tables to '{output_path}'")

if __name__ == '__main__':
    # Example usage
    df1 = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02"],
        "Item Description": ["Item A", "Item B"],
        "Quantity": [1, 2],
        "Total": [10.0, 25.0]
    })
    df2 = pd.DataFrame({
        "Date": ["2023-02-01"],
        "Item Description": ["Another Item"],
        "Quantity": [3],
        "Unit Price": [5.0],
        "Total": [15.0]
    })
    export_to_excel([df1, df2], "test_output.xlsx")