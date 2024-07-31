import logging

from fastapi import APIRouter, Request
from starlette import status

from src.config import get_settings

settings = get_settings()

logger = logging.getLogger(settings.app_name)


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Healthcheck
    """
    return {"Status": "OK"}
