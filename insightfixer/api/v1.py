from fastapi import APIRouter
from pydantic import BaseModel
from core import InternalAgent

api_router = APIRouter()
internal_agent = InternalAgent()

class QueryRequest(BaseModel):
    query: str

@api_router.post("/query")
def ask_agent(request: QueryRequest):
    response = internal_agent.ask_agent(request.query)
    return {"response": response}
