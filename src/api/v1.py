from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..core import InternalAgent

api_router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@api_router.post("/query")
def ask_agent(request: Request, payload: QueryRequest):
    # Only create agent if not already attached
    if not hasattr(request.app.state, "internal_agent"):
        request.app.state.internal_agent = InternalAgent(
            request.app.state.qdrant_client
        )

    response = request.app.state.internal_agent.ask_agent(payload.query)
    return {"response": response}
