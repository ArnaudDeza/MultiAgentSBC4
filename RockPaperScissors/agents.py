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
        
        # Ensure name clearly identifies the model for logging
        if self.model not in self.name and self.name != self.model:
            self.name = f"{self.model}({self.name})"
    
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
        """Create a comprehensive, context-aware prompt for the LLM.
        
        Args:
            round_num: Current round number in this match
            opponent_history: List of opponent's previous moves in this match
            own_history: List of own previous moves in this match
            
        Returns:
            Detailed formatted prompt string with complete match context
        """
        prompt_parts = [
            "=" * 60,
            "ROCK PAPER SCISSORS TOURNAMENT - MATCH IN PROGRESS",
            "=" * 60,
            "",
            f"🤖 You are: {self.name}",
            f"🎯 Current Round: {round_num}",
            "",
            "📋 GAME RULES:",
            "• Rock beats Scissors (crushes)",
            "• Paper beats Rock (covers)", 
            "• Scissors beats Paper (cuts)",
            "• Identical moves = Draw",
            "",
            "🏆 MATCH FORMAT:",
            "• This is a multi-round match between two LLM agents",
            "• Each round, both players simultaneously choose: rock, paper, or scissors",
            "• Winner is determined by best performance across all rounds",
            "• You can see the complete playing history below",
            ""
        ]
        
        # Add detailed match history if available
        if opponent_history is not None and own_history is not None:
            if len(opponent_history) > 0:
                prompt_parts.extend([
                    "📊 COMPLETE MATCH HISTORY:",
                    "-" * 40,
                ])
                
                # Create round-by-round breakdown
                for i in range(len(opponent_history)):
                    your_move = own_history[i].value
                    opp_move = opponent_history[i].value
                    
                    # Determine round result
                    if your_move == opp_move:
                        result = "DRAW"
                        emoji = "🤝"
                    elif ((your_move == "rock" and opp_move == "scissors") or
                          (your_move == "paper" and opp_move == "rock") or
                          (your_move == "scissors" and opp_move == "paper")):
                        result = "YOU WON"
                        emoji = "✅"
                    else:
                        result = "YOU LOST"
                        emoji = "❌"
                    
                    prompt_parts.append(f"Round {i+1:2d}: You={your_move:8s} | Opponent={opp_move:8s} | {emoji} {result}")
                
                prompt_parts.extend(["", "📈 PATTERN ANALYSIS:"])
                
                # Your move frequency
                your_rock = own_history.count(Move.ROCK)
                your_paper = own_history.count(Move.PAPER)
                your_scissors = own_history.count(Move.SCISSORS)
                total_rounds = len(own_history)
                
                prompt_parts.extend([
                    f"Your move frequency: Rock={your_rock}/{total_rounds} Paper={your_paper}/{total_rounds} Scissors={your_scissors}/{total_rounds}",
                ])
                
                # Opponent move frequency  
                opp_rock = opponent_history.count(Move.ROCK)
                opp_paper = opponent_history.count(Move.PAPER)
                opp_scissors = opponent_history.count(Move.SCISSORS)
                
                prompt_parts.extend([
                    f"Opponent frequency:   Rock={opp_rock}/{total_rounds} Paper={opp_paper}/{total_rounds} Scissors={opp_scissors}/{total_rounds}",
                    ""
                ])
                
                # Recent patterns
                if len(opponent_history) >= 3:
                    recent_yours = " → ".join([move.value for move in own_history[-3:]])
                    recent_opps = " → ".join([move.value for move in opponent_history[-3:]])
                    prompt_parts.extend([
                        "🔍 RECENT PATTERNS (last 3 rounds):",
                        f"Your recent moves:     {recent_yours}",
                        f"Opponent recent moves: {recent_opps}",
                        ""
                    ])
                
                # Calculate current score
                wins = 0
                losses = 0
                draws = 0
                for i in range(len(opponent_history)):
                    your_move = own_history[i]
                    opp_move = opponent_history[i]
                    if your_move == opp_move:
                        draws += 1
                    elif ((your_move == Move.ROCK and opp_move == Move.SCISSORS) or
                          (your_move == Move.PAPER and opp_move == Move.ROCK) or
                          (your_move == Move.SCISSORS and opp_move == Move.PAPER)):
                        wins += 1
                    else:
                        losses += 1
                
                prompt_parts.extend([
                    f"📊 CURRENT MATCH SCORE:",
                    f"Wins: {wins} | Losses: {losses} | Draws: {draws}",
                    f"Win Rate: {wins/total_rounds:.1%}" if total_rounds > 0 else "Win Rate: 0%",
                    ""
                ])
            else:
                prompt_parts.extend([
                    "📊 MATCH STATUS:",
                    "• This is the first round of the match",
                    "• No previous history available",
                    "• Both players start fresh",
                    ""
                ])
        else:
            prompt_parts.extend([
                "📊 MATCH STATUS:",
                "• Match information not available",
                "• Playing as standalone round",
                ""
            ])
        
        prompt_parts.extend([
            "🎯 YOUR TASK FOR THIS ROUND:",
            "Analyze the complete match history above and choose your move strategically.",
            "Consider patterns, frequencies, and opponent behavior to maximize your chances.",
            "",
            "⚡ RESPOND WITH EXACTLY ONE WORD:",
            "• rock",
            "• paper", 
            "• scissors",
            "",
            "💭 Think strategically based on the history, then choose:",
            ""
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