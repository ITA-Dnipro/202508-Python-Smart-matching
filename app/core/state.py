import numpy as np
from qdrant_client import QdrantClient
from typing import Optional


class AppState:
    """A container for a state that lives throughout the lifetime of an application."""

    def __init__(self) -> None:
        self.startup_vectors: Optional[np.ndarray] = None
        self.qdrant_client: Optional[QdrantClient] = None


app_state = AppState()