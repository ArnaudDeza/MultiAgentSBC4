"""JSONL logging utilities for Tic-Tac-Toe tournament."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


def ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    os.makedirs("logs", exist_ok=True)


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


class GameLogger:
    """Logger for Tic-Tac-Toe game moves and results."""
    
    def __init__(self, log_file: str = "logs/tournament.jsonl") -> None:
        """Initialize the logger.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.log_file = log_file
        ensure_logs_directory()
        
        # Clear the log file at the start of a new tournament
        with open(self.log_file, 'w') as f:
            pass  # Just clear the file
    
    def log_move(self, game_id: str, player: str, move: tuple, board: List[List[str]]) -> None:
        """Log a single move.
        
        Args:
            game_id: Unique identifier for the game
            player: Player symbol ('X' or 'O')
            move: Tuple of (row, col) for the move
            board: Current board state after the move
        """
        record = {
            "timestamp": now_iso(),
            "type": "move",
            "game_id": game_id,
            "player": player,
            "move": {"row": move[0], "col": move[1]},
            "board": board
        }
        self._write_record(record)
    
    def log_result(self, game_id: str, result: str, final_board: List[List[str]], 
                   winner: str = None) -> None:
        """Log the final result of a game.
        
        Args:
            game_id: Unique identifier for the game
            result: Result string ('win', 'draw')
            final_board: Final board state
            winner: Winner symbol ('X' or 'O') if there was a winner
        """
        record = {
            "timestamp": now_iso(),
            "type": "result",
            "game_id": game_id,
            "result": result,
            "winner": winner,
            "final_board": final_board
        }
        self._write_record(record)
    
    def log_tournament_start(self, models: List[str], rounds: int) -> None:
        """Log the start of a tournament.
        
        Args:
            models: List of model names participating
            rounds: Number of tournament rounds
        """
        record = {
            "timestamp": now_iso(),
            "type": "tournament_start",
            "models": models,
            "rounds": rounds
        }
        self._write_record(record)
    
    def log_round_start(self, round_num: int, matches: List[Dict[str, Any]]) -> None:
        """Log the start of a tournament round.
        
        Args:
            round_num: Round number (1-indexed)
            matches: List of match information
        """
        record = {
            "timestamp": now_iso(),
            "type": "round_start",
            "round": round_num,
            "matches": matches
        }
        self._write_record(record)
    
    def _write_record(self, record: Dict[str, Any]) -> None:
        """Write a record to the JSONL file.
        
        Args:
            record: Dictionary to write as JSON
        """
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n") 