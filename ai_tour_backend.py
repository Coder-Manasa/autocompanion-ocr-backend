# ai_tour_backend.py
# Simple Flask backend for AI Tour Planner using Gemini

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# ================== CONFIGURE GEMINI ==================

# ❗ PUT YOUR VALID GEMINI API KEY HERE
GEMINI_API_KEY = os.environ.get("AIzaSyA2HqvjsIpmXJXVz_3q69W9M_vONGdca3I")

# if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("PUT_"):
#     raise ValueError("Please set your Gemini API key in GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"   # Works with your key

# ================== FLASK APP SETUP ==================

app = Flask(__name__)
CORS(app)  # allow calls from Flutter / localhost etc.

# ================== HELPER: BUILD PROMPT ==================


def build_tour_prompt(data: dict) -> str:
    """
    Build a natural language prompt for Gemini based on user inputs.
    """
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

    prompt = f"""
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
1. Provide a **day-wise itinerary** (Day 1, Day 2, etc.).
2. For each day include:
   - Main places to visit (with short description)
   - Suggested timings (morning / afternoon / evening)
   - Approx travel time between places
   - Food / rest suggestions if needed
3. Format cleanly with headings.

At the end provide:
- A short trip summary
- 3 to 5 travel safety tips
"""

    return prompt


# ================== ROUTE: HEALTH CHECK ==================


@app.get("/ping")
def ping():
    return jsonify({"status": "ok", "message": "AI Tour Planner backend is running"})


# ================== ROUTE: AI TOUR PLANNER ==================


@app.post("/api/ai-tour-plan")
def ai_tour_plan():
    """
    Expects JSON body like:
    {
      "start_location": "Bangalore",
      "destination": "Goa",
      "start_date": "2025-12-20",
      "end_date": "2025-12-24",
      "days": 4,
      "budget": "₹15,000 per person",
      "travelers": 2,
      "vehicle_type": "car",
      "interests": ["beach", "sunset", "local food"],
      "pace": "relaxed"
    }
    """
    try:
        data = request.get_json(force=True) or {}
    except:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Build prompt
    prompt = build_tour_prompt(data)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        text = response.text if hasattr(response, "text") else str(response)

        return jsonify({
            "success": True,
            "itinerary": text
        })
    except Exception as e:
        print("Error calling Gemini:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ================== MAIN ==================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)