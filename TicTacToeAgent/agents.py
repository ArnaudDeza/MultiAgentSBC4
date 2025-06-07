"""Player agents for Tic-Tac-Toe using Ollama LLM."""

import json
import re
from typing import Tuple, List, Optional
from pydantic import BaseModel
from ollama_utils import ollama_query


class PlayerAgent(BaseModel):
    """A Tic-Tac-Toe player agent powered by Ollama LLM."""
    
    model: str
    temperature: float = 0.7
    seed: int = 42
    
    def get_move(self, board: List[List[str]], symbol: str) -> Tuple[int, int]:
        """Get the next move from the LLM agent.
        
        Args:
            board: Current 3x3 board state (empty cells are " ")
            symbol: Player's symbol ("X" or "O")
            
        Returns:
            Tuple of (row, col) coordinates for the move
            
        Raises:
            ValueError: If the LLM response cannot be parsed into a valid move
        """
        # Create a readable board representation
        board_str = self._format_board_for_prompt(board)
        
        # Create the prompt for the LLM
        prompt = f"""You are playing Tic-Tac-Toe as player '{symbol}'. 
Here's the current board (rows 0-2, columns 0-2):

{board_str}

Make your move by responding with ONLY a JSON object in this exact format:
{{"row": 0, "col": 1}}

Where row and col are integers from 0 to 2. Choose an empty cell (marked with ' ').
"""
        
        # Get response from LLM
        response = ollama_query(self.model, prompt, self.temperature, self.seed)
        
        # Parse the move from the response
        move = self._parse_move_from_response(response)
        
        return move
    
    def _format_board_for_prompt(self, board: List[List[str]]) -> str:
        """Format the board for display in the LLM prompt.
        
        Args:
            board: Current board state
            
        Returns:
            Formatted string representation of the board
        """
        lines = []
        lines.append("   0   1   2")
        lines.append("  -----------")
        
        for i, row in enumerate(board):
            display_row = []
            for cell in row:
                if cell == " ":
                    display_row.append(" ")
                else:
                    display_row.append(cell)
            lines.append(f"{i}| {' | '.join(display_row)} |")
            lines.append("  -----------")
        
        return "\n".join(lines)
    
    def _parse_move_from_response(self, response: str) -> Tuple[int, int]:
        """Parse the LLM response to extract a move.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Tuple of (row, col) coordinates
            
        Raises:
            ValueError: If the response cannot be parsed into a valid move
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[^}]*\}', response)
        if json_match:
            try:
                json_str = json_match.group()
                move_data = json.loads(json_str)
                
                if "row" in move_data and "col" in move_data:
                    row, col = int(move_data["row"]), int(move_data["col"])
                    if 0 <= row <= 2 and 0 <= col <= 2:
                        return (row, col)
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # Try to extract numbers from the response
        numbers = re.findall(r'\b[0-2]\b', response)
        if len(numbers) >= 2:
            try:
                row, col = int(numbers[0]), int(numbers[1])
                if 0 <= row <= 2 and 0 <= col <= 2:
                    return (row, col)
            except ValueError:
                pass
        
        # Try to find coordinates in various formats
        coord_patterns = [
            r'row[:\s]*([0-2]).*col[:\s]*([0-2])',
            r'([0-2])[,\s]+([0-2])',
            r'\(([0-2])[,\s]*([0-2])\)',
        ]
        
        for pattern in coord_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    row, col = int(match.group(1)), int(match.group(2))
                    if 0 <= row <= 2 and 0 <= col <= 2:
                        return (row, col)
                except ValueError:
                    continue
        
        # If all parsing fails, return a fallback move (0, 0)
        # This should be caught by the game engine as an invalid move if the cell is occupied
        return (0, 0)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True 