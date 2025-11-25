import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from ..services.embeddings import embed_texts
from .state import app_state
from ..services.vector_db import upsert_startups

logger = logging.getLogger(__name__)

VECTOR_SIZE = 384
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application's lifespan events for startup and shutdown."""
    logger.info("Application startup...")

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url:
        logger.warning("QDRANT_URL not set!")

    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        app_state.qdrant_client = client

        if not client.collection_exists(COLLECTION_NAME):
            logger.info(f"Collection '{COLLECTION_NAME}' not found. Creating...")

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Collection created")

    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")

    yield

    if app_state.qdrant_client:
        app_state.qdrant_client.close()
    app_state.qdrant_client = None