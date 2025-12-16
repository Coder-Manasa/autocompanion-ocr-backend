from fastapi import APIRouter

router = APIRouter(prefix="/api/service", tags=["service"])


@router.get("/history")
def list_service_history():
    return {"services": []}
