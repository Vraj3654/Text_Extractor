import pytesseract
from PIL import Image
import re
import os

# Default Windows Path (Adjust if needed)
DEFAULT_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def configure_tesseract(tesseract_cmd=DEFAULT_TESSERACT_CMD):
    """Sets the path to the Tesseract executable."""
    if not os.path.exists(tesseract_cmd):
        raise FileNotFoundError(f"Tesseract executable not found at: {tesseract_cmd}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def clean_text(text):
    """
    Specific cleanup for the A.D. Patel Letter
    """
    # 1. Fix "Rupee" symbol confusion (Tesseract sees £ or ? often)
    # The image has "₹28,500"
    text = text.replace('£', '₹').replace('?', '₹')

    # 2. Fix the "th" superscript date issue (30° -> 30th)
    # Regex: Look for number followed by degree symbol
    text = re.sub(r'(\d+)°', r'\1th', text)

    # 3. Fix common "Principal" typos
    text = text.replace('Principat', 'Principal')

    # 4. Fix pipe '|' or '!' errors at start of words
    text = re.sub(r'\b[|!](?=\s)', 'I', text) 
    text = re.sub(r'(?<=[A-Za-z])[|!](?=[A-Za-z])', 'I', text)

    return text

def extract_text_from_image(image_path, output_txt_path=None):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # OCR Config: PSM 6 is usually best for letters/blocks of text
    custom_config = r'--oem 3 --psm 6' 
    
    img = Image.open(image_path)
    
    # Extract
    raw_text = pytesseract.image_to_string(img, config=custom_config)
    final_text = clean_text(raw_text)

    if output_txt_path:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_txt_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(final_text)

    return final_text

if __name__ == "__main__":
    # Test block
    try:
        configure_tesseract()
        print("Test run successful.")
    except Exception as e:
        print(f"Error: {e}")