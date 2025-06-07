#!/usr/bin/env python3
"""Demo script for the Enhanced Tournament System with Logging."""

import time
from pathlib import Path
import sys

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print('🎮 Enhanced Tournament System Demo with Logging')
print('=' * 60)

# Import the new modules
try:
    from game_interface import GameConfig, IGame
    from generic_tictactoe import GenericTicTacToe
    from connect_four import ConnectFour
    from tournament_system import TournamentConfig, TournamentFormat, TournamentEngine
    from llm_agents import LLMAgent
    from enhanced_logger import EnhancedLogger, create_session_name
    from enhanced_viz import create_enhanced_visualizations
    
    print('✅ All enhanced modules imported successfully!')
    
    # Demo different game configurations
    print('\n🎲 Game Configuration Examples:')
    print('-' * 30)
    
    # Standard Tic-Tac-Toe
    config1 = GameConfig(board_size=3, win_length=3)
    game1 = GenericTicTacToe(config1)
    print(f'📋 Standard 3x3 Tic-Tac-Toe:')
    print(game1.display())
    
    # Large board
    config2 = GameConfig(board_size=5, win_length=4)
    game2 = GenericTicTacToe(config2)
    print(f'\n📋 5x5 Strategic Tic-Tac-Toe (need 4 in a row):')
    print(game2.display())
    
    # Connect Four
    config3 = GameConfig(board_size=7, win_length=4)
    config3.extra_params['height'] = 6
    game3 = ConnectFour(config3)
    print(f'\n📋 Connect Four (7x6 board):')
    print(game3.display())
    
    # Test some moves
    print(f'\n🎯 Testing Game Mechanics:')
    print('-' * 30)
    
    # Tic-Tac-Toe moves
    game1.make_move((1, 1), 'X')
    game1.make_move((0, 0), 'O')
    game1.make_move((2, 2), 'X')
    print(f'Tic-Tac-Toe after some moves:')
    print(game1.display())
    print(f'Valid moves for X: {game1.get_valid_moves("X")}')
    
    # Connect Four moves
    game3.make_move(3, 'R')  # Drop in column 3
    game3.make_move(3, 'Y')  # Drop in column 3
    game3.make_move(4, 'R')  # Drop in column 4
    print(f'\nConnect Four after some moves:')
    print(game3.display())
    print(f'Valid moves for R: {game3.get_valid_moves("R")}')
    
    # Tournament formats demo
    print(f'\n🏆 Tournament Format Options:')
    print('-' * 30)
    for fmt in TournamentFormat:
        print(f'• {fmt.value.replace("_", " ").title()}')
    
    # Configuration examples
    print(f'\n⚙️ Configuration Examples:')
    print('-' * 30)
    
    configs = [
        {
            'name': 'Classic Tournament',
            'game': GameConfig(board_size=3, win_length=3),
            'tournament': TournamentConfig(format=TournamentFormat.SINGLE_ELIMINATION, best_of=1)
        },
        {
            'name': 'Strategic Tournament',
            'game': GameConfig(board_size=5, win_length=4),
            'tournament': TournamentConfig(format=TournamentFormat.ROUND_ROBIN, best_of=3)
        },
        {
            'name': 'Swiss Championship',
            'game': GameConfig(board_size=4, win_length=3),
            'tournament': TournamentConfig(format=TournamentFormat.SWISS, best_of=1, max_rounds=6)
        }
    ]
    
    for config in configs:
        print(f"\n🎯 {config['name']}:")
        print(f"   Board: {config['game'].board_size}x{config['game'].board_size}")
        print(f"   Win condition: {config['game'].win_length} in a row")
        print(f"   Format: {config['tournament'].format.value.replace('_', ' ').title()}")
        print(f"   Best of: {config['tournament'].best_of}")


    # Demo Enhanced Logging System
    print(f'\n📝 Enhanced Logging System Demo:')
    print('-' * 40)
    
    def run_demo_tournament(title: str, models: list, config: TournamentConfig, 
                           game_config: GameConfig, game_class):
        """Run a single demo tournament with enhanced logging."""
        print(f"\n{'='*50}")
        print(f"🎮 {title}")
        print(f"{'='*50}")
        print(f"🤖 Models: {', '.join(models)}")
        print(f"🏆 Format: {config.format.value.replace('_', ' ').title()}")
        print(f"🎯 Best of: {config.best_of}")
        
        if hasattr(game_config, 'board_size'):
            print(f"🎲 Board: {game_config.board_size}x{game_config.board_size}")
            print(f"🎯 Win length: {game_config.win_length}")
        
        # Create session name
        session_name = f"demo_{create_session_name(config, game_config, models)}"
        
        # Initialize enhanced logger
        logger = EnhancedLogger(session_name, "demo_outputs")
        
        # Save configuration 
        cli_args = {
            "title": title,
            "demo": True,
            "timestamp": int(time.time())
        }
        logger.save_configuration(config, game_config, models, cli_args)
        
        # Create agents
        agents = [LLMAgent(model, temperature=0.3) for model in models]
        
        # Create game factory
        def game_factory():
            return game_class(game_config)
        
        # Initialize tournament
        tournament = TournamentEngine(config, game_factory, logger)
        
        print("🚀 Starting tournament...")
        start_time = time.time()
        
        try:
            # Run tournament
            results = tournament.run_tournament()
            
            duration = time.time() - start_time
            
            # Save results to enhanced logger
            enhanced_results = logger.save_tournament_results(results)
            
            # Display results
            print(f"\n🏆 Tournament Results:")
            print(f"   Champion: {results['champion']}")
            print(f"   Total matches: {results['total_matches']}")
            print(f"   Total games: {results['total_games']}") 
            print(f"   Duration: {duration:.1f}s")
            
            # Show top 3
            standings = results['standings']
            sorted_players = sorted(standings.items(), 
                                  key=lambda x: x[1]['points'], reverse=True)
            
            print(f"\n📊 Top 3 Players:")
            for i, (player, stats) in enumerate(sorted_players[:3], 1):
                points = stats['points']
                games_won = stats.get('games_won', 0)
                games_lost = stats.get('games_lost', 0)
                total_games = games_won + games_lost
                win_rate = games_won / total_games if total_games > 0 else 0
                
                print(f"   {i}. {player}: {points} points, {win_rate:.1%} win rate")
            
            # Create visualizations
            print(f"📊 Generating visualizations...")
            
            try:
                viz_config = logger.get_visualization_config()
                create_enhanced_visualizations(enhanced_results, viz_config["output_dir"])
                print(f"✅ Visualizations saved to: {viz_config['output_dir']}")
            except Exception as e:
                print(f"⚠️ Could not generate visualizations: {e}")
            
            # Finalize session
            session_summary = logger.finalize_session()
            
            print(f"\n📁 Enhanced Logging Results:")
            print(f"   Session: {logger.session_dir}")
            print(f"   Config: {logger.config_file}")
            print(f"   Results: {logger.summary_file}")
            print(f"   Plots: {logger.plots_dir}")
            print(f"   Duration: {session_summary['metadata']['total_duration']}")
            
            return results, session_summary
            
        except Exception as e:
            print(f"❌ Tournament failed: {e}")
            return None, None
    
    # Run demo tournaments with different configurations
    demo_models = ["demo_model_A", "demo_model_B", "demo_model_C"]
    
    # Demo 1: Classic Single Elimination
    result1, session1 = run_demo_tournament(
        "Classic Demo Tournament",
        demo_models[:3],
        TournamentConfig(format=TournamentFormat.SINGLE_ELIMINATION, best_of=1),
        GameConfig(board_size=3, win_length=3),
        GenericTicTacToe
    )
    
    # Demo 2: Round Robin with Best-of-3
    result2, session2 = run_demo_tournament(
        "Strategic Round Robin Demo",
        demo_models[:2],  # Smaller for demo
        TournamentConfig(format=TournamentFormat.ROUND_ROBIN, best_of=3),
        GameConfig(board_size=4, win_length=3),
        GenericTicTacToe
    )
    
    print(f'\n🎯 Key Enhanced Features Implemented:')
    print('-' * 40)
    print('✅ Generic game interface (IGame)')
    print('✅ Configurable board sizes and win conditions')
    print('✅ Multiple tournament formats (Single Elim, Round Robin, Swiss)')
    print('✅ Best-of-X match system')
    print('✅ Enhanced logging with JSON parameter storage')
    print('✅ Automatic file naming with timestamps')
    print('✅ Structured output directories')
    print('✅ Session management and metadata tracking')
    print('✅ Automatic visualization generation')
    print('✅ Complete tournament summaries')
    print('✅ Extensible architecture')
    print('✅ Connect-Four example game')
    print('✅ Flexible CLI with many options')
    
    print(f'\n🚀 Usage Examples:')
    print('-' * 30)
    print('# Basic enhanced tournament:')
    print('python main_enhanced.py --models phi4:latest qwq:latest')
    print('')
    print('# Round robin with best-of-3:')
    print('python main_enhanced.py --models phi4:latest qwq:latest llama3.3:latest --format round_robin --best-of 3')
    print('')
    print('# Large board strategic play:')
    print('python main_enhanced.py --models phi4:latest qwq:latest --board-size 5 --win-length 4')
    print('')
    print('# Swiss tournament:')
    print('python main_enhanced.py --models phi4:latest qwq:latest llama3.3:latest phi4-mini:latest --format swiss --max-rounds 3')
    
    print(f'\n📁 Session Management:')
    print('-' * 30)
    print('# List all tournament sessions:')
    print('python session_manager.py list')
    print('')
    print('# Analyze a specific session:')
    print('python session_manager.py analyze outputs/tournament_20231201_143022')
    print('')
    print('# Compare multiple sessions:')
    print('python session_manager.py compare outputs/session1 outputs/session2')
    print('')
    print('# Export session data:')
    print('python session_manager.py export outputs/session1 --output data.json')
    
    print(f'\n🎉 Enhanced tournament system with logging ready to use!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('Make sure all enhanced modules are available.')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc() 