"""JSONL logging and scoring utilities for Rock Paper Scissors Royale."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple
from enum import Enum


class Move(Enum):
    """Valid moves in Rock Paper Scissors."""
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class GameResult(Enum):
    """Game result outcomes."""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


def ensure_data_directories() -> None:
    """Ensure the data and logs directories exist."""
    os.makedirs("data/logs", exist_ok=True)


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def determine_winner(move1: Move, move2: Move) -> Tuple[GameResult, GameResult]:
    """Determine the winner of a Rock Paper Scissors match.
    
    Args:
        move1: First player's move
        move2: Second player's move
        
    Returns:
        Tuple of (result_for_player1, result_for_player2)
    """
    if move1 == move2:
        return GameResult.DRAW, GameResult.DRAW
    
    winning_combinations = {
        (Move.ROCK, Move.SCISSORS),
        (Move.PAPER, Move.ROCK),
        (Move.SCISSORS, Move.PAPER)
    }
    
    if (move1, move2) in winning_combinations:
        return GameResult.WIN, GameResult.LOSS
    else:
        return GameResult.LOSS, GameResult.WIN


def parse_move(move_str: str) -> Move:
    """Parse a move string into a Move enum.
    
    Args:
        move_str: String representation of the move
        
    Returns:
        Move enum value
        
    Raises:
        ValueError: If the move string is invalid
    """
    move_str = move_str.lower().strip()
    
    # Handle common variations
    move_mappings = {
        'rock': Move.ROCK,
        'r': Move.ROCK,
        'stone': Move.ROCK,
        'paper': Move.PAPER,
        'p': Move.PAPER,
        'scissors': Move.SCISSORS,
        's': Move.SCISSORS,
        'scissor': Move.SCISSORS,
    }
    
    if move_str in move_mappings:
        return move_mappings[move_str]
    
    raise ValueError(f"Invalid move: {move_str}")


class RPSLogger:
    """Logger for Rock Paper Scissors tournament matches and results."""
    
    def __init__(self, log_file: str = "data/logs/tournament.jsonl") -> None:
        """Initialize the logger.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.log_file = log_file
        ensure_data_directories()
        
        # Clear the log file at the start of a new tournament
        with open(self.log_file, 'w') as f:
            pass  # Just clear the file
    
    def log_tournament_start(self, models: List[str], tournament_type: str, rounds: int) -> None:
        """Log the start of a tournament.
        
        Args:
            models: List of participating models
            tournament_type: Type of tournament (e.g., "round_robin", "single_elimination")
            rounds: Number of rounds or matches
        """
        record = {
            "timestamp": now_iso(),
            "type": "tournament_start",
            "models": models,
            "tournament_type": tournament_type,
            "rounds": rounds
        }
        self._write_record(record)
    
    def log_match(self, match_id: str, player1: str, player2: str, 
                  move1: Move, move2: Move, result1: GameResult, result2: GameResult) -> None:
        """Log a single match result.
        
        Args:
            match_id: Unique identifier for the match
            player1: First player model name
            player2: Second player model name
            move1: First player's move
            move2: Second player's move
            result1: Result for first player
            result2: Result for second player
        """
        record = {
            "timestamp": now_iso(),
            "type": "match",
            "match_id": match_id,
            "player1": player1,
            "player2": player2,
            "move1": move1.value,
            "move2": move2.value,
            "result1": result1.value,
            "result2": result2.value
        }
        self._write_record(record)
    
    def log_round_summary(self, round_num: int, standings: Dict[str, Any]) -> None:
        """Log the summary of a tournament round.
        
        Args:
            round_num: Round number
            standings: Current tournament standings
        """
        record = {
            "timestamp": now_iso(),
            "type": "round_summary",
            "round": round_num,
            "standings": standings
        }
        self._write_record(record)
    
    def log_tournament_end(self, final_standings: Dict[str, Any], champion: str) -> None:
        """Log the end of a tournament with final results.
        
        Args:
            final_standings: Final tournament standings
            champion: Tournament champion
        """
        record = {
            "timestamp": now_iso(),
            "type": "tournament_end",
            "final_standings": final_standings,
            "champion": champion
        }
        self._write_record(record)
    
    def _write_record(self, record: Dict[str, Any]) -> None:
        """Write a record to the JSONL file.
        
        Args:
            record: Dictionary to write as JSON
        """
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")


class TournamentScorer:
    """Manages scoring and standings for tournaments."""
    
    def __init__(self, models: List[str]) -> None:
        """Initialize the scorer.
        
        Args:
            models: List of participating models
        """
        self.models = models
        self.reset_scores()
    
    def reset_scores(self) -> None:
        """Reset all scores to zero."""
        self.wins = {model: 0 for model in self.models}
        self.losses = {model: 0 for model in self.models}
        self.draws = {model: 0 for model in self.models}
        self.matches_played = {model: 0 for model in self.models}
    
    def record_match(self, player1: str, player2: str, result1: GameResult, result2: GameResult) -> None:
        """Record the result of a match.
        
        Args:
            player1: First player model name
            player2: Second player model name
            result1: Result for first player
            result2: Result for second player
        """
        # Update match counts
        self.matches_played[player1] += 1
        self.matches_played[player2] += 1
        
        # Update results
        if result1 == GameResult.WIN:
            self.wins[player1] += 1
        elif result1 == GameResult.LOSS:
            self.losses[player1] += 1
        else:
            self.draws[player1] += 1
        
        if result2 == GameResult.WIN:
            self.wins[player2] += 1
        elif result2 == GameResult.LOSS:
            self.losses[player2] += 1
        else:
            self.draws[player2] += 1
    
    def get_standings(self) -> Dict[str, Any]:
        """Get current tournament standings.
        
        Returns:
            Dictionary with standings information
        """
        standings = {}
        
        for model in self.models:
            matches = self.matches_played[model]
            wins = self.wins[model]
            losses = self.losses[model]
            draws = self.draws[model]
            
            # Calculate win rate
            win_rate = wins / matches if matches > 0 else 0.0
            
            # Calculate points (3 for win, 1 for draw, 0 for loss)
            points = wins * 3 + draws * 1
            
            standings[model] = {
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "matches_played": matches,
                "win_rate": win_rate,
                "points": points
            }
        
        return standings
    
    def get_leaderboard(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Get leaderboard sorted by points then win rate.
        
        Returns:
            List of (model, stats) tuples sorted by performance
        """
        standings = self.get_standings()
        
        # Sort by points (descending), then by win rate (descending), then by wins (descending)
        leaderboard = sorted(
            standings.items(),
            key=lambda x: (x[1]["points"], x[1]["win_rate"], x[1]["wins"]),
            reverse=True
        )
        
        return leaderboard
    
    def get_champion(self) -> str:
        """Get the current tournament champion.
        
        Returns:
            Model name of the current leader
        """
        leaderboard = self.get_leaderboard()
        return leaderboard[0][0] if leaderboard else ""


def load_tournament_data(log_file: str = "data/logs/tournament.jsonl") -> List[Dict[str, Any]]:
    """Load tournament data from JSONL log file.
    
    Args:
        log_file: Path to the JSONL log file
        
    Returns:
        List of tournament records
    """
    records = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass  # Return empty list if file doesn't exist
    
    return records 