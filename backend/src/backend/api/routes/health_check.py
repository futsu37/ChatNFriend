from fastapi import APIRouter

router = APIRouter(tags=["health check"])

@router.get("/health-check/")
async def health_check() -> bool:
    return True