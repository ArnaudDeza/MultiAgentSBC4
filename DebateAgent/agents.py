"""
Agent classes for multi-agent debate system.
"""

import re
from typing import List, Dict, Any, Tuple
from ollama_utils import ollama_query
from config import (
    DEFAULT_NUM_CTX, DEFAULT_TOP_K, DEFAULT_TOP_P, 
    DEFAULT_MIN_P, DEFAULT_REPEAT_PENALTY
)
from prompts import JUDGE_SYSTEM_PROMPT


class DebateAgent:
    """Agent that participates in debates using an LLM."""
    
    def __init__(self, agent_id: int, model: str, temp: float, seed: int) -> None:
        """
        Initialize debate agent.
        
        Args:
            agent_id: Unique identifier for this agent
            model: Ollama model name to use
            temp: Temperature for generation
            seed: Random seed for reproducibility
        """
        self.agent_id = agent_id
        self.model = model
        self.temp = temp
        self.seed = seed
        
    def respond(self, message: str) -> str:
        """
        Generate response to a message using the LLM.
        
        Args:
            message: Input prompt/message
            
        Returns:
            LLM response text
        """
        try:
            # First attempt to get a response
            return ollama_query(
                ollama_model=self.model,
                prompt_to_LLM=message,
                temperature=self.temp,
                seed=self.seed,
                num_ctx=DEFAULT_NUM_CTX,
                top_k=DEFAULT_TOP_K,
                top_p=DEFAULT_TOP_P,
                min_p=DEFAULT_MIN_P,
                repeat_penalty=DEFAULT_REPEAT_PENALTY
            )
        except Exception as e:
            print(f"Error in agent {self.agent_id} response: {e}. Retrying once...")
            try:
                # Retry once with a different seed
                return ollama_query(
                    ollama_model=self.model,
                    prompt_to_LLM=message,
                    temperature=self.temp,
                    seed=self.seed + 1,  # Use a different seed for the retry
                    num_ctx=DEFAULT_NUM_CTX,
                    top_k=DEFAULT_TOP_K,
                    top_p=DEFAULT_TOP_P,
                    min_p=DEFAULT_MIN_P,
                    repeat_penalty=DEFAULT_REPEAT_PENALTY
                )
            except Exception as e2:
                print(f"Retry failed for agent {self.agent_id}: {e2}")
                return f"Agent {self.agent_id} encountered an error and could not respond."


class JudgeAgent:
    """Agent that judges debate outcomes."""
    
    def __init__(self, model: str, temp: float, seed: int) -> None:
        """
        Initialize judge agent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature for generation
            seed: Random seed for reproducibility
        """
        self.model = model
        self.temp = temp
        self.seed = seed
        
    def pick_winner(self, transcripts: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Analyze debate transcripts and pick a winner.
        
        Args:
            transcripts: List of debate log records
            
        Returns:
            Tuple of (winner_id, justification)
        """
        # Format the transcript for the prompt
        formatted_transcript = ""
        for record in transcripts:
            if "agent" in record and "message" in record:
                formatted_transcript += f"Round {record.get('round', 'N/A')}, Agent {record['agent']}: {record['message']}\n\n"
        
        prompt = JUDGE_SYSTEM_PROMPT.format(transcript=formatted_transcript)
        
        try:
            response = ollama_query(
                ollama_model=self.model,
                prompt_to_LLM=prompt,
                temperature=self.temp,
                seed=self.seed,
                num_ctx=DEFAULT_NUM_CTX,
                top_k=DEFAULT_TOP_K,
                top_p=DEFAULT_TOP_P,
                min_p=DEFAULT_MIN_P,
                repeat_penalty=DEFAULT_REPEAT_PENALTY
            )
            
            # Parse the winner and justification from the response
            winner_match = re.search(r"Winner: Agent (\w+)", response, re.IGNORECASE)
            justification_match = re.search(r"Justification: (.*)", response, re.DOTALL | re.IGNORECASE)
            
            winner_id = "Unknown"
            justification = "Could not parse justification from response."

            if winner_match:
                winner_id = winner_match.group(1).strip()
            
            if justification_match:
                justification = justification_match.group(1).strip()
            else:
                 justification = response # Return the full response if parsing fails

            return winner_id, justification

        except Exception as e:
            print(f"Error in judge agent response: {e}")
            return "Error", f"An exception occurred while judging: {e}"
         