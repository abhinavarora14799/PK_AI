#!/usr/bin/env python3
"""
AI-Powered Data Mapper for PDF to Excel Conversion
Uses intelligent pattern recognition and machine learning to automatically detect table structures
"""

import pandas as pd
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import difflib
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AIDataMapper:
    def __init__(self):
        self.confidence_threshold = 0.3
        self.min_table_rows = 2
        self.max_columns = 20
        
    def process_ocr_outputs(self, text_results: List[Dict], table_results: List[Dict]) -> List[pd.DataFrame]:
        """
        AI-powered processing of OCR outputs to automatically detect and structure tables.
        
        Args:
            text_results: List of text detection results from OCR
            table_results: List of table detection results from OCR (may be empty for EasyOCR)
            
        Returns:
            List of pandas DataFrames containing structured data
        """
        print("[*] Starting AI-powered data mapping process...")
        
        if not text_results:
            print("[!] No text results to process")
            return []
        
        # Extract text and position information
        text_elements = self._extract_text_elements(text_results)
        
        if len(text_elements) < 5:
            print("[!] Insufficient text elements for table detection")
            return self._create_fallback_table(text_elements)
        
        print(f"[*] Processing {len(text_elements)} text elements with AI")
        
        # Step 1: Detect potential table regions using spatial clustering
        table_regions = self._detect_table_regions(text_elements)
        
        if not table_regions:
            print("[!] No table regions detected, creating fallback")
            return self._create_fallback_table(text_elements)
        
        # Step 2: For each table region, detect structure
        all_dataframes = []
        for i, region in enumerate(table_regions):
            print(f"[*] Processing table region {i+1}/{len(table_regions)}")
            df = self._process_table_region(region)
            if df is not None and not df.empty:
                all_dataframes.append(df)
        
        if not all_dataframes:
            print("[!] No structured tables found, creating fallback")
            return self._create_fallback_table(text_elements)
        
        return all_dataframes

    def _extract_text_elements(self, text_results: List[Dict]) -> List[Dict]:
        """Extract text elements with position and confidence information"""
        elements = []
        
        for result in text_results:
            text = result.get('text', '').strip()
            if not text:
                continue
                
            bbox = result.get('bbox', [])
            confidence = result.get('confidence', 1.0)
            
            # Calculate center position for clustering
            if bbox and len(bbox) >= 4:
                # Handle different bbox formats
                if isinstance(bbox[0], list):  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                else:  # [x1, y1, x2, y2] or similar
                    x_coords = [bbox[0], bbox[2]] if len(bbox) >= 4 else [0, 0]
                    y_coords = [bbox[1], bbox[3]] if len(bbox) >= 4 else [0, 0]
                
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
            else:
                center_x, center_y = 0, 0
            
            elements.append({
                'text': text,
                'x': center_x,
                'y': center_y,
                'confidence': confidence,
                'bbox': bbox
            })
        
        # Sort by y-coordinate (top to bottom), then x-coordinate (left to right)
        elements.sort(key=lambda e: (e['y'], e['x']))
        
        return elements

    def _detect_table_regions(self, text_elements: List[Dict]) -> List[List[Dict]]:
        """Use spatial clustering to detect potential table regions"""
        if len(text_elements) < 5:
            return [text_elements]
        
        # Extract positions for clustering
        positions = np.array([[elem['x'], elem['y']] for elem in text_elements])
        
        # Use DBSCAN clustering to group spatially close elements
        clustering = DBSCAN(eps=50, min_samples=3).fit(positions)
        labels = clustering.labels_
        
        # Group elements by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            if label != -1:  # -1 is noise in DBSCAN
                clusters[label].append(text_elements[i])
        
        # Filter clusters that might be tables (have enough elements)
        table_regions = []
        for cluster_elements in clusters.values():
            if len(cluster_elements) >= self.min_table_rows * 2:  # At least 2 rows with some columns
                # Sort elements within cluster
                cluster_elements.sort(key=lambda e: (e['y'], e['x']))
                table_regions.append(cluster_elements)
        
        # If no good clusters found, treat all elements as one region
        if not table_regions:
            table_regions = [text_elements]
        
        return table_regions

    def _process_table_region(self, elements: List[Dict]) -> Optional[pd.DataFrame]:
        """Process a table region to extract structured data"""
        print(f"    - Processing region with {len(elements)} elements")
        
        # Step 1: Detect headers using AI techniques
        headers = self._detect_headers_ai(elements)
        
        if not headers:
            print("    - No headers detected")
            return None
        
        print(f"    - Detected headers: {[h['text'] for h in headers]}")
        
        # Step 2: Detect rows and columns structure
        table_structure = self._detect_table_structure(elements, headers)
        
        if not table_structure or len(table_structure) < self.min_table_rows:
            print("    - Insufficient table structure detected")
            return None
        
        # Step 3: Create DataFrame
        df = self._create_dataframe_from_structure(table_structure, headers)
        
        # Step 4: Clean and validate data
        df = self._clean_dataframe_ai(df)
        
        print(f"    - Created DataFrame with shape: {df.shape}")
        return df

    def _detect_headers_ai(self, elements: List[Dict]) -> List[Dict]:
        """Use AI techniques to detect table headers"""
        if len(elements) < 3:
            return []
        
        # Strategy 1: Look for elements that appear to be headers based on content
        header_candidates = []
        
        for elem in elements:
            text = elem['text'].lower()
            
            # Check if text looks like a header
            header_score = 0
            
            # Common header patterns
            header_patterns = [
                r'\b(number|no|id|code)\b',
                r'\b(name|description|item|product)\b',
                r'\b(quantity|qty|amount|count)\b',
                r'\b(price|cost|rate|value)\b',
                r'\b(date|time|when)\b',
                r'\b(size|dimension|length|width|height|diameter)\b',
                r'\b(tolerance|precision|accuracy)\b',
                r'\b(machine|equipment|device)\b',
                r'\b(part|component|element)\b',
                r'\b(total|sum|subtotal)\b'
            ]
            
            for pattern in header_patterns:
                if re.search(pattern, text):
                    header_score += 1
            
            # Check for units in parentheses
            if re.search(r'\([a-zA-Z]+\)', text):
                header_score += 0.5
            
            # Prefer shorter texts for headers
            if len(text.split()) <= 3:
                header_score += 0.3
            
            # Check if it's likely a data value (numbers, codes)
            if re.match(r'^[A-Z0-9-]+$', elem['text']) or re.match(r'^\d+\.?\d*$', elem['text']):
                header_score -= 1
            
            if header_score > 0:
                elem['header_score'] = header_score
                header_candidates.append(elem)
        
        if not header_candidates:
            # Fallback: use first row as headers
            first_row_y = elements[0]['y']
            tolerance = 20  # pixels
            first_row = [e for e in elements if abs(e['y'] - first_row_y) < tolerance]
            return sorted(first_row, key=lambda e: e['x'])
        
        # Strategy 2: Group candidates by y-coordinate to find header row
        header_candidates.sort(key=lambda e: (-e['header_score'], e['y'], e['x']))
        
        # Find the y-coordinate with the most header candidates
        y_groups = defaultdict(list)
        for candidate in header_candidates:
            y_rounded = round(candidate['y'] / 20) * 20  # Group by 20-pixel intervals
            y_groups[y_rounded].append(candidate)
        
        # Select the group with highest total score
        best_group = max(y_groups.values(), key=lambda group: sum(e['header_score'] for e in group))
        
        return sorted(best_group, key=lambda e: e['x'])

    def _detect_table_structure(self, elements: List[Dict], headers: List[Dict]) -> List[List[Dict]]:
        """Detect table structure (rows and columns) using AI"""
        if not headers:
            return []
        
        # Get header y-coordinate
        header_y = headers[0]['y']
        tolerance = 30  # pixels
        
        # Filter out header elements and elements above headers
        data_elements = [e for e in elements if e['y'] > header_y + tolerance]
        
        if not data_elements:
            return []
        
        # Filter out obvious non-data elements
        filtered_elements = []
        for elem in data_elements:
            text = elem['text'].strip()
            # Skip file paths, single characters that are likely noise, etc.
            if ('file://' in text or 
                text in ['II', 'Log', 'NaN'] or 
                (len(text) <= 2 and not text.isalnum())):
                continue
            filtered_elements.append(elem)
        
        data_elements = filtered_elements
        
        # Group elements into rows based on y-coordinate with improved clustering
        rows = []
        current_row = []
        current_y = None
        
        for elem in sorted(data_elements, key=lambda e: (e['y'], e['x'])):
            if current_y is None:
                current_y = elem['y']
                current_row = [elem]
            elif abs(elem['y'] - current_y) < tolerance:
                current_row.append(elem)
            else:
                if current_row and len(current_row) >= 2:  # Only keep rows with multiple elements
                    rows.append(sorted(current_row, key=lambda e: e['x']))
                current_row = [elem]
                current_y = elem['y']
        
        # Add the last row
        if current_row and len(current_row) >= 2:
            rows.append(sorted(current_row, key=lambda e: e['x']))
        
        # Improved column alignment with headers
        aligned_rows = []
        header_x_positions = [h['x'] for h in headers]
        
        for row in rows:
            aligned_row = [None] * len(headers)
            used_positions = set()
            
            # First pass: exact matches and very close matches
            for elem in row:
                distances = [abs(elem['x'] - hx) for hx in header_x_positions]
                min_distance = min(distances)
                closest_col = distances.index(min_distance)
                
                # Only assign if reasonably close and position not used
                if min_distance < 80 and closest_col not in used_positions:
                    aligned_row[closest_col] = elem
                    used_positions.add(closest_col)
            
            # Second pass: assign remaining elements to empty columns
            unassigned_elements = [elem for elem in row if elem not in aligned_row]
            empty_columns = [i for i, cell in enumerate(aligned_row) if cell is None]
            
            for elem, col_idx in zip(unassigned_elements, empty_columns):
                aligned_row[col_idx] = elem
            
            # Only keep rows with at least half the columns filled
            filled_columns = sum(1 for cell in aligned_row if cell is not None)
            if filled_columns >= len(headers) // 2:
                aligned_rows.append(aligned_row)
        
        return aligned_rows

    def _create_dataframe_from_structure(self, table_structure: List[List[Dict]], headers: List[Dict]) -> pd.DataFrame:
        """Create DataFrame from detected table structure"""
        # Create column names
        column_names = []
        for header in headers:
            col_name = header['text'].strip()
            # Clean up column name
            col_name = re.sub(r'\s+', ' ', col_name)
            column_names.append(col_name)
        
        # Create data rows
        data_rows = []
        for row in table_structure:
            data_row = []
            for cell in row:
                if cell is not None:
                    data_row.append(cell['text'].strip())
                else:
                    data_row.append('')
            data_rows.append(data_row)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=column_names)
        
        return df

    def _clean_dataframe_ai(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced AI-powered data cleaning"""
        if df.empty:
            return df
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        df = df[~(df == '').all(axis=1)]
        
        # Remove rows that are likely header repetitions or units
        rows_to_remove = []
        for idx, row in df.iterrows():
            row_text = ' '.join(str(val) for val in row.values if pd.notna(val) and str(val).strip())
            
            # Check if row contains only units or header-like text
            if (any(unit in row_text.lower() for unit in ['(mm)', '(cm)', '(in)', 'number']) or
                row_text.lower().strip() in ['number', 'part', 'machine', 'diameter', 'length', 'tolerance', 'quantity']):
                rows_to_remove.append(idx)
        
        df = df.drop(rows_to_remove)
        df = df.reset_index(drop=True)
        
        # Auto-detect and clean data types for each column
        for col in df.columns:
            df[col] = self._clean_column_ai(df[col])
        
        # Final cleanup: remove rows that are still mostly empty after cleaning
        df = df.dropna(thresh=len(df.columns)//2)  # Keep rows with at least half non-null values
        
        return df

    def _clean_column_ai(self, series: pd.Series) -> pd.Series:
        """AI-powered column cleaning"""
        # Remove empty values for analysis
        non_empty = series[series.str.strip() != ''].dropna()
        
        if len(non_empty) == 0:
            return series
        
        # Detect column type and apply appropriate cleaning
        column_type = self._detect_column_type(non_empty)
        
        if column_type == 'numeric':
            return self._clean_numeric_column(series)
        elif column_type == 'code':
            return self._clean_code_column(series)
        elif column_type == 'tolerance':
            return self._clean_tolerance_column(series)
        else:
            return self._clean_text_column(series)

    def _detect_column_type(self, series: pd.Series) -> str:
        """Detect the type of data in a column"""
        sample_values = series.head(10).tolist()
        
        # Check for numeric values
        numeric_count = 0
        code_count = 0
        tolerance_count = 0
        
        for value in sample_values:
            value_str = str(value).strip()
            
            # Check for tolerance patterns
            if re.match(r'^[±+]\d+\.\d+$|^t\d+\.\d+$', value_str):
                tolerance_count += 1
            # Check for code patterns (letters and numbers with dashes)
            elif re.match(r'^[A-Z0-9-]+$', value_str) and any(c.isalpha() for c in value_str):
                code_count += 1
            # Check for numeric patterns
            elif re.match(r'^\d+\.?\d*$', value_str.replace(',', '')):
                numeric_count += 1
        
        total = len(sample_values)
        if tolerance_count / total > 0.5:
            return 'tolerance'
        elif code_count / total > 0.5:
            return 'code'
        elif numeric_count / total > 0.5:
            return 'numeric'
        else:
            return 'text'

    def _clean_numeric_column(self, series: pd.Series) -> pd.Series:
        """Clean numeric column with OCR error correction"""
        def clean_numeric(value):
            if pd.isna(value) or value == '':
                return value
            
            value_str = str(value).strip()
            
            # Common OCR errors in numbers
            corrections = {
                'O': '0', 'o': '0', 'I': '1', 'l': '1', 'S': '5', 's': '5',
                'G': '6', 'B': '8', 'g': '9', '$': '.5', '..': '.'
            }
            
            for error, correction in corrections.items():
                value_str = value_str.replace(error, correction)
            
            # Handle special cases
            if value_str == 'ISO':
                return '150'
            elif value_str == 'Soo':
                return '500'
            
            return value_str
        
        return series.apply(clean_numeric)

    def _clean_code_column(self, series: pd.Series) -> pd.Series:
        """Clean code/ID column with OCR error correction"""
        def clean_code(value):
            if pd.isna(value) or value == '':
                return value
            
            value_str = str(value).strip()
            
            # Common OCR errors in codes
            corrections = {
                'SSI': '551',  # Common OCR error
                'I2': '12',    # I mistaken for 1
                '0S': '05',    # 0 and S confusion
            }
            
            for error, correction in corrections.items():
                value_str = value_str.replace(error, correction)
            
            return value_str
        
        return series.apply(clean_code)

    def _clean_tolerance_column(self, series: pd.Series) -> pd.Series:
        """Clean tolerance column with proper formatting"""
        def clean_tolerance(value):
            if pd.isna(value) or value == '':
                return value
            
            value_str = str(value).strip()
            
            # Convert 't' prefix to '±'
            if value_str.startswith('t'):
                value_str = '±' + value_str[1:]
            
            # Fix common OCR errors
            value_str = value_str.replace('0S', '05')
            
            return value_str
        
        return series.apply(clean_tolerance)

    def _clean_text_column(self, series: pd.Series) -> pd.Series:
        """Clean text column"""
        def clean_text(value):
            if pd.isna(value) or value == '':
                return value
            
            # Basic text cleaning
            return str(value).strip()
        
        return series.apply(clean_text)

    def _create_fallback_table(self, text_elements: List[Dict]) -> List[pd.DataFrame]:
        """Create a fallback table when structure detection fails"""
        if not text_elements:
            return []
        
        texts = [elem['text'] for elem in text_elements]
        confidences = [elem.get('confidence', 1.0) for elem in text_elements]
        
        df = pd.DataFrame({
            'Extracted_Text': texts,
            'Confidence': confidences,
            'Position_X': [elem['x'] for elem in text_elements],
            'Position_Y': [elem['y'] for elem in text_elements]
        })
        
        return [df]

# Test the AI data mapper
if __name__ == '__main__':
    # Test with sample data
    sample_text_results = [
        {'text': 'Manufacturing Parts Log', 'bbox': [[100, 50], [300, 50], [300, 70], [100, 70]], 'confidence': 0.9},
        {'text': 'Part Number', 'bbox': [[50, 100], [150, 100], [150, 120], [50, 120]], 'confidence': 0.95},
        {'text': 'Machine Number', 'bbox': [[160, 100], [260, 100], [260, 120], [160, 120]], 'confidence': 0.93},
        {'text': 'Diameter (mm)', 'bbox': [[270, 100], [370, 100], [370, 120], [270, 120]], 'confidence': 0.91},
        {'text': 'PN-482-4', 'bbox': [[50, 140], [150, 140], [150, 160], [50, 160]], 'confidence': 0.88},
        {'text': 'M-03', 'bbox': [[160, 140], [260, 140], [260, 160], [160, 160]], 'confidence': 0.92},
        {'text': '12.5', 'bbox': [[270, 140], [370, 140], [370, 160], [270, 160]], 'confidence': 0.85},
    ]
    
    mapper = AIDataMapper()
    dfs = mapper.process_ocr_outputs(sample_text_results, [])
    
    if dfs:
        print("AI-Generated Table:")
        print(dfs[0].to_string(index=False))
    else:
        print("No tables generated") 