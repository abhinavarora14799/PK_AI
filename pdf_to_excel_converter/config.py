# Configuration settings # config.py

# Directory to store temporary images extracted from PDF
TEMP_IMAGE_DIR = "temp_images"

# Directory to store output Excel files
OUTPUT_DIR = "output_excel"

# Mapping of detected header keywords (case-insensitive) to desired Excel column names.
# This helps standardize column names in the final Excel file.
# Add more mappings as needed based on your handwritten notes' common headers.
# The keys are the desired Excel column names. The values are lists of possible
# text snippets that PaddleOCR might recognize for that header.
COLUMN_MAPPINGS = {
    "Date": ["date", "receipt date", "transaction date"],
    "Item Description": ["item", "description", "product", "details"],
    "Quantity": ["qty", "quantity", "amount", "units"],
    "Unit Price": ["unit price", "price", "cost", "rate"],
    "Total": ["total", "sum", "grand total", "net amount"],
    "Notes": ["notes", "remarks", "comments"]
    # Add more as per your specific handwritten table headers
}

# OCR Model Configuration
# lang: 'en' for English, 'ch' for Chinese, etc.
# use_angle_cls: True for angle classification (detects rotated text)
# use_gpu: Set to True if you have a compatible GPU and PaddlePaddle GPU version installed
OCR_CONFIG = {
    "lang": "en",
    "use_angle_cls": True,
    "use_gpu": False # Set to True if you have GPU and installed paddlepaddle-gpu
}

# Poppler path for pdf2image (only needed if Poppler is not in PATH)
# POPPLER_PATH = r"C:\path\to\poppler\bin" # Example for Windows
POPPLER_PATH = None