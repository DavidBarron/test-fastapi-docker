import logging
from asyncio import timeout
from time import sleep

import redis_lock
from fastapi import APIRouter, Request
from redis import Redis, StrictRedis
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


@router.get("/bump_lock", status_code=status.HTTP_200_OK)
def bump_lock():
    """
    Bump count in mongo doc using redis lock
    """
    mongo_collection = get_mongo_collection()

    conn = StrictRedis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_general_cache_db,
    )

    with redis_lock.Lock(conn, "default-lock", expire=60):
        doc = mongo_collection.find_one({"_id": 1})
        count = doc["val"]
        count += 1
        logger.info(f"Bump count {count}")
        mongo_collection.update_one({"_id": 1}, {"$set": {"val": count}})

    return {"count": count}
