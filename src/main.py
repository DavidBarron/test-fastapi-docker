import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.config import get_settings
from src.config.clients import (
    close_mongo,
    close_redis,
    initialize_mongo,
    initialize_redis,
)
from src.config.logging import init_logging

# for now, init stuff here
init_logging()

settings = get_settings()

logger = logging.getLogger(settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Preform app pre-startup actions before `yield` and app post-shutdown actions after, i.e. managing database or queue
    connections would happen here.
    Ref: https://fastapi.tiangolo.com/advanced/events/
    """
    initialize_mongo()
    initialize_redis()
    yield
    close_mongo()
    close_redis()


def create_application() -> FastAPI:
    from src.routing import router as app_router

    app = FastAPI(lifespan=lifespan)
    app.include_router(app_router)

    return app


if __name__ == "__main__":
    logger.info("Starting in debug mode")
    uvicorn.run(
        create_application(),
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )
