import json
import logging
from time import sleep

import redis_lock
from fastapi import APIRouter, Depends, Request
from starlette import status

from src.config import get_settings
from src.config.clients import get_mongo_collection, get_redis_client

settings = get_settings()

logger = logging.getLogger(settings.app_name)

router: APIRouter = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


async def get_json(request: Request) -> dict:
    """
    Workaround for retrieving a Request body in JSON format in a sync endpoint. FastApi will first set up the Dependency
    using this async function before sending off the request to be serviced in its own Thread where it can block
    independently without blocking the event loop which runs the parent application.
    """
    return await request.json()


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
    redis_client = get_redis_client()

    with redis_lock.Lock(redis_client, "default-lock", expire=60):
        doc = mongo_collection.find_one({"_id": 1})
        count = doc["val"]
        count += 1
        logger.info(f"Bump count {count}")
        mongo_collection.update_one({"_id": 1}, {"$set": {"val": count}})

    return {"count": count}


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
def post_to_redis_set_by_name(
    json_payload: dict = Depends(get_json),
):
    """
    Post an event to redis set by name

    Format for event is:
    {
        "system_id": str,
        "action": str
    }
    """
    set_name = json_payload["set_name"]
    event = json_payload["event"]

    redis_client = get_redis_client()
    redis_client.sadd(set_name, json.dumps(event))

    logger.info(f"Added event to set: {set_name}.", extra={"event": event})


@router.get("/peek/{set_name}")
def get_redis_set_by_name(set_name: str):
    """
    Get all set contents
    """
    logger.info(f"Getting all set contents: {set_name}")

    redis_client = get_redis_client()
    set_members = redis_client.smembers(set_name)

    return [json.loads(member) for member in set_members]


@router.get("/queue-status", status_code=status.HTTP_200_OK)
def get_queue_status() -> dict:
    """
    Get name of all sets and count of items in each.
    """
    logger.info(f"Get all sets and count of items in each.")

    redis_client = get_redis_client()
    sets = []
    response: dict = {}

    for key in redis_client.scan_iter():
        logger.info(f"Got key: {key}")
        if redis_client.type(key) == b"set":
            sets.append(key.decode("utf-8"))

    for set_name in sets:
        response[set_name] = redis_client.scard(set_name)

    return response


@router.get("/fetch/{set_name}")
def get_redis_and_clear_set_by_name(set_name: str):
    """
    Get all set contents and clear set to reset
    """
    redis_client = get_redis_client()
    set_members = redis_client.smembers(set_name)

    for member in set_members:
        redis_client.srem(set_name, member)

    return [json.loads(member) for member in set_members]
