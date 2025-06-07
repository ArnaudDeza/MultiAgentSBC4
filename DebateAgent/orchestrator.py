"""
Main orchestrator for multi-agent debate system.
"""

import argparse
import random
import json
from typing import List, Dict, Any

from config import (
    DEFAULT_MODEL, DEFAULT_TEMP, DEFAULT_NUM_AGENTS, 
    DEFAULT_ROUNDS, DEFAULT_SEED, DEFAULT_OUTPUT
)
from utils import JsonLogger
from agents import DebateAgent, JudgeAgent


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load records from a JSONL file."""
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except FileNotFoundError:
        pass  # File doesn't exist yet
    return records


def run_debate(
    topic: str,
    num_agents: int,
    rounds: int,
    model: str,
    temp: float,
    seed: int,
    output: str
) -> None:
    """
    Run a multi-agent debate on the given topic.
    
    Args:
        topic: Debate topic
        num_agents: Number of debate agents
        rounds: Number of debate rounds
        model: Ollama model to use
        temp: Temperature for generation
        seed: Random seed
        output: Output file path
    """
    # Set random seed
    random.seed(seed)
    
    # Initialize logger
    logger = JsonLogger(output)
    
    # Log debate start
    logger.log({
        "event": "debate_start",
        "topic": topic,
        "num_agents": num_agents,
        "rounds": rounds,
        "model": model,
        "temperature": temp,
        "seed": seed
    })
    
    # Create debate agents
    agents = []
    for i in range(num_agents):
        agent = DebateAgent(
            agent_id=i,
            model=model,
            temp=temp,
            seed=seed + i  # Different seed for each agent
        )
        agents.append(agent)
    
    print(f"Starting debate on topic: {topic}")
    print(f"Agents: {num_agents}, Rounds: {rounds}, Model: {model}")
    print("=" * 60)
    
    # Opening statements
    print("OPENING STATEMENTS:")
    for i, agent in enumerate(agents):
        prompt = f"Please introduce your position on this topic: {topic}. Be clear and concise in your opening statement."
        response = agent.respond(prompt)
        
        logger.log({
            "round": 0,
            "agent": i,
            "message": response,
            "type": "opening_statement"
        })
        
        print(f"Agent {i}: {response[:200]}{'...' if len(response) > 200 else ''}")
        print()
    
    print("=" * 60)
    
    # Main debate rounds
    for round_num in range(1, rounds + 1):
        print(f"ROUND {round_num}:")
        
        for i, agent in enumerate(agents):
            # Gather last messages from other agents
            last_messages = []
            current_transcripts = load_jsonl(output)
            
            # Get the most recent message from each other agent
            other_agents_latest = {}
            for record in reversed(current_transcripts):
                if (record.get('agent') is not None and 
                    record['agent'] != i and 
                    record['agent'] not in other_agents_latest):
                    other_agents_latest[record['agent']] = record.get('message', '')
            
            # Build combined prompt
            if other_agents_latest:
                others_combined = "\n\n".join([
                    f"Agent {agent_id}: {msg}" 
                    for agent_id, msg in sorted(other_agents_latest.items())
                ])
                prompt = f"Round {round_num}: Respond to these statements from other agents:\n\n{others_combined}\n\nYour response:"
            else:
                prompt = f"Round {round_num}: Continue the debate on {topic}. Present your arguments clearly."
            
            response = agent.respond(prompt)
            
            logger.log({
                "round": round_num,
                "agent": i,
                "message": response,
                "type": "debate_response"
            })
            
            print(f"Agent {i}: {response[:200]}{'...' if len(response) > 200 else ''}")
            print()
        
        print("-" * 40)
    
    print("=" * 60)
    print("JUDGING PHASE:")
    
    # Load full transcript for judging
    transcripts = load_jsonl(output)
    
    # Create judge and pick winner
    judge = JudgeAgent(model=model, temp=temp, seed=seed + 1000)
    winner_letter, justification = judge.pick_winner(transcripts)
    
    # Log verdict
    verdict = {
        "event": "verdict",
        "winner": winner_letter,
        "justification": justification
    }
    logger.log(verdict)
    
    print(f"WINNER: Agent {winner_letter}")
    print(f"Justification: {justification}")
    print(f"\nFull debate log saved to: {output}")


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Multi-agent debate system")
    
    parser.add_argument(
        "--topic",
        type=str,
        default="The benefits and drawbacks of artificial intelligence in education",
        help="Debate topic"
    )
    parser.add_argument(
        "--num_agents",
        type=int,
        default=DEFAULT_NUM_AGENTS,
        help=f"Number of debate agents (default: {DEFAULT_NUM_AGENTS})"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        help=f"Number of debate rounds (default: {DEFAULT_ROUNDS})"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=DEFAULT_TEMP,
        help=f"Temperature for generation (default: {DEFAULT_TEMP})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Output JSONL file (default: {DEFAULT_OUTPUT})"
    )
    
    args = parser.parse_args()
    
    run_debate(
        topic=args.topic,
        num_agents=args.num_agents,
        rounds=args.rounds,
        model=args.model,
        temp=args.temp,
        seed=args.seed,
        output=args.output
    )


if __name__ == "__main__":
    main() 