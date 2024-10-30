import logging

from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from redis import Redis

from src.config import get_settings

settings = get_settings()

logger = logging.getLogger(settings.app_name)

mongo_client: MongoClient | None = None
mongo_collection: Collection | None = None
redis_client: Redis | None = None


def initialize_mongo() -> None:
    global mongo_client, mongo_collection

    mongo_client = MongoClient(settings.mongo_host)

    try:
        mongo_client.admin.command("ping")
        logger.info("MongoDB connection successful!")
    except Exception as e:
        # log error and re-raise exception separately so the application crashes and does not complete startup
        logger.error("Failed to establish MongoDB connection.")
        raise e

    mongo_database = mongo_client[settings.mongo_db]
    mongo_collection = mongo_database[settings.mongo_collection]
    doc = mongo_collection.find_one({"_id": 1})

    if not doc:
        mongo_collection.insert_one({"_id": 1, "val": 1})


def close_mongo() -> None:
    global mongo_client

    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")
    else:
        logger.warning("MongoDB connection already closed.")


def initialize_redis() -> None:
    global redis_client

    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_general_cache_db,
    )

    try:
        redis_client.ping()
        logger.info("Redis connection successful!")
    except Exception as e:
        # log error and re-raise exception separately so the application crashes and does not complete startup
        logger.error("Failed to establish Redis connection.")
        raise e


def close_redis() -> None:
    global redis_client

    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed.")
    else:
        logger.warning("Redis connection already closed.")


def get_mongo_collection() -> Collection:
    global mongo_collection

    if mongo_collection is None:
        initialize_mongo()

    return mongo_collection


def get_redis_client() -> Redis:
    global redis_client

    if redis_client is None:
        initialize_redis()

    return redis_client
