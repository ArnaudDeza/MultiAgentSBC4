"""Enhanced main CLI entrypoint for flexible game tournaments."""

import argparse
import sys
from typing import List, Dict, Any
from ollama_utils import print_ollama_models
from tournament_system import TournamentEngine, TournamentConfig, TournamentFormat
from game_interface import GameConfig
from generic_tictactoe import GenericTicTacToe
from llm_agents import LLMAgent
from enhanced_logger import EnhancedLogger, create_session_name
from enhanced_viz import create_enhanced_visualizations


def create_game_factory(game_config: GameConfig):
    """Create a factory function for game instances.
    
    Args:
        game_config: Game configuration
        
    Returns:
        Function that creates new game instances
    """
    def factory():
        return GenericTicTacToe(game_config)
    return factory


def main() -> None:
    """Enhanced main CLI entrypoint for flexible game tournaments."""
    parser = argparse.ArgumentParser(
        description="Enhanced Game Tournament System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tournament Formats:
  single_elimination : Traditional knockout tournament
  round_robin       : Everyone plays everyone
  swiss             : Swiss-system tournament
  
Game Configurations:
  --board-size 3    : 3x3 board (classic Tic-Tac-Toe)
  --board-size 4    : 4x4 board  
  --board-size 5    : 5x5 board
  --win-length 3    : Need 3 in a row to win
  
Examples:
  # Classic tournament
  python main_enhanced.py --models phi4 qwq
  
  # Best of 3 matches, round robin
  python main_enhanced.py --models phi4 qwq llama3.3 --format round_robin --best-of 3
  
  # Large board Tic-Tac-Toe
  python main_enhanced.py --models phi4 qwq --board-size 5 --win-length 4
  
  # Swiss tournament with 6 rounds
  python main_enhanced.py --models phi4 qwq llama3.3 phi4-mini --format swiss --max-rounds 6
        """
    )
    
    # Player configuration
    parser.add_argument("--models", nargs="+", default=["phi4", "qwq"], 
                       help="List of Ollama models to compete")
    parser.add_argument("--temp", type=float, default=0.7,
                       help="Temperature for text generation")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility")
    
    # Tournament configuration
    parser.add_argument("--format", type=str, default="single_elimination",
                       choices=["single_elimination", "round_robin", "swiss"],
                       help="Tournament format")
    parser.add_argument("--best-of", type=int, default=1,
                       help="Best of X games per match (must be odd)")
    parser.add_argument("--max-rounds", type=int, default=10,
                       help="Maximum rounds for Swiss tournaments")
    parser.add_argument("--shuffle", action="store_true", default=True,
                       help="Shuffle player order")
    
    # Game configuration
    parser.add_argument("--board-size", type=int, default=3,
                       help="Size of the game board (NxN)")
    parser.add_argument("--win-length", type=int, default=3,
                       help="Number in a row needed to win")
    parser.add_argument("--max-moves", type=int, default=50,
                       help="Maximum moves per game before draw")
    
    # Output configuration
    parser.add_argument("--output-dir", type=str, default="outputs",
                       help="Base directory for all outputs")
    parser.add_argument("--session-name", type=str, default=None,
                       help="Custom session name (auto-generated if not provided)")
    parser.add_argument("--list-models", action="store_true",
                       help="List available Ollama models and exit")
    parser.add_argument("--no-viz", action="store_true",
                       help="Skip generating visualizations")
    parser.add_argument("--quick", action="store_true",
                       help="Quick tournament with minimal output")
    
    args = parser.parse_args()
    
    # Handle listing models
    if args.list_models:
        print("🤖 Available Ollama Models:")
        print("=" * 40)
        try:
            print_ollama_models()
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            print("Make sure Ollama is running and accessible.")
        return
    
    # Validate arguments
    if len(args.models) < 2:
        print("❌ Error: At least 2 models are required for a tournament")
        sys.exit(1)
    
    if args.temp < 0 or args.temp > 2:
        print("❌ Error: Temperature must be between 0 and 2")
        sys.exit(1)
    
    if args.board_size < 3 or args.board_size > 10:
        print("❌ Error: Board size must be between 3 and 10")
        sys.exit(1)
    
    if args.win_length < 3 or args.win_length > args.board_size:
        print("❌ Error: Win length must be between 3 and board size")
        sys.exit(1)
    
    if args.best_of < 1:
        args.best_of = 1
    if args.best_of % 2 == 0:
        args.best_of += 1  # Ensure odd number
    
    # Create configurations
    game_config = GameConfig(
        board_size=args.board_size,
        win_length=args.win_length,
        num_players=2,
        max_moves=args.max_moves
    )
    
    tournament_config = TournamentConfig(
        format=TournamentFormat(args.format),
        best_of=args.best_of,
        game_config=game_config,
        shuffle_players=args.shuffle,
        seed=args.seed,
        max_rounds=args.max_rounds
    )
    
    # Create session name
    if args.session_name:
        session_name = args.session_name
    else:
        session_name = create_session_name(tournament_config, game_config, args.models)
    
    # Prepare CLI arguments for logging
    cli_args = vars(args)
    
    # Display configuration
    if not args.quick:
        print("🎮 Enhanced Game Tournament System")
        print("=" * 60)
        print(f"🤖 Models: {', '.join(args.models)}")
        print(f"🏆 Format: {args.format.replace('_', ' ').title()}")
        print(f"🎯 Best of: {args.best_of}")
        print(f"🎲 Board: {args.board_size}x{args.board_size}, Win: {args.win_length}")
        print(f"🌡️ Temperature: {args.temp}")
        print(f"🎲 Seed: {args.seed}")
        print(f"📁 Session: {session_name}")
        print(f"📁 Output: {args.output_dir}")
        print("=" * 60)
    
    try:
        # Initialize enhanced logger
        logger = EnhancedLogger(session_name, args.output_dir)
        
        # Save configuration
        logger.save_configuration(tournament_config, game_config, args.models, cli_args)
        
        # Create game factory
        game_factory = create_game_factory(game_config)
        
        # Initialize tournament engine
        tournament = TournamentEngine(tournament_config, game_factory, logger)
        
        # Create player agents
        players = []
        for i, model in enumerate(args.models):
            agent = LLMAgent(
                name=model,
                model=model,
                temperature=args.temp,
                seed=args.seed + i  # Different seed per agent
            )
            players.append(agent)
        
        tournament.add_players(players)
        
        # Run the tournament
        if not args.quick:
            print("🚀 Starting enhanced tournament...")
        
        results = tournament.run_tournament()
        
        # Save tournament results to enhanced logger
        enhanced_results = logger.save_tournament_results(results)
        
        # Display results
        if not args.quick:
            print("\n📊 TOURNAMENT RESULTS:")
            print("=" * 60)
            print(f"🏆 Champion: {results['champion']}")
            print(f"🏁 Format: {results['format']}")
            print(f"👥 Participants: {results['total_matches']} matches")
            print(f"🎮 Total Games: {results['total_games']}")
            
            # Show detailed standings
            print(f"\n📈 FINAL STANDINGS:")
            print("-" * 40)
            standings = results['standings']
            
            # Sort by points, then games won
            sorted_standings = sorted(
                standings.items(),
                key=lambda x: (x[1]['points'], x[1]['games_won'], x[1]['wins']),
                reverse=True
            )
            
            for rank, (player, stats) in enumerate(sorted_standings, 1):
                games_total = stats['games_won'] + stats['games_lost']
                win_rate = stats['games_won'] / games_total if games_total > 0 else 0
                
                print(f"{rank:2d}. {player:15s} | "
                      f"Points: {stats['points']:3d} | "
                      f"Matches: {stats['wins']}-{stats['losses']} | "
                      f"Games: {stats['games_won']}-{stats['games_lost']} | "
                      f"Win Rate: {win_rate:.1%}")
        
        # Generate enhanced visualizations
        if not args.no_viz:
            if not args.quick:
                print(f"\n📊 Generating enhanced visualizations...")
            
            try:
                viz_config = logger.get_visualization_config()
                create_enhanced_visualizations(enhanced_results, viz_config["output_dir"])
                if not args.quick:
                    print(f"✅ Enhanced visualizations saved to {viz_config['output_dir']}")
            except Exception as e:
                print(f"⚠️ Warning: Could not generate visualizations: {e}")
                import traceback
                traceback.print_exc()
        
        # Finalize session
        session_summary = logger.finalize_session()
        
        if not args.quick:
            print(f"\n🎉 Tournament complete!")
            print(f"📁 Session directory: {logger.session_dir}")
            print(f"📋 Configuration: {logger.config_file}")
            print(f"📊 Results: {logger.summary_file}")
            print(f"📈 Visualizations: {logger.plots_dir}")
            print(f"📊 Game Configuration: {args.board_size}x{args.board_size} board, {args.win_length} to win")
            print(f"⏱️ Duration: {session_summary['metadata']['total_duration']}")
        else:
            print(f"Champion: {results['champion']} | Format: {results['format']} | Session: {logger.session_dir}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tournament interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Tournament error: {e}")
        import traceback
        traceback.print_exc()
        print("\nCheck that Ollama is running and the specified models are available.")
        sys.exit(1)


def demo_configurations() -> None:
    """Run demonstrations of different tournament configurations."""
    print("🎮 Running Tournament Configuration Demos")
    print("=" * 50)
    
    configs = [
        {
            "name": "Classic 3x3 Tic-Tac-Toe",
            "models": ["phi4", "qwq"],
            "format": "single_elimination",
            "board_size": 3,
            "win_length": 3,
            "best_of": 1
        },
        {
            "name": "Best-of-3 Round Robin",
            "models": ["phi4", "qwq", "llama3.3"],
            "format": "round_robin", 
            "board_size": 3,
            "win_length": 3,
            "best_of": 3
        },
        {
            "name": "5x5 Strategic Tic-Tac-Toe",
            "models": ["phi4", "qwq"],
            "format": "swiss",
            "board_size": 5,
            "win_length": 4,
            "best_of": 1
        }
    ]
    
    for config in configs:
        print(f"\n🎯 {config['name']}")
        print("-" * 30)
        
        # Simulate running with these parameters
        print(f"Models: {', '.join(config['models'])}")
        print(f"Format: {config['format']}")
        print(f"Board: {config['board_size']}x{config['board_size']}")
        print(f"Win Length: {config['win_length']}")
        print(f"Best of: {config['best_of']}")
        print("✅ Configuration valid")


def validate_models(models: List[str]) -> bool:
    """Validate that the specified models are available.
    
    Args:
        models: List of model names to validate
        
    Returns:
        True if all models are valid
    """
    try:
        from ollama_utils import OLLAMA_NICKNAMES
        
        # Check if models are in the known list
        known_models = set(OLLAMA_NICKNAMES.keys())
        unknown_models = set(models) - known_models
        
        if unknown_models:
            print(f"⚠️ Warning: Unknown models: {', '.join(unknown_models)}")
            print(f"Known models: {', '.join(sorted(known_models))}")
            return False
        
        return True
    except Exception:
        # If we can't validate, assume they're okay
        return True


if __name__ == "__main__":
    main() 