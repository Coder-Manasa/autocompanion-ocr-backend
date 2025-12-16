from fastapi import APIRouter

router = APIRouter(prefix="/api/emergency", tags=["emergency"])


@router.get("/help")
def emergency_help():
    return {"message": "Emergency endpoint (demo)"}
