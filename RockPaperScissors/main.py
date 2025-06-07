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
    """Create comprehensive visualization plots from tournament data.
    
    Args:
        tournament_data: List of tournament records from JSONL
        output_dir: Directory to save plots
    """
    ensure_data_directories()
    
    # Import the analyzer
    from utils import TournamentAnalyzer
    
    # Initialize analyzer
    analyzer = TournamentAnalyzer(tournament_data)
    
    if not analyzer.matches:
        print("⚠️ No match data found for visualization")
        return
    
    print("📊 Generating comprehensive tournament visualizations...")
    
    # Create multiple plot figures
    _create_basic_analysis_plots(analyzer, output_dir)
    _create_advanced_analysis_plots(analyzer, output_dir)
    _create_agent_comparison_plots(analyzer, output_dir)
    
    print("✅ All visualization plots generated successfully!")


def _create_basic_analysis_plots(analyzer, output_dir: str) -> None:
    """Create basic tournament analysis plots.
    
    Args:
        analyzer: TournamentAnalyzer instance
        output_dir: Directory to save plots
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rock Paper Scissors Royale - Basic Tournament Analysis", fontsize=16, fontweight='bold')
    
    # Plot 1: Move Frequency Heatmap
    agents = analyzer.agents
    moves = ["rock", "paper", "scissors"]
    
    # Get move frequency data for all agents
    heatmap_data = np.zeros((len(agents), len(moves)))
    for i, agent in enumerate(agents):
        agent_stats = analyzer.get_agent_statistics(agent)
        move_dist = agent_stats["move_distribution"]
        for j, move in enumerate(moves):
            heatmap_data[i, j] = move_dist.get(move, 0)
    
    im1 = ax1.imshow(heatmap_data, cmap='Blues', aspect='auto')
    ax1.set_xticks(range(len(moves)))
    ax1.set_xticklabels([move.title() for move in moves])
    ax1.set_yticks(range(len(agents)))
    ax1.set_yticklabels(agents, fontsize=9)
    ax1.set_title("Move Frequency Distribution by Agent", fontweight='bold')
    
    # Add percentage labels
    for i in range(len(agents)):
        for j in range(len(moves)):
            text = ax1.text(j, i, f'{heatmap_data[i, j]:.1%}',
                          ha="center", va="center", 
                          color="white" if heatmap_data[i, j] > 0.6 else "black", 
                          fontweight='bold')
    
    plt.colorbar(im1, ax=ax1, label="Move Frequency", shrink=0.8)
    
    # Plot 2: Round vs Match Win Rates Comparison
    round_win_rates = []
    match_win_rates = []
    agent_labels = []
    
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        round_win_rates.append(stats["round_win_rate"])
        match_win_rates.append(stats["match_win_rate"])
        agent_labels.append(agent)
    
    x = np.arange(len(agent_labels))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, round_win_rates, width, label='Round Win Rate', 
                    color='lightcoral', alpha=0.8)
    bars2 = ax2.bar(x + width/2, match_win_rates, width, label='Match Win Rate', 
                    color='skyblue', alpha=0.8)
    
    ax2.set_xlabel("Agents")
    ax2.set_ylabel("Win Rate")
    ax2.set_title("Round vs Match Win Rates by Agent", fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(agent_labels, rotation=45, ha='right', fontsize=9)
    ax2.legend()
    ax2.set_ylim(0, 1)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, rate in zip(bars1, round_win_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                f'{rate:.1%}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    for bar, rate in zip(bars2, match_win_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                f'{rate:.1%}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Plot 3: Enhanced Move Effectiveness Matrix
    effectiveness_matrix = analyzer.get_move_effectiveness_matrix()
    
    # Create win rate matrix for move matchups
    matchup_matrix = np.zeros((3, 3))
    encounter_matrix = np.zeros((3, 3))
    
    for i, move1 in enumerate(moves):
        for j, move2 in enumerate(moves):
            if move1 in effectiveness_matrix and move2 in effectiveness_matrix[move1]:
                data = effectiveness_matrix[move1][move2]
                matchup_matrix[i, j] = data["win_rate"]
                encounter_matrix[i, j] = data["total_encounters"]
    
    im3 = ax3.imshow(matchup_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
    ax3.set_xticks(range(3))
    ax3.set_xticklabels([f"{move.title()}\n(Defender)" for move in moves], fontsize=9)
    ax3.set_yticks(range(3))
    ax3.set_yticklabels([f"{move.title()}\n(Attacker)" for move in moves], fontsize=9)
    ax3.set_title("Move Effectiveness Matrix", fontweight='bold')
    
    # Add win rate and encounter count labels
    for i in range(3):
        for j in range(3):
            encounters = int(encounter_matrix[i, j])
            win_rate = matchup_matrix[i, j]
            if encounters > 0:
                # Color text based on background
                text_color = "white" if win_rate > 0.6 or win_rate < 0.4 else "black"
                ax3.text(j, i, f'{win_rate:.1%}\n({encounters} games)',
                        ha="center", va="center", color=text_color, 
                        fontweight='bold', fontsize=8)
    
    plt.colorbar(im3, ax=ax3, label="Win Rate", shrink=0.8)
    
    # Plot 4: Tournament Statistics Summary
    tournament_summary = analyzer.get_tournament_summary()
    
    # Create a detailed statistics display
    stats_text = [
        f"🏆 TOURNAMENT SUMMARY",
        f"═══════════════════════════",
        f"Type: {tournament_summary['tournament_type'].title()}",
        f"Participants: {tournament_summary['total_participants']}",
        f"Total Rounds: {tournament_summary['total_rounds']:,}",
        f"Total Matches: {tournament_summary['total_matches']}",
        f"Champion: {tournament_summary['champion']}",
        "",
        f"⚙️ CONFIGURATION",
        f"Temperature: {tournament_summary['temperature']}",
        f"Random Seed: {tournament_summary['seed']}",
        "",
        f"📊 GLOBAL MOVE DISTRIBUTION",
    ]
    
    move_dist = tournament_summary['global_move_distribution']
    total_moves = sum(move_dist.values())
    
    for move in moves:
        count = move_dist.get(move, 0)
        percentage = count / total_moves * 100 if total_moves > 0 else 0
        bar_length = int(percentage / 2)  # Scale for visual bar
        bar = "█" * bar_length + "░" * (50 - bar_length)
        stats_text.append(f"{move.title():>9}: {count:>4} ({percentage:>5.1f}%) {bar[:20]}")
    
    # Add performance metrics
    stats_text.extend([
        "",
        f"📈 PERFORMANCE METRICS",
        f"Rounds per Agent: {tournament_summary['rounds_per_participant']:.1f}",
    ])
    
    if tournament_summary['tournament_duration']:
        duration = tournament_summary['tournament_duration']
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        stats_text.append(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    ax4.text(0.05, 0.95, "\n".join(stats_text), transform=ax4.transAxes, 
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    ax4.set_title("Tournament Statistics Dashboard", fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(output_dir, "basic_tournament_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📈 Saved basic analysis plot: {output_path}")
    
    plt.close()


def _create_advanced_analysis_plots(analyzer, output_dir: str) -> None:
    """Create advanced tournament analysis plots.
    
    Args:
        analyzer: TournamentAnalyzer instance
        output_dir: Directory to save plots
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rock Paper Scissors Royale - Advanced Analysis", fontsize=16, fontweight='bold')
    
    agents = analyzer.agents
    
    # Plot 1: Agent Performance Radar Chart (simplified as bar chart for now)
    agent_metrics = []
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        agent_metrics.append({
            'name': agent,
            'round_win_rate': stats['round_win_rate'],
            'match_win_rate': stats['match_win_rate'],
            'total_opponents': stats['total_opponents'],
            'total_rounds': stats['total_rounds']
        })
    
    # Sort by match win rate
    agent_metrics.sort(key=lambda x: x['match_win_rate'], reverse=True)
    
    names = [m['name'] for m in agent_metrics]
    match_wr = [m['match_win_rate'] for m in agent_metrics]
    
    bars = ax1.barh(range(len(names)), match_wr, color=plt.cm.viridis(np.linspace(0, 1, len(names))))
    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names)
    ax1.set_xlabel("Match Win Rate")
    ax1.set_title("Agent Performance Ranking", fontweight='bold')
    ax1.set_xlim(0, 1)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars, match_wr)):
        ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{rate:.1%}', va='center', fontweight='bold')
    
    # Plot 2: Head-to-Head Matrix
    if len(agents) >= 2:
        h2h_matrix = np.zeros((len(agents), len(agents)))
        
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    h2h = analyzer.get_head_to_head_analysis(agent1, agent2)
                    if h2h['total_rounds'] > 0:
                        h2h_matrix[i, j] = h2h['agent1_win_rate']
        
        im2 = ax2.imshow(h2h_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
        ax2.set_xticks(range(len(agents)))
        ax2.set_xticklabels(agents, rotation=45, ha='right', fontsize=9)
        ax2.set_yticks(range(len(agents)))
        ax2.set_yticklabels(agents, fontsize=9)
        ax2.set_title("Head-to-Head Win Rate Matrix", fontweight='bold')
        
        # Add win rate labels
        for i in range(len(agents)):
            for j in range(len(agents)):
                if i != j and h2h_matrix[i, j] > 0:
                    text_color = "white" if h2h_matrix[i, j] > 0.6 or h2h_matrix[i, j] < 0.4 else "black"
                    ax2.text(j, i, f'{h2h_matrix[i, j]:.1%}',
                            ha="center", va="center", color=text_color, fontweight='bold')
        
        plt.colorbar(im2, ax=ax2, label="Win Rate vs Opponent", shrink=0.8)
    else:
        ax2.text(0.5, 0.5, "Need at least 2 agents\nfor head-to-head analysis", 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title("Head-to-Head Analysis", fontweight='bold')
    
    # Plot 3: Move Frequency Distribution (Pie Charts)
    if len(agents) <= 4:  # Only show if we have few agents
        for idx, agent in enumerate(agents[:4]):
            stats = analyzer.get_agent_statistics(agent)
            move_freq = stats['move_frequency']
            
            # Create subplot for pie chart
            ax_pie = plt.subplot(4, 4, 12 + idx)  # Position in bottom area
            
            sizes = [move_freq.get(move, 0) for move in ['rock', 'paper', 'scissors']]
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            if sum(sizes) > 0:
                ax_pie.pie(sizes, labels=['Rock', 'Paper', 'Scissors'], colors=colors, 
                          autopct='%1.1f%%', startangle=90)
                ax_pie.set_title(f"{agent}", fontsize=10, fontweight='bold')
            else:
                ax_pie.text(0.5, 0.5, "No data", ha='center', va='center')
                ax_pie.set_title(f"{agent}", fontsize=10)
    
    # Plot 4: Tournament Timeline (if available)
    round_summaries = [r for r in analyzer.data if r.get("type") == "round_summary"]
    
    if round_summaries:
        rounds = []
        agent_scores = defaultdict(list)
        
        for summary in round_summaries:
            round_num = summary["round"]
            standings = summary["standings"]
            rounds.append(round_num)
            
            for agent in agents:
                points = standings.get(agent, {}).get("points", 0)
                agent_scores[agent].append(points)
        
        # Plot progression for top 3 agents
        top_agents = sorted(agents, key=lambda x: agent_scores[x][-1] if agent_scores[x] else 0, reverse=True)[:3]
        
        for agent in top_agents:
            if agent_scores[agent]:
                ax4.plot(rounds, agent_scores[agent], marker='o', label=agent, linewidth=2, markersize=4)
        
        ax4.set_xlabel("Round Number")
        ax4.set_ylabel("Points")
        ax4.set_title("Tournament Progression (Top 3)", fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        # Show match distribution over time if no round summaries
        match_times = []
        for i, match in enumerate(analyzer.matches):
            match_times.append(i + 1)
        
        if match_times:
            ax4.hist(match_times, bins=min(20, len(match_times)//5 + 1), alpha=0.7, color='skyblue')
            ax4.set_xlabel("Match Number")
            ax4.set_ylabel("Frequency")
            ax4.set_title("Match Distribution", fontweight='bold')
            ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(output_dir, "advanced_tournament_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📈 Saved advanced analysis plot: {output_path}")
    
    plt.close()


def _create_agent_comparison_plots(analyzer, output_dir: str) -> None:
    """Create detailed agent comparison plots.
    
    Args:
        analyzer: TournamentAnalyzer instance
        output_dir: Directory to save plots
    """
    agents = analyzer.agents
    
    if len(agents) < 2:
        print("⚠️ Need at least 2 agents for comparison plots")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rock Paper Scissors Royale - Agent Comparison", fontsize=16, fontweight='bold')
    
    # Plot 1: Multi-metric comparison
    metrics = ['round_win_rate', 'match_win_rate', 'total_opponents', 'total_rounds']
    metric_data = {metric: [] for metric in metrics}
    
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        for metric in metrics:
            if metric in ['total_opponents', 'total_rounds']:
                # Normalize these metrics
                metric_data[metric].append(stats[metric] / max(1, max([analyzer.get_agent_statistics(a)[metric] for a in agents])))
            else:
                metric_data[metric].append(stats[metric])
    
    x = np.arange(len(agents))
    width = 0.2
    
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    labels = ['Round Win Rate', 'Match Win Rate', 'Opponent Diversity', 'Experience']
    
    for i, (metric, color, label) in enumerate(zip(metrics, colors, labels)):
        ax1.bar(x + i * width, metric_data[metric], width, label=label, color=color, alpha=0.8)
    
    ax1.set_xlabel("Agents")
    ax1.set_ylabel("Normalized Score")
    ax1.set_title("Multi-Metric Agent Comparison", fontweight='bold')
    ax1.set_xticks(x + width * 1.5)
    ax1.set_xticklabels(agents, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Move preference scatter plot
    rock_prefs = []
    paper_prefs = []
    
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        move_dist = stats['move_distribution']
        rock_prefs.append(move_dist.get('rock', 0))
        paper_prefs.append(move_dist.get('paper', 0))
    
    scatter = ax2.scatter(rock_prefs, paper_prefs, s=100, alpha=0.7, c=range(len(agents)), cmap='viridis')
    
    for i, agent in enumerate(agents):
        ax2.annotate(agent, (rock_prefs[i], paper_prefs[i]), xytext=(5, 5), 
                    textcoords='offset points', fontsize=9, fontweight='bold')
    
    ax2.set_xlabel("Rock Preference")
    ax2.set_ylabel("Paper Preference")
    ax2.set_title("Agent Move Preference Map", fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # Add reference lines
    ax2.axline((0.33, 0.33), slope=0, color='red', linestyle='--', alpha=0.5, label='Balanced Strategy')
    ax2.legend()
    
    # Plot 3: Performance vs Experience
    experience = []
    performance = []
    
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        experience.append(stats['total_rounds'])
        performance.append(stats['match_win_rate'])
    
    ax3.scatter(experience, performance, s=100, alpha=0.7, c=range(len(agents)), cmap='plasma')
    
    for i, agent in enumerate(agents):
        ax3.annotate(agent, (experience[i], performance[i]), xytext=(5, 5), 
                    textcoords='offset points', fontsize=9, fontweight='bold')
    
    ax3.set_xlabel("Total Rounds Played")
    ax3.set_ylabel("Match Win Rate")
    ax3.set_title("Performance vs Experience", fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1)
    
    # Plot 4: Agent statistics table
    ax4.axis('tight')
    ax4.axis('off')
    
    # Create table data
    table_data = []
    headers = ['Agent', 'Rounds', 'R.W.R.', 'M.W.R.', 'Rock%', 'Paper%', 'Scissors%']
    
    for agent in agents:
        stats = analyzer.get_agent_statistics(agent)
        move_dist = stats['move_distribution']
        row = [
            agent,
            f"{stats['total_rounds']}",
            f"{stats['round_win_rate']:.1%}",
            f"{stats['match_win_rate']:.1%}",
            f"{move_dist.get('rock', 0):.1%}",
            f"{move_dist.get('paper', 0):.1%}",
            f"{move_dist.get('scissors', 0):.1%}"
        ]
        table_data.append(row)
    
    table = ax4.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax4.set_title("Agent Performance Summary", fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(output_dir, "agent_comparison_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📈 Saved agent comparison plot: {output_path}")
    
    plt.close()


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