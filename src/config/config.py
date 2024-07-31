import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "app-name-here"  # TODO: give your app a name
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: int = logging.INFO
