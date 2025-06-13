#!/usr/bin/env python3
"""
AI-Powered PDF to Excel Converter
Fully automated, robust solution that can handle any PDF document structure
"""

import os
import gc
import sys
import shutil
import argparse
import traceback

from pdf_processor import process_pdf
from ocr_processor_easyocr import OCRProcessor
from data_mapper_ai import AIDataMapper  # Use AI-powered data mapper
from excel_exporter import export_to_excel
from config import TEMP_IMAGE_DIR, OUTPUT_DIR

def run_ai_extraction(pdf_path: str, output_excel_filename: str):
    """
    AI-powered PDF to Excel conversion that automatically detects table structures.
    """
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return False

    print(f"\n===== AI-Powered PDF to Excel Conversion =====")
    print(f"📄 Processing: '{pdf_path}'")
    print("🤖 Using AI for automatic table structure detection")
    print("🔍 No hardcoding - fully adaptive to any document structure")

    try:
        # 1. Process PDF to Images
        print("\n[Step 1/4] Converting PDF to images...")
        image_paths = process_pdf(pdf_path)
        if not image_paths:
            print("[!] No images generated from PDF. Exiting.")
            return False

        # 2. Perform OCR on Images
        print("\n[Step 2/4] Performing OCR (text recognition) on images...")
        ocr_processor = None
        all_extracted_data = []
        
        try:
            ocr_processor = OCRProcessor()
            
            for i, img_path in enumerate(image_paths):
                print(f"    Processing image {i+1}/{len(image_paths)}: {os.path.basename(img_path)}")
                
                try:
                    text_results, table_results = ocr_processor.process_image(img_path)
                    all_extracted_data.append({
                        "image_path": img_path,
                        "text_results": text_results,
                        "table_results": table_results
                    })
                    
                    # Force garbage collection after each image to free memory
                    gc.collect()
                    
                except Exception as e:
                    print(f"    [ERROR] Failed to process {img_path}: {e}")
                    print(f"    [ERROR] Traceback: {traceback.format_exc()}")
                    # Continue with other images instead of failing completely
                    all_extracted_data.append({
                        "image_path": img_path,
                        "text_results": [],
                        "table_results": []
                    })
                    continue
                    
        except Exception as e:
            print(f"[ERROR] Failed to initialize or run OCR processor: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False
        finally:
            # Clean up OCR processor
            if ocr_processor:
                try:
                    del ocr_processor
                    gc.collect()
                except:
                    pass

        # 3. AI-Powered Data Mapping
        print("\n[Step 3/4] AI-powered table structure detection and data mapping...")
        try:
            ai_mapper = AIDataMapper()
            all_dataframes = []
            
            for page_data in all_extracted_data:
                print(f"    🤖 Analyzing page: {os.path.basename(page_data['image_path'])}")
                try:
                    page_dfs = ai_mapper.process_ocr_outputs(
                        page_data["text_results"], 
                        page_data["table_results"]
                    )
                    all_dataframes.extend(page_dfs)
                except Exception as e:
                    print(f"    [WARNING] AI processing failed for {page_data['image_path']}: {e}")
                    continue
            
            if not all_dataframes:
                print("[!] AI could not detect any structured tables.")
                return False
                
        except Exception as e:
            print(f"[ERROR] AI data mapping failed: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

        # 4. Export to Excel
        print("\n[Step 4/4] Exporting AI-detected data to Excel...")
        try:
            export_to_excel(all_dataframes, output_excel_filename)
        except Exception as e:
            print(f"[ERROR] Failed to export to Excel: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

        print("\n===== 🎉 AI Conversion Complete! =====")
        print(f"📊 Detected and structured {len(all_dataframes)} table(s)")
        print(f"📁 Output saved to: {os.path.join(OUTPUT_DIR, output_excel_filename)}")
        print("🤖 AI automatically detected table structure without any hardcoding!")
        return True

    except Exception as e:
        print(f"[ERROR] Unexpected error during AI conversion: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False
        
    finally:
        # Clean up temporary images
        try:
            if os.path.exists(TEMP_IMAGE_DIR):
                print(f"[*] Cleaning up temporary images in '{TEMP_IMAGE_DIR}'...")
                shutil.rmtree(TEMP_IMAGE_DIR)
        except Exception as e:
            print(f"[WARNING] Failed to clean up temporary files: {e}")
        
        # Force final garbage collection
        gc.collect()

def main():
    """Main function with enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="AI-Powered PDF to Excel Converter - Automatically detects any table structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_ai.py document.pdf
  python main_ai.py "Manufacturing Parts.pdf" -o parts_data.xlsx
  python main_ai.py invoice.pdf -o invoice_data.xlsx

Features:
  🤖 AI-powered table detection
  📊 Automatic column header recognition  
  🔍 Spatial clustering for table regions
  🧠 Machine learning for data type detection
  ✨ No hardcoding - works with any document structure
        """
    )
    
    parser.add_argument("pdf_file", type=str, help="Path to the input PDF file")
    parser.add_argument("-o", "--output", type=str, 
                        default="ai_extracted_data.xlsx",
                        help="Name of the output Excel file (default: ai_extracted_data.xlsx)")
    
    args = parser.parse_args()

    try:
        success = run_ai_extraction(args.pdf_file, args.output)
        if not success:
            print("\n❌ [ERROR] AI conversion failed. Please check the error messages above.")
            sys.exit(1)
        else:
            print("\n✅ [SUCCESS] AI conversion completed successfully!")
            print("🚀 Ready to process any other PDF with the same intelligent approach!")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n[INFO] AI conversion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main() 