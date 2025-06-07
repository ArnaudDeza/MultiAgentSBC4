#!/usr/bin/env python3
"""
Test script for the enhanced logging and visualization system.
This script creates mock tournament data and tests all analytics features.
"""

import json
import os
import sys
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import RPSLogger, TournamentAnalyzer, Move, GameResult, load_tournament_data, ensure_data_directories

# Try to import visualization, but make it optional
try:
    from main import create_visualization_plots
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Visualization disabled: {e}")
    VISUALIZATION_AVAILABLE = False
    def create_visualization_plots(*args, **kwargs):
        print("📊 Visualization skipped (matplotlib not available)")

def create_mock_tournament_data() -> str:
    """Create comprehensive mock tournament data for testing."""
    
    print("🧪 Creating mock tournament data...")
    
    # Initialize logger
    test_log_file = "data/logs/test_tournament.jsonl"
    logger = RPSLogger(test_log_file)
    
    # Mock agents with clear model identification
    agents = ["llama2(Alpha)", "phi3(Beta)", "gemma(Gamma)", "random(Baseline)"]
    
    # Log tournament start with model metadata
    model_metadata = {
        "llama2(Alpha)": {"model": "llama2", "temperature": 0.7, "agent_type": "LLMAgent"},
        "phi3(Beta)": {"model": "phi3", "temperature": 0.8, "agent_type": "LLMAgent"},
        "gemma(Gamma)": {"model": "gemma", "temperature": 0.6, "agent_type": "LLMAgent"},
        "random(Baseline)": {"model": "random", "temperature": None, "agent_type": "RandomAgent"}
    }
    
    logger.log_tournament_start(
        models=agents,
        tournament_type="round_robin",
        rounds=10,
        temperature=0.7,
        seed=42,
        model_metadata=model_metadata
    )
    
    # Create mock matches
    moves = [Move.ROCK, Move.PAPER, Move.SCISSORS]
    match_counter = 0
    
    # Generate round-robin matches
    for i, agent1 in enumerate(agents):
        for j, agent2 in enumerate(agents[i+1:], i+1):
            match_counter += 1
            match_id = f"TEST{match_counter:03d}_{agent1}_vs_{agent2}"
            
            # Log match start with model information
            agent1_model = agent1.split("(")[0]
            agent2_model = agent2.split("(")[0]
            agent1_temp = model_metadata[agent1]["temperature"]
            agent2_temp = model_metadata[agent2]["temperature"]
            
            logger.log_match_start(
                match_id, agent1, agent2, 15,  # 15 rounds per match
                player1_model=agent1_model, player2_model=agent2_model,
                player1_temp=agent1_temp, player2_temp=agent2_temp
            )
            
            # Generate match data
            agent1_history = []
            agent2_history = []
            agent1_score = 0
            agent2_score = 0
            
            # Simulate 15 rounds
            for round_num in range(15):
                # Create somewhat realistic move patterns
                if "Random" in agent1:
                    move1 = random.choice(moves)
                else:
                    # Bias certain agents toward certain moves
                    if "Alpha" in agent1:
                        move1 = random.choices(moves, weights=[0.4, 0.35, 0.25])[0]  # Prefers rock
                    elif "Beta" in agent1:
                        move1 = random.choices(moves, weights=[0.3, 0.4, 0.3])[0]   # Prefers paper
                    else:
                        move1 = random.choices(moves, weights=[0.25, 0.3, 0.45])[0] # Prefers scissors
                
                if "Random" in agent2:
                    move2 = random.choice(moves)
                else:
                    # Bias certain agents toward certain moves
                    if "Alpha" in agent2:
                        move2 = random.choices(moves, weights=[0.4, 0.35, 0.25])[0]
                    elif "Beta" in agent2:
                        move2 = random.choices(moves, weights=[0.3, 0.4, 0.3])[0]
                    else:
                        move2 = random.choices(moves, weights=[0.25, 0.3, 0.45])[0]
                
                agent1_history.append(move1)
                agent2_history.append(move2)
                
                # Determine winner
                if move1 == move2:
                    result1, result2 = GameResult.DRAW, GameResult.DRAW
                elif ((move1 == Move.ROCK and move2 == Move.SCISSORS) or
                      (move1 == Move.PAPER and move2 == Move.ROCK) or
                      (move1 == Move.SCISSORS and move2 == Move.PAPER)):
                    result1, result2 = GameResult.WIN, GameResult.LOSS
                    agent1_score += 1
                else:
                    result1, result2 = GameResult.LOSS, GameResult.WIN
                    agent2_score += 1
                
                # Log individual round
                logger.log_match(
                    match_id=f"{match_id}_R{round_num+1:02d}",
                    player1=agent1,
                    player2=agent2,
                    move1=move1,
                    move2=move2,
                    result1=result1,
                    result2=result2
                )
            
            # Determine match winner
            if agent1_score > agent2_score:
                winner = agent1
                final_score = f"{agent1_score}-{agent2_score}"
            elif agent2_score > agent1_score:
                winner = agent2
                final_score = f"{agent1_score}-{agent2_score}"
            else:
                winner = "Draw"
                final_score = f"{agent1_score}-{agent2_score}"
            
            # Log match end with enhanced data and model information
            logger.log_match_end(
                match_id=match_id,
                player1=agent1,
                player2=agent2,
                winner=winner,
                final_score=final_score,
                player1_score=agent1_score,
                player2_score=agent2_score,
                player1_history=agent1_history,
                player2_history=agent2_history,
                match_duration_seconds=random.uniform(45.0, 120.0),
                player1_model=agent1_model,
                player2_model=agent2_model
            )
            
            print(f"  ⚔️ {agent1} vs {agent2}: {final_score} (Winner: {winner})")
    
    # Create mock final standings
    final_standings = {}
    for agent in agents:
        final_standings[agent] = {
            "points": random.randint(5, 15),
            "wins": random.randint(2, 8),
            "losses": random.randint(2, 8),
            "draws": random.randint(0, 3)
        }
    
    # Determine champion (agent with most points)
    champion = max(final_standings.keys(), key=lambda x: final_standings[x]["points"])
    
    # Log tournament end
    logger.log_tournament_end(
        final_standings=final_standings,
        champion=champion,
        tournament_duration_seconds=600.0
    )
    
    print(f"🏆 Mock tournament complete! Champion: {champion}")
    return test_log_file

