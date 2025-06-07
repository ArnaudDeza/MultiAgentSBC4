"""Main CLI entrypoint for Tic-Tac-Toe Showdown tournament."""

import argparse
import sys
from typing import List
from ollama_utils import print_ollama_models
from tournament import run_tournament, get_tournament_stats
from viz import create_all_visualizations
from logger import GameLogger


def main() -> None:
    """Main CLI entrypoint for the Tic-Tac-Toe tournament."""
    parser = argparse.ArgumentParser(
        description="Tic-Tac-Toe Showdown: LLM Tournament",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic tournament with 4 default models
  python main.py
  
  # Tournament with specific models
  python main.py --models phi4 qwq llama3.3 phi4-mini
  
  # Custom settings
  python main.py --models phi4 qwq --temp 0.8 --seed 123
  
  # List available models
  python main.py --list-models
        """
    )
    
    parser.add_argument("--models", nargs="+", default=["phi4", "qwq"], 
                       help="List of Ollama models to compete (default: phi4 qwq)")
    parser.add_argument("--temp", type=float, default=0.7,
                       help="Temperature for text generation (default: 0.7)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--logfile", type=str, default="logs/tournament.jsonl",
                       help="Path to log file (default: logs/tournament.jsonl)")
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
    
    # Welcome message
    if not args.quick:
        print("🎮 Welcome to Tic-Tac-Toe Showdown!")
        print("=" * 50)
        print(f"🤖 Models competing: {', '.join(args.models)}")
        print(f"🌡️ Temperature: {args.temp}")
        print(f"🎲 Seed: {args.seed}")
        print(f"📝 Log file: {args.logfile}")
        print("=" * 50)
    
    try:
        # Initialize logger
        logger = GameLogger(args.logfile)
        
        # Run the tournament
        if not args.quick:
            print("🚀 Starting tournament...")
        
        results = run_tournament(
            models=args.models,
            temperature=args.temp,
            seed=args.seed,
            logger=logger
        )
        
        # Display results
        if not args.quick:
            print("\n📊 TOURNAMENT SUMMARY:")
            print("=" * 50)
            print(f"🏆 Champion: {results['champion']}")
            print(f"👥 Total Participants: {results['total_participants']}")
            print(f"🔄 Total Rounds: {results['total_rounds']}")
            print(f"🎮 Total Matches: {len(results['all_matches'])}")
            
            # Generate and display statistics
            stats = get_tournament_stats(results)
            print(f"\n📈 STATISTICS:")
            print("-" * 30)
            print(f"Total Games Played: {stats['total_games']}")
            
            print("\nWin Rates by Model:")
            for model, rate in stats['win_rates'].items():
                games = stats['games_by_model'][model]
                wins = stats['wins_by_model'][model]
                print(f"  {model}: {wins}/{games} ({rate:.1%})")
        
        # Generate visualizations
        if not args.no_viz:
            if not args.quick:
                print(f"\n📊 Generating visualizations...")
            
            try:
                create_all_visualizations(args.logfile)
                if not args.quick:
                    print("✅ Visualizations saved to plots/ directory")
            except Exception as e:
                print(f"⚠️ Warning: Could not generate visualizations: {e}")
                print("This may be due to missing matplotlib or display issues.")
        
        if not args.quick:
            print(f"\n🎉 Tournament complete! Check {args.logfile} for detailed logs.")
        else:
            print(f"Champion: {results['champion']}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tournament interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Tournament error: {e}")
        print("Check that Ollama is running and the specified models are available.")
        sys.exit(1)


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
            print(f"Known models: {', '.join(known_models)}")
            return False
        
        return True
    except Exception:
        # If we can't validate, assume they're okay
        return True


if __name__ == "__main__":
    main() 