"""Enhanced visualization functions with improved UI for tournament analysis."""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.sankey import Sankey
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio


def ensure_plots_directory() -> None:
    """Ensure the plots directory exists."""
    os.makedirs("plots", exist_ok=True)


class TournamentVisualizer:
    """Enhanced tournament visualization with multiple chart types and interactive features."""
    
    def __init__(self, results_data: Dict[str, Any], output_dir: str = "plots"):
        """Initialize the visualizer with tournament results.
        
        Args:
            results_data: Tournament results dictionary
            output_dir: Directory to save visualizations
        """
        self.results = results_data
        self.output_dir = output_dir
        ensure_plots_directory()
        
        # Set up styling
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['font.size'] = 10
    
    def create_all_visualizations(self) -> None:
        """Create all available visualizations."""
        print("📊 Creating enhanced tournament visualizations...")
        
        try:
            # Traditional matplotlib plots
            self.plot_tournament_bracket()
            self.plot_standings_heatmap()
            self.plot_performance_metrics()
            self.plot_win_rate_trends()
            self.plot_match_progression()
            
            print("✅ All visualizations created successfully!")
            
        except Exception as e:
            print(f"⚠️ Error creating visualizations: {e}")
    
    def plot_tournament_bracket(self) -> None:
        """Create an enhanced tournament bracket visualization."""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        matches = self.results.get('matches', [])
        if not matches:
            self._create_sample_bracket(ax)
        else:
            self._draw_tournament_tree(ax, matches)
        
        ax.set_title(f'{self.results.get("format", "Tournament").title()} Bracket', 
                    fontsize=20, fontweight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/enhanced_bracket.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"🏆 Enhanced bracket saved to: {self.output_dir}/enhanced_bracket.png")
    
    def plot_standings_heatmap(self) -> None:
        """Create a comprehensive standings heatmap."""
        standings = self.results.get('standings', {})
        if not standings:
            print("⚠️ No standings data available")
            return
        
        # Prepare data for heatmap
        players = list(standings.keys())
        metrics = ['wins', 'losses', 'games_won', 'games_lost', 'points']
        
        # Create data matrix
        data_matrix = []
        for player in players:
            row = [standings[player].get(metric, 0) for metric in metrics]
            data_matrix.append(row)
        
        data_matrix = np.array(data_matrix)
        
        # Normalize each column for better visualization
        normalized_data = np.zeros_like(data_matrix, dtype=float)
        for i in range(len(metrics)):
            col = data_matrix[:, i]
            if col.max() > 0:
                normalized_data[:, i] = col / col.max()
        
        # Create heatmap
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Raw values heatmap
        im1 = ax1.imshow(data_matrix, cmap='Blues', aspect='auto')
        ax1.set_xticks(range(len(metrics)))
        ax1.set_xticklabels(metrics, rotation=45, ha='right')
        ax1.set_yticks(range(len(players)))
        ax1.set_yticklabels(players)
        ax1.set_title('Tournament Statistics (Raw Values)', fontsize=14, fontweight='bold')
        
        # Add text annotations
        for i in range(len(players)):
            for j in range(len(metrics)):
                ax1.text(j, i, str(data_matrix[i, j]), ha='center', va='center', 
                        color='white' if normalized_data[i, j] > 0.5 else 'black')
        
        # Normalized heatmap
        im2 = ax2.imshow(normalized_data, cmap='RdYlBu_r', aspect='auto')
        ax2.set_xticks(range(len(metrics)))
        ax2.set_xticklabels(metrics, rotation=45, ha='right')
        ax2.set_yticks(range(len(players)))
        ax2.set_yticklabels(players)
        ax2.set_title('Tournament Performance (Normalized)', fontsize=14, fontweight='bold')
        
        # Add colorbars
        plt.colorbar(im1, ax=ax1, label='Count')
        plt.colorbar(im2, ax=ax2, label='Normalized Score')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/standings_heatmap.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Standings heatmap saved to: {self.output_dir}/standings_heatmap.png")
    
    def plot_performance_metrics(self) -> None:
        """Create comprehensive performance metrics visualization."""
        standings = self.results.get('standings', {})
        if not standings:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        players = list(standings.keys())
        colors = plt.cm.Set3(np.linspace(0, 1, len(players)))
        
        # Win rate pie chart
        win_rates = []
        labels_with_rates = []
        for player in players:
            total_games = standings[player].get('games_won', 0) + standings[player].get('games_lost', 0)
            win_rate = standings[player].get('games_won', 0) / total_games if total_games > 0 else 0
            win_rates.append(win_rate)
            labels_with_rates.append(f"{player}\n({win_rate:.1%})")
        
        wedges, texts, autotexts = ax1.pie(win_rates, labels=labels_with_rates, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        ax1.set_title('Game Win Rates', fontsize=14, fontweight='bold')
        
        # Match performance bar chart
        match_wins = [standings[p].get('wins', 0) for p in players]
        match_losses = [standings[p].get('losses', 0) for p in players]
        
        x = np.arange(len(players))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, match_wins, width, label='Wins', alpha=0.8, color='green')
        bars2 = ax2.bar(x + width/2, match_losses, width, label='Losses', alpha=0.8, color='red')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{int(height)}', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{int(height)}', ha='center', va='bottom')
        
        ax2.set_xlabel('Players')
        ax2.set_ylabel('Matches')
        ax2.set_title('Match Win/Loss Record', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(players, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Points progression
        points = [standings[p].get('points', 0) for p in players]
        bars = ax3.bar(players, points, color=colors, alpha=0.7)
        ax3.set_xlabel('Players')
        ax3.set_ylabel('Tournament Points')
        ax3.set_title('Tournament Points Ranking', fontsize=14, fontweight='bold')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, point in zip(bars, points):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{point}', ha='center', va='bottom', fontweight='bold')
        
        # Game efficiency scatter plot
        efficiency = []
        match_counts = []
        for player in players:
            matches = standings[player].get('matches_played', 1)
            games_won = standings[player].get('games_won', 0)
            efficiency.append(games_won / matches if matches > 0 else 0)
            match_counts.append(matches)
        
        scatter = ax4.scatter(match_counts, efficiency, s=150, c=colors, alpha=0.7, edgecolors='black')
        
        # Add player labels
        for i, player in enumerate(players):
            ax4.annotate(player, (match_counts[i], efficiency[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax4.set_xlabel('Matches Played')
        ax4.set_ylabel('Games Won per Match')
        ax4.set_title('Game Efficiency vs Experience', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/performance_metrics.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📈 Performance metrics saved to: {self.output_dir}/performance_metrics.png")
    
    def plot_win_rate_trends(self) -> None:
        """Create win rate trend analysis."""
        matches = self.results.get('matches', [])
        if not matches:
            return
        
        # Track cumulative performance
        player_performance = defaultdict(lambda: {'matches': [], 'cumulative_wins': [], 'win_rates': []})
        
        match_count = 0
        for match in matches:
            match_count += 1
            player1, player2 = match['players']
            winner = match['winner']
            
            for player in [player1, player2]:
                player_performance[player]['matches'].append(match_count)
                
                # Update cumulative wins
                if player_performance[player]['cumulative_wins']:
                    prev_wins = player_performance[player]['cumulative_wins'][-1]
                else:
                    prev_wins = 0
                
                new_wins = prev_wins + (1 if player == winner else 0)
                player_performance[player]['cumulative_wins'].append(new_wins)
                
                # Calculate current win rate
                total_matches = len(player_performance[player]['matches'])
                win_rate = new_wins / total_matches if total_matches > 0 else 0
                player_performance[player]['win_rates'].append(win_rate)
        
        # Plot trends
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(player_performance)))
        
        # Cumulative wins over time
        for i, (player, data) in enumerate(player_performance.items()):
            ax1.plot(data['matches'], data['cumulative_wins'], 
                    marker='o', label=player, linewidth=2, markersize=4, color=colors[i])
        
        ax1.set_xlabel('Match Number')
        ax1.set_ylabel('Cumulative Wins')
        ax1.set_title('Cumulative Win Progression', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Win rate over time
        for i, (player, data) in enumerate(player_performance.items()):
            ax2.plot(data['matches'], data['win_rates'], 
                    marker='s', label=player, linewidth=2, markersize=3, color=colors[i])
        
        ax2.set_xlabel('Match Number')
        ax2.set_ylabel('Win Rate')
        ax2.set_title('Win Rate Evolution', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
        
        # Add horizontal line at 50%
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='50% Win Rate')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/win_rate_trends.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📈 Win rate trends saved to: {self.output_dir}/win_rate_trends.png")
    
    def plot_match_progression(self) -> None:
        """Create a match progression flowchart."""
        matches = self.results.get('matches', [])
        if not matches:
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Organize matches by tournament format
        tournament_format = self.results.get('format', 'single_elimination')
        
        if tournament_format == 'round_robin':
            self._plot_round_robin_matrix(ax, matches)
        else:
            self._plot_elimination_bracket(ax, matches)
        
        ax.set_title(f'{tournament_format.title().replace("_", " ")} Tournament Progression', 
                    fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/match_progression.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"🔄 Match progression saved to: {self.output_dir}/match_progression.png")
    
    def _plot_round_robin_matrix(self, ax, matches: List[Dict[str, Any]]) -> None:
        """Plot round robin results as a matrix."""
        # Get all players
        all_players = set()
        for match in matches:
            all_players.update(match['players'])
        
        players = sorted(list(all_players))
        n_players = len(players)
        
        # Create result matrix
        result_matrix = np.zeros((n_players, n_players))
        
        for match in matches:
            p1, p2 = match['players']
            winner = match['winner']
            
            i, j = players.index(p1), players.index(p2)
            
            if winner == p1:
                result_matrix[i, j] = 1
                result_matrix[j, i] = -1
            elif winner == p2:
                result_matrix[i, j] = -1
                result_matrix[j, i] = 1
            # else: draw (0)
        
        # Plot matrix
        im = ax.imshow(result_matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='equal')
        
        # Set ticks and labels
        ax.set_xticks(range(n_players))
        ax.set_yticks(range(n_players))
        ax.set_xticklabels(players, rotation=45, ha='right')
        ax.set_yticklabels(players)
        
        # Add text annotations
        for i in range(n_players):
            for j in range(n_players):
                if i != j:
                    text = 'W' if result_matrix[i, j] == 1 else 'L' if result_matrix[i, j] == -1 else 'D'
                    color = 'white' if abs(result_matrix[i, j]) > 0.5 else 'black'
                    ax.text(j, i, text, ha='center', va='center', color=color, fontweight='bold')
                else:
                    ax.text(j, i, '-', ha='center', va='center', color='gray')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Match Result (Green=Win, Red=Loss)', rotation=270, labelpad=20)
    
    def _plot_elimination_bracket(self, ax, matches: List[Dict[str, Any]]) -> None:
        """Plot elimination bracket."""
        # Group matches by rounds
        rounds = defaultdict(list)
        for match in matches:
            match_id = match['match_id']
            if 'R' in match_id and 'M' in match_id:
                round_num = int(match_id.split('R')[1].split('M')[0])
                rounds[round_num].append(match)
        
        if not rounds:
            ax.text(0.5, 0.5, 'No bracket data available', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14)
            return
        
        max_round = max(rounds.keys())
        
        # Calculate positions
        for round_num in sorted(rounds.keys()):
            round_matches = rounds[round_num]
            x_pos = round_num
            
            # Vertical spacing
            total_height = len(round_matches)
            for i, match in enumerate(round_matches):
                y_pos = i + 1
                
                # Draw match box
                rect = patches.FancyBboxPatch(
                    (x_pos - 0.4, y_pos - 0.3), 0.8, 0.6,
                    boxstyle="round,pad=0.05",
                    linewidth=2, edgecolor='navy', 
                    facecolor='lightblue', alpha=0.8
                )
                ax.add_patch(rect)
                
                # Add match information
                p1, p2 = match['players']
                winner = match['winner']
                score = match.get('score', (0, 0))
                
                match_text = f"{p1}\nvs\n{p2}\n\n🏆 {winner}\n({score[0]}-{score[1]})"
                ax.text(x_pos, y_pos, match_text, ha='center', va='center', 
                       fontsize=8, fontweight='bold')
                
                # Draw connection lines to next round
                if round_num < max_round:
                    # Simple connection to next round
                    ax.plot([x_pos + 0.4, x_pos + 0.6], [y_pos, y_pos], 
                           'k-', linewidth=2, alpha=0.7)
        
        ax.set_xlim(0.5, max_round + 1)
        ax.set_ylim(0.5, max(len(rounds[r]) for r in rounds) + 1)
    
    def _draw_tournament_tree(self, ax, matches: List[Dict[str, Any]]) -> None:
        """Draw the tournament tree structure."""
        # This is a simplified version - for complex brackets, you'd need more sophisticated layout
        self._plot_elimination_bracket(ax, matches)
    
    def _create_sample_bracket(self, ax) -> None:
        """Create a sample bracket when no data is available."""
        ax.text(0.5, 0.5, 'No tournament data available\nfor bracket visualization', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=16, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray'))


def create_enhanced_visualizations(results_data: Dict[str, Any], output_dir: str = "plots") -> None:
    """Create all enhanced visualizations from tournament results.
    
    Args:
        results_data: Tournament results dictionary
        output_dir: Directory to save visualizations
    """
    visualizer = TournamentVisualizer(results_data, output_dir)
    visualizer.create_all_visualizations()


def load_tournament_results_from_log(logfile: str) -> Dict[str, Any]:
    """Load tournament results from a JSONL log file.
    
    Args:
        logfile: Path to tournament log file
        
    Returns:
        Tournament results dictionary
    """
    results = {
        "format": "unknown",
        "champion": "Unknown",
        "participants": [],
        "standings": {},
        "matches": []
    }
    
    try:
        with open(logfile, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    
                    if record.get("type") == "tournament_start":
                        results["participants"] = record.get("models", [])
                    
                    elif record.get("type") == "result":
                        game_id = record.get("game_id", "")
                        winner = record.get("winner")
                        
                        # Extract player names from game context (this would need to be improved)
                        # For now, create a basic match structure
                        if winner:
                            match_data = {
                                "match_id": game_id,
                                "players": ["Player1", "Player2"],  # Would need better parsing
                                "winner": winner,
                                "score": (1, 0) if winner else (0, 0)
                            }
                            results["matches"].append(match_data)
        
        # Create basic standings from matches
        for participant in results["participants"]:
            results["standings"][participant] = {
                "wins": 0,
                "losses": 0,
                "games_won": 0,
                "games_lost": 0,
                "points": 0,
                "matches_played": 0
            }
        
        return results
        
    except FileNotFoundError:
        print(f"⚠️ Log file {logfile} not found")
        return results
    except Exception as e:
        print(f"⚠️ Error loading tournament results: {e}")
        return results 