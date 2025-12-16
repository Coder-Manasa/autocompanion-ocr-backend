from fastapi import APIRouter

router = APIRouter(prefix="/api/docs", tags=["documents"])


@router.get("/")
def list_documents():
    return {"documents": []}
