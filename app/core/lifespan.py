import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ..static_data import STATIC_STARTUPS
from ..services.embeddings import embed_texts
from .state import app_state

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application's lifespan events for startup and shutdown."""
    logger.info("Application startup...")
    try:
        startup_descriptions = [startup['description'] for startup in STATIC_STARTUPS]
        logger.info(f"Calculating embeddings for {len(startup_descriptions)}...")

        app_state.startup_vectors = embed_texts(startup_descriptions)

        logger.info(f"Calculated {len(app_state.startup_vectors)} vectors.")
    except Exception as e:
        logger.error(f"Failed to initialize startup vectors: {e}")
        app_state.startup_vectors = None

    yield

    logger.info("Application shutdown...")
    app_state.startup_vectors = None