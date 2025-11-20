from fastapi import APIRouter, HTTPException, Header
import logging
import os
from .schema import EmbedIn, InvestorSearchRequest, MatchResult, EchoIn
from ..services.embeddings import embed_text
from ..services.search import find_matches_for_investor
from ..core.exceptions import UserNotFoundException, MonolithServiceException
from ..core.state import app_state

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "model": os.getenv("EMBEDDING_MODEL")}


@router.post("/search", response_model=list[MatchResult])
async def find_matches(request: InvestorSearchRequest, authorization: str | None = Header(None)) -> list[MatchResult]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    if not request.investor_id:
        raise HTTPException(status_code=400, detail="investor_id is required")
    try:
        results = await find_matches_for_investor(
            investor_id=request.investor_id,
            top_k=request.top_k,
            authorization = authorization
        )
        return results
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MonolithServiceException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Search Error")