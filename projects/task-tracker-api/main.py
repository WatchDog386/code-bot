import logging

from fastapi import FastAPI

from app import __version__
from app.api import router
from app.config import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)

app = FastAPI(title=settings.app_name, version=__version__)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__}
