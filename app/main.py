from fastapi import FastAPI
import logging
from .api.routes import router as api_router
from .core.lifespan import lifespan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartMatching Service", lifespan=lifespan)

app.include_router(api_router, prefix="/api/smart-matching")

@app.get("/")
def root():
    return {"message": "SmartMatching Service is running"}