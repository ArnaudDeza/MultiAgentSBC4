"""Visualization functions for Tic-Tac-Toe tournament analysis."""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any, Tuple
from collections import defaultdict


def ensure_plots_directory() -> None:
    """Ensure the plots directory exists."""
    os.makedirs("plots", exist_ok=True)


def plot_heatmap(logfile: str = "logs/tournament.jsonl", save_path: str = "plots/move_heatmap.png") -> None:
    """Create a heatmap showing move frequency by board position.
    
    Args:
        logfile: Path to the JSONL log file
        save_path: Path to save the heatmap image
    """
    ensure_plots_directory()
    
    # Initialize move counter for 3x3 grid
    move_counts = np.zeros((3, 3))
    
    # Parse the log file
    try:
        with open(logfile, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    
                    # Count moves
                    if record.get("type") == "move":
                        move = record.get("move", {})
                        row = move.get("row")
                        col = move.get("col")
                        
                        if row is not None and col is not None:
                            if 0 <= row <= 2 and 0 <= col <= 2:
                                move_counts[row][col] += 1
    
    except FileNotFoundError:
        print(f"Warning: Log file {logfile} not found, creating empty heatmap")
        move_counts = np.ones((3, 3))  # Default pattern
    
    # Create the heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create heatmap with custom colormap
    im = ax.imshow(move_counts, cmap='YlOrRd', interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Number of Moves', rotation=270, labelpad=20)
    
    # Set labels and ticks
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(['Col 0', 'Col 1', 'Col 2'])
    ax.set_yticklabels(['Row 0', 'Row 1', 'Row 2'])
    
    # Add move counts as text
    for i in range(3):
        for j in range(3):
            text = ax.text(j, i, f'{int(move_counts[i, j])}',
                          ha="center", va="center", color="black", fontweight="bold")
    
    # Styling
    ax.set_title('Tic-Tac-Toe Move Frequency Heatmap', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Board Columns', fontsize=12)
    ax.set_ylabel('Board Rows', fontsize=12)
    
    # Add grid lines
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 3, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", size=0)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Move heatmap saved to: {save_path}")


def plot_bracket(logfile: str = "logs/tournament.jsonl", save_path: str = "plots/tournament_bracket.png") -> None:
    """Create a tournament bracket visualization.
    
    Args:
        logfile: Path to the JSONL log file
        save_path: Path to save the bracket image
    """
    ensure_plots_directory()
    
    # Parse tournament data
    matches = []
    tournament_info = None
    
    try:
        with open(logfile, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    
                    if record.get("type") == "tournament_start":
                        tournament_info = record
                    elif record.get("type") == "result":
                        # Extract match info from game_id and result
                        game_id = record.get("game_id", "")
                        winner = record.get("winner")
                        matches.append({
                            "game_id": game_id,
                            "winner": winner,
                            "result": record.get("result")
                        })
    
    except FileNotFoundError:
        print(f"Warning: Log file {logfile} not found, creating sample bracket")
        matches = [
            {"game_id": "R1M1", "winner": "X", "result": "win"},
            {"game_id": "R1M2", "winner": "O", "result": "win"},
            {"game_id": "R2M1", "winner": "X", "result": "win"},
        ]
        tournament_info = {"models": ["phi4", "phi4", "qwq", "qwq"], "rounds": 2}
    
    # Create bracket visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if tournament_info:
        models = tournament_info.get("models", [])
        total_rounds = tournament_info.get("rounds", 1)
    else:
        models = ["Model1", "Model2", "Model3", "Model4"]
        total_rounds = 2
    
    # Calculate layout parameters
    num_participants = len(models)
    max_height = num_participants
    max_width = total_rounds + 1
    
    # Draw bracket structure
    _draw_bracket_structure(ax, models, matches, total_rounds)
    
    # Set plot limits and styling
    ax.set_xlim(-0.5, max_width + 0.5)
    ax.set_ylim(-0.5, max_height + 0.5)
    ax.set_aspect('equal')
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Add title
    plt.title('Tic-Tac-Toe Tournament Bracket', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"🏆 Tournament bracket saved to: {save_path}")


def _draw_bracket_structure(ax, models: List[str], matches: List[Dict], total_rounds: int) -> None:
    """Draw the tournament bracket structure.
    
    Args:
        ax: Matplotlib axes object
        models: List of participating models
        matches: List of match results
        total_rounds: Total number of tournament rounds
    """
    # Calculate positions for initial participants
    num_participants = len(models)
    y_positions = np.linspace(1, num_participants, num_participants)
    
    # Draw initial participants
    for i, model in enumerate(models):
        ax.text(0, y_positions[i], model, ha='left', va='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
               fontsize=10, fontweight='bold')
    
    # Process matches by round
    current_positions = list(y_positions)
    
    for round_num in range(1, total_rounds + 1):
        next_positions = []
        
        # Calculate positions for this round
        for i in range(0, len(current_positions), 2):
            if i + 1 < len(current_positions):
                y1, y2 = current_positions[i], current_positions[i + 1]
                mid_y = (y1 + y2) / 2
                next_positions.append(mid_y)
                
                # Draw connection lines
                ax.plot([round_num - 0.2, round_num], [y1, y1], 'k-', linewidth=1)
                ax.plot([round_num - 0.2, round_num], [y2, y2], 'k-', linewidth=1)
                ax.plot([round_num, round_num], [y1, y2], 'k-', linewidth=1)
                ax.plot([round_num, round_num + 0.2], [mid_y, mid_y], 'k-', linewidth=1)
                
                # Find corresponding match result
                match_id = f"R{round_num}M{len(next_positions)}"
                winner_symbol = None
                for match in matches:
                    if match.get("game_id") == match_id:
                        winner_symbol = match.get("winner")
                        break
                
                # Determine advancing participant
                if winner_symbol == 'X':
                    advancing = models[i] if i < len(models) else "Unknown"
                elif winner_symbol == 'O':
                    advancing = models[i + 1] if i + 1 < len(models) else "Unknown"
                else:
                    advancing = "TBD"
                
                # Draw winner box
                color = 'lightgreen' if winner_symbol else 'lightyellow'
                ax.text(round_num + 0.3, mid_y, advancing, ha='left', va='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                       fontsize=9, fontweight='bold')
        
        current_positions = next_positions
    
    # Add round labels
    for round_num in range(1, total_rounds + 1):
        if round_num == total_rounds:
            label = "Final"
        elif round_num == total_rounds - 1:
            label = "Semi-Final"
        else:
            label = f"Round {round_num}"
        
        ax.text(round_num, num_participants + 0.5, label, ha='center', va='bottom',
               fontsize=12, fontweight='bold')


def plot_move_patterns(logfile: str = "logs/tournament.jsonl", save_path: str = "plots/move_patterns.png") -> None:
    """Create visualizations of move patterns and preferences.
    
    Args:
        logfile: Path to the JSONL log file
        save_path: Path to save the patterns plot
    """
    ensure_plots_directory()
    
    # Parse moves by player and position
    x_moves = np.zeros((3, 3))
    o_moves = np.zeros((3, 3))
    
    try:
        with open(logfile, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    
                    if record.get("type") == "move":
                        player = record.get("player")
                        move = record.get("move", {})
                        row = move.get("row")
                        col = move.get("col")
                        
                        if row is not None and col is not None and 0 <= row <= 2 and 0 <= col <= 2:
                            if player == 'X':
                                x_moves[row][col] += 1
                            elif player == 'O':
                                o_moves[row][col] += 1
    
    except FileNotFoundError:
        print(f"Warning: Log file {logfile} not found")
        return
    
    # Create subplot for X and O patterns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # X player heatmap
    im1 = ax1.imshow(x_moves, cmap='Reds', interpolation='nearest')
    ax1.set_title('X Player Move Patterns', fontweight='bold')
    ax1.set_xticks(range(3))
    ax1.set_yticks(range(3))
    ax1.set_xticklabels(['Col 0', 'Col 1', 'Col 2'])
    ax1.set_yticklabels(['Row 0', 'Row 1', 'Row 2'])
    
    # Add text annotations
    for i in range(3):
        for j in range(3):
            ax1.text(j, i, f'{int(x_moves[i, j])}', ha="center", va="center", 
                    color="white" if x_moves[i, j] > x_moves.max()/2 else "black", fontweight="bold")
    
    # O player heatmap  
    im2 = ax2.imshow(o_moves, cmap='Blues', interpolation='nearest')
    ax2.set_title('O Player Move Patterns', fontweight='bold')
    ax2.set_xticks(range(3))
    ax2.set_yticks(range(3))
    ax2.set_xticklabels(['Col 0', 'Col 1', 'Col 2'])
    ax2.set_yticklabels(['Row 0', 'Row 1', 'Row 2'])
    
    # Add text annotations
    for i in range(3):
        for j in range(3):
            ax2.text(j, i, f'{int(o_moves[i, j])}', ha="center", va="center",
                    color="white" if o_moves[i, j] > o_moves.max()/2 else "black", fontweight="bold")
    
    # Add colorbars
    plt.colorbar(im1, ax=ax1, label='Moves by X')
    plt.colorbar(im2, ax=ax2, label='Moves by O')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📈 Move patterns saved to: {save_path}")


def create_all_visualizations(logfile: str = "logs/tournament.jsonl") -> None:
    """Create all available visualizations.
    
    Args:
        logfile: Path to the JSONL log file
    """
    print("📊 Creating visualizations...")
    
    plot_heatmap(logfile)
    plot_bracket(logfile)
    plot_move_patterns(logfile)
    
    print("✅ All visualizations complete!") 