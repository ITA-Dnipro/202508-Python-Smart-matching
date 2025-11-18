import os
from fastembed import TextEmbedding
import numpy as np

_model = None


def _get_model():
    global _model
    if _model is None:
        name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        _model = TextEmbedding(name)
    return _model


def _normalize_l2(x: np.ndarray) -> np.ndarray:
    """L2 normalizes a numpy array."""
    if x.ndim == 1:
        norm = np.linalg.norm(x)
        if norm == 0:
            return x
        return x / norm
    else:
        norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
        norm[norm == 0] = 1
        return x / norm


def embed_text(text: str) -> np.ndarray:
    """Vectorizes a single text and returns an L2-normalized numpy array"""
    model = _get_model()
    vec = next(model.embed([text]))
    vec_normalized = _normalize_l2(vec)
    expected = int(os.getenv("EMBEDDING_DIM", "384"))
    if vec_normalized.shape[0] != expected:
        raise RuntimeError(f"Embedding dim mismatch: got {vec_normalized.shape[0]} expected {expected}")
    return vec_normalized


def embed_texts(texts: list[str]) -> np.ndarray:
    """Vectorizes a list of texts and returns an L2-normalized numpy matrix."""
    model = _get_model()
    embeddings = np.array(list(model.embed(texts)))
    embeddings_normalized = _normalize_l2(embeddings)

    return embeddings_normalized