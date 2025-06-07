"""Enhanced logging system with better file naming and parameter management."""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from pathlib import Path

from game_interface import GameConfig


class EnhancedLogger:
    """Enhanced logging system with comprehensive parameter tracking and better file organization."""
    
    def __init__(self, base_name: str = "tournament", output_dir: str = "outputs"):
        """Initialize the enhanced logger.
        
        Args:
            base_name: Base name for log files
            output_dir: Base directory for all outputs
        """
        self.base_name = base_name
        self.output_dir = Path(output_dir)
        
        # Create timestamp for this session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory structure
        self.session_dir = self.output_dir / f"{base_name}_{self.timestamp}"
        self.logs_dir = self.session_dir / "logs"
        self.plots_dir = self.session_dir / "plots"
        self.data_dir = self.session_dir / "data"
        
        # Create directories
        for dir_path in [self.session_dir, self.logs_dir, self.plots_dir, self.data_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize files
        self.config_file = self.data_dir / "tournament_config.json"
        self.metadata_file = self.data_dir / "session_metadata.json"
        self.moves_log = self.logs_dir / "moves.jsonl"
        self.results_log = self.logs_dir / "results.jsonl"
        self.summary_file = self.data_dir / "tournament_summary.json"
        
        # Session metadata
        self.session_metadata = {
            "session_id": f"{base_name}_{self.timestamp}",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_duration": None,
            "files_created": [],
            "status": "running"
        }
        
        # Tournament data
        self.tournament_data = {
            "config": {},
            "participants": [],
            "matches": [],
            "standings": {},
            "results": {}
        }
        
        print(f"📁 Session directory: {self.session_dir}")
        print(f"📝 Logs: {self.logs_dir}")
        print(f"📊 Plots: {self.plots_dir}")
        print(f"💾 Data: {self.data_dir}")
    
    def save_configuration(self, tournament_config: Any, 
                          game_config: GameConfig, 
                          models: List[str],
                          cli_args: Dict[str, Any] = None) -> None:
        """Save complete tournament configuration.
        
        Args:
            tournament_config: Tournament configuration object
            game_config: Game configuration object
            models: List of model names
            cli_args: CLI arguments used
        """
        config_data = {
            "tournament": {
                "format": tournament_config.format.value,
                "best_of": tournament_config.best_of,
                "shuffle_players": tournament_config.shuffle_players,
                "seed": tournament_config.seed,
                "max_rounds": tournament_config.max_rounds
            },
            "game": game_config.to_dict(),
            "models": models,
            "cli_args": cli_args or {},
            "timestamp": self.timestamp,
            "session_id": self.session_metadata["session_id"]
        }
        
        # Save configuration
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Update tournament data
        self.tournament_data["config"] = config_data
        
        # Update session metadata
        self.session_metadata["files_created"].append(str(self.config_file))
        self._save_session_metadata()
        
        print(f"💾 Configuration saved to: {self.config_file}")
    
    def log_tournament_start(self, models: List[str], total_rounds: int) -> None:
        """Log tournament start information.
        
        Args:
            models: List of participating models
            total_rounds: Expected number of rounds
        """
        start_data = {
            "type": "tournament_start",
            "timestamp": datetime.now().isoformat(),
            "models": models,
            "total_rounds": total_rounds
        }
        
        # Log to results file
        self._append_to_log(self.results_log, start_data)
        
        # Update tournament data
        self.tournament_data["participants"] = models
        
        print(f"🏁 Tournament started - logged to: {self.results_log}")
    
    def log_round_start(self, round_num: int, matches: List[Dict[str, Any]]) -> None:
        """Log round start information.
        
        Args:
            round_num: Round number
            matches: List of matches in this round
        """
        round_data = {
            "type": "round_start",
            "timestamp": datetime.now().isoformat(),
            "round_number": round_num,
            "matches": matches
        }
        
        self._append_to_log(self.results_log, round_data)
    
    def log_move(self, game_id: str, player: str, move: Any, board_state: Any) -> None:
        """Log individual game moves.
        
        Args:
            game_id: Unique game identifier
            player: Player making the move
            move: Move data
            board_state: Current board state
        """
        move_data = {
            "type": "move",
            "timestamp": datetime.now().isoformat(),
            "game_id": game_id,
            "player": player,
            "move": move,
            "board_state": board_state
        }
        
        self._append_to_log(self.moves_log, move_data)
    
    def log_result(self, game_id: str, result: str, final_state: Any, winner: Optional[str]) -> None:
        """Log game result.
        
        Args:
            game_id: Unique game identifier
            result: Game result (win/draw)
            final_state: Final board state
            winner: Winner identifier (if any)
        """
        result_data = {
            "type": "game_result",
            "timestamp": datetime.now().isoformat(),
            "game_id": game_id,
            "result": result,
            "winner": winner,
            "final_state": final_state
        }
        
        self._append_to_log(self.results_log, result_data)
    
    def log_match_result(self, match_data: Dict[str, Any]) -> None:
        """Log complete match result.
        
        Args:
            match_data: Complete match information
        """
        enhanced_match_data = {
            "type": "match_result",
            "timestamp": datetime.now().isoformat(),
            **match_data
        }
        
        self._append_to_log(self.results_log, enhanced_match_data)
        
        # Add to tournament data
        self.tournament_data["matches"].append(enhanced_match_data)
    
    def save_tournament_results(self, results: Dict[str, Any]) -> None:
        """Save complete tournament results and generate summary.
        
        Args:
            results: Tournament results dictionary
        """
        # Add timestamp and session info
        enhanced_results = {
            **results,
            "session_id": self.session_metadata["session_id"],
            "timestamp": self.timestamp,
            "completion_time": datetime.now().isoformat(),
            "session_directory": str(self.session_dir),
            "files": {
                "config": str(self.config_file),
                "moves_log": str(self.moves_log),
                "results_log": str(self.results_log),
                "plots_directory": str(self.plots_dir)
            }
        }
        
        # Save complete results
        with open(self.summary_file, 'w') as f:
            json.dump(enhanced_results, f, indent=2)
        
        # Update tournament data
        self.tournament_data["results"] = enhanced_results
        self.tournament_data["standings"] = results.get("standings", {})
        
        # Log final tournament result
        final_log_entry = {
            "type": "tournament_complete",
            "timestamp": datetime.now().isoformat(),
            "champion": results["champion"],
            "total_matches": results["total_matches"],
            "total_games": results["total_games"],
            "summary_file": str(self.summary_file)
        }
        
        self._append_to_log(self.results_log, final_log_entry)
        
        print(f"🏆 Tournament results saved to: {self.summary_file}")
        return enhanced_results
    
    def finalize_session(self) -> Dict[str, Any]:
        """Finalize the logging session and return session summary.
        
        Returns:
            Complete session summary
        """
        end_time = datetime.now()
        self.session_metadata["end_time"] = end_time.isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.session_metadata["start_time"])
        duration = end_time - start_time
        self.session_metadata["total_duration"] = str(duration)
        self.session_metadata["status"] = "completed"
        
        # Add file list
        all_files = []
        for root, dirs, files in os.walk(self.session_dir):
            for file in files:
                all_files.append(os.path.relpath(os.path.join(root, file), self.session_dir))
        
        self.session_metadata["files_created"] = all_files
        
        # Save final metadata
        self._save_session_metadata()
        
        # Create session summary
        session_summary = {
            "metadata": self.session_metadata,
            "tournament_data": self.tournament_data,
            "file_structure": self._generate_file_structure()
        }
        
        # Save session summary
        session_summary_file = self.session_dir / "session_summary.json"
        with open(session_summary_file, 'w') as f:
            json.dump(session_summary, f, indent=2)
        
        print(f"✅ Session finalized: {self.session_dir}")
        print(f"📋 Session summary: {session_summary_file}")
        
        return session_summary
    
    def get_visualization_config(self) -> Dict[str, Any]:
        """Get configuration for visualization generation.
        
        Returns:
            Configuration for visualization system
        """
        return {
            "results_data": self.tournament_data["results"],
            "output_dir": str(self.plots_dir),
            "session_id": self.session_metadata["session_id"],
            "moves_log": str(self.moves_log),
            "results_log": str(self.results_log),
            "tournament_config": self.tournament_data["config"]
        }
    
    def _append_to_log(self, log_file: Path, data: Dict[str, Any]) -> None:
        """Append data to a log file.
        
        Args:
            log_file: Path to log file
            data: Data to append
        """
        with open(log_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _save_session_metadata(self) -> None:
        """Save session metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.session_metadata, f, indent=2)
    
    def _generate_file_structure(self) -> Dict[str, Any]:
        """Generate file structure summary.
        
        Returns:
            File structure information
        """
        structure = {
            "session_directory": str(self.session_dir),
            "subdirectories": {
                "logs": str(self.logs_dir),
                "plots": str(self.plots_dir),
                "data": str(self.data_dir)
            },
            "key_files": {
                "configuration": str(self.config_file),
                "session_metadata": str(self.metadata_file),
                "moves_log": str(self.moves_log),
                "results_log": str(self.results_log),
                "tournament_summary": str(self.summary_file)
            },
            "total_files": len(self.session_metadata.get("files_created", []))
        }
        
        return structure


def create_session_name(tournament_config: Any, 
                       game_config: GameConfig, 
                       models: List[str]) -> str:
    """Create a descriptive session name based on configuration.
    
    Args:
        tournament_config: Tournament configuration
        game_config: Game configuration
        models: List of models
        
    Returns:
        Descriptive session name
    """
    # Extract key parameters
    format_short = tournament_config.format.value.replace("_", "")[:4]  # e.g., "sing", "roun", "swis"
    board_info = f"{game_config.board_size}x{game_config.board_size}"
    win_info = f"w{game_config.win_length}"
    best_of = f"bo{tournament_config.best_of}" if tournament_config.best_of > 1 else ""
    models_count = f"{len(models)}p"  # number of players
    
    # Create name parts
    parts = [format_short, board_info, win_info, best_of, models_count]
    parts = [p for p in parts if p]  # Remove empty parts
    
    return "_".join(parts)


def load_session_summary(session_dir: str) -> Dict[str, Any]:
    """Load session summary from directory.
    
    Args:
        session_dir: Path to session directory
        
    Returns:
        Session summary data
    """
    summary_file = Path(session_dir) / "session_summary.json"
    
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Session summary not found: {summary_file}")


def list_tournament_sessions(base_dir: str = "outputs") -> List[Dict[str, Any]]:
    """List all tournament sessions in the base directory.
    
    Args:
        base_dir: Base directory to search
        
    Returns:
        List of session information
    """
    sessions = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return sessions
    
    for session_dir in base_path.iterdir():
        if session_dir.is_dir() and session_dir.name.startswith("tournament_"):
            try:
                summary = load_session_summary(str(session_dir))
                sessions.append({
                    "session_id": summary["metadata"]["session_id"],
                    "start_time": summary["metadata"]["start_time"],
                    "duration": summary["metadata"].get("total_duration", "Unknown"),
                    "champion": summary["tournament_data"]["results"].get("champion", "Unknown"),
                    "format": summary["tournament_data"]["config"]["tournament"]["format"],
                    "directory": str(session_dir)
                })
            except Exception as e:
                print(f"⚠️ Error loading session {session_dir}: {e}")
    
    # Sort by start time (newest first)
    sessions.sort(key=lambda x: x["start_time"], reverse=True)
    
    return sessions 