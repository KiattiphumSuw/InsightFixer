from fastapi import APIRouter
from pydantic import BaseModel
from src.core.internal_agent import InternalAgent

router = APIRouter()
internal_agent = InternalAgent()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def ask_agent(request: QueryRequest):
    response = internal_agent.ask_agent(request.query)
    return {"response": response}
