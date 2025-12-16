from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
import requests
import cv2
import numpy as np
import re
from PIL import Image
from io import BytesIO

# Path to Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

# -----------------------------------
# CLEAN DOCUMENT PREPROCESSING
# -----------------------------------
def preprocess_image(img):

    # Rotate if image is sideways
    if img.shape[1] > img.shape[0]:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Upscale for better OCR
    img = cv2.resize(
        img, None,
        fx=2.5, fy=2.5,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Light denoising only (NO thresholding)
    gray = cv2.medianBlur(gray, 3)

    return gray


# -----------------------------------
# EXPIRY DATE EXTRACTION
# -----------------------------------
def extract_expiry(text):
    text = text.replace("\n", " ")

    patterns = [
        r"(expiry\s*date|valid\s*upto|valid\s*till|expires)[^\d]*"
        r"(\d{1,2}(st|nd|rd|th)?\s*(of\s*)?"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"[,\s]*\d{4})",

        r"(\d{1,2}(st|nd|rd|th)?\s*"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s*\d{4})",

        r"((January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s*\d{1,2}\s*\d{4})",

        r"(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})",

        r"(\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2})"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(2 if m.lastindex and m.lastindex >= 2 else 1)

    return None


# -----------------------------------
# OCR API ROUTE
# -----------------------------------
@app.route("/ocr-url", methods=["POST"])
def ocr_from_url():
    try:
        data = request.json
        file_url = data.get("file_url")

        print("\n🔥 New OCR request")
        print("Image URL:", file_url)

        # Download image
        img_bytes = requests.get(file_url).content
        pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Save raw image (debug)
        cv2.imwrite("received_raw.jpg", img)

        # Preprocess
        processed = preprocess_image(img)

        # Save processed image (debug)
        cv2.imwrite("processed_output.jpg", processed)

        # 🔥 DOCUMENT OCR MODE (THIS FIXES GARBAGE TEXT)
        config = "--oem 3 --psm 11 -l eng --dpi 300"
        text = pytesseract.image_to_string(processed, config=config)

        print("\n--- OCR TEXT START ---")
        print(text)
        print("--- OCR TEXT END ---\n")

        expiry = extract_expiry(text)

        return jsonify({
            "success": True,
            "extracted_text": text.strip(),
            "expiry_date": expiry or "Not detected"
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------
if __name__ == "__main__":
    print("\n🚀 OCR Backend Running on port 5002...\n")
    app.run(host="0.0.0.0", port=5002, debug=True)
