from fastapi import FastAPI

from backend.api.main import api_router
from backend.core.config import settings

app = FastAPI()

app.include_router(api_router,prefix=settings.API_V1_STR,)

@app.get("/")
def root():
    return {"Health check": "Working"}