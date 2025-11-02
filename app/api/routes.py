from fastapi import APIRouter
from .schema import EmbedIn
from app.services.embeddings import embed_text


router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/test/enmbed")
def test_embed(body: EmbedIn):
    vec = embed_text(body.text)
    return {"dim": len(vec), "vector": vec[:8]}