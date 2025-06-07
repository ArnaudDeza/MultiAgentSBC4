#!/usr/bin/env python3
"""Rock Paper Scissors Royale - Main entry point for LLM tournaments."""

import argparse
import sys
import os
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter

from ollama_utils import get_available_models
from agents import PlayerAgent, create_agent
from tournament import TournamentManager
from utils import load_tournament_data, Move, ensure_data_directories


def create_visualization_plots(tournament_data: List[dict], output_dir: str = "data/") -> None:
    """Create visualization plots from tournament data.
    
    Args:
        tournament_data: List of tournament records from JSONL
        output_dir: Directory to save plots
    """
    ensure_data_directories()
    
    # Extract match data
    matches = [record for record in tournament_data if record.get("type") == "match"]
    
    if not matches:
        print("⚠️ No match data found for visualization")
        return
    
    print("📊 Generating tournament visualizations...")
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle("Rock Paper Scissors Royale - Tournament Analysis", fontsize=16, fontweight='bold')
    
    # Plot 1: Move Frequency Heatmap
    move_counts = defaultdict(lambda: defaultdict(int))
    agents = set()
    
    for match in matches:
        player1 = match["player1"]
        player2 = match["player2"]
        move1 = match["move1"]
        move2 = match["move2"]
        
        agents.add(player1)
        agents.add(player2)
        move_counts[player1][move1] += 1
        move_counts[player2][move2] += 1
    
    agents = sorted(list(agents))
    moves = ["rock", "paper", "scissors"]
    
    # Create heatmap data
    heatmap_data = np.zeros((len(agents), len(moves)))
    for i, agent in enumerate(agents):
        for j, move in enumerate(moves):
            heatmap_data[i, j] = move_counts[agent][move]
    
    # Normalize by total moves per agent
    row_sums = heatmap_data.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    heatmap_data = heatmap_data / row_sums
    
    im1 = ax1.imshow(heatmap_data, cmap='Blues', aspect='auto')
    ax1.set_xticks(range(len(moves)))
    ax1.set_xticklabels(moves)
    ax1.set_yticks(range(len(agents)))
    ax1.set_yticklabels(agents, fontsize=8)
    ax1.set_title("Move Frequency by Agent (%)")
    
    # Add percentage labels
    for i in range(len(agents)):
        for j in range(len(moves)):
            text = ax1.text(j, i, f'{heatmap_data[i, j]:.1%}',
                          ha="center", va="center", color="black" if heatmap_data[i, j] < 0.5 else "white")
    
    plt.colorbar(im1, ax=ax1, label="Frequency")
    
    # Plot 2: Win Rate Analysis
    win_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})
    
    for match in matches:
        player1 = match["player1"]
        player2 = match["player2"]
        result1 = match["result1"]
        result2 = match["result2"]
        
        if result1 == "win":
            win_stats[player1]["wins"] += 1
            win_stats[player2]["losses"] += 1
        elif result1 == "loss":
            win_stats[player1]["losses"] += 1
            win_stats[player2]["wins"] += 1
        else:
            win_stats[player1]["draws"] += 1
            win_stats[player2]["draws"] += 1
    
    # Calculate win rates
    agents_sorted = sorted(agents)
    win_rates = []
    total_games = []
    
    for agent in agents_sorted:
        stats = win_stats[agent]
        total = stats["wins"] + stats["losses"] + stats["draws"]
        win_rate = stats["wins"] / total if total > 0 else 0
        win_rates.append(win_rate)
        total_games.append(total)
    
    bars = ax2.bar(range(len(agents_sorted)), win_rates, color='skyblue', alpha=0.7)
    ax2.set_xticks(range(len(agents_sorted)))
    ax2.set_xticklabels(agents_sorted, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel("Win Rate")
    ax2.set_title("Win Rate by Agent")
    ax2.set_ylim(0, 1)
    
    # Add value labels on bars
    for i, (bar, rate, total) in enumerate(zip(bars, win_rates, total_games)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{rate:.1%}\n({total} games)', ha='center', va='bottom', fontsize=8)
    
    # Plot 3: Move Matchup Matrix
    matchup_results = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "total": 0}))
    
    for match in matches:
        move1 = match["move1"]
        move2 = match["move2"]
        result1 = match["result1"]
        
        matchup_results[move1][move2]["total"] += 1
        if result1 == "win":
            matchup_results[move1][move2]["wins"] += 1
    
    # Create win rate matrix for move matchups
    matchup_matrix = np.zeros((3, 3))
    for i, move1 in enumerate(moves):
        for j, move2 in enumerate(moves):
            total = matchup_results[move1][move2]["total"]
            wins = matchup_results[move1][move2]["wins"]
            win_rate = wins / total if total > 0 else 0
            matchup_matrix[i, j] = win_rate
    
    im3 = ax3.imshow(matchup_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
    ax3.set_xticks(range(3))
    ax3.set_xticklabels([f"{move}\n(defender)" for move in moves])
    ax3.set_yticks(range(3))
    ax3.set_yticklabels([f"{move}\n(attacker)" for move in moves])
    ax3.set_title("Move vs Move Win Rates")
    
    # Add win rate labels
    for i in range(3):
        for j in range(3):
            total_games = matchup_results[moves[i]][moves[j]]["total"]
            if total_games > 0:
                text = ax3.text(j, i, f'{matchup_matrix[i, j]:.1%}\n({total_games})',
                              ha="center", va="center", 
                              color="white" if matchup_matrix[i, j] > 0.5 else "black")
    
    plt.colorbar(im3, ax=ax3, label="Win Rate")
    
    # Plot 4: Tournament Timeline
    if any(record.get("type") == "round_summary" for record in tournament_data):
        # Plot scoring progression over rounds
        round_summaries = [r for r in tournament_data if r.get("type") == "round_summary"]
        
        if round_summaries:
            rounds = []
            agent_scores = defaultdict(list)
            
            for summary in round_summaries:
                round_num = summary["round"]
                standings = summary["standings"]
                rounds.append(round_num)
                
                for agent in agents_sorted:
                    points = standings.get(agent, {}).get("points", 0)
                    agent_scores[agent].append(points)
            
            for agent in agents_sorted[:5]:  # Top 5 agents only to avoid clutter
                ax4.plot(rounds, agent_scores[agent], marker='o', label=agent, linewidth=2)
            
            ax4.set_xlabel("Round")
            ax4.set_ylabel("Points")
            ax4.set_title("Tournament Progression (Top 5)")
            ax4.legend(fontsize=8)
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, "No round progression data available", 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title("Tournament Progression")
    else:
        # Show overall tournament statistics
        total_matches = len(matches)
        total_agents = len(agents)
        
        stats_text = [
            f"Total Matches: {total_matches}",
            f"Total Agents: {total_agents}",
            f"Avg Matches per Agent: {total_matches * 2 / total_agents:.1f}",
            "",
            "Move Distribution:",
        ]
        
        all_moves = [match["move1"] for match in matches] + [match["move2"] for match in matches]
        move_counter = Counter(all_moves)
        
        for move in moves:
            count = move_counter[move]
            percentage = count / len(all_moves) * 100
            stats_text.append(f"  {move.title()}: {count} ({percentage:.1f}%)")
        
        ax4.text(0.1, 0.9, "\n".join(stats_text), transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        ax4.set_title("Tournament Statistics")
        ax4.axis('off')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(output_dir, "tournament_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📈 Saved tournament analysis plot: {output_path}")
    
    plt.show()


def list_available_models() -> None:
    """List all available Ollama models."""
    try:
        models = get_available_models()
        if models:
            print("🤖 Available Ollama models:")
            for i, model in enumerate(models, 1):
                print(f"  {i:2d}. {model}")
        else:
            print("❌ No Ollama models found. Please install some models first.")
            print("   Example: ollama pull phi3")
    except Exception as e:
        print(f"❌ Error listing models: {e}")


def main() -> None:
    """Main entry point for Rock Paper Scissors Royale."""
    parser = argparse.ArgumentParser(
        description="Rock Paper Scissors Royale - LLM Tournament System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-models                              # List available models
  %(prog)s phi3 llama2                                # Quick tournament with 2 models
  %(prog)s phi3 gemma llama2 --tournament elimination # Single elimination
  %(prog)s phi3 llama2 --tournament round-robin       # Round robin tournament
  %(prog)s phi3 llama2 --rounds 20 --temperature 0.5  # Custom settings
  %(prog)s --analyze-only                             # Just show analysis plots
        """
    )
    
    parser.add_argument("models", nargs="*", help="Ollama model names to participate in the tournament")
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models and exit")
    parser.add_argument("--tournament", choices=["round-robin", "elimination", "league"], 
                       default="league", help="Tournament type (default: league)")
    parser.add_argument("--rounds", type=int, default=10, 
                       help="Number of rounds per match (or total rounds for league)")
    parser.add_argument("--temperature", type=float, default=0.7, 
                       help="LLM temperature (0.0-1.0, default: 0.7)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--add-baselines", action="store_true", 
                       help="Add Random and Counter baseline agents")
    parser.add_argument("--log-file", default="data/logs/tournament.jsonl",
                       help="JSONL log file path")
    parser.add_argument("--no-viz", action="store_true", help="Skip visualization generation")
    parser.add_argument("--analyze-only", action="store_true", 
                       help="Only generate analysis plots from existing log file")
    
    args = parser.parse_args()
    
    # Handle list models
    if args.list_models:
        list_available_models()
        return
    
    # Handle analyze-only mode
    if args.analyze_only:
        if os.path.exists(args.log_file):
            tournament_data = load_tournament_data(args.log_file)
            if tournament_data:
                create_visualization_plots(tournament_data)
            else:
                print("❌ No tournament data found in log file")
        else:
            print("❌ Log file not found")
        return
    
    # Validate models
    if not args.models:
        print("❌ No models specified. Use --list-models to see available models.")
        return
    
    # Validate temperature
    if not 0.0 <= args.temperature <= 1.0:
        print("❌ Temperature must be between 0.0 and 1.0")
        return
    
    # Validate rounds
    if args.rounds < 1:
        print("❌ Number of rounds must be at least 1")
        return
    
    # Check if models exist
    try:
        available_models = get_available_models()
        for model in args.models:
            if model not in available_models:
                print(f"❌ Model '{model}' not found. Use --list-models to see available models.")
                return
    except Exception as e:
        print(f"⚠️ Warning: Could not verify model availability: {e}")
    
    print("🎮 Rock Paper Scissors Royale")
    print("=" * 50)
    
    # Create agents
    agents = []
    
    for i, model in enumerate(args.models):
        agent = create_agent(
            model=model,
            agent_type="llm",
            temperature=args.temperature,
            seed=args.seed + i,
            name=model
        )
        agents.append(agent)
        print(f"🤖 Created agent: {agent.name}")
    
    # Add baseline agents if requested
    if args.add_baselines:
        random_agent = create_agent("random", "random", name="Random")
        counter_agent = create_agent("counter", "counter", name="Counter")
        agents.extend([random_agent, counter_agent])
        print("🎲 Added baseline agents: Random, Counter")
    
    if len(agents) < 2:
        print("❌ Need at least 2 agents for a tournament")
        return
    
    print(f"\n👥 Tournament participants: {[agent.name for agent in agents]}")
    print(f"🎯 Tournament type: {args.tournament}")
    print(f"🎲 Rounds: {args.rounds}")
    print(f"🌡️ Temperature: {args.temperature}")
    
    # Run tournament
    try:
        tournament_manager = TournamentManager(args.log_file)
        
        if args.tournament == "round-robin":
            results = tournament_manager.run_round_robin(agents, args.rounds)
        elif args.tournament == "elimination":
            results = tournament_manager.run_single_elimination(agents, args.rounds)
        else:  # league
            results = tournament_manager.run_league(agents, args.rounds)
        
        print(f"\n🎉 Tournament completed! Champion: {results['champion']}")
        
        # Generate visualizations
        if not args.no_viz:
            tournament_data = load_tournament_data(args.log_file)
            if tournament_data:
                create_visualization_plots(tournament_data)
            else:
                print("⚠️ No tournament data found for visualization")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tournament interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Tournament error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 