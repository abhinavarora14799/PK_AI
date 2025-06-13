# Functions for processing PDFs # pdf_processor.py
import os
from pdf2image import convert_from_path
from PIL import Image

from config import TEMP_IMAGE_DIR, POPPLER_PATH

def process_pdf(pdf_path: str) -> list[str]:
    """
    Converts a PDF file into a list of high-resolution images, one per page.

    Args:
        pdf_path (str): The path to the input PDF file.

    Returns:
        list[str]: A list of file paths to the generated images.
    """
    if not os.path.exists(TEMP_IMAGE_DIR):
        os.makedirs(TEMP_IMAGE_DIR)

    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    image_paths = []
    for i, image in enumerate(images):
        img_path = os.path.join(TEMP_IMAGE_DIR, f"page_{i+1}.png")
        image.save(img_path, "PNG")
        image_paths.append(img_path)
    print(f"[*] Converted {len(images)} pages from '{pdf_path}' to images.")
    return image_paths

if __name__ == '__main__':
    # Example usage (for testing this module independently)
    # Create a dummy PDF for testing if you don't have one
    # from reportlab.lib.pagesizes import letter
    # from reportlab.pdfgen import canvas
    # c = canvas.Canvas("sample_document.pdf", pagesize=letter)
    # c.drawString(100, 750, "Hello, this is a sample page.")
    # c.drawString(100, 700, "With some text on it.")
    # c.save()

    # if os.path.exists("sample_document.pdf"):
    #     processed_images = process_pdf("sample_document.pdf")
    #     print(f"Generated images: {processed_images}")
    # else:
    #     print("Please create 'sample_document.pdf' for testing.")
    pass