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

def analyze_emotion(image_path: str, model: str = "llama3.2-vision") -> EmotionResponse:
    """
    Analyzes an image to detect emotions using an Ollama vision model.

    Args:
        image_path: The path to the image file.
        model: The name of the Ollama model to use.

    Returns:
        An EmotionResponse object containing the list of detected emotions.
    """
    # TODO: Define the prompt for the vision model.
    # The prompt should instruct the model to analyze the image and return emotion
    # scores (happiness, sadness, etc.) as a JSON object. You can use the
    # EmotionResponse.model_json_schema() to get the required JSON structure.
    prompt_text = "..."

    # TODO: Read the image file from `image_path` in binary mode.
    # The 'images' parameter of ollama.chat expects a list of byte arrays.
    image_bytes = b""

    # TODO: Call the Ollama chat API.
    # Use ollama.chat() with the specified model, the user prompt (including the
    # prompt text and image bytes), and set format='json' to ensure the
    # model returns a JSON response. Set temperature to 0 for deterministic output.
    res = {}

    # TODO: Parse the JSON response from the model.
    # The response content is in res['message']['content'].
    # Use EmotionResponse.model_validate_json() to parse this string
    # into a Pydantic object.
    response_content = ""
    parsed_response = None

    # TODO: Return the parsed EmotionResponse object.
    return parsed_response
