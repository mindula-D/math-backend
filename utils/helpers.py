# utils\helpers.py
from typing import Dict, Any

def adjust_difficulty(mastery_prob: float) -> str:
    """
    Determine difficulty level based on mastery probability
    
    Args:
        mastery_prob: The current mastery probability (0.0-1.0)
        
    Returns:
        The appropriate difficulty level (Easy, Medium, Hard)
    """
    if mastery_prob < 0.5:
        return "Easy"
    elif mastery_prob < 0.8:
        return "Medium"
    else:
        return "Hard"

def adjust_mastery_with_time(mastery_prob: float, response_time: float) -> float:
    """
    Adjust mastery probability based on response time
    
    Args:
        mastery_prob: Current mastery probability
        response_time: Time taken to respond in seconds
        
    Returns:
        Adjusted mastery probability
    """
    T_ideal = 5  # Ideal response time in seconds
    T_max = 20   # Maximum threshold for penalty application
    
    if response_time <= T_ideal:
        return mastery_prob  # No penalty if within ideal time
    
    # Compute penalty factor (linear decay)
    penalty_factor = 1 - (min(response_time, T_max) - T_ideal) / (T_max - T_ideal)
    penalty_factor = max(0.5, penalty_factor)  # Ensure a minimum penalty of 0.5
    
    # Apply penalty to mastery probability
    adjusted_mastery = mastery_prob * penalty_factor
    return max(0.1, min(0.99, adjusted_mastery))  # Keep within valid range