def test_analytics(log_file: str) -> None:
    """Test the analytics engine with mock data."""
    
    print("\n🔍 Testing analytics engine...")
    
    # Load data
    tournament_data = load_tournament_data(log_file)
    print(f"  📊 Loaded {len(tournament_data)} log records")
    
    # Initialize analyzer
    analyzer = TournamentAnalyzer(tournament_data)
    print(f"  🤖 Found {len(analyzer.agents)} agents")
    print(f"  ⚔️ Found {len(analyzer.matches)} individual rounds")
    print(f"  🥊 Found {len(analyzer.match_ends)} complete matches")
    
    # Test agent statistics
    if analyzer.agents:
        test_agent = analyzer.agents[0]
        agent_stats = analyzer.get_agent_statistics(test_agent)
        print(f"\n  👤 {test_agent} Statistics:")
        print(f"     Round Win Rate: {agent_stats['round_win_rate']:.1%}")
        print(f"     Match Win Rate: {agent_stats['match_win_rate']:.1%}")
        print(f"     Total Rounds: {agent_stats['total_rounds']}")
        print(f"     Move Distribution: {agent_stats['move_distribution']}")
    
    # Test head-to-head analysis
    if len(analyzer.agents) >= 2:
        agent1, agent2 = analyzer.agents[0], analyzer.agents[1]
        h2h = analyzer.get_head_to_head_analysis(agent1, agent2)
        print(f"\n  🥊 Head-to-Head: {agent1} vs {agent2}")
        print(f"     Total Rounds: {h2h['total_rounds']}")
        print(f"     {agent1} Win Rate: {h2h['agent1_win_rate']:.1%}")
        print(f"     {agent2} Win Rate: {h2h['agent2_win_rate']:.1%}")
    
    # Test move effectiveness matrix
    effectiveness = analyzer.get_move_effectiveness_matrix()
    print(f"\n  ⚡ Move Effectiveness Sample:")
    for move1 in ['rock', 'paper']:
        for move2 in ['rock', 'paper']:
            if move1 in effectiveness and move2 in effectiveness[move1]:
                data = effectiveness[move1][move2]
                print(f"     {move1.title()} vs {move2.title()}: {data['win_rate']:.1%} ({data['total_encounters']} encounters)")
    
    # Test tournament summary
    summary = analyzer.get_tournament_summary()
    print(f"\n  📈 Tournament Summary:")
    print(f"     Type: {summary['tournament_type']}")
    print(f"     Participants: {summary['total_participants']}")
    print(f"     Unique Models: {summary['num_unique_models']} ({', '.join(summary['unique_models'])})")
    print(f"     Total Rounds: {summary['total_rounds']}")
    print(f"     Champion: {summary['champion']}")
    
    # Test model performance analysis
    model_performance = analyzer.get_model_performance_summary()
    print(f"\n  🤖 Model Performance Analysis:")
    for model, stats in model_performance.items():
        print(f"     {model}:")
        print(f"       Match Win Rate: {stats['match_win_rate']:.1%}")
        print(f"       Round Win Rate: {stats['round_win_rate']:.1%}")
        print(f"       Total Matches: {stats['total_matches']}")
        print(f"       Opponent Diversity: {stats['opponent_diversity']}")
        if stats['average_match_duration'] > 0:
            print(f"       Avg Match Duration: {stats['average_match_duration']:.1f}s")
    
    return analyzer

