# Main script to run the PDF to Excel conversion using EasyOCR
import os
import gc
import sys
import shutil
import argparse
import traceback

from pdf_processor import process_pdf
from ocr_processor_easyocr import OCRProcessor  # Use EasyOCR version
from data_mapper import DataMapper
from excel_exporter import export_to_excel
from config import TEMP_IMAGE_DIR, OUTPUT_DIR

def run_extraction(pdf_path: str, output_excel_filename: str):
    """
    Main function to run the PDF to Excel conversion process using EasyOCR.
    """
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return False

    print(f"\n===== Starting PDF to Excel Conversion for '{pdf_path}' =====")
    print("[INFO] Using EasyOCR for text recognition")

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

        # 3. Map OCR Results to Structured Data
        print("\n[Step 3/4] Mapping OCR results to structured tables...")
        try:
            data_mapper = DataMapper()
            all_dataframes = []
            for page_data in all_extracted_data:
                # Pass both text and table results from the current page
                try:
                    page_dfs = data_mapper.process_ocr_outputs(
                        page_data["text_results"], 
                        page_data["table_results"]
                    )
                    all_dataframes.extend(page_dfs)
                except Exception as e:
                    print(f"    [WARNING] Failed to process data from {page_data['image_path']}: {e}")
                    continue
            
            if not all_dataframes:
                print("[!] No structured tables found or extracted from the PDF.")
                print("[INFO] This might be because EasyOCR doesn't support table structure detection.")
                print("[INFO] Creating a simple table from all detected text...")
                
                # Create a simple fallback table from all text
                all_text_data = []
                for page_data in all_extracted_data:
                    for text_result in page_data["text_results"]:
                        all_text_data.append({
                            "Text": text_result.get("text", ""),
                            "Confidence": text_result.get("confidence", 0),
                            "Page": os.path.basename(page_data["image_path"])
                        })
                
                if all_text_data:
                    import pandas as pd
                    df = pd.DataFrame(all_text_data)
                    all_dataframes = [df]
                else:
                    print("[!] No text data found. Exiting.")
                    return False
                
        except Exception as e:
            print(f"[ERROR] Failed to map OCR results: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

        # 4. Export to Excel
        print("\n[Step 4/4] Exporting extracted data to Excel...")
        try:
            export_to_excel(all_dataframes, output_excel_filename)
        except Exception as e:
            print(f"[ERROR] Failed to export to Excel: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

        print("\n===== Conversion Complete! =====")
        print(f"Output saved to: {os.path.join(OUTPUT_DIR, output_excel_filename)}")
        return True

    except Exception as e:
        print(f"[ERROR] Unexpected error during conversion: {e}")
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert PDF with handwritten notes to Excel using EasyOCR.")
    parser.add_argument("pdf_file", type=str, help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", type=str, 
                        default="extracted_data.xlsx",
                        help="Name of the output Excel file (default: extracted_data.xlsx).")
    
    args = parser.parse_args()

    # Example Usage:
    # python main_easyocr.py my_handwritten_notes.pdf -o my_notes_table.xlsx
    
    try:
        success = run_extraction(args.pdf_file, args.output)
        if not success:
            print("\n[ERROR] Conversion failed. Please check the error messages above.")
            sys.exit(1)
        else:
            print("\n[SUCCESS] Conversion completed successfully!")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n[INFO] Conversion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        sys.exit(1) 