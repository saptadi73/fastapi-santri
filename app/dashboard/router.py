from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary():
    return {
        "total_santri": 12540,
        "miskin": 3240,
        "rentan": 4680,
    }
