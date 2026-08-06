from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_assistant import GuardianAIRAGAssistant

router = APIRouter()
assistant = GuardianAIRAGAssistant()

class ChatQueryRequest(BaseModel):
    query: str

class ChatQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence: float

@router.post("", response_model=ChatQueryResponse)
async def query_ai_assistant(request: ChatQueryRequest):
    result = await assistant.answer_query(request.query)
    return result
