"""Game engine for Tic-Tac-Toe with built-in referee logic."""

from typing import List, Optional, Tuple, Union
from logger import GameLogger
from agents import PlayerAgent


class Board:
    """Represents a 3x3 Tic-Tac-Toe board."""
    
    def __init__(self) -> None:
        """Initialize an empty 3x3 board."""
        self.grid: List[List[str]] = [[" " for _ in range(3)] for _ in range(3)]
        self.move_count = 0
    
    def make_move(self, row: int, col: int, symbol: str) -> bool:
        """Make a move on the board.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            symbol: Player symbol ('X' or 'O')
            
        Returns:
            True if move was successful, False if invalid
        """
        if not self.is_valid_move(row, col):
            return False
        
        self.grid[row][col] = symbol
        self.move_count += 1
        return True
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            
        Returns:
            True if the move is valid (cell is empty and in bounds)
        """
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False
        return self.grid[row][col] == " "
    
    def check_win(self, symbol: str) -> bool:
        """Check if the given symbol has won.
        
        Args:
            symbol: Player symbol to check ('X' or 'O')
            
        Returns:
            True if the symbol has three in a row
        """
        # Check rows
        for row in self.grid:
            if all(cell == symbol for cell in row):
                return True
        
        # Check columns
        for col in range(3):
            if all(self.grid[row][col] == symbol for row in range(3)):
                return True
        
        # Check diagonals
        if all(self.grid[i][i] == symbol for i in range(3)):
            return True
        if all(self.grid[i][2-i] == symbol for i in range(3)):
            return True
        
        return False
    
    def check_draw(self) -> bool:
        """Check if the game is a draw.
        
        Returns:
            True if the board is full and no one has won
        """
        return self.move_count == 9 and not (self.check_win('X') or self.check_win('O'))
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if the game is over and return the result.
        
        Returns:
            Tuple of (is_over, winner) where winner is 'X', 'O', or None for draw
        """
        if self.check_win('X'):
            return True, 'X'
        elif self.check_win('O'):
            return True, 'O'
        elif self.check_draw():
            return True, None
        else:
            return False, None
    
    def get_board_copy(self) -> List[List[str]]:
        """Get a copy of the current board state.
        
        Returns:
            Deep copy of the board grid
        """
        return [row[:] for row in self.grid]
    
    def display(self) -> str:
        """Get a string representation of the board.
        
        Returns:
            Formatted board string
        """
        lines = []
        lines.append("   0   1   2")
        lines.append("  -----------")
        
        for i, row in enumerate(self.grid):
            display_row = []
            for cell in row:
                if cell == " ":
                    display_row.append(" ")
                else:
                    display_row.append(cell)
            lines.append(f"{i}| {' | '.join(display_row)} |")
            lines.append("  -----------")
        
        return "\n".join(lines)


def play_game(agent_x: PlayerAgent, agent_o: PlayerAgent, game_id: str, 
              logger: GameLogger, max_moves: int = 50) -> Tuple[str, Optional[str]]:
    """Play a single game of Tic-Tac-Toe between two agents.
    
    Args:
        agent_x: Agent playing as 'X' (goes first)
        agent_o: Agent playing as 'O' (goes second)
        game_id: Unique identifier for this game
        logger: Logger instance to record moves and results
        max_moves: Maximum number of moves to prevent infinite loops
        
    Returns:
        Tuple of (result, winner) where result is 'win' or 'draw'
        and winner is 'X', 'O', or None
    """
    board = Board()
    current_player = 'X'
    current_agent = agent_x
    move_count = 0
    
    print(f"🎮 Starting game {game_id}")
    print(f"🔴 X: {agent_x.model}")
    print(f"🔵 O: {agent_o.model}")
    print(board.display())
    
    while move_count < max_moves:
        try:
            # Get move from current agent
            move = current_agent.get_move(board.get_board_copy(), current_player)
            row, col = move
            
            print(f"Player {current_player} attempts move: ({row}, {col})")
            
            # Validate and make the move
            if not board.make_move(row, col, current_player):
                print(f"❌ Invalid move by {current_player} at ({row}, {col})")
                # For invalid moves, try to find a valid alternative
                valid_move = find_valid_move(board)
                if valid_move:
                    row, col = valid_move
                    board.make_move(row, col, current_player)
                    print(f"🔄 Auto-corrected to ({row}, {col})")
                else:
                    # This shouldn't happen unless board is full
                    break
            
            # Log the move
            logger.log_move(game_id, current_player, (row, col), board.get_board_copy())
            
            print(f"✅ {current_player} plays ({row}, {col})")
            print(board.display())
            
            # Check for game over
            game_over, winner = board.is_game_over()
            if game_over:
                if winner:
                    result = "win"
                    print(f"🏆 {winner} wins!")
                else:
                    result = "draw"
                    print("🤝 It's a draw!")
                
                logger.log_result(game_id, result, board.get_board_copy(), winner)
                return result, winner
            
            # Switch players
            if current_player == 'X':
                current_player = 'O'
                current_agent = agent_o
            else:
                current_player = 'X'
                current_agent = agent_x
            
            move_count += 1
            
        except Exception as e:
            print(f"❌ Error during {current_player}'s turn: {e}")
            # Try to find a valid move as fallback
            valid_move = find_valid_move(board)
            if valid_move:
                row, col = valid_move
                board.make_move(row, col, current_player)
                logger.log_move(game_id, current_player, (row, col), board.get_board_copy())
                print(f"🔄 Emergency move at ({row}, {col})")
                print(board.display())
                
                # Check for game over after emergency move
                game_over, winner = board.is_game_over()
                if game_over:
                    result = "win" if winner else "draw"
                    logger.log_result(game_id, result, board.get_board_copy(), winner)
                    return result, winner
                
                # Switch players
                if current_player == 'X':
                    current_player = 'O'
                    current_agent = agent_o
                else:
                    current_player = 'X'
                    current_agent = agent_x
                
                move_count += 1
            else:
                break
    
    # If we reach here, something went wrong (max moves exceeded)
    print(f"⚠️ Game {game_id} exceeded maximum moves, declaring draw")
    logger.log_result(game_id, "draw", board.get_board_copy(), None)
    return "draw", None


def find_valid_move(board: Board) -> Optional[Tuple[int, int]]:
    """Find any valid move on the board.
    
    Args:
        board: Current board state
        
    Returns:
        Tuple of (row, col) for a valid move, or None if board is full
    """
    for row in range(3):
        for col in range(3):
            if board.is_valid_move(row, col):
                return (row, col)
    return None 