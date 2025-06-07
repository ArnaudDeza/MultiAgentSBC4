"""Tournament management for Tic-Tac-Toe showdown."""

import math
import random
from typing import List, Dict, Any, Tuple, Optional
from agents import PlayerAgent
from game_engine import play_game
from logger import GameLogger


class TournamentBracket:
    """Manages tournament bracket and progression."""
    
    def __init__(self, models: List[str], temperature: float = 0.7, seed: int = 42):
        """Initialize tournament bracket.
        
        Args:
            models: List of model names to participate
            temperature: Temperature setting for all agents
            seed: Base seed for reproducibility
        """
        self.models = models[:]  # Copy to avoid modifying original
        self.temperature = temperature
        self.seed = seed
        self.bracket_history: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {}
        
        # Ensure we have a power of 2 number of participants
        self._pad_to_power_of_two()
    
    def _pad_to_power_of_two(self) -> None:
        """Pad the models list to the next power of 2."""
        if len(self.models) == 0:
            self.models = ["phi4", "phi4"]  # Default fallback
            return
        
        if len(self.models) == 1:
            self.models.append(self.models[0])  # Duplicate for self-play
            return
        
        # Find next power of 2
        next_power = 2 ** math.ceil(math.log2(len(self.models)))
        
        # Add duplicates or random selections to reach power of 2
        while len(self.models) < next_power:
            self.models.append(random.choice(self.models[:len(self.models)//2]))
    
    def get_total_rounds(self) -> int:
        """Get the total number of rounds in the tournament.
        
        Returns:
            Number of rounds (log2 of participants)
        """
        return int(math.log2(len(self.models)))


def run_tournament(models: List[str], temperature: float = 0.7, seed: int = 42, 
                  logger: Optional[GameLogger] = None) -> Dict[str, Any]:
    """Run a complete single-elimination tournament.
    
    Args:
        models: List of model names to compete
        temperature: Temperature setting for all agents
        seed: Random seed for reproducibility
        logger: Logger instance (created if None)
        
    Returns:
        Dictionary containing tournament results
    """
    if logger is None:
        logger = GameLogger()
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Create tournament bracket
    bracket = TournamentBracket(models, temperature, seed)
    total_rounds = bracket.get_total_rounds()
    
    print(f"🏆 Starting Tic-Tac-Toe Tournament")
    print(f"👥 Participants: {len(bracket.models)}")
    print(f"🔄 Total Rounds: {total_rounds}")
    print(f"📊 Models: {', '.join(set(bracket.models))}")
    print("=" * 60)
    
    # Log tournament start
    logger.log_tournament_start(bracket.models, total_rounds)
    
    current_round = bracket.models[:]
    round_num = 1
    all_results = []
    
    while len(current_round) > 1:
        print(f"\n🔥 Round {round_num} - {len(current_round)} participants")
        print("-" * 40)
        
        next_round = []
        round_matches = []
        
        # Create pairs for this round
        for i in range(0, len(current_round), 2):
            model1 = current_round[i]
            model2 = current_round[i + 1] if i + 1 < len(current_round) else model1
            
            match_info = {
                "match_id": f"R{round_num}M{i//2 + 1}",
                "model1": model1,
                "model2": model2
            }
            round_matches.append(match_info)
        
        # Log round start
        logger.log_round_start(round_num, round_matches)
        
        # Play matches in this round
        for match in round_matches:
            model1, model2 = match["model1"], match["model2"]
            match_id = match["match_id"]
            
            print(f"⚔️ {match_id}: {model1} vs {model2}")
            
            # Create agents with different seeds for variety
            agent1 = PlayerAgent(model=model1, temperature=temperature, seed=seed + round_num * 100 + len(next_round))
            agent2 = PlayerAgent(model=model2, temperature=temperature, seed=seed + round_num * 100 + len(next_round) + 1)
            
            # Play the match
            result, winner = play_game(agent1, agent2, match_id, logger)
            
            # Determine advancing model
            if winner == 'X':
                advancing_model = model1
            elif winner == 'O':
                advancing_model = model2
            else:
                # In case of draw, choose randomly or use a tiebreaker
                advancing_model = random.choice([model1, model2])
                print(f"🎲 Draw! Randomly advancing: {advancing_model}")
            
            next_round.append(advancing_model)
            
            match_result = {
                "round": round_num,
                "match_id": match_id,
                "model1": model1,
                "model2": model2,
                "winner": winner,
                "advancing": advancing_model,
                "result": result
            }
            all_results.append(match_result)
            
            print(f"✅ {advancing_model} advances!\n")
        
        current_round = next_round
        round_num += 1
    
    # Tournament completed
    champion = current_round[0]
    
    print("=" * 60)
    print(f"🏆 TOURNAMENT CHAMPION: {champion}")
    print("=" * 60)
    
    # Compile final results
    tournament_results = {
        "champion": champion,
        "total_rounds": total_rounds,
        "total_participants": len(bracket.models),
        "unique_models": list(set(bracket.models)),
        "all_matches": all_results,
        "bracket": bracket.models
    }
    
    return tournament_results


def create_seeded_bracket(models: List[str], shuffle: bool = True) -> List[str]:
    """Create a seeded tournament bracket.
    
    Args:
        models: List of model names
        shuffle: Whether to shuffle the initial order
        
    Returns:
        List of models arranged for tournament bracket
    """
    bracket_models = models[:]
    
    if shuffle:
        random.shuffle(bracket_models)
    
    # Pad to power of 2
    while len(bracket_models) & (len(bracket_models) - 1) != 0:
        bracket_models.append(random.choice(models))
    
    return bracket_models


def get_tournament_stats(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate tournament statistics.
    
    Args:
        results: Tournament results dictionary
        
    Returns:
        Dictionary of compiled statistics
    """
    stats = {
        "total_games": len(results["all_matches"]),
        "total_moves": 0,
        "wins_by_model": {},
        "games_by_model": {},
        "avg_game_length": 0
    }
    
    # Count wins and games per model
    for match in results["all_matches"]:
        model1, model2 = match["model1"], match["model2"]
        advancing = match["advancing"]
        
        # Initialize counters
        for model in [model1, model2]:
            if model not in stats["wins_by_model"]:
                stats["wins_by_model"][model] = 0
            if model not in stats["games_by_model"]:
                stats["games_by_model"][model] = 0
            stats["games_by_model"][model] += 1
        
        # Count win
        if advancing in stats["wins_by_model"]:
            stats["wins_by_model"][advancing] += 1
    
    # Calculate win rates
    stats["win_rates"] = {}
    for model in stats["games_by_model"]:
        games = stats["games_by_model"][model]
        wins = stats["wins_by_model"].get(model, 0)
        stats["win_rates"][model] = wins / games if games > 0 else 0
    
    return stats 