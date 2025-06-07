"""Flexible tournament system supporting multiple formats and best-of-X matches."""

import math
import random
import itertools
from typing import List, Dict, Any, Tuple, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from game_interface import IGame, PlayerAgent, GameConfig
from enhanced_logger import EnhancedLogger


class TournamentFormat(Enum):
    """Supported tournament formats."""
    SINGLE_ELIMINATION = "single_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    DOUBLE_ELIMINATION = "double_elimination"


@dataclass
class MatchResult:
    """Result of a single match between two players."""
    match_id: str
    player1: str
    player2: str
    games: List[Dict[str, Any]]
    winner: Optional[str]
    score: Tuple[int, int]  # (player1_wins, player2_wins)
    format: str = "best_of_1"


@dataclass
class TournamentConfig:
    """Configuration for tournament settings."""
    format: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION
    best_of: int = 1  # Best of X games per match
    game_config: GameConfig = field(default_factory=GameConfig)
    shuffle_players: bool = True
    seed: int = 42
    max_rounds: int = 10  # For Swiss tournaments
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.best_of < 1:
            self.best_of = 1
        if self.best_of % 2 == 0:
            self.best_of += 1  # Ensure odd number for clear winner


class TournamentEngine:
    """Generic tournament engine supporting multiple formats."""
    
    def __init__(self, 
                 config: TournamentConfig,
                 game_factory: Callable[[], IGame],
                 logger: Optional[EnhancedLogger] = None):
        """Initialize the tournament engine.
        
        Args:
            config: Tournament configuration
            game_factory: Function that creates new game instances
            logger: Optional enhanced logger for recording tournament events
        """
        self.config = config
        self.game_factory = game_factory
        self.logger = logger or EnhancedLogger()
        
        # Tournament state
        self.players: List[PlayerAgent] = []
        self.matches: List[MatchResult] = []
        self.standings: Dict[str, Dict[str, Any]] = {}
        self.eliminated_players: List[str] = []
        
        # Format-specific data
        self.bracket: Dict[str, Any] = {}
        self.swiss_pairings: List[List[Tuple[str, str]]] = []
        
        random.seed(config.seed)
    
    def add_players(self, players: List[PlayerAgent]) -> None:
        """Add players to the tournament.
        
        Args:
            players: List of player agents
        """
        self.players = players[:]
        if self.config.shuffle_players:
            random.shuffle(self.players)
        
        # Initialize standings
        for player in self.players:
            self.standings[player.name] = {
                "wins": 0,
                "losses": 0,
                "games_won": 0,
                "games_lost": 0,
                "matches_played": 0,
                "points": 0,  # For Swiss tournaments
                "opponents": []
            }
    
    def run_tournament(self) -> Dict[str, Any]:
        """Run the complete tournament.
        
        Returns:
            Tournament results dictionary
        """
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players for a tournament")
        
        print(f"🏆 Starting {self.config.format.value} tournament")
        print(f"👥 Players: {[p.name for p in self.players]}")
        print(f"🎯 Format: Best of {self.config.best_of}")
        print("=" * 60)
        
        # Log tournament start
        self.logger.log_tournament_start(
            [p.name for p in self.players], 
            self._estimate_total_rounds()
        )
        
        # Run tournament based on format
        if self.config.format == TournamentFormat.SINGLE_ELIMINATION:
            return self._run_single_elimination()
        elif self.config.format == TournamentFormat.ROUND_ROBIN:
            return self._run_round_robin()
        elif self.config.format == TournamentFormat.SWISS:
            return self._run_swiss()
        elif self.config.format == TournamentFormat.DOUBLE_ELIMINATION:
            return self._run_double_elimination()
        else:
            raise ValueError(f"Unsupported tournament format: {self.config.format}")
    
    def _run_single_elimination(self) -> Dict[str, Any]:
        """Run single elimination tournament."""
        # Pad to power of 2
        while len(self.players) & (len(self.players) - 1) != 0:
            # Add duplicate players for padding
            self.players.append(random.choice(self.players))
        
        current_round = [p.name for p in self.players]
        round_num = 1
        
        while len(current_round) > 1:
            print(f"\n🔥 Round {round_num} - {len(current_round)} players")
            print("-" * 40)
            
            next_round = []
            round_matches = []
            
            # Create pairs
            for i in range(0, len(current_round), 2):
                player1 = current_round[i]
                player2 = current_round[i + 1] if i + 1 < len(current_round) else player1
                
                if player1 != player2:
                    match_result = self._play_match(player1, player2, f"R{round_num}M{i//2 + 1}")
                    round_matches.append(match_result)
                    next_round.append(match_result.winner)
                    print(f"✅ {match_result.winner} defeats {player1 if match_result.winner == player2 else player2}")
                else:
                    next_round.append(player1)
                    print(f"🔄 {player1} advances (bye)")
            
            current_round = next_round
            round_num += 1
        
        champion = current_round[0]
        print(f"\n🏆 CHAMPION: {champion}")
        
        return self._compile_results(champion)
    
    def _run_round_robin(self) -> Dict[str, Any]:
        """Run round robin tournament."""
        player_names = [p.name for p in self.players]
        
        # Generate all possible pairings
        pairings = list(itertools.combinations(player_names, 2))
        
        print(f"🔄 Round Robin: {len(pairings)} matches to play")
        
        match_num = 1
        for player1, player2 in pairings:
            print(f"\n⚔️ Match {match_num}/{len(pairings)}: {player1} vs {player2}")
            
            match_result = self._play_match(player1, player2, f"RR{match_num}")
            print(f"✅ Winner: {match_result.winner} ({match_result.score[0]}-{match_result.score[1]})")
            
            match_num += 1
        
        # Determine winner based on points
        champion = max(self.standings.items(), key=lambda x: (x[1]["points"], x[1]["games_won"]))[0]
        print(f"\n🏆 CHAMPION: {champion}")
        
        return self._compile_results(champion)
    
    def _run_swiss(self) -> Dict[str, Any]:
        """Run Swiss tournament."""
        num_rounds = min(self.config.max_rounds, math.ceil(math.log2(len(self.players))))
        
        for round_num in range(1, num_rounds + 1):
            print(f"\n🔄 Swiss Round {round_num}/{num_rounds}")
            print("-" * 40)
            
            # Generate pairings for this round
            pairings = self._generate_swiss_pairings(round_num)
            self.swiss_pairings.append(pairings)
            
            # Play matches
            for i, (player1, player2) in enumerate(pairings):
                match_result = self._play_match(player1, player2, f"S{round_num}M{i+1}")
                print(f"✅ {match_result.winner} defeats {player1 if match_result.winner == player2 else player2}")
        
        # Determine winner based on points and tiebreakers
        champion = max(self.standings.items(), 
                      key=lambda x: (x[1]["points"], x[1]["games_won"], x[1]["wins"]))[0]
        print(f"\n🏆 CHAMPION: {champion}")
        
        return self._compile_results(champion)
    
    def _run_double_elimination(self) -> Dict[str, Any]:
        """Run double elimination tournament."""
        # TODO: Implement double elimination
        print("🚧 Double elimination not yet implemented, running single elimination")
        return self._run_single_elimination()
    
    def _play_match(self, player1_name: str, player2_name: str, match_id: str) -> MatchResult:
        """Play a best-of-X match between two players.
        
        Args:
            player1_name: Name of first player
            player2_name: Name of second player
            match_id: Unique match identifier
            
        Returns:
            Match result
        """
        # Get player objects
        player1 = next(p for p in self.players if p.name == player1_name)
        player2 = next(p for p in self.players if p.name == player2_name)
        
        games = []
        player1_wins = 0
        player2_wins = 0
        wins_needed = (self.config.best_of + 1) // 2
        
        game_num = 1
        while player1_wins < wins_needed and player2_wins < wins_needed:
            print(f"  🎮 Game {game_num}/{self.config.best_of} - {player1_name} vs {player2_name}")
            
            # Create new game instance
            game = self.game_factory()
            
            # Alternate who goes first
            if game_num % 2 == 1:
                first_player, second_player = player1, player2
                first_symbol, second_symbol = 'X', 'O'
            else:
                first_player, second_player = player2, player1
                first_symbol, second_symbol = 'X', 'O'
            
            # Play the game
            game_result = self._play_single_game(
                game, first_player, second_player, 
                first_symbol, second_symbol, f"{match_id}G{game_num}"
            )
            
            games.append(game_result)
            
            # Update scores
            if game_result['winner'] == player1_name:
                player1_wins += 1
            elif game_result['winner'] == player2_name:
                player2_wins += 1
            
            print(f"    Result: {game_result['winner'] or 'Draw'} (Score: {player1_wins}-{player2_wins})")
            game_num += 1
        
        # Determine match winner
        match_winner = player1_name if player1_wins > player2_wins else player2_name
        
        # Update standings
        self._update_standings(player1_name, player2_name, player1_wins, player2_wins)
        
        match_result = MatchResult(
            match_id=match_id,
            player1=player1_name,
            player2=player2_name,
            games=games,
            winner=match_winner,
            score=(player1_wins, player2_wins),
            format=f"best_of_{self.config.best_of}"
        )
        
        # Log match result to enhanced logger
        if hasattr(self.logger, 'log_match_result'):
            match_data = {
                "match_id": match_id,
                "players": [player1_name, player2_name],
                "winner": match_winner,
                "score": (player1_wins, player2_wins),
                "games": len(games),
                "format": f"best_of_{self.config.best_of}"
            }
            self.logger.log_match_result(match_data)
        
        self.matches.append(match_result)
        return match_result
    
    def _play_single_game(self, game: IGame, player1: PlayerAgent, player2: PlayerAgent,
                         p1_symbol: str, p2_symbol: str, game_id: str) -> Dict[str, Any]:
        """Play a single game between two players.
        
        Args:
            game: Game instance
            player1: First player agent
            player2: Second player agent
            p1_symbol: Symbol for player 1
            p2_symbol: Symbol for player 2
            game_id: Unique game identifier
            
        Returns:
            Game result dictionary
        """
        current_player = player1
        current_symbol = p1_symbol
        move_count = 0
        max_moves = game.get_game_config().get('max_moves', 50)
        
        while move_count < max_moves:
            try:
                # Get move from current player
                game_state = game.get_state()
                move = current_player.get_move(game_state, current_symbol, game)
                
                # Make the move
                if not game.make_move(move, current_symbol):
                    # Invalid move, try to find a valid one
                    valid_moves = game.get_valid_moves(current_symbol)
                    if valid_moves:
                        move = valid_moves[0]
                        game.make_move(move, current_symbol)
                    else:
                        break  # No valid moves available
                
                # Log the move
                self.logger.log_move(game_id, current_symbol, move, game.get_state())
                
                # Check for game over
                is_over, winner = game.is_game_over()
                if is_over:
                    winner_name = None
                    if winner == p1_symbol:
                        winner_name = player1.name
                    elif winner == p2_symbol:
                        winner_name = player2.name
                    
                    result = {
                        'game_id': game_id,
                        'winner': winner_name,
                        'moves': move_count + 1,
                        'final_state': game.get_state()
                    }
                    
                    self.logger.log_result(game_id, "win" if winner else "draw", 
                                         game.get_state(), winner_name)
                    return result
                
                # Switch players
                if current_player == player1:
                    current_player = player2
                    current_symbol = p2_symbol
                else:
                    current_player = player1
                    current_symbol = p1_symbol
                
                move_count += 1
                
            except Exception as e:
                print(f"❌ Error in game {game_id}: {e}")
                break
        
        # Game ended without winner (timeout or error)
        result = {
            'game_id': game_id,
            'winner': None,
            'moves': move_count,
            'final_state': game.get_state()
        }
        
        self.logger.log_result(game_id, "draw", game.get_state(), None)
        return result
    
    def _update_standings(self, player1: str, player2: str, p1_wins: int, p2_wins: int) -> None:
        """Update tournament standings after a match.
        
        Args:
            player1: First player name
            player2: Second player name
            p1_wins: Games won by player 1
            p2_wins: Games won by player 2
        """
        # Update match counts
        self.standings[player1]["matches_played"] += 1
        self.standings[player2]["matches_played"] += 1
        
        # Update game counts
        self.standings[player1]["games_won"] += p1_wins
        self.standings[player1]["games_lost"] += p2_wins
        self.standings[player2]["games_won"] += p2_wins
        self.standings[player2]["games_lost"] += p1_wins
        
        # Update match wins/losses and points
        if p1_wins > p2_wins:
            self.standings[player1]["wins"] += 1
            self.standings[player2]["losses"] += 1
            self.standings[player1]["points"] += 3  # 3 points for match win
            self.standings[player2]["points"] += 1  # 1 point for participation
        elif p2_wins > p1_wins:
            self.standings[player2]["wins"] += 1
            self.standings[player1]["losses"] += 1
            self.standings[player2]["points"] += 3
            self.standings[player1]["points"] += 1
        else:
            # Draw
            self.standings[player1]["points"] += 2  # 2 points for draw
            self.standings[player2]["points"] += 2
        
        # Track opponents for Swiss pairing
        self.standings[player1]["opponents"].append(player2)
        self.standings[player2]["opponents"].append(player1)
    
    def _generate_swiss_pairings(self, round_num: int) -> List[Tuple[str, str]]:
        """Generate pairings for a Swiss tournament round.
        
        Args:
            round_num: Current round number
            
        Returns:
            List of player pairings
        """
        if round_num == 1:
            # First round: random or seeded pairings
            players = [p.name for p in self.players]
            random.shuffle(players)
            return [(players[i], players[i+1]) for i in range(0, len(players)-1, 2)]
        
        # Subsequent rounds: pair by points, avoiding rematches
        players_by_points = sorted(
            self.standings.items(),
            key=lambda x: (x[1]["points"], x[1]["games_won"]),
            reverse=True
        )
        
        pairings = []
        unpaired = [p[0] for p in players_by_points]
        
        while len(unpaired) >= 2:
            player1 = unpaired[0]
            
            # Find best opponent who hasn't played player1
            for i in range(1, len(unpaired)):
                player2 = unpaired[i]
                if player2 not in self.standings[player1]["opponents"]:
                    pairings.append((player1, player2))
                    unpaired.remove(player1)
                    unpaired.remove(player2)
                    break
            else:
                # No unused opponent found, pair with closest rating
                player2 = unpaired[1]
                pairings.append((player1, player2))
                unpaired.remove(player1)
                unpaired.remove(player2)
        
        # Handle odd number of players (bye round)
        if unpaired:
            print(f"🔄 {unpaired[0]} gets a bye this round")
            self.standings[unpaired[0]]["points"] += 2  # Bye = 2 points
        
        return pairings
    
    def _estimate_total_rounds(self) -> int:
        """Estimate total number of rounds based on format.
        
        Returns:
            Estimated number of rounds
        """
        if self.config.format == TournamentFormat.SINGLE_ELIMINATION:
            return math.ceil(math.log2(len(self.players)))
        elif self.config.format == TournamentFormat.ROUND_ROBIN:
            return len(self.players) - 1  # Actually number of rounds in complete round-robin
        elif self.config.format == TournamentFormat.SWISS:
            return min(self.config.max_rounds, math.ceil(math.log2(len(self.players))))
        else:
            return len(self.players)  # Conservative estimate
    
    def _compile_results(self, champion: str) -> Dict[str, Any]:
        """Compile final tournament results.
        
        Args:
            champion: Tournament winner
            
        Returns:
            Complete results dictionary
        """
        return {
            "format": self.config.format.value,
            "champion": champion,
            "total_rounds": len(set(m.match_id.split('M')[0] for m in self.matches)),
            "total_matches": len(self.matches),
            "total_games": sum(len(m.games) for m in self.matches),
            "participants": [p.name for p in self.players],
            "standings": self.standings,
            "matches": [
                {
                    "match_id": m.match_id,
                    "players": [m.player1, m.player2],
                    "winner": m.winner,
                    "score": m.score,
                    "games": len(m.games)
                }
                for m in self.matches
            ],
            "config": {
                "format": self.config.format.value,
                "best_of": self.config.best_of,
                "game_config": self.config.game_config.to_dict()
            }
        } 