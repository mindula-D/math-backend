# services\session.py
import random
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
import traceback

# Import services & utils
from services.bkt_model import load_model, predict_mastery, is_valid_skill
from services.question import generate_question
from utils.helpers import adjust_difficulty

import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Correct way to fetch the API key
genai_api_key = os.getenv("GEMINI_API_KEY")

if not genai_api_key:
    raise ValueError("GEMINI_API_KEY is missing in the .env file")

genai.configure(api_key=genai_api_key)
gemini_model = GenerativeModel('gemini-2.0-flash')


# In-memory session storage
SESSIONS = {}

def get_session(session_id: int) -> Optional[Dict[str, Any]]:
    """Get session data by ID"""
    return SESSIONS.get(session_id)

def create_new_session(skill: str) -> Dict[str, Any]:
    """
    Create a new learning session
    
    Args:
        skill: The skill to practice
        
    Returns:
        Session initialization data
    """
    try:
        if not is_valid_skill(skill):
            raise HTTPException(status_code=400, detail="Invalid skill selected")
        
        # Load model
        model = load_model(skill)
        if model is None:
            raise HTTPException(status_code=500, detail="Error loading model")
        
        # Generate session ID and initial question
        session_id = random.randint(10000, 99999)
        question_data = generate_question(skill, "Easy")
        
        # Create session data
        SESSIONS[session_id] = {
            'skill': skill,
            'question_number': 0,
            'responses': [],
            'progress': [],
            'current_difficulty': "Easy",
            'current_answer': question_data['answer'],
            'current_question': question_data['question'],
            'mastery_prob': 0.1,
            'skipped_questions': 0,
            'hints_remaining': 3,
            'hints_used': []
        }
        
        # Return initial data
        return {
            'session_id': session_id,
            'question': question_data['question'],
            'difficulty': "Easy",
            'question_number': 1,
            'total_questions': 10,
            'skips_remaining': 3
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_new_session: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

def process_answer(
    session_id: int, 
    answer: Optional[str], 
    response_time: float, 
    is_skip: bool
) -> Dict[str, Any]:
    """
    Process a submitted answer
    
    Args:
        session_id: The session ID
        answer: The submitted answer (can be None if skipped)
        response_time: Time taken to respond in seconds
        is_skip: Whether the question was skipped
        
    Returns:
        Response with next question or session summary
    """
    try:
        session = SESSIONS[session_id]
        session['question_number'] += 1

        # Handle skipped questions
        if is_skip:
            if session['skipped_questions'] >= 3:
                raise HTTPException(status_code=400, detail="No skips remaining")
            
            session['skipped_questions'] += 1
            is_correct = None  # Mark skipped questions as None
            
            # Count skips as incorrect for BKT model
            session['responses'].append({
                "user_id": 1,
                "skill_name": session['skill'],
                "correct": 0
            })
        else:
            # Normal answer submission logic
            try:
                is_correct = int(answer) == session['current_answer']
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Invalid answer format")

            # Log response
            session['responses'].append({
                "user_id": 1,
                "skill_name": session['skill'],
                "correct": int(is_correct)
            })

            # Update mastery probability using BKT model
            bkt_model = load_model(session['skill'])
            if bkt_model:
                new_mastery = predict_mastery(bkt_model, session['responses'])
                smoothing_weight = 0.5 if is_correct else (-1.0)
                adjusted_mastery = smoothing_weight * new_mastery + (1 - smoothing_weight) * session['mastery_prob']
                adjusted_mastery = max(0.1, min(0.99, adjusted_mastery))
                session['mastery_prob'] = adjusted_mastery

        # Log progress
        session['progress'].append({
            'question_number': session['question_number'],
            'difficulty': session['current_difficulty'],
            'correct': is_correct,
            'response_time': response_time if not is_skip else None,
            'mastery_probability': session['mastery_prob'],
            'skipped': is_skip
        })

        # Check if session is complete
        if session['question_number'] >= 10:
            # Calculate non-skipped questions with response times
            valid_response_times = [p['response_time'] for p in session['progress'] 
                                    if p['response_time'] is not None]
            
            avg_response_time = (sum(valid_response_times) / len(valid_response_times)) if valid_response_times else 0
            
            summary = {
                'total_questions': 10,
                'correct_answers': sum(1 for p in session['progress'] if p['correct'] is True),
                'skipped_questions': sum(1 for p in session['progress'] if p['skipped']),
                'average_response_time': avg_response_time,
                'final_mastery': session['mastery_prob'],
                'progress': session['progress'],
                'correct_answer': str(session['current_answer']),
                'is_correct': is_correct,
                'difficulty': session['current_difficulty'],
                'mastery_probability': session['mastery_prob']
            }
            
            # Clean up session data
            del SESSIONS[session_id]
            
            return {
                'status': 'complete',
                'summary': summary,
                'correct_answer': str(session['current_answer']),
                'is_correct': is_correct,
                'difficulty': session['current_difficulty'],
                'mastery_probability': session['mastery_prob']
            }

        # Generate next question
        difficulty = adjust_difficulty(session['mastery_prob'])
        question_data = generate_question(session['skill'], difficulty)

        session['current_difficulty'] = difficulty
        session['current_answer'] = question_data['answer']
        session['current_question'] = question_data['question']

        return {
            'status': 'continue',
            'question': question_data['question'],
            'correct_answer': str(session['current_answer']),
            'difficulty': difficulty,
            'question_number': session['question_number'] + 1,
            'total_questions': 10,
            'mastery_probability': session['mastery_prob'],
            'is_correct': is_correct,
            'skips_remaining': 3 - session['skipped_questions']
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in process_answer: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

def generate_hint(session_id: int) -> Dict[str, Any]:
    """
    Generate a hint for the current question
    
    Args:
        session_id: The session ID
        
    Returns:
        A hint and the number of hints remaining
    """
    try:
        session = SESSIONS[session_id]
        
        if session['hints_remaining'] <= 0:
            raise HTTPException(status_code=400, detail="No hints remaining")

        if 'current_question' not in session:
            raise HTTPException(status_code=400, detail="No current question found")

        current_question = session['current_question']
        current_answer = session['current_answer']
        
        # Create an age-appropriate prompt for Gemini
        prompt = f"""
        You are helping a 3rd grade student solve this math problem: {current_question}
        The answer is {current_answer}.
        Give a simple, encouraging hint that helps them think about the problem without giving away the answer.
        Make the hint very short (1-2 sentences) and easy to understand for a 3rd grader.
        Don't use complex mathematical terms.
        """

        # Generate hint using Gemini
        response = gemini_model.generate_content(prompt)
        hint = response.text

        # Update session data
        session['hints_remaining'] -= 1
        session['hints_used'].append({
            'question': current_question,
            'hint': hint,
            'timestamp': datetime.now().isoformat()
        })

        return {
            'hint': hint,
            'hints_remaining': session['hints_remaining']
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating hint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to generate hint")