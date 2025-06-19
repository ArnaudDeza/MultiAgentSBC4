import ollama
from pydantic import BaseModel
from typing import List
from pathlib import Path
import json

class Emotion(BaseModel):
    """Represents a single detected emotion with its corresponding score."""
    name: str
    score: float

class EmotionResponse(BaseModel):
    """Represents the list of emotions detected in an image."""
    emotions: List[Emotion]

def analyze_emotion(image_path: str, model: str = "gemma3:4b") -> EmotionResponse:
    """
    Analyzes an image to detect emotions using an Ollama vision model.

    Args:
        image_path: The path to the image file.
        model: The name of the Ollama model to use.

    Returns:
        An EmotionResponse object containing the list of detected emotions.
    """
    prompt_text = f"""
    Analyze the facial expression in this image and provide the intensity of the following
    emotions as scores between 0 and 1: happiness, sadness, anger, fear, surprise, disgust, and neutral.

    Respond with ONLY a JSON object that follows this schema:
    {json.dumps(EmotionResponse.model_json_schema(), indent=2)}
    """
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    res = ollama.chat(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': prompt_text,
                'images': [image_bytes]
            }
        ],
        format='json',
        options={'temperature': 0}
    )

    response_content = res['message']['content']
    return EmotionResponse.model_validate_json(response_content)
