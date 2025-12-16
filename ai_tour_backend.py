# ai_tour_backend.py
# Simple Flask backend for AI Tour Planner + OCR using Gemini

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import re


# ================== CONFIGURE GEMINI ==================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please set your Gemini API key in GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"


# ================== FLASK APP SETUP ==================

app = Flask(__name__)
CORS(app)


# ================== HELPER: BUILD PROMPT ==================

def build_tour_prompt(data: dict) -> str:
    destination = data.get("destination", "Unknown place")
    start_date = data.get("start_date", "Not specified")
    end_date = data.get("end_date", "Not specified")
    days = data.get("days", None)
    budget = data.get("budget", "Not specified")
    travelers = data.get("travelers", 1)
    start_location = data.get("start_location", "User's home")
    vehicle_type = data.get("vehicle_type", "car")
    interests = data.get("interests", [])
    pace = data.get("pace", "normal")

    interests_text = ", ".join(interests) if interests else "general sightseeing"

    return f"""
You are an AI tour planner assistant for an app called AutoCompanion.

Plan a road trip itinerary.

Details:
- Start location: {start_location}
- Destination: {destination}
- Start date: {start_date}
- End date: {end_date}
- Approx days: {days if days else "calculate based on dates if possible"}
- Vehicle type: {vehicle_type}
- Number of travelers: {travelers}
- Budget: {budget}
- User interests: {interests_text}
- Preferred pace: {pace}

Requirements:
1. Provide a day-wise itinerary.
2. Include places, timings, travel time.
3. Add food/rest suggestions.

End with summary and safety tips.
"""


# ================== ROUTE: HEALTH ==================

@app.get("/ping")
def ping():
    return jsonify({"status": "ok"})


# ================== ROUTE: AI TOUR ==================

@app.post("/api/ai-tour-plan")
def ai_tour_plan():
    try:
        data = request.get_json(force=True) or {}
        prompt = build_tour_prompt(data)

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "itinerary": response.text
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ================== ROUTE: OCR ==================

@app.post("/ocr-url")
def ocr_from_url():
    try:
        data = request.get_json(force=True)
        image_url = data.get("file_url")

        if not image_url:
            return jsonify({"success": False, "error": "file_url missing"}), 400

        # Download image
        response = requests.get(image_url, timeout=15)
        image = Image.open(BytesIO(response.content))

        # OCR extract
        extracted_text = pytesseract.image_to_string(image)

        # ✅ IMPROVED EXPIRY DATE LOGIC (supports till / to / ranges)
        # ✅ FIXED EXPIRY DATE LOGIC (returns full date, not just day)

        patterns = [
            # from 01/06/2023 to 31/05/2024  → take END date
            r'(?:from\s+)?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:to|till|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',

            # valid till / valid upto / expiry date
            r'(?:valid\s*(?:till|upto|to)|expiry\s*date|validity)[:\s]*'
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',

            # FULL capture: 28th of May 2024
            r'(\d{1,2}(?:st|nd|rd|th)?\s+of\s+'
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',

            # FULL capture: 28 May 2024
            r'(\d{1,2}\s+'
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
        ]

        expiry_date = "Not detected"
        for pattern in patterns:
            match = re.search(pattern, extracted_text, re.IGNORECASE)
            if match:
                expiry_date = match.group(1)
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