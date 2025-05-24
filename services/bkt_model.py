# services\bkt_model.py
import pandas as pd
from pyBKT.models import Model
from typing import Dict, List, Optional

# Skill-to-model mapping
SKILL_MAPPING = {
    "Addition": "bkt_model_addition.pkl",
    "Subtraction": "bkt_model_subtraction.pkl",
    "Multiplication": "bkt_model_multiplication.pkl",
    "Division": "bkt_model_division.pkl"
}

# Global model cache to avoid reloading models
MODEL_CACHE = {}

def load_model(skill_name: str) -> Optional[Model]:
    """
    Load BKT model from cache or file
    
    Args:
        skill_name: The name of the skill to load the model for
        
    Returns:
        The loaded BKT model or None if loading failed
    """
    if skill_name not in MODEL_CACHE:
        try:
            model = Model()
            model.load(SKILL_MAPPING[skill_name])
            MODEL_CACHE[skill_name] = model
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None
    return MODEL_CACHE[skill_name]

def predict_mastery(model: Model, responses: List[Dict]) -> float:
    """
    Predict mastery level using BKT model
    
    Args:
        model: The BKT model to use for prediction
        responses: List of student responses
        
    Returns:
        Predicted mastery probability (0.0-1.0)
    """
    try:
        df = pd.DataFrame(responses)
        if len(df) > 0:
            predictions = model.predict(data=df)
            return predictions.iloc[-1]["state_predictions"]
    except Exception as e:
        print(f"Error predicting mastery: {str(e)}")
    return 0.5  # Default mastery if prediction fails

def is_valid_skill(skill_name: str) -> bool:
    """
    Check if the provided skill name is valid
    
    Args:
        skill_name: The name of the skill to check
        
    Returns:
        True if valid, False otherwise
    """
    return skill_name in SKILL_MAPPING