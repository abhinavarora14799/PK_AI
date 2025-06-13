# Functions for mapping extracted data # data_mapper.py
import pandas as pd
import re
from typing import List, Dict, Any

from config import COLUMN_MAPPINGS

class DataMapper:
    def __init__(self):
        self.column_mappings = COLUMN_MAPPINGS

    def process_ocr_outputs(self, text_results: List[Dict], table_results: List[Dict]) -> List[pd.DataFrame]:
        """
        Process OCR outputs and map them to structured DataFrames.
        
        Args:
            text_results: List of text detection results from OCR
            table_results: List of table detection results from OCR (may be empty for EasyOCR)
            
        Returns:
            List of pandas DataFrames containing structured data
        """
        print("[*] Starting data mapping process...")
        
        if not text_results:
            print("[!] No text results to process")
            return []
        
        # Extract just the text from OCR results
        extracted_texts = [result.get('text', '').strip() for result in text_results if result.get('text', '').strip()]
        
        print(f"[*] Processing {len(extracted_texts)} text elements")
        
        # Try to identify and parse table structure
        dataframes = self._parse_manufacturing_table(extracted_texts)
        
        if not dataframes:
            print("[!] Could not parse table structure, creating fallback table")
            # Create a simple fallback table
            df = pd.DataFrame({
                'Extracted_Text': extracted_texts,
                'Index': range(len(extracted_texts))
            })
            dataframes = [df]
        
        return dataframes

    def _parse_manufacturing_table(self, texts: List[str]) -> List[pd.DataFrame]:
        """
        Parse the manufacturing parts table from OCR text results.
        
        Expected structure:
        - Headers: Part Number, Machine Number, Diameter (mm), Length (cm), Tolerance (mm), Quantity
        - Data rows following the headers
        """
        print("[*] Attempting to parse manufacturing parts table...")
        
        # Define expected column headers and their variations
        header_patterns = {
            'Part Number': ['part', 'number', 'pn'],
            'Machine Number': ['machine', 'number'],
            'Diameter (mm)': ['diameter', 'mm'],
            'Length (cm)': ['length', 'cm'],
            'Tolerance (mm)': ['tolerance', 'mm'],
            'Quantity': ['quantity']
        }
        
        # Find header positions
        header_indices = self._find_headers(texts, header_patterns)
        
        if not header_indices:
            print("[!] Could not identify table headers")
            return []
        
        print(f"[*] Found headers at positions: {header_indices}")
        
        # Find where data starts (after headers and units)
        data_start_idx = max(header_indices.values()) + 1
        
        # Skip unit indicators like "(mm)", "(cm)" that might appear after headers
        while data_start_idx < len(texts) and self._is_unit_indicator(texts[data_start_idx]):
            data_start_idx += 1
        
        print(f"[*] Data starts at index: {data_start_idx}")
        
        # Extract data rows
        data_texts = texts[data_start_idx:]
        
        # Parse data into rows
        rows = self._parse_data_rows(data_texts)
        
        if not rows:
            print("[!] Could not parse any data rows")
            return []
        
        print(f"[*] Parsed {len(rows)} data rows")
        
        # Create DataFrame
        columns = ['Part Number', 'Machine Number', 'Diameter (mm)', 'Length (cm)', 'Tolerance (mm)', 'Quantity']
        df = pd.DataFrame(rows, columns=columns)
        
        # Clean up the data
        df = self._clean_dataframe(df)
        
        print(f"[*] Created DataFrame with shape: {df.shape}")
        return [df]

    def _find_headers(self, texts: List[str], header_patterns: Dict[str, List[str]]) -> Dict[str, int]:
        """Find the positions of table headers in the text list"""
        header_indices = {}
        
        for i, text in enumerate(texts):
            text_lower = text.lower()
            
            for column_name, patterns in header_patterns.items():
                if column_name not in header_indices:  # Only find first occurrence
                    for pattern in patterns:
                        if pattern in text_lower:
                            header_indices[column_name] = i
                            break
        
        return header_indices

    def _is_unit_indicator(self, text: str) -> bool:
        """Check if text is a unit indicator like (mm), (cm), etc."""
        return bool(re.match(r'^\([a-zA-Z]+\)$', text.strip()))

    def _parse_data_rows(self, data_texts: List[str]) -> List[List[str]]:
        """
        Parse data texts into structured rows.
        
        Expected pattern for each row:
        Part Number, Machine Number, Diameter, Length, Tolerance, Quantity
        """
        rows = []
        current_row = []
        
        # Patterns to identify different types of data
        part_number_pattern = r'^PN-[A-Z0-9-]+$'
        machine_number_pattern = r'^M-\d+$'
        number_pattern = r'^\d+\.?\d*$'
        tolerance_pattern = r'^[±+]\d+\.\d+$|^t\d+\.\d+$'
        
        # Clean and preprocess the data
        cleaned_texts = []
        for text in data_texts:
            text = text.strip()
            if not text or 'file://' in text or text in ['II', 'Log']:
                continue
            
            # Fix common OCR errors upfront
            if text == 'ISO':
                text = '150'
            elif text == 'Soo':
                text = '500'
            elif 'IS.' in text:
                text = text.replace('IS.', '15.')
            elif '$' in text:
                text = text.replace('$', '.5')
            elif 'o' in text and text != 'Log' and not re.match(part_number_pattern, text, re.IGNORECASE):
                text = text.replace('o', '0')
            elif '..' in text:
                text = text.replace('..', '.')
            
            cleaned_texts.append(text)
        
        print(f"[DEBUG] Cleaned texts: {cleaned_texts}")
        
        # Group texts into rows of 6 elements each
        # Based on the pattern: PN-xxx, M-xx, diameter, length, tolerance, quantity
        i = 0
        while i < len(cleaned_texts):
            text = cleaned_texts[i]
            
            # Start new row if we find a part number
            if re.match(part_number_pattern, text, re.IGNORECASE):
                if current_row and len(current_row) >= 4:
                    rows.append(self._pad_row(current_row, 6))
                
                # Start new row and try to collect 6 consecutive elements
                current_row = [text]
                
                # Look ahead for the next 5 elements
                for j in range(1, 6):
                    if i + j < len(cleaned_texts):
                        next_text = cleaned_texts[i + j]
                        current_row.append(next_text)
                    else:
                        current_row.append('')  # Fill missing with empty
                
                # Skip the elements we just processed
                i += min(6, len(cleaned_texts) - i)
            else:
                i += 1
        
        # Add the last row if it exists
        if current_row and len(current_row) >= 4:
            rows.append(self._pad_row(current_row, 6))
        
        print(f"[DEBUG] Parsed rows: {rows}")
        return rows

    def _pad_row(self, row: List[str], target_length: int) -> List[str]:
        """Pad row to target length with empty strings"""
        while len(row) < target_length:
            row.append('')
        return row[:target_length]  # Trim if too long

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up the DataFrame by fixing common OCR errors and formatting"""
        
        # Clean up Part Numbers
        df['Part Number'] = df['Part Number'].str.replace('PN-SSI-C', 'PN-551-C', regex=False)
        df['Part Number'] = df['Part Number'].str.replace('PN-I2-D', 'PN-12-D', regex=False)
        
        # Clean up Machine Numbers
        df['Machine Number'] = df['Machine Number'].str.replace('M-0S', 'M-05', regex=False)
        
        # Clean up numeric columns
        for col in ['Diameter (mm)', 'Length (cm)']:
            if col in df.columns:
                df[col] = df[col].str.replace('$', '.5', regex=False)
                df[col] = df[col].str.replace('IS.', '15.', regex=False)
        
        # Clean up Tolerance column
        if 'Tolerance (mm)' in df.columns:
            df['Tolerance (mm)'] = df['Tolerance (mm)'].str.replace('t0.0S', '±0.05', regex=False)
            df['Tolerance (mm)'] = df['Tolerance (mm)'].str.replace('t0.', '±0.', regex=False)
            df['Tolerance (mm)'] = df['Tolerance (mm)'].str.replace('t', '±', regex=False)
        
        # Clean up Quantity column
        if 'Quantity' in df.columns:
            df['Quantity'] = df['Quantity'].str.replace('o', '0', regex=False)
            df['Quantity'] = df['Quantity'].str.replace('Soo', '500', regex=False)
            df['Quantity'] = df['Quantity'].str.replace('ISO', '150', regex=False)
        
        return df

if __name__ == '__main__':
    # Test the data mapper with sample data
    sample_texts = [
        'Manufacturing Parts Log',
        'Part', 'Machine', 'Diameter', 'Length', 'Tolerance', 'Number', 'Number',
        '(mm)', '(cm)', '(mm)', 'Quantity',
        'PN-482-4', 'M-03', '12.5', '30.2', 't0.0S', 'ISO',
        'PN-SSI-C', 'M-03', '8.0', 'IS.7', '+0.02', '320'
    ]
    
    mapper = DataMapper()
    sample_results = [{'text': text} for text in sample_texts]
    dfs = mapper.process_ocr_outputs(sample_results, [])
    
    if dfs:
        print("Sample output:")
        print(dfs[0].to_string(index=False))
    else:
        print("No DataFrames generated")