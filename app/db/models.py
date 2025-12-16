# app/db/models.py
from sqlalchemy import Column, Integer, String, Text

from app.db.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)         # Firebase UID (string)
    from_place = Column(String, nullable=False)
    to_place = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    style = Column(String, nullable=False)
    ai_raw_text = Column(Text)                   # Full Gemini response text
