# models\session.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class SessionData(BaseModel):
    """Model for session data"""
    skill: str
    question_number: int
    responses: List[Dict[str, Any]]
    progress: List[Dict[str, Any]]
    current_difficulty: str
    current_answer: int
    current_question: str
    mastery_prob: float
    skipped_questions: int
    hints_remaining: int
    hints_used: List[Dict[str, Any]]

class ResponseLog(BaseModel):
    """Model for logging student responses"""
    user_id: int = 1
    skill_name: str
    correct: int

class ProgressEntry(BaseModel):
    """Model for tracking progress"""
    question_number: int
    difficulty: str
    correct: Optional[bool]
    response_time: Optional[float]
    mastery_probability: float
    skipped: bool