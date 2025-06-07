"""Generic Tic-Tac-Toe implementation using the IGame interface."""

import copy
from typing import List, Optional, Tuple, Any, Dict
from game_interface import IGame, GameConfig


class GenericTicTacToe(IGame):
    """Generic Tic-Tac-Toe game that can be configured for different board sizes and win conditions."""
    
    def __init__(self, config: GameConfig = None):
        """Initialize the game.
        
        Args:
            config: Game configuration, defaults to standard 3x3 Tic-Tac-Toe
        """
        if config is None:
            config = GameConfig()
        
        self.config = config
        self.board_size = config.board_size
        self.win_length = config.win_length
        self.num_players = config.num_players
        
        # Initialize empty board
        self.board: List[List[str]] = [[" " for _ in range(self.board_size)] 
                                       for _ in range(self.board_size)]
        self.move_count = 0
        
        # Player symbols (supports more than 2 players)
        self.player_symbols = ['X', 'O', 'A', 'B', 'C', 'D', 'E', 'F'][:self.num_players]
        self.current_player_index = 0
    
    def make_move(self, move: Tuple[int, int], player: str) -> bool:
        """Make a move on the board.
        
        Args:
            move: Tuple of (row, col) coordinates
            player: Player symbol making the move
            
        Returns:
            True if move was successful, False if invalid
        """
        if not isinstance(move, tuple) or len(move) != 2:
            return False
        
        row, col = move
        
        if not self.is_valid_move(move, player):
            return False
        
        self.board[row][col] = player
        self.move_count += 1
        return True
    
    def is_valid_move(self, move: Tuple[int, int], player: str) -> bool:
        """Check if a move is valid.
        
        Args:
            move: Tuple of (row, col) coordinates
            player: Player attempting the move
            
        Returns:
            True if the move is valid
        """
        if not isinstance(move, tuple) or len(move) != 2:
            return False
        
        row, col = move
        
        # Check bounds
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        
        # Check if cell is empty
        return self.board[row][col] == " "
    
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
        if self.move_count >= self.board_size * self.board_size:
            return True, None
        
        return False, None
    
    def get_state(self) -> List[List[str]]:
        """Get the current game state.
        
        Returns:
            Deep copy of the current board state
        """
        return [row[:] for row in self.board]
    
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        """Get all valid moves for a player.
        
        Args:
            player: The player to get moves for
            
        Returns:
            List of valid (row, col) moves
        """
        valid_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move((row, col), player):
                    valid_moves.append((row, col))
        return valid_moves
    
    def copy(self) -> 'GenericTicTacToe':
        """Create a deep copy of the game state.
        
        Returns:
            A new game instance with the same state
        """
        new_game = GenericTicTacToe(self.config)
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
        col_headers = "   " + "   ".join(str(i) for i in range(self.board_size))
        lines.append(col_headers)
        
        # Separator line
        separator = "  " + "-" * (4 * self.board_size - 1)
        lines.append(separator)
        
        # Board rows
        for i, row in enumerate(self.board):
            display_row = []
            for cell in row:
                display_row.append(cell if cell != " " else " ")
            lines.append(f"{i}| {' | '.join(display_row)} |")
            lines.append(separator)
        
        return "\n".join(lines)
    
    def get_game_config(self) -> Dict[str, Any]:
        """Get the game configuration parameters.
        
        Returns:
            Dictionary of game configuration
        """
        return self.config.to_dict()
    
    def _check_win(self, player: str) -> bool:
        """Check if the given player has won.
        
        Args:
            player: Player symbol to check
            
        Returns:
            True if the player has won
        """
        # Check rows
        for row in range(self.board_size):
            if self._check_line(player, [(row, col) for col in range(self.board_size)]):
                return True
        
        # Check columns
        for col in range(self.board_size):
            if self._check_line(player, [(row, col) for row in range(self.board_size)]):
                return True
        
        # Check diagonals
        # Main diagonal
        if self._check_line(player, [(i, i) for i in range(self.board_size)]):
            return True
        
        # Anti-diagonal
        if self._check_line(player, [(i, self.board_size - 1 - i) for i in range(self.board_size)]):
            return True
        
        # For larger boards, check all possible win_length sequences
        if self.board_size > 3 or self.win_length != self.board_size:
            return self._check_all_sequences(player)
        
        return False
    
    def _check_line(self, player: str, positions: List[Tuple[int, int]]) -> bool:
        """Check if a line of positions contains a win for the player.
        
        Args:
            player: Player symbol to check
            positions: List of (row, col) positions to check
            
        Returns:
            True if the line contains enough consecutive pieces for a win
        """
        if len(positions) < self.win_length:
            return False
        
        # For standard case where win_length equals board_size
        if self.win_length == len(positions):
            return all(self.board[row][col] == player for row, col in positions)
        
        # For cases where we need to find consecutive sequences
        consecutive = 0
        for row, col in positions:
            if self.board[row][col] == player:
                consecutive += 1
                if consecutive >= self.win_length:
                    return True
            else:
                consecutive = 0
        
        return False
    
    def _check_all_sequences(self, player: str) -> bool:
        """Check all possible sequences for wins (for non-standard board sizes).
        
        Args:
            player: Player symbol to check
            
        Returns:
            True if any sequence forms a win
        """
        # Horizontal sequences
        for row in range(self.board_size):
            for start_col in range(self.board_size - self.win_length + 1):
                if all(self.board[row][start_col + i] == player for i in range(self.win_length)):
                    return True
        
        # Vertical sequences
        for col in range(self.board_size):
            for start_row in range(self.board_size - self.win_length + 1):
                if all(self.board[start_row + i][col] == player for i in range(self.win_length)):
                    return True
        
        # Diagonal sequences (top-left to bottom-right)
        for start_row in range(self.board_size - self.win_length + 1):
            for start_col in range(self.board_size - self.win_length + 1):
                if all(self.board[start_row + i][start_col + i] == player for i in range(self.win_length)):
                    return True
        
        # Diagonal sequences (top-right to bottom-left)
        for start_row in range(self.board_size - self.win_length + 1):
            for start_col in range(self.win_length - 1, self.board_size):
                if all(self.board[start_row + i][start_col - i] == player for i in range(self.win_length)):
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