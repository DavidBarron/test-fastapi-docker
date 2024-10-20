import logging
from time import sleep

import redis_lock
from fastapi import APIRouter
from starlette import status

from src.config import get_settings
from src.config.clients import get_mongo_collection, get_redis_connection

settings = get_settings()

logger = logging.getLogger(settings.app_name)

router: APIRouter = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Healthcheck
    """
    return {"Status": "OK"}


@router.get("/bump", status_code=status.HTTP_200_OK)
def bump() -> dict:
    """
    Bump count in mongo doc using manual doc lock
    """
    mongo_collection = get_mongo_collection()
    doc = mongo_collection.find_one({"_id": 1})

    while doc.get("is_locked", False):
        sleep(3)
        doc = mongo_collection.find_one({"_id": 1})

    mongo_collection.update_one({"_id": 1}, {"$set": {"is_locked": True}})
    count = doc["val"]
    count += 1
    logger.info(f"Bump count {count}")
    mongo_collection.update_one(
        {"_id": 1}, {"$set": {"val": count, "is_locked": False}}
    )

    return {"count": count}


@router.get("/bump-lock", status_code=status.HTTP_200_OK)
def bump_lock() -> dict:
    """
    Bump count in mongo doc using redis lock
    """
    mongo_collection = get_mongo_collection()
    redis_connection = get_redis_connection()

    with redis_lock.Lock(redis_connection, "default-lock", expire=60):
        doc = mongo_collection.find_one({"_id": 1})
        count = doc["val"]
        count += 1
        logger.info(f"Bump count {count}")
        mongo_collection.update_one({"_id": 1}, {"$set": {"val": count}})

    return {"count": count}
