import os
import logging
from qdrant_client.models import PointStruct
from ..core.state import app_state
from ..api.schema import MatchResult

logger = logging.getLogger(__name__)

COLLECTION_NAME = os.getenv('QDRANT_COLLECTION')

def upsert_startups(vectors: list, payloads: list[dict]):
    """
    Maintains (updates) startups in Qdrant.
    """
    client = app_state.qdrant_client
    if not client:
        raise Exception("Database client not initialized")

    points = []
    for i, payload in enumerate(payloads):
        points.append(PointStruct(
            id=i,
            vector=vectors[i].tolist(),
            payload=payload
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)


def search_similar_startups(query_vector: list, top_k: int) -> list[MatchResult]:
    """
    Searches for similar vectors and immediately returns good MatchResult objects.
    """
    client = app_state.qdrant_client
    if not client:
        raise Exception("Database client not initialized")
    
    logger.info(f"DEBUG: Client Type: {type(client)}")
    logger.info(f"DEBUG: Client Dir: {dir(client)}")

    search_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,      
        limit=top_k
    ).points

    results = []
    for hit in search_results:
        results.append(
            MatchResult(
                startup_id=str(hit.payload.get('id')),
                startup_name=hit.payload.get('name', 'Unknown'),
                startup_description=hit.payload.get('description', ''),
                similarity_score=round(hit.score, 4)
            )
        )
    return results