import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Task Tracker API"
    debug: bool = False
    default_page_size: int = 20
    max_page_size: int = 100


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", Settings.app_name),
        debug=os.getenv("DEBUG", "false").lower() in ("1", "true", "yes"),
        default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("MAX_PAGE_SIZE", "100")),
    )


settings = load_settings()
