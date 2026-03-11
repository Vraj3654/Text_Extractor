import pytesseract
from PIL import Image
import re
import os

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# TESSERACT CONFIGURATION
# =========================

# We use the system default so Docker can locate it automatically.
DEFAULT_TESSERACT_CMD = "tesseract"

def configure_tesseract(tesseract_cmd=DEFAULT_TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


# =========================
# LOAD AI MODEL (ONCE)
# =========================

MODEL_NAME = "vennify/t5-base-grammar-correction"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


# =========================
# POST-OCR FIXES (SAFE)
# =========================

def fix_ocr_artifacts(text):
    """
    Fix OCR mechanical errors (rule-based, safe)
    """
    text = text.replace('£', '₹')
    text = re.sub(r'(\d+)°', r'\1th', text)
    # Fix common pipeline artifacts (I vs l, | vs I)
    text = re.sub(r'(?<=[a-z])[|!](?=[a-z])', 'l', text)
    text = re.sub(r'(?<=[A-Z])[|!](?=[A-Z])', 'I', text)
    return text


# =========================
# AI TEXT CORRECTION
# =========================

def ai_text_correction(text):
    """
    Applies transformer-based grammar & spelling correction.
    Only runs on alphabet-heavy lines to protect numbers & IDs.
    """

    corrected_lines = []

    for line in text.split('\n'):

        # Skip empty lines
        if not line.strip():
            corrected_lines.append(line)
            continue

        # Skip lines with lots of digits (IDs, dates, amounts)
        digit_ratio = sum(c.isdigit() for c in line) / max(len(line), 1)
        if digit_ratio > 0.25:
            corrected_lines.append(line)
            continue

        # Apply AI correction
        input_text = "grammar: " + line
        input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True)

        outputs = model.generate(
            input_ids,
            max_length=128,
            num_beams=4,
            early_stopping=True
        )

        corrected_line = tokenizer.decode(outputs[0], skip_special_tokens=True)
        corrected_lines.append(corrected_line)

    return "\n".join(corrected_lines)


# =========================
# DOCUMENT-SPECIFIC FIXES
# =========================

def document_specific_fix(text):
    text = text.replace('Principat', 'Principal')
    return text


# =========================
# MAIN OCR FUNCTION
# =========================

def extract_text_from_image(cv2_image_array):
    
    custom_config = r'--oem 3 --psm 4 -c preserve_interword_spaces=1'
    
    # Convert cv2 numpy array to PIL Image compatible with pytesseract
    img = Image.fromarray(cv2_image_array)

    # Step 1: OCR
    raw_text = pytesseract.image_to_string(img, config=custom_config)

    # Step 2: OCR artifact fixes
    text = fix_ocr_artifacts(raw_text)

    # Step 3: AI correction
    text = ai_text_correction(text)

    # Step 4: Document-specific cleanup
    final_text = document_specific_fix(text)

    return {"raw_text": raw_text, "corrected_text": final_text}


# =========================
# TEST BLOCK
# =========================

if __name__ == "__main__":
    try:
        configure_tesseract()
        print("AI-powered OCR pipeline ready.")
    except Exception as e:
        print(f"Error: {e}")
