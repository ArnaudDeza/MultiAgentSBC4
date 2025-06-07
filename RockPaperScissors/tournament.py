"""Tournament management for Rock Paper Scissors Royale."""

import itertools
import random
from typing import List, Dict, Any, Tuple, Optional
from agents import PlayerAgent, create_agent
from utils import Move, GameResult, determine_winner, RPSLogger, TournamentScorer


class TournamentManager:
    """Manages different types of Rock Paper Scissors tournaments."""
    
    def __init__(self, log_file: str = "data/logs/tournament.jsonl") -> None:
        """Initialize the tournament manager.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.logger = RPSLogger(log_file)
        self.match_counter = 0
    
    def run_round_robin(self, agents: List[PlayerAgent], rounds_per_match: int = 10) -> Dict[str, Any]:
        """Run a round-robin tournament where every agent plays every other agent.
        
        Args:
            agents: List of participating agents
            rounds_per_match: Number of rounds in each match
            
        Returns:
            Tournament results dictionary
        """
        print(f"🏆 Starting Round-Robin Tournament")
        print(f"👥 {len(agents)} agents, {rounds_per_match} rounds per match")
        print("=" * 60)
        
        # Initialize scorer
        agent_names = [agent.name for agent in agents]
        scorer = TournamentScorer(agent_names)
        
        # Log tournament start with model metadata
        total_matches = len(list(itertools.combinations(agents, 2)))
        
        # Collect model metadata
        model_metadata = {}
        for agent in agents:
            if hasattr(agent, 'model') and hasattr(agent, 'temperature'):
                model_metadata[agent.name] = {
                    "model": agent.model,
                    "temperature": agent.temperature,
                    "agent_type": type(agent).__name__
                }
        
        self.logger.log_tournament_start(
            agent_names, "round_robin", total_matches, 
            temperature=agents[0].temperature if agents and hasattr(agents[0], 'temperature') else 0.7,
            seed=agents[0].seed if agents and hasattr(agents[0], 'seed') else 42,
            model_metadata=model_metadata
        )
        
        # Generate all pairings
        pairings = list(itertools.combinations(agents, 2))
        
        print(f"🎮 Playing {total_matches} matches...")
        
        for i, (agent1, agent2) in enumerate(pairings, 1):
            print(f"\n⚔️ Match {i}/{total_matches}: {agent1.name} vs {agent2.name}")
            
            # Log match start with model information
            match_id = f"RR{i:03d}_{agent1.name}_vs_{agent2.name}"
            self.logger.log_match_start(
                match_id, agent1.name, agent2.name, rounds_per_match,
                player1_model=getattr(agent1, 'model', agent1.name),
                player2_model=getattr(agent2, 'model', agent2.name),
                player1_temp=getattr(agent1, 'temperature', None),
                player2_temp=getattr(agent2, 'temperature', None)
            )
            
            # Play the match
            match_result = self._play_match(agent1, agent2, rounds_per_match, match_id)
            
            # Log match end with detailed statistics and model information
            self.logger.log_match_end(
                match_id, agent1.name, agent2.name, match_result["winner"],
                match_result["score"], match_result["agent1_score"], match_result["agent2_score"],
                match_result["agent1_history"], match_result["agent2_history"],
                match_duration_seconds=match_result.get("duration", None),
                player1_model=getattr(agent1, 'model', agent1.name),
                player2_model=getattr(agent2, 'model', agent2.name)
            )
            
            # Update scores
            if match_result["winner"] == agent1.name:
                scorer.record_match(agent1.name, agent2.name, GameResult.WIN, GameResult.LOSS)
            elif match_result["winner"] == agent2.name:
                scorer.record_match(agent1.name, agent2.name, GameResult.LOSS, GameResult.WIN)
            else:
                scorer.record_match(agent1.name, agent2.name, GameResult.DRAW, GameResult.DRAW)
            
            print(f"🏅 Winner: {match_result['winner']}")
            print(f"📊 Score: {match_result['score']}")
        
        # Get final standings
        final_standings = scorer.get_standings()
        champion = scorer.get_champion()
        
        # Log tournament end
        self.logger.log_tournament_end(final_standings, champion)
        
        # Display final results
        self._display_final_results(scorer, "Round-Robin")
        
        return {
            "tournament_type": "round_robin",
            "participants": agent_names,
            "champion": champion,
            "final_standings": final_standings,
            "total_matches": total_matches
        }
    
    def run_single_elimination(self, agents: List[PlayerAgent], rounds_per_match: int = 5) -> Dict[str, Any]:
        """Run a single-elimination tournament.
        
        Args:
            agents: List of participating agents
            rounds_per_match: Number of rounds in each match
            
        Returns:
            Tournament results dictionary
        """
        print(f"🏆 Starting Single-Elimination Tournament")
        print(f"👥 {len(agents)} agents, {rounds_per_match} rounds per match")
        print("=" * 60)
        
        # Pad to power of 2 if needed
        tournament_agents = self._pad_bracket(agents)
        agent_names = [agent.name for agent in tournament_agents]
        
        # Calculate total rounds
        import math
        total_rounds = int(math.log2(len(tournament_agents)))
        
        # Log tournament start
        self.logger.log_tournament_start(agent_names, "single_elimination", total_rounds)
        
        current_round = tournament_agents[:]
        round_num = 1
        
        while len(current_round) > 1:
            print(f"\n🔥 Round {round_num} - {len(current_round)} participants")
            print("-" * 40)
            
            next_round = []
            
            # Pair up agents for this round
            for i in range(0, len(current_round), 2):
                agent1 = current_round[i]
                agent2 = current_round[i + 1] if i + 1 < len(current_round) else current_round[i]
                
                print(f"⚔️ {agent1.name} vs {agent2.name}")
                
                # Play the match
                match_result = self._play_match(agent1, agent2, rounds_per_match)
                
                # Determine who advances
                if match_result["winner"] == agent1.name:
                    advancing_agent = agent1
                elif match_result["winner"] == agent2.name:
                    advancing_agent = agent2
                else:
                    # In case of draw, choose randomly
                    advancing_agent = random.choice([agent1, agent2])
                    print(f"🎲 Draw! Randomly advancing: {advancing_agent.name}")
                
                next_round.append(advancing_agent)
                print(f"✅ {advancing_agent.name} advances!")
            
            current_round = next_round
            round_num += 1
        
        # Tournament completed
        champion = current_round[0].name
        
        print("=" * 60)
        print(f"🏆 TOURNAMENT CHAMPION: {champion}")
        print("=" * 60)
        
        # Log tournament end
        final_standings = {champion: {"position": 1}}
        self.logger.log_tournament_end(final_standings, champion)
        
        return {
            "tournament_type": "single_elimination",
            "participants": agent_names,
            "champion": champion,
            "total_rounds": total_rounds
        }
    
    def run_league(self, agents: List[PlayerAgent], rounds: int = 20) -> Dict[str, Any]:
        """Run a league tournament where agents play multiple random matches.
        
        Args:
            agents: List of participating agents
            rounds: Total number of rounds to play
            
        Returns:
            Tournament results dictionary
        """
        print(f"🏆 Starting League Tournament")
        print(f"👥 {len(agents)} agents, {rounds} total rounds")
        print("=" * 60)
        
        # Initialize scorer
        agent_names = [agent.name for agent in agents]
        scorer = TournamentScorer(agent_names)
        
        # Log tournament start
        self.logger.log_tournament_start(agent_names, "league", rounds)
        
        print(f"🎮 Playing {rounds} rounds...")
        
        for round_num in range(1, rounds + 1):
            # Randomly pair agents for this round
            shuffled_agents = agents[:]
            random.shuffle(shuffled_agents)
            
            pairs = []
            for i in range(0, len(shuffled_agents), 2):
                if i + 1 < len(shuffled_agents):
                    pairs.append((shuffled_agents[i], shuffled_agents[i + 1]))
            
            print(f"\n🔄 Round {round_num}/{rounds}")
            
            round_results = []
            for agent1, agent2 in pairs:
                # Play single round
                match_result = self._play_single_round(agent1, agent2, round_num)
                round_results.append(match_result)
                
                # Update scores
                if match_result["result1"] == GameResult.WIN:
                    scorer.record_match(agent1.name, agent2.name, GameResult.WIN, GameResult.LOSS)
                elif match_result["result1"] == GameResult.LOSS:
                    scorer.record_match(agent1.name, agent2.name, GameResult.LOSS, GameResult.WIN)
                else:
                    scorer.record_match(agent1.name, agent2.name, GameResult.DRAW, GameResult.DRAW)
            
            # Log round summary every 5 rounds
            if round_num % 5 == 0:
                standings = scorer.get_standings()
                self.logger.log_round_summary(round_num, standings)
                self._display_standings(scorer, f"After Round {round_num}")
        
        # Get final standings
        final_standings = scorer.get_standings()
        champion = scorer.get_champion()
        
        # Log tournament end
        self.logger.log_tournament_end(final_standings, champion)
        
        # Display final results
        self._display_final_results(scorer, "League")
        
        return {
            "tournament_type": "league",
            "participants": agent_names,
            "champion": champion,
            "final_standings": final_standings,
            "total_rounds": rounds
        }
    
    def _play_match(self, agent1: PlayerAgent, agent2: PlayerAgent, num_rounds: int, match_id: str = None) -> Dict[str, Any]:
        """Play a multi-round match between two agents.
        
        This plays a complete match consisting of multiple rounds. Each round:
        1. Both agents receive the complete history of previous rounds in this match
        2. Both agents simultaneously choose their moves
        3. Round winner is determined and history is updated
        4. Process repeats for specified number of rounds
        
        Args:
            agent1: First agent
            agent2: Second agent
            num_rounds: Number of rounds to play in this match
            match_id: Optional match identifier for logging
            
        Returns:
            Match result dictionary with winner, detailed scores, and timing
        """
        import time
        match_start_time = time.time()
        
        print(f"    🎲 Playing {num_rounds}-round match...")
        
        agent1_score = 0
        agent2_score = 0
        agent1_history = []  # Agent1's move history (what agent1 played)
        agent2_history = []  # Agent2's move history (what agent2 played)
        
        # Play each round with complete history
        for round_num in range(1, num_rounds + 1):
            # Each agent gets the opponent's history and their own history
            result = self._play_single_round(agent1, agent2, round_num, agent1_history, agent2_history)
            
            # Update match score
            if result["result1"] == GameResult.WIN:
                agent1_score += 1
            elif result["result1"] == GameResult.LOSS:
                agent2_score += 1
            # Draws don't change scores
            
            # Update histories for next round (agent1_history contains agent1's moves)
            agent1_history.append(result["move1"])  # Agent1's move this round
            agent2_history.append(result["move2"])  # Agent2's move this round
            
            # Show round result
            move1_str = result["move1"].value
            move2_str = result["move2"].value
            result_str = "🤝 Draw" if result["result1"] == GameResult.DRAW else (
                f"✅ {agent1.name}" if result["result1"] == GameResult.WIN else f"✅ {agent2.name}"
            )
            print(f"      Round {round_num:2d}: {agent1.name}={move1_str:8s} vs {agent2.name}={move2_str:8s} → {result_str}")
        
        # Determine overall match winner
        if agent1_score > agent2_score:
            winner = agent1.name
        elif agent2_score > agent1_score:
            winner = agent2.name
        else:
            winner = "Draw"
        
        match_end_time = time.time()
        match_duration = match_end_time - match_start_time
        
        print(f"    📊 Final Score: {agent1.name} {agent1_score}-{agent2_score} {agent2.name} ({match_duration:.1f}s)")
        
        return {
            "winner": winner,
            "score": f"{agent1_score}-{agent2_score}",
            "agent1_score": agent1_score,
            "agent2_score": agent2_score,
            "total_rounds": num_rounds,
            "agent1_history": agent1_history,
            "agent2_history": agent2_history,
            "duration": match_duration
        }
    
    def _play_single_round(self, agent1: PlayerAgent, agent2: PlayerAgent, round_num: int,
                          agent1_history: List[Move] = None, agent2_history: List[Move] = None) -> Dict[str, Any]:
        """Play a single round between two agents with complete match history.
        
        Each agent receives:
        - Their own complete move history from this match
        - Their opponent's complete move history from this match  
        - Current round number
        
        Both agents make moves simultaneously based on this information.
        
        Args:
            agent1: First agent
            agent2: Second agent  
            round_num: Current round number in this match
            agent1_history: Agent1's previous moves in this match (what agent1 has played)
            agent2_history: Agent2's previous moves in this match (what agent2 has played)
            
        Returns:
            Round result dictionary with moves and outcomes
        """
        self.match_counter += 1
        match_id = f"M{self.match_counter:04d}"
        
        # Initialize histories if not provided
        if agent1_history is None:
            agent1_history = []
        if agent2_history is None:
            agent2_history = []
        
        # Get moves from both agents simultaneously
        # CRITICAL: Each agent gets their opponent's history and their own history
        try:
            # Agent1 gets: opponent_history=agent2_history, own_history=agent1_history  
            move1 = agent1.make_move(round_num, agent2_history, agent1_history)
            
            # Agent2 gets: opponent_history=agent1_history, own_history=agent2_history
            move2 = agent2.make_move(round_num, agent1_history, agent2_history)
            
        except Exception as e:
            print(f"⚠️ Error getting moves in round {round_num}: {e}")
            # Fallback to random moves if LLM fails
            move1 = random.choice(list(Move))
            move2 = random.choice(list(Move))
        
        # Determine round results based on Rock Paper Scissors rules
        result1, result2 = determine_winner(move1, move2)
        
        # Log this round to JSONL
        self.logger.log_match(match_id, agent1.name, agent2.name, move1, move2, result1, result2)
        
        return {
            "match_id": match_id,
            "agent1": agent1.name,
            "agent2": agent2.name,
            "move1": move1,      # What agent1 played this round
            "move2": move2,      # What agent2 played this round
            "result1": result1,  # Agent1's result (win/loss/draw)
            "result2": result2   # Agent2's result (win/loss/draw)
        }
    
    def _pad_bracket(self, agents: List[PlayerAgent]) -> List[PlayerAgent]:
        """Pad the agents list to the next power of 2 for single elimination.
        
        Args:
            agents: Original list of agents
            
        Returns:
            Padded list of agents
        """
        import math
        
        if len(agents) <= 1:
            return agents + [create_agent("random", "random", name="Bye")] * (2 - len(agents))
        
        # Find next power of 2
        next_power = 2 ** math.ceil(math.log2(len(agents)))
        
        # Add random agents to fill the bracket
        padded_agents = agents[:]
        while len(padded_agents) < next_power:
            bye_agent = create_agent("random", "random", name=f"Bye{len(padded_agents)}")
            padded_agents.append(bye_agent)
        
        return padded_agents
    
    def _display_standings(self, scorer: TournamentScorer, title: str) -> None:
        """Display current tournament standings.
        
        Args:
            scorer: Tournament scorer instance
            title: Title for the standings display
        """
        print(f"\n📊 {title}")
        print("-" * 50)
        
        leaderboard = scorer.get_leaderboard()
        
        for i, (model, stats) in enumerate(leaderboard, 1):
            wins = stats["wins"]
            losses = stats["losses"]
            draws = stats["draws"]
            points = stats["points"]
            win_rate = stats["win_rate"]
            
            print(f"{i:2d}. {model:15s} | {points:3d}pts | {wins:2d}W-{losses:2d}L-{draws:2d}D | {win_rate:.1%}")
    
    def _display_final_results(self, scorer: TournamentScorer, tournament_type: str) -> None:
        """Display final tournament results.
        
        Args:
            scorer: Tournament scorer instance
            tournament_type: Type of tournament
        """
        print("\n" + "=" * 60)
        print(f"🏆 {tournament_type.upper()} TOURNAMENT RESULTS")
        print("=" * 60)
        
        leaderboard = scorer.get_leaderboard()
        champion = leaderboard[0][0] if leaderboard else "Unknown"
        
        print(f"🥇 CHAMPION: {champion}")
        print("\n📊 Final Standings:")
        print("-" * 60)
        
        for i, (model, stats) in enumerate(leaderboard, 1):
            wins = stats["wins"]
            losses = stats["losses"]
            draws = stats["draws"]
            matches = stats["matches_played"]
            points = stats["points"]
            win_rate = stats["win_rate"]
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{medal} {i:2d}. {model:15s} | {points:3d} pts | {wins:2d}-{losses:2d}-{draws:2d} | {win_rate:.1%} | {matches} matches")
        
        print("=" * 60) 