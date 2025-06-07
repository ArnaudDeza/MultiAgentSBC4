"""Connect-Four game implementation using the IGame interface."""

import copy
from typing import List, Optional, Tuple, Any, Dict
from game_interface import IGame, GameConfig


class ConnectFour(IGame):
    """Connect-Four game implementation."""
    
    def __init__(self, config: GameConfig = None):
        """Initialize Connect-Four game.
        
        Args:
            config: Game configuration (defaults to 7x6 board, 4 to win)
        """
        if config is None:
            config = GameConfig(
                board_size=7,  # Width
                win_length=4,
                num_players=2,
                max_moves=42  # 7x6 board
            )
            config.extra_params['height'] = 6
        
        self.config = config
        self.width = config.board_size
        self.height = config.extra_params.get('height', 6)
        self.win_length = config.win_length
        self.num_players = config.num_players
        
        # Initialize empty board (height x width)
        self.board: List[List[str]] = [[" " for _ in range(self.width)] 
                                       for _ in range(self.height)]
        self.move_count = 0
        
        # Player symbols
        self.player_symbols = ['R', 'Y', 'B', 'G'][:self.num_players]  # Red, Yellow, Blue, Green
        self.current_player_index = 0
    
    def make_move(self, move: int, player: str) -> bool:
        """Make a move by dropping a piece in the specified column.
        
        Args:
            move: Column number (0 to width-1)
            player: Player symbol making the move
            
        Returns:
            True if move was successful, False if invalid
        """
        if not isinstance(move, int):
            return False
        
        if not self.is_valid_move(move, player):
            return False
        
        # Find the lowest empty row in the column
        for row in range(self.height - 1, -1, -1):
            if self.board[row][move] == " ":
                self.board[row][move] = player
                self.move_count += 1
                return True
        
        return False  # Column is full
    
    def is_valid_move(self, move: int, player: str) -> bool:
        """Check if a move is valid.
        
        Args:
            move: Column number to drop piece
            player: Player attempting the move
            
        Returns:
            True if the move is valid
        """
        if not isinstance(move, int):
            return False
        
        # Check bounds
        if not (0 <= move < self.width):
            return False
        
        # Check if column has space (top row is empty)
        return self.board[0][move] == " "
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if the game is over.
        
        Returns:
            Tuple of (is_over, winner) where winner is player symbol or None for draw
        """
        # Check for wins
        for player in self.player_symbols:
            if self._check_win(player):
                return True, player
        
        # Check for draw (board full)
        if self.move_count >= self.width * self.height:
            return True, None
        
        return False, None
    
    def get_state(self) -> List[List[str]]:
        """Get the current game state.
        
        Returns:
            Deep copy of the current board state
        """
        return [row[:] for row in self.board]
    
    def get_valid_moves(self, player: str) -> List[int]:
        """Get all valid moves for a player.
        
        Args:
            player: The player to get moves for
            
        Returns:
            List of valid column numbers
        """
        valid_moves = []
        for col in range(self.width):
            if self.is_valid_move(col, player):
                valid_moves.append(col)
        return valid_moves
    
    def copy(self) -> 'ConnectFour':
        """Create a deep copy of the game state.
        
        Returns:
            A new game instance with the same state
        """
        new_game = ConnectFour(self.config)
        new_game.board = [row[:] for row in self.board]
        new_game.move_count = self.move_count
        new_game.current_player_index = self.current_player_index
        return new_game
    
    def display(self) -> str:
        """Get a string representation of the current game state.
        
        Returns:
            Human-readable game state
        """
        lines = []
        
        # Column headers
        col_headers = "  " + " ".join(str(i) for i in range(self.width))
        lines.append(col_headers)
        
        # Separator line
        separator = " +" + "-" * (2 * self.width - 1) + "+"
        lines.append(separator)
        
        # Board rows (top to bottom)
        for row in self.board:
            display_row = []
            for cell in row:
                if cell == " ":
                    display_row.append(".")
                else:
                    display_row.append(cell)
            lines.append(" |" + "|".join(display_row) + "|")
        
        lines.append(separator)
        
        return "\n".join(lines)
    
    def get_game_config(self) -> Dict[str, Any]:
        """Get the game configuration parameters.
        
        Returns:
            Dictionary of game configuration
        """
        config_dict = self.config.to_dict()
        config_dict['width'] = self.width
        config_dict['height'] = self.height
        return config_dict
    
    def _check_win(self, player: str) -> bool:
        """Check if the given player has won.
        
        Args:
            player: Player symbol to check
            
        Returns:
            True if the player has won
        """
        # Check horizontal
        for row in range(self.height):
            for col in range(self.width - self.win_length + 1):
                if all(self.board[row][col + i] == player for i in range(self.win_length)):
                    return True
        
        # Check vertical
        for row in range(self.height - self.win_length + 1):
            for col in range(self.width):
                if all(self.board[row + i][col] == player for i in range(self.win_length)):
                    return True
        
        # Check diagonal (top-left to bottom-right)
        for row in range(self.height - self.win_length + 1):
            for col in range(self.width - self.win_length + 1):
                if all(self.board[row + i][col + i] == player for i in range(self.win_length)):
                    return True
        
        # Check diagonal (top-right to bottom-left)
        for row in range(self.height - self.win_length + 1):
            for col in range(self.win_length - 1, self.width):
                if all(self.board[row + i][col - i] == player for i in range(self.win_length)):
                    return True
        
        return False
    
    def get_current_player(self) -> str:
        """Get the current player symbol.
        
        Returns:
            Current player's symbol
        """
        return self.player_symbols[self.current_player_index]
    
    def advance_turn(self) -> str:
        """Advance to the next player's turn.
        
        Returns:
            Next player's symbol
        """
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        return self.get_current_player()
    
    def get_column_height(self, col: int) -> int:
        """Get the number of pieces in a column.
        
        Args:
            col: Column number
            
        Returns:
            Number of pieces in the column
        """
        if not (0 <= col < self.width):
            return 0
        
        count = 0
        for row in range(self.height - 1, -1, -1):
            if self.board[row][col] != " ":
                count += 1
            else:
                break
        return count 