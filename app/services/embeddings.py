import os
from fastembed import TextEmbedding

_model = None

def _get_model():
    global _model
    if _model is None:
        name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        _model = TextEmbedding(name)
    return _model

def embed_text(text: str) -> list[float]:
    model = _get_model()
    vec = next(model.embed([text]))
    result = vec.tolist()
    expected = int(os.getenv("EMBEDDING_DIM", "384"))
    if len(result) != expected:
        raise RuntimeError(f"Embedding dim mismatch: got {len(result)} expected {expected}")
    return result
