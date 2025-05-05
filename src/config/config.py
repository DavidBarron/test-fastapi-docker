import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "test-app"
    host: str = "0.0.0.0"
    port: int = 8080
    env: str = "local"
    log_level: int = logging.INFO

    mongo_host: str = "mongodb://localhost:27017"
    mongo_db: str = "default"
    mongo_collection: str = "default_collection"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_general_cache_db: int = 0
