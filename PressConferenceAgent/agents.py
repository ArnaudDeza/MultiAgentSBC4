"""
Agent classes for the multi-agent press conference system.
"""

from ollama_utils import ollama_query
from prompts import (
    SPOKESPERSON_OPENING_PROMPT, SPOKESPERSON_RESPONSE_PROMPT,
    JOURNALIST_QUESTION_PROMPT, NOTE_TAKER_PROMPT, SUMMARIZER_PROMPT
)

class Agent:
    """Base class for all agents in the press conference."""
    def __init__(self, model: str, temp: float, seed: int):
        self.model = model
        self.temp = temp
        self.seed = seed

    def _query_llm(self, prompt: str) -> str:
        """Helper method to query the LLM with retry logic."""
        try:
            return ollama_query(
                ollama_model=self.model,
                prompt_to_LLM=prompt,
                temperature=self.temp,
                seed=self.seed
            )
        except Exception as e:
            print(f"Error querying model {self.model}: {e}. Retrying...")
            try:
                # Retry once with a different seed
                return ollama_query(
                    ollama_model=self.model,
                    prompt_to_LLM=prompt,
                    temperature=self.temp,
                    seed=self.seed + 1
                )
            except Exception as e2:
                print(f"Retry failed for model {self.model}: {e2}")
                return f"Agent using model {self.model} encountered an error."

class SpokespersonAgent(Agent):
    """Represents the spokesperson answering questions."""
    def generate_opening_statement(self, event_details: str) -> str:
        """Generates the initial statement about the event."""
        prompt = SPOKESPERSON_OPENING_PROMPT.format(event_details=event_details)
        return self._query_llm(prompt)

    def generate_response(self, event_details: str, transcript: str, question: str) -> str:
        """Responds to a journalist's question."""
        prompt = SPOKESPERSON_RESPONSE_PROMPT.format(
            event_details=event_details,
            transcript=transcript,
            question=question
        )
        return self._query_llm(prompt)

class JournalistAgent(Agent):
    """Represents a journalist asking questions with a specific bias."""
    def __init__(self, model: str, temp: float, seed: int, bias: str):
        super().__init__(model, temp, seed)
        self.bias = bias

    def generate_question(self, transcript: str) -> str:
        """Generates a question based on the transcript and bias."""
        prompt = JOURNALIST_QUESTION_PROMPT.format(
            bias=self.bias,
            transcript=transcript
        )
        return self._query_llm(prompt)

class NoteTakerAgent(Agent):
    """Represents the note-taker creating minutes."""
    def generate_minutes(self, transcript: str) -> str:
        """Converts the full transcript to meeting minutes."""
        prompt = NOTE_TAKER_PROMPT.format(transcript=transcript)
        return self._query_llm(prompt)

class SummarizerAgent(Agent):
    """Represents the summarizer creating a final summary."""
    def generate_summary(self, meeting_minutes: str) -> str:
        """Summarizes the meeting minutes."""
        prompt = SUMMARIZER_PROMPT.format(meeting_minutes=meeting_minutes)
        return self._query_llm(prompt) 