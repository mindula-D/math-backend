# models\request_models.py
from pydantic import BaseModel
from typing import Optional

class SessionRequest(BaseModel):
    """Request model for starting a new session"""
    skill: str

class AnswerRequest(BaseModel):
    """Request model for submitting an answer"""
    session_id: int
    answer: Optional[str] = None
    response_time: float = 0
    skip: bool = False

class HintRequest(BaseModel):
    """Request model for getting a hint"""
    session_id: int