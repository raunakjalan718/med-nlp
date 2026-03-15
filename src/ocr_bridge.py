import pytesseract
from PIL import Image

def extract_raw_text(image_path):
    """Takes a document image and returns a raw string of text."""
    try:
        image = Image.open(image_path)
        # Basic OCR extraction
        raw_text = pytesseract.image_to_string(image)
        # Clean up excessive newlines and whitespace
        clean_text = " ".join(raw_text.split())
        return clean_text
    except Exception as e:
        return f"OCR Error: {str(e)}"