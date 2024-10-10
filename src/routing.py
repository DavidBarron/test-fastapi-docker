import logging

from fastapi import APIRouter, Request
from starlette import status

from src.config import get_settings
from src.config.clients import get_mongo_collection

settings = get_settings()

logger = logging.getLogger(settings.app_name)


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Healthcheck
    """
    return {"Status": "OK"}


@router.get("/bump", status_code=status.HTTP_200_OK)
def bump():
    """
    Bump count in mongo doc
    """
    mongo_collection = get_mongo_collection()
    doc = mongo_collection.find_one({"_id": 1})
    count = doc["val"]
    count += 1
    logger.info(f"Bump count {count}")
    mongo_collection.update_one({"_id": 1}, {"$set": {"val": count}})

    return {"count": count}
