#!/usr/bin/env python3
"""Session management utility for tournament analysis and comparison."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from enhanced_logger import list_tournament_sessions, load_session_summary
from enhanced_viz import create_enhanced_visualizations


def list_sessions(base_dir: str = "outputs") -> None:
    """List all tournament sessions with summary information.
    
    Args:
        base_dir: Base directory to search for sessions
    """
    sessions = list_tournament_sessions(base_dir)
    
    if not sessions:
        print(f"No tournament sessions found in {base_dir}")
        return
    
    print(f"📁 Tournament Sessions in {base_dir}:")
    print("=" * 80)
    print(f"{'#':<3} {'Session ID':<25} {'Champion':<15} {'Format':<12} {'Duration':<12} {'Start Time'}")
    print("-" * 80)
    
    for i, session in enumerate(sessions, 1):
        start_time = session['start_time'][:16].replace('T', ' ')  # Truncate for display
        duration = session['duration'].split('.')[0] if '.' in session['duration'] else session['duration']
        
        print(f"{i:<3} {session['session_id']:<25} {session['champion']:<15} "
              f"{session['format']:<12} {duration:<12} {start_time}")
    
    print(f"\nTotal sessions: {len(sessions)}")


def analyze_session(session_dir: str, regenerate_viz: bool = False) -> None:
    """Analyze a specific tournament session.
    
    Args:
        session_dir: Directory of the session to analyze
        regenerate_viz: Whether to regenerate visualizations
    """
    try:
        session_summary = load_session_summary(session_dir)
        
        print(f"📊 Session Analysis: {session_summary['metadata']['session_id']}")
        print("=" * 60)
        
        # Session metadata
        metadata = session_summary['metadata']
        print(f"🕒 Start time: {metadata['start_time']}")
        print(f"🕒 End time: {metadata.get('end_time', 'N/A')}")
        print(f"⏱️ Duration: {metadata.get('total_duration', 'N/A')}")
        print(f"📊 Status: {metadata.get('status', 'Unknown')}")
        
        # Tournament configuration
        config = session_summary['tournament_data']['config']
        print(f"\n🎮 Tournament Configuration:")
        print(f"   Format: {config['tournament']['format']}")
        print(f"   Best of: {config['tournament']['best_of']}")
        print(f"   Board: {config['game']['board_size']}x{config['game']['board_size']}")
        print(f"   Win length: {config['game']['win_length']}")
        print(f"   Models: {', '.join(config['models'])}")
        
        # Results
        results = session_summary['tournament_data']['results']
        if results:
            print(f"\n🏆 Tournament Results:")
            print(f"   Champion: {results.get('champion', 'N/A')}")
            print(f"   Total matches: {results.get('total_matches', 0)}")
            print(f"   Total games: {results.get('total_games', 0)}")
            
            # Standings
            standings = results.get('standings', {})
            if standings:
                print(f"\n📈 Final Standings:")
                sorted_standings = sorted(
                    standings.items(),
                    key=lambda x: (x[1].get('points', 0), x[1].get('games_won', 0)),
                    reverse=True
                )
                
                for rank, (player, stats) in enumerate(sorted_standings[:5], 1):  # Top 5
                    games_total = stats.get('games_won', 0) + stats.get('games_lost', 0)
                    win_rate = stats.get('games_won', 0) / games_total if games_total > 0 else 0
                    print(f"   {rank}. {player:<15} - Points: {stats.get('points', 0):3d}, "
                          f"Win Rate: {win_rate:.1%}")
        
        # File structure
        file_structure = session_summary['file_structure']
        print(f"\n📁 Files Created: {file_structure['total_files']}")
        print(f"   Session directory: {file_structure['session_directory']}")
        
        # Regenerate visualizations if requested
        if regenerate_viz:
            print(f"\n📊 Regenerating visualizations...")
            try:
                plots_dir = Path(session_dir) / "plots"
                create_enhanced_visualizations(results, str(plots_dir))
                print(f"✅ Visualizations regenerated in: {plots_dir}")
            except Exception as e:
                print(f"❌ Error regenerating visualizations: {e}")
        
    except FileNotFoundError:
        print(f"❌ Session not found: {session_dir}")
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")


def compare_sessions(session_dirs: List[str]) -> None:
    """Compare multiple tournament sessions.
    
    Args:
        session_dirs: List of session directories to compare
    """
    if len(session_dirs) < 2:
        print("❌ Need at least 2 sessions to compare")
        return
    
    sessions_data = []
    
    # Load all sessions
    for session_dir in session_dirs:
        try:
            summary = load_session_summary(session_dir)
            sessions_data.append(summary)
        except Exception as e:
            print(f"⚠️ Could not load session {session_dir}: {e}")
    
    if len(sessions_data) < 2:
        print("❌ Could not load enough sessions for comparison")
        return
    
    print(f"📊 Comparing {len(sessions_data)} Sessions")
    print("=" * 80)
    
    # Header
    print(f"{'Session':<20} {'Champion':<15} {'Format':<12} {'Games':<6} {'Duration':<12}")
    print("-" * 80)
    
    # Session comparison
    for session in sessions_data:
        session_id = session['metadata']['session_id'][-15:]  # Truncate
        champion = session['tournament_data']['results'].get('champion', 'N/A')
        fmt = session['tournament_data']['config']['tournament']['format'][:10]
        games = session['tournament_data']['results'].get('total_games', 0)
        duration = session['metadata'].get('total_duration', 'N/A')
        if '.' in duration:
            duration = duration.split('.')[0]
        
        print(f"{session_id:<20} {champion:<15} {fmt:<12} {games:<6} {duration:<12}")
    
    # Model performance comparison
    print(f"\n🤖 Model Performance Across Sessions:")
    print("-" * 50)
    
    model_stats = {}
    
    for session in sessions_data:
        standings = session['tournament_data']['results'].get('standings', {})
        for model, stats in standings.items():
            if model not in model_stats:
                model_stats[model] = {
                    'sessions': 0,
                    'total_points': 0,
                    'total_games': 0,
                    'total_wins': 0,
                    'championships': 0
                }
            
            model_stats[model]['sessions'] += 1
            model_stats[model]['total_points'] += stats.get('points', 0)
            model_stats[model]['total_games'] += stats.get('games_won', 0) + stats.get('games_lost', 0)
            model_stats[model]['total_wins'] += stats.get('games_won', 0)
            
            # Check if champion
            champion = session['tournament_data']['results'].get('champion')
            if champion == model:
                model_stats[model]['championships'] += 1
    
    # Display model comparison
    print(f"{'Model':<15} {'Sessions':<8} {'Championships':<12} {'Avg Win Rate':<12} {'Total Points'}")
    print("-" * 65)
    
    for model, stats in sorted(model_stats.items(), key=lambda x: x[1]['championships'], reverse=True):
        avg_win_rate = stats['total_wins'] / stats['total_games'] if stats['total_games'] > 0 else 0
        print(f"{model:<15} {stats['sessions']:<8} {stats['championships']:<12} "
              f"{avg_win_rate:<12.1%} {stats['total_points']}")


def export_session_data(session_dir: str, output_file: str, format_type: str = "json") -> None:
    """Export session data to different formats.
    
    Args:
        session_dir: Session directory to export
        output_file: Output file path
        format_type: Export format (json, csv)
    """
    try:
        session_summary = load_session_summary(session_dir)
        
        if format_type.lower() == "json":
            with open(output_file, 'w') as f:
                json.dump(session_summary, f, indent=2)
            print(f"✅ Session data exported to: {output_file}")
            
        elif format_type.lower() == "csv":
            import csv
            
            # Export standings as CSV
            standings = session_summary['tournament_data']['results'].get('standings', {})
            
            with open(output_file, 'w', newline='') as f:
                if standings:
                    fieldnames = ['model'] + list(next(iter(standings.values())).keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for model, stats in standings.items():
                        row = {'model': model, **stats}
                        writer.writerow(row)
                
            print(f"✅ Standings exported to CSV: {output_file}")
            
        else:
            print(f"❌ Unsupported format: {format_type}")
            
    except Exception as e:
        print(f"❌ Error exporting session data: {e}")


def cleanup_old_sessions(base_dir: str, days_old: int = 30, dry_run: bool = True) -> None:
    """Clean up old tournament sessions.
    
    Args:
        base_dir: Base directory to search
        days_old: Sessions older than this many days
        dry_run: If True, only show what would be deleted
    """
    from datetime import datetime, timedelta
    import shutil
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    sessions = list_tournament_sessions(base_dir)
    
    old_sessions = []
    for session in sessions:
        session_date = datetime.fromisoformat(session['start_time'])
        if session_date < cutoff_date:
            old_sessions.append(session)
    
    if not old_sessions:
        print(f"No sessions older than {days_old} days found")
        return
    
    print(f"Found {len(old_sessions)} sessions older than {days_old} days:")
    
    for session in old_sessions:
        print(f"  - {session['session_id']} ({session['start_time'][:10]})")
    
    if dry_run:
        print(f"\n💡 This was a dry run. Use --no-dry-run to actually delete these sessions.")
    else:
        confirm = input(f"\n⚠️ Delete {len(old_sessions)} sessions? (y/N): ")
        if confirm.lower() == 'y':
            for session in old_sessions:
                try:
                    shutil.rmtree(session['directory'])
                    print(f"✅ Deleted: {session['session_id']}")
                except Exception as e:
                    print(f"❌ Error deleting {session['session_id']}: {e}")
        else:
            print("Cleanup cancelled")


def main():
    """Main CLI for session management."""
    parser = argparse.ArgumentParser(
        description="Tournament Session Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all sessions
  python session_manager.py list
  
  # Analyze a specific session
  python session_manager.py analyze outputs/tournament_20231201_143022
  
  # Compare multiple sessions
  python session_manager.py compare outputs/session1 outputs/session2
  
  # Export session data
  python session_manager.py export outputs/session1 --output data.json
  
  # Clean up old sessions
  python session_manager.py cleanup --days 30
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tournament sessions')
    list_parser.add_argument('--base-dir', default='outputs', help='Base directory to search')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a specific session')
    analyze_parser.add_argument('session_dir', help='Session directory to analyze')
    analyze_parser.add_argument('--regenerate-viz', action='store_true', 
                               help='Regenerate visualizations')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple sessions')
    compare_parser.add_argument('session_dirs', nargs='+', help='Session directories to compare')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export session data')
    export_parser.add_argument('session_dir', help='Session directory to export')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Export format')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old sessions')
    cleanup_parser.add_argument('--base-dir', default='outputs', help='Base directory')
    cleanup_parser.add_argument('--days', type=int, default=30, 
                               help='Delete sessions older than this many days')
    cleanup_parser.add_argument('--no-dry-run', action='store_true',
                               help='Actually delete (default is dry run)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_sessions(args.base_dir)
        
        elif args.command == 'analyze':
            analyze_session(args.session_dir, args.regenerate_viz)
        
        elif args.command == 'compare':
            compare_sessions(args.session_dirs)
        
        elif args.command == 'export':
            export_session_data(args.session_dir, args.output, args.format)
        
        elif args.command == 'cleanup':
            cleanup_old_sessions(args.base_dir, args.days, not args.no_dry_run)
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 