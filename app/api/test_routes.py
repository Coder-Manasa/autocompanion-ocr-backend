# app/api/test_routes.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["test"],
)


@router.get("/ping")
def ping():
    """
    Simple health-check:
    GET /api/ping
    """
    return {"status": "pong"}
