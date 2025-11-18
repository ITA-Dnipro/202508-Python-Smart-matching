import numpy as np

class AppState:
    """A container for a state that lives throughout the lifetime of an application."""
    startup_vectors: np.ndarray | None = None

app_state = AppState()