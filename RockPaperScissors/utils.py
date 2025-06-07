"""JSONL logging and scoring utilities for Rock Paper Scissors Royale."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple
from enum import Enum


class Move(Enum):
    """Valid moves in Rock Paper Scissors."""
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class GameResult(Enum):
    """Game result outcomes."""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


def ensure_data_directories() -> None:
    """Ensure the data and logs directories exist."""
    os.makedirs("data/logs", exist_ok=True)


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def determine_winner(move1: Move, move2: Move) -> Tuple[GameResult, GameResult]:
    """Determine the winner of a Rock Paper Scissors match.
    
    Args:
        move1: First player's move
        move2: Second player's move
        
    Returns:
        Tuple of (result_for_player1, result_for_player2)
    """
    if move1 == move2:
        return GameResult.DRAW, GameResult.DRAW
    
    winning_combinations = {
        (Move.ROCK, Move.SCISSORS),
        (Move.PAPER, Move.ROCK),
        (Move.SCISSORS, Move.PAPER)
    }
    
    if (move1, move2) in winning_combinations:
        return GameResult.WIN, GameResult.LOSS
    else:
        return GameResult.LOSS, GameResult.WIN


def parse_move(move_str: str) -> Move:
    """Parse a move string into a Move enum.
    
    Args:
        move_str: String representation of the move
        
    Returns:
        Move enum value
        
    Raises:
        ValueError: If the move string is invalid
    """
    move_str = move_str.lower().strip()
    
    # Handle common variations
    move_mappings = {
        'rock': Move.ROCK,
        'r': Move.ROCK,
        'stone': Move.ROCK,
        'paper': Move.PAPER,
        'p': Move.PAPER,
        'scissors': Move.SCISSORS,
        's': Move.SCISSORS,
        'scissor': Move.SCISSORS,
    }
    
    if move_str in move_mappings:
        return move_mappings[move_str]
    
    raise ValueError(f"Invalid move: {move_str}")


class RPSLogger:
    """Comprehensive logger for Rock Paper Scissors tournament matches and detailed analytics."""
    
    def __init__(self, log_file: str = "data/logs/tournament.jsonl") -> None:
        """Initialize the logger.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.log_file = log_file
        self.tournament_start_time = None
        self.match_counter = 0
        ensure_data_directories()
        
        # Clear the log file at the start of a new tournament
        with open(self.log_file, 'w') as f:
            pass  # Just clear the file
    
    def log_tournament_start(self, models: List[str], tournament_type: str, rounds: int, 
                           temperature: float = 0.7, seed: int = 42, 
                           model_metadata: dict = None) -> None:
        """Log the start of a tournament with comprehensive metadata.
        
        Args:
            models: List of participating models/agents
            tournament_type: Type of tournament (e.g., "round_robin", "single_elimination")
            rounds: Number of rounds or matches
            temperature: LLM temperature setting
            seed: Random seed used
            model_metadata: Additional metadata about models (versions, sizes, etc.)
        """
        self.tournament_start_time = now_iso()
        
        # Extract actual model names from agent names if they contain parentheses
        actual_models = []
        for model_name in models:
            if "(" in model_name and ")" in model_name:
                # Extract base model from format like "llama2(Agent1)" 
                base_model = model_name.split("(")[0]
                actual_models.append(base_model)
            else:
                actual_models.append(model_name)
        
        record = {
            "timestamp": self.tournament_start_time,
            "type": "tournament_start",
            "agent_names": models,  # Full agent names for identification
            "models": actual_models,  # Base model names
            "unique_models": list(set(actual_models)),  # Unique model types
            "num_participants": len(models),
            "num_unique_models": len(set(actual_models)),
            "tournament_type": tournament_type,
            "rounds": rounds,
            "temperature": temperature,
            "seed": seed,
            "model_metadata": model_metadata or {},
            "expected_total_matches": self._calculate_expected_matches(len(models), tournament_type)
        }
        self._write_record(record)
    
    def log_match(self, match_id: str, player1: str, player2: str, 
                  move1: Move, move2: Move, result1: GameResult, result2: GameResult) -> None:
        """Log a single match result.
        
        Args:
            match_id: Unique identifier for the match
            player1: First player model name
            player2: Second player model name
            move1: First player's move
            move2: Second player's move
            result1: Result for first player
            result2: Result for second player
        """
        record = {
            "timestamp": now_iso(),
            "type": "match",
            "match_id": match_id,
            "player1": player1,
            "player2": player2,
            "move1": move1.value,
            "move2": move2.value,
            "result1": result1.value,
            "result2": result2.value
        }
        self._write_record(record)
    
    def log_round_summary(self, round_num: int, standings: Dict[str, Any]) -> None:
        """Log the summary of a tournament round.
        
        Args:
            round_num: Round number
            standings: Current tournament standings
        """
        record = {
            "timestamp": now_iso(),
            "type": "round_summary",
            "round": round_num,
            "standings": standings
        }
        self._write_record(record)
    
    def log_match_start(self, match_id: str, player1: str, player2: str, rounds_in_match: int,
                       player1_model: str = None, player2_model: str = None, 
                       player1_temp: float = None, player2_temp: float = None) -> None:
        """Log the start of a multi-round match.
        
        Args:
            match_id: Unique match identifier
            player1: First player name
            player2: Second player name
            rounds_in_match: Number of rounds in this match
            player1_model: Player 1's LLM model
            player2_model: Player 2's LLM model
            player1_temp: Player 1's temperature setting
            player2_temp: Player 2's temperature setting
        """
        self.match_counter += 1
        
        # Extract model names from player names if not provided
        if player1_model is None:
            player1_model = player1.split("(")[0] if "(" in player1 else player1
        if player2_model is None:
            player2_model = player2.split("(")[0] if "(" in player2 else player2
        
        record = {
            "timestamp": now_iso(),
            "type": "match_start",
            "match_id": match_id,
            "player1": player1,
            "player2": player2,
            "player1_model": player1_model,
            "player2_model": player2_model,
            "player1_temperature": player1_temp,
            "player2_temperature": player2_temp,
            "model_matchup": f"{player1_model}_vs_{player2_model}",
            "is_same_model": player1_model == player2_model,
            "rounds_in_match": rounds_in_match,
            "match_number": self.match_counter
        }
        self._write_record(record)
    
    def log_match_end(self, match_id: str, player1: str, player2: str, winner: str,
                     final_score: str, player1_score: int, player2_score: int,
                     player1_history: List[Move], player2_history: List[Move],
                     match_duration_seconds: float = None, player1_model: str = None, 
                     player2_model: str = None) -> None:
        """Log the end of a match with comprehensive statistics.
        
        Args:
            match_id: Unique match identifier
            player1: First player name
            player2: Second player name
            winner: Match winner
            final_score: Score string (e.g., "7-3")
            player1_score: Player1's round wins
            player2_score: Player2's round wins
            player1_history: Player1's complete move history
            player2_history: Player2's complete move history
            match_duration_seconds: Optional match duration
            player1_model: Player 1's LLM model
            player2_model: Player 2's LLM model
        """
        # Calculate detailed match statistics
        total_rounds = len(player1_history)
        draws = total_rounds - player1_score - player2_score
        
        # Extract model names if not provided
        if player1_model is None:
            player1_model = player1.split("(")[0] if "(" in player1 else player1
        if player2_model is None:
            player2_model = player2.split("(")[0] if "(" in player2 else player2
        
        # Move frequency analysis
        p1_moves = {"rock": 0, "paper": 0, "scissors": 0}
        p2_moves = {"rock": 0, "paper": 0, "scissors": 0}
        
        for move in player1_history:
            p1_moves[move.value] += 1
        for move in player2_history:
            p2_moves[move.value] += 1
        
        # Pattern analysis
        move_sequences = []
        for i in range(total_rounds):
            move_sequences.append({
                "round": i + 1,
                "player1_move": player1_history[i].value,
                "player2_move": player2_history[i].value
            })
        
        # Streak analysis
        p1_streaks = self._calculate_streaks(player1_history, player2_history)
        p2_streaks = self._calculate_streaks(player2_history, player1_history)
        
        record = {
            "timestamp": now_iso(),
            "type": "match_end",
            "match_id": match_id,
            "player1": player1,
            "player2": player2,
            "player1_model": player1_model,
            "player2_model": player2_model,
            "model_matchup": f"{player1_model}_vs_{player2_model}",
            "is_same_model": player1_model == player2_model,
            "winner": winner,
            "winner_model": winner.split("(")[0] if "(" in winner and winner != "Draw" else winner,
            "final_score": final_score,
            "player1_score": player1_score,
            "player2_score": player2_score,
            "draws": draws,
            "total_rounds": total_rounds,
            "player1_win_rate": player1_score / total_rounds if total_rounds > 0 else 0,
            "player2_win_rate": player2_score / total_rounds if total_rounds > 0 else 0,
            "player1_move_frequency": p1_moves,
            "player2_move_frequency": p2_moves,
            "move_sequences": move_sequences,
            "player1_streaks": p1_streaks,
            "player2_streaks": p2_streaks,
            "match_duration_seconds": match_duration_seconds,
            "model_performance": {
                player1_model: {
                    "score": player1_score,
                    "win_rate": player1_score / total_rounds if total_rounds > 0 else 0,
                    "move_distribution": {move: count / total_rounds if total_rounds > 0 else 0 for move, count in p1_moves.items()}
                },
                player2_model: {
                    "score": player2_score,
                    "win_rate": player2_score / total_rounds if total_rounds > 0 else 0,
                    "move_distribution": {move: count / total_rounds if total_rounds > 0 else 0 for move, count in p2_moves.items()}
                }
            }
        }
        self._write_record(record)
    
    def log_agent_analysis(self, agent_name: str, analysis_data: Dict[str, Any]) -> None:
        """Log detailed analysis of an individual agent's performance.
        
        Args:
            agent_name: Name of the agent
            analysis_data: Dictionary containing analysis metrics
        """
        record = {
            "timestamp": now_iso(),
            "type": "agent_analysis",
            "agent_name": agent_name,
            **analysis_data
        }
        self._write_record(record)
    
    def log_head_to_head(self, player1: str, player2: str, h2h_stats: Dict[str, Any]) -> None:
        """Log head-to-head statistics between two players.
        
        Args:
            player1: First player name
            player2: Second player name
            h2h_stats: Head-to-head statistics dictionary
        """
        record = {
            "timestamp": now_iso(),
            "type": "head_to_head",
            "player1": player1,
            "player2": player2,
            **h2h_stats
        }
        self._write_record(record)

    def log_tournament_end(self, final_standings: Dict[str, Any], champion: str,
                          tournament_duration_seconds: float = None) -> None:
        """Log the end of a tournament with comprehensive final results.
        
        Args:
            final_standings: Final tournament standings
            champion: Tournament champion
            tournament_duration_seconds: Optional tournament duration
        """
        end_time = now_iso()
        
        # Calculate tournament-wide statistics
        total_participants = len(final_standings)
        total_matches_played = self.match_counter
        
        record = {
            "timestamp": end_time,
            "type": "tournament_end",
            "tournament_start_time": self.tournament_start_time,
            "tournament_end_time": end_time,
            "tournament_duration_seconds": tournament_duration_seconds,
            "final_standings": final_standings,
            "champion": champion,
            "total_participants": total_participants,
            "total_matches_played": total_matches_played,
            "matches_per_participant": total_matches_played / total_participants if total_participants > 0 else 0
        }
        self._write_record(record)
    
    def _calculate_expected_matches(self, num_participants: int, tournament_type: str) -> int:
        """Calculate expected number of matches for a tournament type.
        
        Args:
            num_participants: Number of participating agents
            tournament_type: Type of tournament
            
        Returns:
            Expected number of matches
        """
        if tournament_type == "round_robin":
            # n * (n-1) / 2 pairings
            return num_participants * (num_participants - 1) // 2
        elif tournament_type == "single_elimination":
            # Need to pad to power of 2, then n-1 matches
            import math
            next_power = 2 ** math.ceil(math.log2(num_participants)) if num_participants > 1 else 2
            return next_power - 1
        else:  # league or other
            return num_participants  # Rough estimate
    
    def _calculate_streaks(self, player_moves: List[Move], opponent_moves: List[Move]) -> Dict[str, Any]:
        """Calculate winning/losing streaks for a player.
        
        Args:
            player_moves: Player's move history
            opponent_moves: Opponent's move history
            
        Returns:
            Dictionary with streak information
        """
        if not player_moves or not opponent_moves:
            return {"longest_win_streak": 0, "longest_loss_streak": 0, "current_streak": 0}
        
        # Calculate wins/losses for each round
        results = []
        for i in range(len(player_moves)):
            player_move = player_moves[i]
            opponent_move = opponent_moves[i]
            
            if player_move == opponent_move:
                results.append("draw")
            elif ((player_move == Move.ROCK and opponent_move == Move.SCISSORS) or
                  (player_move == Move.PAPER and opponent_move == Move.ROCK) or
                  (player_move == Move.SCISSORS and opponent_move == Move.PAPER)):
                results.append("win")
            else:
                results.append("loss")
        
        # Calculate streaks
        longest_win_streak = 0
        longest_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for result in results:
            if result == "win":
                current_win_streak += 1
                current_loss_streak = 0
                longest_win_streak = max(longest_win_streak, current_win_streak)
            elif result == "loss":
                current_loss_streak += 1
                current_win_streak = 0
                longest_loss_streak = max(longest_loss_streak, current_loss_streak)
            else:  # draw
                current_win_streak = 0
                current_loss_streak = 0
        
        # Determine current streak
        if results:
            if results[-1] == "win":
                current_streak = current_win_streak
            elif results[-1] == "loss":
                current_streak = -current_loss_streak
            else:
                current_streak = 0
        else:
            current_streak = 0
        
        return {
            "longest_win_streak": longest_win_streak,
            "longest_loss_streak": longest_loss_streak,
            "current_streak": current_streak,
            "streak_type": "win" if current_streak > 0 else ("loss" if current_streak < 0 else "none")
        }

    def _write_record(self, record: Dict[str, Any]) -> None:
        """Write a record to the JSONL file.
        
        Args:
            record: Dictionary to write as JSON
        """
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")


