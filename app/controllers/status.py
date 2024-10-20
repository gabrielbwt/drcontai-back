from fastapi import APIRouter, status
from app.utils.settings import Settings

router = APIRouter(
    tags=["Status"]
)
settings = Settings()

@router.get('/status', status_code=status.HTTP_200_OK)
async def status_server():

    return f"Server is Running in {settings.environment}!"
