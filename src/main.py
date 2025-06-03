from fastapi import FastAPI
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
import os
from .api import v1_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Qdrant client once
    app.state.qdrant_client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333)),
    )
    yield


app = FastAPI(title="Agentic AI Assistant", lifespan=lifespan)

app.include_router(v1_api_router, prefix="/api/v1")
