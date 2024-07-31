import logging

import uvicorn
from fastapi import FastAPI

from src.config import get_settings
from src.config.logging import init_logging

# for now, init stuff here
init_logging()

settings = get_settings()

logger = logging.getLogger(settings.app_name)


def create_application() -> FastAPI:
    from src.routing import router as app_router

    app = FastAPI()
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
