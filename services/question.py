# services\question.py
import random
from typing import Dict, Any

def generate_question(skill: str, difficulty: str) -> Dict[str, Any]:
    """
    Generate a question for the specified skill and difficulty level
    
    Args:
        skill: The skill type (Addition, Subtraction, etc.)
        difficulty: The difficulty level (Easy, Medium, Hard)
        
    Returns:
        A dictionary containing the question and answer
    """
    if skill == "Addition":
        if difficulty == "Easy":
            a, b = random.randint(1, 10), random.randint(1, 10)
        elif difficulty == "Medium":
            a, b = random.randint(10, 50), random.randint(10, 50)
        else:  # Hard
            a, b = random.randint(50, 200), random.randint(50, 200)
        return {"question": f"{a} + {b} = ?", "answer": a + b}
    
    elif skill == "Subtraction":
        if difficulty == "Easy":
            a, b = random.randint(5, 15), random.randint(1, 10)
        elif difficulty == "Medium":
            a, b = random.randint(20, 100), random.randint(10, 50)
        else:  # Hard
            a, b = random.randint(100, 500), random.randint(50, 300)
        return {"question": f"{a} - {b} = ?", "answer": a - b}
    
    elif skill == "Multiplication":
        if difficulty == "Easy":
            a, b = random.randint(1, 5), random.randint(1, 5)
        elif difficulty == "Medium":
            a, b = random.randint(6, 12), random.randint(6, 12)
        else:  # Hard
            a, b = random.randint(13, 20), random.randint(13, 20)
        return {"question": f"{a} × {b} = ?", "answer": a * b}
    
    elif skill == "Division":
        if difficulty == "Easy":
            a, b = random.randint(1, 5), random.randint(1, 5)
        elif difficulty == "Medium":
            a, b = random.randint(6, 20), random.randint(1, 5)
        else:  # Hard
            a, b = random.randint(21, 50), random.randint(6, 10)
        return {"question": f"{a * b} ÷ {b} = ?", "answer": a}