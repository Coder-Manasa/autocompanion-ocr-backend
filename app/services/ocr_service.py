import pytesseract
from PIL import Image

def run_ocr(path: str):
    try:
        text = pytesseract.image_to_string(Image.open(path))
        return text
    except:
        return ""
