import httpx
import os
import logging
from qdrant_client import QdrantClient
from ..core.celery_app import celery_app
from ..services.embeddings import embed_texts
from ..services.vector_db import upsert_startups
from ..core.state import app_state

logger = logging.getLogger(__name__)

MONOLITH_URL = os.getenv("USER_SERVICE_URL", "http://web:8000")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


@celery_app.task
def sync_startups_task():
    logger.info("🔄 Celery: Starting daily startup sync...")

    if app_state.qdrant_client is None:
        try:
            logger.info("🔌 Connecting to Qdrant Cloud...")
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            app_state.qdrant_client = client
        except Exception as e:
            logger.error(f"❌ Celery: Failed to connect to Qdrant: {e}")
            return

    try:
        logger.info(f"📥 Fetching startups from {MONOLITH_URL}...")

        with httpx.Client(timeout=60.0) as client:
            response = client.get(
                f"{MONOLITH_URL}/api/projects/internal/startups/",
            )
            response.raise_for_status()
            startups_data = response.json()

        if not startups_data:
            logger.warning("⚠️ Celery: No startups received from Monolith.")
            return

        logger.info(f"📦 Celery: Received {len(startups_data)} startups. Processing...")

        texts_to_embed = []

        for startup in startups_data:
            desc = startup.get("description", "")
            texts_to_embed.append(desc)

        logger.info("🧠 Generating embeddings (this might take time)...")
        vectors = embed_texts(texts_to_embed)

        upsert_startups(vectors, startups_data)

        logger.info(f"✅ Celery: Successfully synced {len(startups_data)} startups.")

    except Exception as e:
        logger.error(f"❌ Celery Task Failed: {e}")