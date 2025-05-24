# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import Pydantic models
from models.request_models import SessionRequest, AnswerRequest, HintRequest

# Import services
from services.session import (
    create_new_session,
    process_answer,
    generate_hint,
    get_session,
)

# Load environment variables
load_dotenv()

# Initialize app
app = FastAPI(title="Math Skills Practice API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/start-session")
async def start_session(request: SessionRequest):
    """Start a new learning session for a specific skill"""
    return create_new_session(request.skill)

@app.post("/api/submit-answer")
async def submit_answer(request: AnswerRequest):
    """Submit an answer for the current question"""
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    return process_answer(
        session_id=request.session_id,
        answer=request.answer,
        response_time=request.response_time,
        is_skip=request.skip
    )

@app.post("/api/get-hint")
async def get_hint_endpoint(request: HintRequest):
    """Get a hint for the current question"""
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    return generate_hint(request.session_id)

if __name__ == '__main__':
    import uvicorn
    # Use PORT environment variable if available (Azure), otherwise default to 5001
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)