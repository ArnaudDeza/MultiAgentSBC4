"""LLM-powered agents for playing games using the generic interface."""

import json
import re
from typing import Tuple, List, Optional, Any
from pydantic import BaseModel
from game_interface import PlayerAgent, IGame
from ollama_utils import ollama_query


class LLMAgent(PlayerAgent):
    """A game-playing agent powered by LLM through Ollama."""
    
    def __init__(self, name: str, model: str, temperature: float = 0.7, seed: int = 42):
        """Initialize the LLM agent.
        
        Args:
            name: Agent identifier
            model: Ollama model name
            temperature: Temperature for text generation
            seed: Random seed for reproducibility
        """
        super().__init__(name, model)
        self.temperature = temperature
        self.seed = seed
    
    def get_move(self, game_state: Any, player_id: str, game: IGame) -> Any:
        """Get the next move from the LLM agent.
        
        Args:
            game_state: Current game state
            player_id: The player ID this agent is playing as
            game: The game instance for context
            
        Returns:
            The move to make (format depends on game type)
        """
        # Create prompt based on game type and state
        prompt = self._create_game_prompt(game_state, player_id, game)
        
        # Get response from LLM
        response = ollama_query(self.model, prompt, self.temperature, self.seed)
        
        # Parse the move from the response based on game type
        move = self._parse_move_from_response(response, game)
        
        return move
    
    def _create_game_prompt(self, game_state: Any, player_id: str, game: IGame) -> str:
        """Create a game-specific prompt for the LLM.
        
        Args:
            game_state: Current game state
            player_id: Player identifier
            game: Game instance
            
        Returns:
            Formatted prompt string
        """
        game_config = game.get_game_config()
        game_type = type(game).__name__
        
        # Get valid moves for context
        valid_moves = game.get_valid_moves(player_id)
        
        if "TicTacToe" in game_type:
            return self._create_tictactoe_prompt(game_state, player_id, game, valid_moves)
        else:
            return self._create_generic_prompt(game_state, player_id, game, valid_moves)
    
    def _create_tictactoe_prompt(self, game_state: List[List[str]], player_id: str, 
                               game: IGame, valid_moves: List[Tuple[int, int]]) -> str:
        """Create a Tic-Tac-Toe specific prompt.
        
        Args:
            game_state: Board state
            player_id: Player symbol
            game: Game instance
            valid_moves: List of valid moves
            
        Returns:
            Formatted prompt
        """
        board_str = game.display()
        config = game.get_game_config()
        board_size = config['board_size']
        win_length = config['win_length']
        
        prompt = f"""You are playing Tic-Tac-Toe as player '{player_id}'.

Board Configuration:
- Board size: {board_size}x{board_size}
- Win condition: {win_length} in a row
- Your symbol: {player_id}

Current board (rows 0-{board_size-1}, columns 0-{board_size-1}):

{board_str}

Valid moves available: {valid_moves}

Make your move by responding with ONLY a JSON object in this exact format:
{{"row": 0, "col": 1}}

Where row and col are integers from 0 to {board_size-1}. Choose an empty cell (marked with ' ').

Strategic considerations:
1. Try to get {win_length} of your symbols in a row (horizontal, vertical, or diagonal)
2. Block your opponent if they're close to winning
3. Take center positions when available
4. Create multiple winning opportunities when possible
"""
        return prompt
    
    def _create_generic_prompt(self, game_state: Any, player_id: str, 
                             game: IGame, valid_moves: List[Any]) -> str:
        """Create a generic game prompt.
        
        Args:
            game_state: Current game state
            player_id: Player identifier
            game: Game instance
            valid_moves: List of valid moves
            
        Returns:
            Formatted prompt
        """
        game_display = game.display()
        game_config = game.get_game_config()
        
        prompt = f"""You are playing a game as player '{player_id}'.

Game Configuration: {game_config}

Current game state:
{game_display}

Valid moves available: {valid_moves}

Make your move by responding with a JSON object representing your chosen move.
The format depends on the game type, but should match one of the valid moves listed above.

For coordinate-based games, use: {{"row": 0, "col": 1}}
"""
        return prompt
    
    def _parse_move_from_response(self, response: str, game: IGame) -> Any:
        """Parse the LLM response to extract a move.
        
        Args:
            response: Raw response from the LLM
            game: Game instance for context
            
        Returns:
            Parsed move in the appropriate format
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[^}]*\}', response)
        if json_match:
            try:
                json_str = json_match.group()
                move_data = json.loads(json_str)
                
                # Handle coordinate-based moves (Tic-Tac-Toe style)
                if "row" in move_data and "col" in move_data:
                    row, col = int(move_data["row"]), int(move_data["col"])
                    game_config = game.get_game_config()
                    board_size = game_config.get('board_size', 3)
                    
                    if 0 <= row < board_size and 0 <= col < board_size:
                        return (row, col)
                
                # Handle other move formats if needed
                if "move" in move_data:
                    return move_data["move"]
                
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # Try to extract coordinate numbers from the response
        numbers = re.findall(r'\b\d+\b', response)
        if len(numbers) >= 2:
            try:
                row, col = int(numbers[0]), int(numbers[1])
                game_config = game.get_game_config()
                board_size = game_config.get('board_size', 3)
                
                if 0 <= row < board_size and 0 <= col < board_size:
                    return (row, col)
            except ValueError:
                pass
        
        # Try coordinate patterns
        coord_patterns = [
            r'row[:\s]*(\d+).*col[:\s]*(\d+)',
            r'(\d+)[,\s]+(\d+)',
            r'\((\d+)[,\s]*(\d+)\)',
        ]
        
        for pattern in coord_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    row, col = int(match.group(1)), int(match.group(2))
                    game_config = game.get_game_config()
                    board_size = game_config.get('board_size', 3)
                    
                    if 0 <= row < board_size and 0 <= col < board_size:
                        return (row, col)
                except ValueError:
                    continue
        
        # Fallback: try to find any valid move
        valid_moves = game.get_valid_moves('X')  # Use placeholder player
        if valid_moves:
            return valid_moves[0]
        
        # Ultimate fallback
        return (0, 0)


class TicTacToeLLMAgent(LLMAgent):
    """Specialized LLM agent for Tic-Tac-Toe (backwards compatibility)."""
    
    def get_move(self, board: List[List[str]], symbol: str) -> Tuple[int, int]:
        """Get move using the old interface for backwards compatibility.
        
        Args:
            board: Board state
            symbol: Player symbol
            
        Returns:
            Move coordinates
        """
        from generic_tictactoe import GenericTicTacToe
        from game_interface import GameConfig
        
        # Create a temporary game instance for the interface
        config = GameConfig(board_size=len(board))
        temp_game = GenericTicTacToe(config)
        temp_game.board = [row[:] for row in board]
        
        # Get move using new interface
        return super().get_move(board, symbol, temp_game) 