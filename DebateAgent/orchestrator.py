"""
Main orchestrator for multi-agent debate system.
"""

import argparse
import random
import json
import os
import platform
import time
from datetime import datetime
from typing import List, Dict, Any

from config import (
    DEFAULT_MODEL, DEFAULT_TEMP, DEFAULT_NUM_AGENTS, 
    DEFAULT_ROUNDS, DEFAULT_SEED, DEFAULT_OUTPUT
)
from utils import JsonLogger
from agents import DebateAgent, JudgeAgent
from topics import get_topic, list_topics, list_topic_keys, DEBATE_TOPICS


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


def create_results_folder(topic: str, num_agents: int, rounds: int, model: str) -> str:
    """
    Create a timestamped results folder for this debate run.
    
    Args:
        topic: Debate topic
        num_agents: Number of agents
        rounds: Number of rounds
        model: Model name
        
    Returns:
        Path to the created results folder
    """
    # Create base results directory
    base_results_dir = "results"
    os.makedirs(base_results_dir, exist_ok=True)
    
    # Create timestamped folder name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean topic for folder name (remove special characters)
    clean_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_topic = clean_topic.replace(' ', '_')[:50]  # Limit length
    
    folder_name = f"{timestamp}_{num_agents}agents_{rounds}rounds_{model}_{clean_topic}"
    results_folder = os.path.join(base_results_dir, folder_name)
    
    os.makedirs(results_folder, exist_ok=True)
    return results_folder


def collect_system_metadata() -> Dict[str, Any]:
    """Collect system and environment metadata."""
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        cpu_count = os.cpu_count()
        memory_gb = "unknown"
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": cpu_count,
            "memory_gb": memory_gb,
            "hostname": platform.node()
        },
        "environment": {
            "working_directory": os.getcwd(),
            "user": os.getenv('USER', 'unknown')
        }
    }


def run_debate(
    topic: str,
    num_agents: int,
    rounds: int,
    model: str,
    temp: float,
    seed: int,
    output: str = None
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
        output: Output file path (if None, creates timestamped folder)
    """
    # Record start time
    start_time = time.time()
    start_datetime = datetime.now()
    
    # Create results folder if output not specified
    if output is None:
        results_folder = create_results_folder(topic, num_agents, rounds, model)
        transcript_path = os.path.join(results_folder, "transcript.jsonl")
        metadata_path = os.path.join(results_folder, "metadata.json")
    else:
        # Use specified output path
        if os.path.dirname(output):
            os.makedirs(os.path.dirname(output), exist_ok=True)
        transcript_path = output
        metadata_path = output.replace('.jsonl', '_metadata.json')
        results_folder = os.path.dirname(output) or "."
    
    # Set random seed
    random.seed(seed)
    
    # Initialize logger
    logger = JsonLogger(transcript_path)
    
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
            current_transcripts = load_jsonl(transcript_path)
            
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
    transcripts = load_jsonl(transcript_path)
    
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
    
    # Record end time and calculate duration
    end_time = time.time()
    end_datetime = datetime.now()
    duration_seconds = end_time - start_time
    
    # Collect system metadata
    system_metadata = collect_system_metadata()
    
    # Create comprehensive metadata
    metadata = {
        "debate_info": {
            "topic": topic,
            "num_agents": num_agents,
            "rounds": rounds,
            "model": model,
            "temperature": temp,
            "seed": seed
        },
        "timing": {
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "duration_seconds": round(duration_seconds, 2),
            "duration_human": f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s"
        },
        "results": {
            "winner": winner_letter,
            "justification": justification,
            "total_messages": len(transcripts),
            "transcript_file": os.path.basename(transcript_path)
        },
        "files": {
            "transcript": os.path.basename(transcript_path),
            "metadata": os.path.basename(metadata_path),
            "results_folder": os.path.basename(results_folder)
        },
        **system_metadata
    }
    
    # Save metadata to JSON file
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"WINNER: Agent {winner_letter}")
    print(f"Justification: {justification}")
    print(f"\nResults saved to: {results_folder}")
    print(f"  - Transcript: {os.path.basename(transcript_path)}")
    print(f"  - Metadata: {os.path.basename(metadata_path)}")
    print(f"  - Duration: {metadata['timing']['duration_human']}")


def resolve_topic(topic_input: str) -> str:
    """
    Resolve topic input to actual topic question.
    
    Args:
        topic_input: Either a topic key or a custom topic question
        
    Returns:
        The resolved topic question
    """
    # First, check if it's a predefined topic key
    predefined_topic = get_topic(topic_input)
    if predefined_topic:
        print(f"Using predefined topic '{topic_input}': {predefined_topic}")
        return predefined_topic
    else:
        # Use as custom topic
        print(f"Using custom topic: {topic_input}")
        return topic_input


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Multi-agent debate system",
        epilog="Examples:\n"
               "  python orchestrator.py --topic ai_education  # Use predefined topic\n"
               "  python orchestrator.py --topic 'Should cats rule the world?'  # Custom topic\n"
               "  python orchestrator.py --list-topics  # Show all predefined topics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        default="ai_education",
        help="Debate topic (can be a predefined topic key or custom question)"
    )
    
    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="List all available predefined topics and exit"
    )
    
    parser.add_argument(
        "--list-keys",
        action="store_true", 
        help="List just the topic keys and exit"
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
        default=None,
        help="Output JSONL file (default: auto-generated timestamped folder)"
    )
    
    args = parser.parse_args()
    
    # Handle list commands
    if args.list_topics:
        list_topics()
        return
    
    if args.list_keys:
        list_topic_keys()
        return
    
    # Resolve the topic
    resolved_topic = resolve_topic(args.topic)
    
    run_debate(
        topic=resolved_topic,
        num_agents=args.num_agents,
        rounds=args.rounds,
        model=args.model,
        temp=args.temp,
        seed=args.seed,
        output=args.output
    )


if __name__ == "__main__":
    main() 