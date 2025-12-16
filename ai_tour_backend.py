# ai_tour_backend.py
# Flask backend for AI Tour Planner + OCR using Gemini Vision

import os
import re
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai


# ================== CONFIGURE GEMINI ==================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

TEXT_MODEL = "models/gemini-1.5-flash"
VISION_MODEL = "models/gemini-1.5-flash"


# ================== FLASK APP ==================

app = Flask(__name__)
CORS(app)


# ================== HEALTH ==================

@app.get("/ping")
def ping():
    return jsonify({"status": "ok"})


# ================== AI TOUR ==================

@app.post("/api/ai-tour-plan")
def ai_tour_plan():
    try:
        data = request.get_json(force=True) or {}

        prompt = f"""
Plan a road trip itinerary.

Destination: {data.get("destination")}
Start date: {data.get("start_date")}
End date: {data.get("end_date")}
Vehicle: {data.get("vehicle_type")}
Budget: {data.get("budget")}
Interests: {', '.join(data.get("interests", []))}
"""

        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "itinerary": response.text
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ================== OCR USING GEMINI VISION ==================

@app.post("/ocr-url")
def ocr_from_url():
    try:
        data = request.get_json(force=True)
        image_url = data.get("file_url")

        if not image_url:
            return jsonify({"success": False, "error": "file_url missing"}), 400

        # Download image
        img_bytes = requests.get(image_url, timeout=15).content
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        model = genai.GenerativeModel(VISION_MODEL)

        prompt = """
Extract all readable text from this document.
Then clearly identify the EXPIRY DATE if present.
If multiple dates exist, choose the FINAL VALIDITY / EXPIRY date.
Return plain text only.
"""

        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": img_base64
            }
        ])

        extracted_text = response.text.strip()

        # ================== EXPIRY DATE PARSING ==================

        patterns = [
            r'(?:valid\s*(?:till|upto|to)|expiry\s*date|validity).*?'
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',

            r'(\d{1,2}(?:st|nd|rd|th)?\s+of\s+'
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',

            r'(\d{1,2}\s+'
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
        ]

        expiry_date = "Not detected"
        for p in patterns:
            m = re.search(p, extracted_text, re.IGNORECASE)
            if m:
                expiry_date = m.group(1)
                break

        return jsonify({
            "success": True,
            "expiry_date": expiry_date,
            "extracted_text": extracted_text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "expiry_date": "Not detected",
            "extracted_text": f"OCR error: {e}"
        }), 500


# ================== MAIN ==================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
