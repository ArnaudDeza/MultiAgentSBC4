"""Player agents for Rock Paper Scissors using Ollama LLM."""

import re
import random
from typing import Optional, List
from pydantic import BaseModel
from ollama_utils import ollama_query
from utils import Move, parse_move


class PlayerAgent(BaseModel):
    """A Rock Paper Scissors player agent powered by Ollama LLM."""
    
    model: str
    temperature: float = 0.7
    seed: int = 42
    name: Optional[str] = None
    
    def __init__(self, **data):
        """Initialize the PlayerAgent."""
        super().__init__(**data)
        if self.name is None:
            self.name = self.model
    
    def make_move(self, round_num: int = 1, opponent_history: List[Move] = None, 
                  own_history: List[Move] = None) -> Move:
        """Make a move in Rock Paper Scissors.
        
        Args:
            round_num: Current round number
            opponent_history: List of opponent's previous moves
            own_history: List of own previous moves
            
        Returns:
            Move enum representing the chosen move
        """
        # Create context-aware prompt
        prompt = self._create_move_prompt(round_num, opponent_history, own_history)
        
        # Get response from LLM
        response = ollama_query(self.model, prompt, self.temperature, self.seed + round_num)
        
        # Parse the move from the response
        move = self._parse_move_from_response(response)
        
        return move
    
    def _create_move_prompt(self, round_num: int, opponent_history: Optional[List[Move]], 
                           own_history: Optional[List[Move]]) -> str:
        """Create a context-aware prompt for the LLM.
        
        Args:
            round_num: Current round number
            opponent_history: List of opponent's previous moves
            own_history: List of own previous moves
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"You are playing Rock Paper Scissors as '{self.name}'.",
            f"This is round {round_num}.",
            "",
            "Rules:",
            "- Rock beats Scissors",
            "- Paper beats Rock", 
            "- Scissors beats Paper",
            "- Same moves result in a draw",
            ""
        ]
        
        # Add history context if available
        if opponent_history and own_history and len(opponent_history) > 0:
            prompt_parts.extend([
                "Game history:",
                f"Your previous moves: {[move.value for move in own_history]}",
                f"Opponent's previous moves: {[move.value for move in opponent_history]}",
                ""
            ])
            
            # Add some strategic analysis
            if len(opponent_history) >= 2:
                last_moves = [move.value for move in opponent_history[-3:]]
                prompt_parts.append(f"Opponent's recent pattern: {' -> '.join(last_moves)}")
                prompt_parts.append("")
        
        prompt_parts.extend([
            "Choose your move for this round. Respond with ONLY one of these words:",
            "- rock",
            "- paper", 
            "- scissors",
            "",
            "Your move:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_move_from_response(self, response: str) -> Move:
        """Parse the LLM response to extract a move.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Move enum value
        """
        # Clean up the response
        response = response.lower().strip()
        
        # Try direct parsing first
        try:
            return parse_move(response)
        except ValueError:
            pass
        
        # Look for move words in the response
        move_patterns = {
            'rock': Move.ROCK,
            'paper': Move.PAPER,
            'scissors': Move.SCISSORS,
            'scissor': Move.SCISSORS,
            'stone': Move.ROCK,
        }
        
        for pattern, move in move_patterns.items():
            if pattern in response:
                return move
        
        # Look for single letter patterns
        if 'r' in response and 'p' not in response and 's' not in response:
            return Move.ROCK
        elif 'p' in response and 'r' not in response and 's' not in response:
            return Move.PAPER
        elif 's' in response and 'r' not in response and 'p' not in response:
            return Move.SCISSORS
        
        # If all parsing fails, return a random move
        return random.choice(list(Move))
    
    def get_strategy_description(self) -> str:
        """Get a description of this agent's strategy.
        
        Returns:
            Strategy description string
        """
        strategies = [
            f"{self.name} uses adaptive pattern recognition",
            f"{self.name} employs mixed strategy with psychological insight",
            f"{self.name} analyzes opponent behavior for optimal counter-play",
            f"{self.name} uses temperature {self.temperature} for balanced randomness",
        ]
        
        return random.choice(strategies)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class RandomAgent(PlayerAgent):
    """A simple random agent for baseline comparison."""
    
    def make_move(self, round_num: int = 1, opponent_history: List[Move] = None, 
                  own_history: List[Move] = None) -> Move:
        """Make a random move.
        
        Args:
            round_num: Current round number (ignored)
            opponent_history: Opponent's history (ignored)
            own_history: Own history (ignored)
            
        Returns:
            Random Move enum value
        """
        return random.choice(list(Move))
    
    def get_strategy_description(self) -> str:
        """Get strategy description for random agent.
        
        Returns:
            Strategy description
        """
        return f"{self.name} uses pure random strategy"


class CounterAgent(PlayerAgent):
    """An agent that tries to counter the opponent's most frequent move."""
    
    def make_move(self, round_num: int = 1, opponent_history: List[Move] = None, 
                  own_history: List[Move] = None) -> Move:
        """Make a move that counters opponent's most frequent move.
        
        Args:
            round_num: Current round number
            opponent_history: List of opponent's previous moves
            own_history: List of own previous moves (ignored)
            
        Returns:
            Counter move
        """
        if not opponent_history or len(opponent_history) == 0:
            return random.choice(list(Move))
        
        # Count opponent's moves
        move_counts = {
            Move.ROCK: opponent_history.count(Move.ROCK),
            Move.PAPER: opponent_history.count(Move.PAPER),
            Move.SCISSORS: opponent_history.count(Move.SCISSORS)
        }
        
        # Find most frequent move
        most_frequent = max(move_counts, key=move_counts.get)
        
        # Return counter move
        counters = {
            Move.ROCK: Move.PAPER,
            Move.PAPER: Move.SCISSORS,
            Move.SCISSORS: Move.ROCK
        }
        
        return counters[most_frequent]
    
    def get_strategy_description(self) -> str:
        """Get strategy description for counter agent.
        
        Returns:
            Strategy description
        """
        return f"{self.name} counters opponent's most frequent move"


def create_agent(model: str, agent_type: str = "llm", temperature: float = 0.7, 
                seed: int = 42, name: Optional[str] = None) -> PlayerAgent:
    """Factory function to create different types of agents.
    
    Args:
        model: Model name for LLM agents
        agent_type: Type of agent ("llm", "random", "counter")
        temperature: Temperature for LLM agents
        seed: Random seed
        name: Optional custom name
        
    Returns:
        PlayerAgent instance
    """
    if agent_type == "random":
        return RandomAgent(model=model, temperature=temperature, seed=seed, name=name or "Random")
    elif agent_type == "counter":
        return CounterAgent(model=model, temperature=temperature, seed=seed, name=name or "Counter")
    else:
        return PlayerAgent(model=model, temperature=temperature, seed=seed, name=name) 