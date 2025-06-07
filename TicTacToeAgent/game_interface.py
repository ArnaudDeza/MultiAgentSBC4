"""Generic game interface for multi-agent tournaments."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Dict
from enum import Enum


class GameResult(Enum):
    """Enumeration of possible game results."""
    WIN = "win"
    DRAW = "draw"
    ONGOING = "ongoing"


class IGame(ABC):
    """Generic game interface that all games must implement."""
    
    @abstractmethod
    def make_move(self, move: Any, player: str) -> bool:
        """Make a move in the game.
        
        Args:
            move: The move to make (format depends on game)
            player: The player making the move
            
        Returns:
            True if move was successful, False if invalid
        """
        pass
    
    @abstractmethod
    def is_valid_move(self, move: Any, player: str) -> bool:
        """Check if a move is valid.
        
        Args:
            move: The move to check
            player: The player attempting the move
            
        Returns:
            True if the move is valid
        """
        pass
    
    @abstractmethod
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if the game is over.
        
        Returns:
            Tuple of (is_over, winner) where winner is player ID or None for draw
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Any:
        """Get the current game state.
        
        Returns:
            Current state representation (format depends on game)
        """
        pass
    
    @abstractmethod
    def get_valid_moves(self, player: str) -> List[Any]:
        """Get all valid moves for a player.
        
        Args:
            player: The player to get moves for
            
        Returns:
            List of valid moves
        """
        pass
    
    @abstractmethod
    def copy(self) -> 'IGame':
        """Create a deep copy of the game state.
        
        Returns:
            A new game instance with the same state
        """
        pass
    
    @abstractmethod
    def display(self) -> str:
        """Get a string representation of the current game state.
        
        Returns:
            Human-readable game state
        """
        pass
    
    @abstractmethod
    def get_game_config(self) -> Dict[str, Any]:
        """Get the game configuration parameters.
        
        Returns:
            Dictionary of game configuration
        """
        pass


class GameConfig:
    """Configuration class for game parameters."""
    
    def __init__(self, 
                 board_size: int = 3,
                 win_length: int = 3,
                 num_players: int = 2,
                 max_moves: int = 50,
                 **kwargs):
        """Initialize game configuration.
        
        Args:
            board_size: Size of the game board (for square boards)
            win_length: Number of pieces in a row needed to win
            num_players: Number of players in the game
            max_moves: Maximum number of moves before declaring draw
            **kwargs: Additional game-specific parameters
        """
        self.board_size = board_size
        self.win_length = win_length
        self.num_players = num_players
        self.max_moves = max_moves
        self.extra_params = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "board_size": self.board_size,
            "win_length": self.win_length,
            "num_players": self.num_players,
            "max_moves": self.max_moves,
            **self.extra_params
        }


class PlayerAgent(ABC):
    """Abstract base class for game-playing agents."""
    
    def __init__(self, name: str, model: str = None, **kwargs):
        """Initialize the agent.
        
        Args:
            name: Agent identifier
            model: Model name (for LLM agents)
            **kwargs: Additional agent parameters
        """
        self.name = name
        self.model = model
        self.params = kwargs
    
    @abstractmethod
    def get_move(self, game_state: Any, player_id: str, game: IGame) -> Any:
        """Get the next move from the agent.
        
        Args:
            game_state: Current game state
            player_id: The player ID this agent is playing as
            game: The game instance for context
            
        Returns:
            The move to make
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name}({self.model})" if self.model else self.name 