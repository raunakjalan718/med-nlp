import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

# --- THE BULLETPROOF WINDOWS FIX ---
# This forces Python to find Tesseract regardless of Windows PATH issues
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_file(file_path):
    try:
        text = ""
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img) + " "
        else:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
        return " ".join(text.split())
    except Exception as e:
        return f"OCR Error: {str(e)}"