# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.api.test_routes import router as test_router
from app.api.trip_routes import router as trip_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoCompanion Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "AutoCompanion backend running"}


# Routers
app.include_router(test_router)
app.include_router(trip_router)