class TournamentScorer:
    """Manages scoring and standings for tournaments."""
    
    def __init__(self, models: List[str]) -> None:
        """Initialize the scorer.
        
        Args:
            models: List of participating models
        """
        self.models = models
        self.reset_scores()
    
    def reset_scores(self) -> None:
        """Reset all scores to zero."""
        self.wins = {model: 0 for model in self.models}
        self.losses = {model: 0 for model in self.models}
        self.draws = {model: 0 for model in self.models}
        self.matches_played = {model: 0 for model in self.models}
    
    def record_match(self, player1: str, player2: str, result1: GameResult, result2: GameResult) -> None:
        """Record the result of a match.
        
        Args:
            player1: First player model name
            player2: Second player model name
            result1: Result for first player
            result2: Result for second player
        """
        # Update match counts
        self.matches_played[player1] += 1
        self.matches_played[player2] += 1
        
        # Update results
        if result1 == GameResult.WIN:
            self.wins[player1] += 1
        elif result1 == GameResult.LOSS:
            self.losses[player1] += 1
        else:
            self.draws[player1] += 1
        
        if result2 == GameResult.WIN:
            self.wins[player2] += 1
        elif result2 == GameResult.LOSS:
            self.losses[player2] += 1
        else:
            self.draws[player2] += 1
    
    def get_standings(self) -> Dict[str, Any]:
        """Get current tournament standings.
        
        Returns:
            Dictionary with standings information
        """
        standings = {}
        
        for model in self.models:
            matches = self.matches_played[model]
            wins = self.wins[model]
            losses = self.losses[model]
            draws = self.draws[model]
            
            # Calculate win rate
            win_rate = wins / matches if matches > 0 else 0.0
            
            # Calculate points (3 for win, 1 for draw, 0 for loss)
            points = wins * 3 + draws * 1
            
            standings[model] = {
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "matches_played": matches,
                "win_rate": win_rate,
                "points": points
            }
        
        return standings
    
    def get_leaderboard(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Get leaderboard sorted by points then win rate.
        
        Returns:
            List of (model, stats) tuples sorted by performance
        """
        standings = self.get_standings()
        
        # Sort by points (descending), then by win rate (descending), then by wins (descending)
        leaderboard = sorted(
            standings.items(),
            key=lambda x: (x[1]["points"], x[1]["win_rate"], x[1]["wins"]),
            reverse=True
        )
        
        return leaderboard
    
    def get_champion(self) -> str:
        """Get the current tournament champion.
        
        Returns:
            Model name of the current leader
        """
        leaderboard = self.get_leaderboard()
        return leaderboard[0][0] if leaderboard else ""


def load_tournament_data(log_file: str = "data/logs/tournament.jsonl") -> List[Dict[str, Any]]:
    """Load tournament data from JSONL log file.
    
    Args:
        log_file: Path to the JSONL log file
        
    Returns:
        List of tournament records
    """
    records = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass  # Return empty list if file doesn't exist
    
    return records


class TournamentAnalyzer:
    """Advanced analytics for tournament data."""
    
    def __init__(self, tournament_data: List[Dict[str, Any]]):
        """Initialize analyzer with tournament data.
        
        Args:
            tournament_data: List of tournament records from JSONL
        """
        self.data = tournament_data
        self.matches = [r for r in tournament_data if r.get("type") == "match"]
        self.match_ends = [r for r in tournament_data if r.get("type") == "match_end"]
        self.agents = self._extract_agents()
    
    def _extract_agents(self) -> List[str]:
        """Extract unique agent names from tournament data."""
        agents = set()
        for record in self.data:
            if record.get("type") == "tournament_start":
                agents.update(record.get("models", []))
        return sorted(list(agents))
    
    def get_agent_statistics(self, agent_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a specific agent.
        
        Args:
            agent_name: Name of the agent to analyze
            
        Returns:
            Dictionary with detailed agent statistics
        """
        agent_matches = []
        total_rounds = 0
        total_wins = 0
        total_losses = 0
        total_draws = 0
        move_counts = {"rock": 0, "paper": 0, "scissors": 0}
        opponents_faced = set()
        match_wins = 0
        match_losses = 0
        match_draws = 0
        
        # Analyze individual rounds
        for match in self.matches:
            if match.get("player1") == agent_name:
                total_rounds += 1
                move_counts[match["move1"]] += 1
                opponents_faced.add(match.get("player2"))
                
                if match["result1"] == "win":
                    total_wins += 1
                elif match["result1"] == "loss":
                    total_losses += 1
                else:
                    total_draws += 1
                    
            elif match.get("player2") == agent_name:
                total_rounds += 1
                move_counts[match["move2"]] += 1
                opponents_faced.add(match.get("player1"))
                
                if match["result2"] == "win":
                    total_wins += 1
                elif match["result2"] == "loss":
                    total_losses += 1
                else:
                    total_draws += 1
        
        # Analyze complete matches
        for match_end in self.match_ends:
            if match_end.get("player1") == agent_name:
                if match_end["winner"] == agent_name:
                    match_wins += 1
                elif match_end["winner"] == "Draw":
                    match_draws += 1
                else:
                    match_losses += 1
            elif match_end.get("player2") == agent_name:
                if match_end["winner"] == agent_name:
                    match_wins += 1
                elif match_end["winner"] == "Draw":
                    match_draws += 1
                else:
                    match_losses += 1
        
        return {
            "agent_name": agent_name,
            "total_rounds": total_rounds,
            "round_wins": total_wins,
            "round_losses": total_losses,
            "round_draws": total_draws,
            "round_win_rate": total_wins / total_rounds if total_rounds > 0 else 0,
            "match_wins": match_wins,
            "match_losses": match_losses,
            "match_draws": match_draws,
            "match_win_rate": match_wins / (match_wins + match_losses + match_draws) if (match_wins + match_losses + match_draws) > 0 else 0,
            "move_frequency": move_counts,
            "move_distribution": {move: count / total_rounds if total_rounds > 0 else 0 for move, count in move_counts.items()},
            "opponents_faced": list(opponents_faced),
            "total_opponents": len(opponents_faced)
        }
    
    def get_head_to_head_analysis(self, agent1: str, agent2: str) -> Dict[str, Any]:
        """Get detailed head-to-head analysis between two agents.
        
        Args:
            agent1: First agent name
            agent2: Second agent name
            
        Returns:
            Head-to-head analysis dictionary
        """
        h2h_rounds = []
        agent1_wins = 0
        agent2_wins = 0
        draws = 0
        
        # Find all rounds between these agents
        for match in self.matches:
            if ((match.get("player1") == agent1 and match.get("player2") == agent2) or
                (match.get("player1") == agent2 and match.get("player2") == agent1)):
                
                if match.get("player1") == agent1:
                    h2h_rounds.append({
                        "agent1_move": match["move1"],
                        "agent2_move": match["move2"],
                        "result": match["result1"]
                    })
                    if match["result1"] == "win":
                        agent1_wins += 1
                    elif match["result1"] == "loss":
                        agent2_wins += 1
                    else:
                        draws += 1
                else:
                    h2h_rounds.append({
                        "agent1_move": match["move2"],
                        "agent2_move": match["move1"],
                        "result": match["result2"]
                    })
                    if match["result2"] == "win":
                        agent1_wins += 1
                    elif match["result2"] == "loss":
                        agent2_wins += 1
                    else:
                        draws += 1
        
        total_h2h_rounds = len(h2h_rounds)
        
        return {
            "agent1": agent1,
            "agent2": agent2,
            "total_rounds": total_h2h_rounds,
            "agent1_wins": agent1_wins,
            "agent2_wins": agent2_wins,
            "draws": draws,
            "agent1_win_rate": agent1_wins / total_h2h_rounds if total_h2h_rounds > 0 else 0,
            "agent2_win_rate": agent2_wins / total_h2h_rounds if total_h2h_rounds > 0 else 0,
            "rounds_detail": h2h_rounds
        }
    
    def get_move_effectiveness_matrix(self) -> Dict[str, Any]:
        """Calculate effectiveness of each move against each other move.
        
        Returns:
            Move effectiveness analysis
        """
        matchups = {
            ("rock", "rock"): {"total": 0, "wins": 0},
            ("rock", "paper"): {"total": 0, "wins": 0},
            ("rock", "scissors"): {"total": 0, "wins": 0},
            ("paper", "rock"): {"total": 0, "wins": 0},
            ("paper", "paper"): {"total": 0, "wins": 0},
            ("paper", "scissors"): {"total": 0, "wins": 0},
            ("scissors", "rock"): {"total": 0, "wins": 0},
            ("scissors", "paper"): {"total": 0, "wins": 0},
            ("scissors", "scissors"): {"total": 0, "wins": 0}
        }
        
        for match in self.matches:
            move1 = match.get("move1")
            move2 = match.get("move2")
            result1 = match.get("result1")
            
            if move1 and move2 and result1:
                key = (move1, move2)
                if key in matchups:
                    matchups[key]["total"] += 1
                    if result1 == "win":
                        matchups[key]["wins"] += 1
        
        # Calculate win rates
        effectiveness_matrix = {}
        for (move1, move2), stats in matchups.items():
            win_rate = stats["wins"] / stats["total"] if stats["total"] > 0 else 0
            if move1 not in effectiveness_matrix:
                effectiveness_matrix[move1] = {}
            effectiveness_matrix[move1][move2] = {
                "win_rate": win_rate,
                "total_encounters": stats["total"],
                "wins": stats["wins"]
            }
        
        return effectiveness_matrix
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary by model type.
        
        Returns:
            Model performance analysis dictionary
        """
        model_stats = {}
        
        # Analyze match_end records for model performance
        for match_end in self.match_ends:
            player1_model = match_end.get("player1_model", "unknown")
            player2_model = match_end.get("player2_model", "unknown")
            winner_model = match_end.get("winner_model", "unknown")
            
            # Initialize model stats if needed
            for model in [player1_model, player2_model]:
                if model not in model_stats:
                    model_stats[model] = {
                        "total_matches": 0,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "total_rounds": 0,
                        "rounds_won": 0,
                        "same_model_matches": 0,
                        "cross_model_matches": 0,
                        "opponents_faced": set(),
                        "average_match_duration": 0,
                        "total_duration": 0
                    }
            
            # Update stats for player1_model
            model_stats[player1_model]["total_matches"] += 1
            model_stats[player1_model]["total_rounds"] += match_end.get("total_rounds", 0)
            model_stats[player1_model]["rounds_won"] += match_end.get("player1_score", 0)
            model_stats[player1_model]["opponents_faced"].add(player2_model)
            
            if match_end.get("match_duration_seconds"):
                model_stats[player1_model]["total_duration"] += match_end["match_duration_seconds"]
            
            if winner_model == player1_model:
                model_stats[player1_model]["wins"] += 1
            elif winner_model == "Draw":
                model_stats[player1_model]["draws"] += 1
            else:
                model_stats[player1_model]["losses"] += 1
            
            if player1_model == player2_model:
                model_stats[player1_model]["same_model_matches"] += 1
            else:
                model_stats[player1_model]["cross_model_matches"] += 1
            
            # Update stats for player2_model (avoiding double counting for same model)
            if player1_model != player2_model:
                model_stats[player2_model]["total_matches"] += 1
                model_stats[player2_model]["total_rounds"] += match_end.get("total_rounds", 0)
                model_stats[player2_model]["rounds_won"] += match_end.get("player2_score", 0)
                model_stats[player2_model]["opponents_faced"].add(player1_model)
                
                if match_end.get("match_duration_seconds"):
                    model_stats[player2_model]["total_duration"] += match_end["match_duration_seconds"]
                
                if winner_model == player2_model:
                    model_stats[player2_model]["wins"] += 1
                elif winner_model == "Draw":
                    model_stats[player2_model]["draws"] += 1
                else:
                    model_stats[player2_model]["losses"] += 1
                
                model_stats[player2_model]["cross_model_matches"] += 1
        
        # Calculate derived metrics
        for model, stats in model_stats.items():
            if stats["total_matches"] > 0:
                stats["match_win_rate"] = stats["wins"] / stats["total_matches"]
                stats["average_match_duration"] = stats["total_duration"] / stats["total_matches"] if stats["total_duration"] > 0 else 0
            else:
                stats["match_win_rate"] = 0
                
            if stats["total_rounds"] > 0:
                stats["round_win_rate"] = stats["rounds_won"] / stats["total_rounds"]
            else:
                stats["round_win_rate"] = 0
                
            stats["opponents_faced"] = list(stats["opponents_faced"])
            stats["opponent_diversity"] = len(stats["opponents_faced"])
        
        return model_stats

    def get_tournament_summary(self) -> Dict[str, Any]:
        """Get comprehensive tournament summary statistics.
        
        Returns:
            Tournament summary dictionary
        """
        tournament_start = next((r for r in self.data if r.get("type") == "tournament_start"), {})
        tournament_end = next((r for r in self.data if r.get("type") == "tournament_end"), {})
        
        total_rounds = len(self.matches)
        total_agents = len(self.agents)
        
        # Move distribution across entire tournament
        all_moves = []
        for match in self.matches:
            all_moves.extend([match.get("move1"), match.get("move2")])
        
        move_counts = {"rock": 0, "paper": 0, "scissors": 0}
        for move in all_moves:
            if move in move_counts:
                move_counts[move] += 1
        
        # Get model information
        unique_models = tournament_start.get("unique_models", [])
        num_unique_models = tournament_start.get("num_unique_models", 0)
        model_metadata = tournament_start.get("model_metadata", {})
        
        return {
            "tournament_type": tournament_start.get("tournament_type", "unknown"),
            "total_participants": total_agents,
            "unique_models": unique_models,
            "num_unique_models": num_unique_models,
            "model_metadata": model_metadata,
            "total_rounds": total_rounds,
            "total_matches": len(self.match_ends),
            "rounds_per_participant": total_rounds / total_agents if total_agents > 0 else 0,
            "champion": tournament_end.get("champion", "unknown"),
            "tournament_duration": tournament_end.get("tournament_duration_seconds"),
            "global_move_distribution": move_counts,
            "temperature": tournament_start.get("temperature", "unknown"),
            "seed": tournament_start.get("seed", "unknown"),
            "model_performance": self.get_model_performance_summary()
        } 