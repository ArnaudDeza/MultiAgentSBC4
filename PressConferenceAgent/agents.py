"""Agent classes for the simulated press conference."""

from typing import List, Dict, Any
from ollama_utils import ollama_query


class SpokespersonAgent:
    """Agent representing the spokesperson who gives opening statements and answers questions."""
    
    def __init__(self, model: str, temp: float, seed: int) -> None:
        """Initialize the SpokespersonAgent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
        """
        self.model = model
        self.temp = temp
        self.seed = seed
    
    def opening_statement(self, topic: str) -> str:
        """Generate an opening statement on the given topic.
        
        Args:
            topic: The topic for the press conference
            
        Returns:
            The opening statement text
        """
        prompt = f"As a spokesperson, give a brief but compelling opening statement on the topic: {topic}. Keep it professional and informative."
        return ollama_query(self.model, prompt, self.temp, self.seed)
    
    def answer_question(self, question: str) -> str:
        """Answer a question from a journalist.
        
        Args:
            question: The question from the journalist
            
        Returns:
            The answer to the question
        """
        prompt = f"Q: {question}\nA: "
        return ollama_query(self.model, prompt, self.temp, self.seed)


class JournalistAgent:
    """Agent representing a journalist who asks questions."""
    
    def __init__(self, id: int, model: str, temp: float, seed: int) -> None:
        """Initialize the JournalistAgent.
        
        Args:
            id: Unique identifier for this journalist
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
        """
        self.id = id
        self.model = model
        self.temp = temp
        self.seed = seed
    
    def ask_question(self, statement: str) -> str:
        """Ask a question based on the opening statement.
        
        Args:
            statement: The opening statement from the spokesperson
            
        Returns:
            A question to ask the spokesperson
        """
        prompt = f'As Journalist {self.id}, given this opening statement:\n"{statement}"\nWhat insightful question would you ask? Keep it concise and professional.'
        return ollama_query(self.model, prompt, self.temp, self.seed)


class NoteTakerAgent:
    """Agent responsible for summarizing the press conference into meeting minutes."""
    
    def __init__(self, model: str, temp: float, seed: int) -> None:
        """Initialize the NoteTakerAgent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
        """
        self.model = model
        self.temp = temp
        self.seed = seed
    
    def summarize(self, transcript: List[Dict[str, Any]]) -> str:
        """Summarize the press conference transcript into five bullet points.
        
        Args:
            transcript: List of conversation records from the press conference
            
        Returns:
            A summary in five bullet points
        """
        # Build the full transcript text
        transcript_text = "Here is the full press conference Q&A:\n"
        
        for record in transcript:
            if record.get("type") == "opening":
                transcript_text += f"Opening Statement: {record.get('text', '')}\n\n"
            elif record.get("type") == "question":
                journalist_id = record.get("journalist", "Unknown")
                transcript_text += f"Journalist {journalist_id}: {record.get('text', '')}\n"
            elif record.get("type") == "answer":
                transcript_text += f"Spokesperson: {record.get('text', '')}\n\n"
        
        transcript_text += "\nSummarize the key points and outcomes into exactly five bullet points."
        
        return ollama_query(self.model, transcript_text, self.temp, self.seed) 