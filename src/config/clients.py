import logging

from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from redis import StrictRedis

from src.config import get_settings

settings = get_settings()

logger = logging.getLogger(settings.app_name)

mongo_client = MongoClient(settings.mongo_host)
mongo_collection: Collection | None = None
redis_connection = StrictRedis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_general_cache_db,
)


def initialize_mongo() -> None:
    global mongo_collection

    try:
        mongo_client.admin.command("ping")
        logger.info("MongoDB connection successful!")
    except Exception as e:
        # log error and re-raise exception separately so the application crashes and does not complete startup
        logger.error("Failed to establish MongoDB connection.")
        raise e

    mongo_database = mongo_client[settings.mongo_db]
    mongo_collection = mongo_database[settings.mongo_collection]
    # mongo_collection.insert_one({"_id": 1, "val": 1})


def close_mongo():
    mongo_client.close()
    logger.info("MongoDB connection closed.")


def get_mongo_collection() -> Collection:
    return mongo_collection


def get_redis_connection() -> StrictRedis:
    return redis_connection
