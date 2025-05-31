from fastapi import APIRouter
from pydantic import BaseModel
from src.core.internal_agent import run_agent

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def ask_agent(request: QueryRequest):
    response = run_agent(request.query)
    return {"response": response}