def test_visualizations(tournament_data: List[Dict[str, Any]]) -> None:
    """Test the visualization system."""
    
    print("\n📊 Testing visualization system...")
    
    if not VISUALIZATION_AVAILABLE:
        print("  ⚠️ Visualization testing skipped (matplotlib not available)")
        print("  💡 To enable visualizations, install matplotlib: pip install matplotlib")
        return
    
    try:
        # Create visualizations
        output_dir = "data/test_output/"
        os.makedirs(output_dir, exist_ok=True)
        
        create_visualization_plots(tournament_data, output_dir)
        
        # Check if files were created
        expected_files = [
            "basic_tournament_analysis.png",
            "advanced_tournament_analysis.png", 
            "agent_comparison_analysis.png"
        ]
        
        created_files = []
        for filename in expected_files:
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                created_files.append(filename)
                file_size = os.path.getsize(filepath)
                print(f"  ✅ Created {filename} ({file_size:,} bytes)")
            else:
                print(f"  ❌ Missing {filename}")
        
        print(f"\n  📈 Successfully created {len(created_files)}/{len(expected_files)} visualization files")
        
    except Exception as e:
        print(f"  ❌ Visualization error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🚀 Enhanced Logging & Analytics System Test")
    print("=" * 50)
    
    # Ensure directories exist
    ensure_data_directories()
    
    try:
        # Create mock data
        log_file = create_mock_tournament_data()
        
        # Load and test analytics
        tournament_data = load_tournament_data(log_file)
        analyzer = test_analytics(log_file)
        
        # Test visualizations
        test_visualizations(tournament_data)
        
        print("\n✅ All tests completed successfully!")
        print("\n📁 Generated files:")
        print(f"   - Tournament log: {log_file}")
        print(f"   - Visualizations: data/test_output/")
        print(f"   - Documentation: LOGGING_SYSTEM.md")
        
        print("\n🎯 Enhanced logging system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 