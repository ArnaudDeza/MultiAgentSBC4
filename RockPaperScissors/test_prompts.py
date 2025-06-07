#!/usr/bin/env python3
"""Test script to demonstrate the detailed LLM prompts for Rock Paper Scissors."""

from agents import PlayerAgent
from utils import Move

def test_prompt_evolution():
    """Demonstrate how prompts evolve as match history builds up."""
    
    print("🎮 ROCK PAPER SCISSORS PROMPT DEMONSTRATION")
    print("=" * 80)
    print()
    print("This shows exactly what information LLMs receive during a match.")
    print("Each match consists of multiple rounds, with complete history provided each time.")
    print()
    
    # Create a test agent
    agent = PlayerAgent(model="test-model", name="TestAgent")
    
    # Simulate a match progression
    test_scenarios = [
        {
            "round": 1,
            "own_history": [],
            "opponent_history": [],
            "description": "First round - no history available"
        },
        {
            "round": 2,
            "own_history": [Move.ROCK],
            "opponent_history": [Move.PAPER],
            "description": "Second round - one previous round"
        },
        {
            "round": 5,
            "own_history": [Move.ROCK, Move.PAPER, Move.SCISSORS, Move.ROCK],
            "opponent_history": [Move.PAPER, Move.ROCK, Move.ROCK, Move.SCISSORS],
            "description": "Fifth round - pattern analysis available"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} SCENARIO {i}: {scenario['description'].upper()} {'='*20}")
        print()
        
        # Generate the prompt
        prompt = agent._create_move_prompt(
            scenario["round"],
            scenario["opponent_history"],
            scenario["own_history"]
        )
        
        print(prompt)
        print("\n" + "="*80)
        
        if i < len(test_scenarios):
            input("\nPress Enter to see the next scenario...")

def demonstrate_match_structure():
    """Explain the overall match structure."""
    
    print("\n🏆 TOURNAMENT STRUCTURE EXPLANATION")
    print("=" * 80)
    
    explanation = """
TOURNAMENT HIERARCHY:
├── Tournament (multiple matches between different agent pairs)
│   ├── Match 1: Agent A vs Agent B (best of N rounds)
│   │   ├── Round 1: Both agents get empty history, choose moves
│   │   ├── Round 2: Both agents get Round 1 history, choose moves  
│   │   ├── Round 3: Both agents get Rounds 1-2 history, choose moves
│   │   └── ... (continue for N rounds)
│   ├── Match 2: Agent A vs Agent C (best of N rounds)
│   └── ... (all possible pairings or bracket progression)

KEY POINTS:
1. Each MATCH consists of multiple ROUNDS (typically 10-20)
2. Each ROUND, both LLMs receive:
   - Complete history of their own moves in this match
   - Complete history of opponent's moves in this match
   - Current round number
   - Detailed analysis (frequencies, patterns, current score)

3. Match winner determined by who wins more rounds
4. Tournament winner determined by overall performance across matches

EXAMPLE MATCH FLOW:
Round 1: phi3=rock     vs llama2=paper    → llama2 wins round
Round 2: phi3=scissors vs llama2=rock     → llama2 wins round  
Round 3: phi3=paper    vs llama2=rock     → phi3 wins round
...
Final:   phi3 wins 6/10 rounds → phi3 wins the match
    """
    
    print(explanation)

if __name__ == "__main__":
    test_prompt_evolution()
    demonstrate_match_structure()
    
    print("\n🎯 SUMMARY:")
    print("The LLMs receive rich, detailed prompts with:")
    print("• Complete round-by-round match history")
    print("• Move frequency analysis") 
    print("• Pattern detection")
    print("• Current match score")
    print("• Strategic context and clear instructions")
    print("\nThis enables sophisticated strategic play beyond random choices!") 