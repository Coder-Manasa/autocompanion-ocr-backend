# app/api/trip_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Trip
from app.services.gemini_client import ask_gemini

router = APIRouter(
    prefix="/api/trip",
    tags=["trip"],
)


def convert_ai_to_itinerary(text: str):
    """
    Convert Gemini plain text into a list of itinerary items.
    Expects lines like:
      - Day 1 - Visit ...
      - Day 2 - ...
    """
    lines = text.split("\n")
    items = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "-" in line:
            title, detail = line.split("-", 1)
        else:
            title, detail = line, ""

        items.append(
            {
                "title": title.strip(" -*\t"),
                "detail": detail.strip(),
                "eta": "Flexible",
            }
        )
    return items


@router.get("/test-auth")
def test_auth(user=Depends(get_current_user)):
    """
    Simple endpoint to check Firebase token works.
    GET /api/trip/test-auth with Authorization: Bearer <token>
    """
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "message": "Firebase token is valid ✅",
    }


@router.post("/generate")
def generate_trip(
    data: dict,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI itinerary:
    POST /api/trip/generate
    Body JSON:
    {
      "from": "Bangalore",
      "to": "Mysore",
      "days": "2",
      "style": "Relaxed"
    }
    Header: Authorization: Bearer <Firebase ID token>
    """

    required = {"from", "to", "days", "style"}
    if not required.issubset(data.keys()):
        raise HTTPException(status_code=400, detail="Missing fields in request body")

    # Build prompt for Gemini
    prompt = (
        f"Create a {data['days']}-day road trip itinerary from {data['from']} to "
        f"{data['to']} for a {data['style']} travel style. "
        "Return bullet points like:\n"
        "- Day 1 - morning & evening plan\n"
        "- Day 2 - ... etc.\n"
    )

    # Call Gemini
    ai_text = ask_gemini(prompt)
    itinerary = convert_ai_to_itinerary(ai_text)

    # Save in DB
    trip = Trip(
        user_id=user.get("uid"),
        from_place=data["from"],
        to_place=data["to"],
        days=int(data["days"]),
        style=data["style"],
        ai_raw_text=ai_text,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    return {
        "trip_id": trip.id,
        "itinerary": itinerary,
    }
