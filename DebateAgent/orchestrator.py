"""
Main orchestrator for the multi-agent debate system.
This script guides the user through setting up and running a debate between LLM agents.
"""

import json
import os
import platform
import random
import time
from datetime import datetime
from typing import Dict, Any, List

from agents import DebateAgent, JudgeAgent
from config import DEFAULT_MODEL, DEFAULT_TEMP, DEFAULT_SEED
from prompts import (
    DEBATE_AGENT_SYSTEM_PROMPT, 
    OPENING_STATEMENT_PROMPT, 
    DEBATE_RESPONSE_PROMPT
)
from topics import get_topic, list_topics, list_topic_keys


def now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.utcnow().isoformat()


class JsonLogger:
    """Simple JSONL logger that appends records with timestamps."""
    def __init__(self, path: str) -> None:
        self.path = path
        
    def log(self, record: Dict[str, Any]) -> None:
        timestamped_record = {"timestamp": now_iso(), **record}
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(timestamped_record) + '\n')


def get_user_config() -> Dict[str, Any]:
    """
    Interactively prompt the user to configure the debate settings.
    """
    print("Welcome to the Multi-Agent Debate System!")
    print("=" * 50)
    
    # 1. Choose topic
    list_topics()
    topic_keys = list_topic_keys()
    while True:
        topic_key = input(f"Choose a topic key from the list: ")
        if topic_key in topic_keys:
            break
        print(f"Invalid topic key. Please choose from: {', '.join(topic_keys)}")
    
    # 2. Number of agents
    while True:
        try:
            num_agents = int(input("Enter the number of debate agents (e.g., 2 or 3): "))
            if num_agents > 1:
                break
            print("You need at least 2 agents to have a debate.")
        except ValueError:
            print("Please enter a valid number.")

    # 3. Number of rounds
    while True:
        try:
            rounds = int(input("Enter the number of debate rounds (e.g., 3 or 5): "))
            if rounds > 0:
                break
            print("You need at least 1 round.")
        except ValueError:
            print("Please enter a valid number.")
            
    # 4. Models and Stances
    agent_models = []
    stances = []
    print("\nDefine each agent's model and stance on the topic.")
    for i in range(num_agents):
        print(f"\n--- Agent {i} ---")
        model = input(f"Enter Ollama model for Agent {i} (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
        stance = input(f"Enter stance for Agent {i} (e.g., 'For', 'Against', 'Neutral', 'Skeptical'): ")
        agent_models.append(model)
        stances.append(stance)

    judge_model = input(f"\nEnter the Ollama model for the judge (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    
    return {
        "topic_key": topic_key,
        "num_agents": num_agents,
        "rounds": rounds,
        "agent_models": agent_models,
        "judge_model": judge_model,
        "stances": stances,
        "temp": DEFAULT_TEMP,
        "seed": DEFAULT_SEED
    }


def create_results_folder(topic: str, num_agents: int, rounds: int, models: List[str]) -> str:
    """Create a timestamped results folder for this debate run."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_results_dir = os.path.join(current_dir, "results")
    os.makedirs(base_results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')[:50]
    
    # Create a model string for the folder name
    unique_models = sorted(list(set(models)))
    if len(unique_models) == 1:
        model_str = unique_models[0].replace(":", "_") # Clean up model name for folder
    else:
        model_str = "multi-model"

    folder_name = f"{timestamp}_{num_agents}agents_{rounds}rounds_{model_str}_{clean_topic}"
    results_folder = os.path.join(base_results_dir, folder_name)
    
    os.makedirs(results_folder, exist_ok=True)
    return results_folder


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load records from a JSONL file."""
    records = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


def run_debate(config: Dict[str, Any]) -> None:
    """Run a multi-agent debate based on the provided configuration."""
    start_time = time.time()
    
    # Unpack config
    topic_key = config["topic_key"]
    topic_question = get_topic(topic_key)
    num_agents = config["num_agents"]
    rounds = config["rounds"]
    agent_models = config["agent_models"]
    judge_model = config["judge_model"]
    stances = config["stances"]
    temp = config["temp"]
    seed = config["seed"]
    
    # Setup results directory and logger
    results_folder = create_results_folder(topic_key, num_agents, rounds, agent_models)
    transcript_path = os.path.join(results_folder, "transcript.jsonl")
    metadata_path = os.path.join(results_folder, "metadata.json")
    logger = JsonLogger(transcript_path)

    # Log debate metadata
    logger.log({
        "event": "debate_start",
        "config": config,
        "topic_question": topic_question
    })
    
    # Initialize agents
    agents = [DebateAgent(i, agent_models[i], temp, seed + i) for i in range(num_agents)]
    judge = JudgeAgent(judge_model, temp, seed + 1000)
    
    agent_model_names = ", ".join(agent_models)
    print("\n" + "=" * 60)
    print(f"Starting Debate On: {topic_question}")
    print(f"Agents: {num_agents} ({agent_model_names}) | Rounds: {rounds} | Judge: {judge_model}")
    print("=" * 60 + "\n")

    # --- OPENING STATEMENTS ---
    print("--- OPENING STATEMENTS ---")
    for i, agent in enumerate(agents):
        system_prompt = DEBATE_AGENT_SYSTEM_PROMPT.format(topic=topic_question, stance=stances[i])
        full_prompt = f"{system_prompt}\n\n{OPENING_STATEMENT_PROMPT}"
        
        response = agent.respond(full_prompt)
        logger.log({"round": 0, "agent": i, "stance": stances[i], "model": agent_models[i], "message": response, "type": "opening_statement"})
        print(f"Agent {i} ({stances[i]}, {agent_models[i]}): {response}\n")
    
    # --- DEBATE ROUNDS ---
    for round_num in range(1, rounds + 1):
        print(f"\n--- ROUND {round_num} ---")
        
        for i, agent in enumerate(agents):
            # Get previous messages from all agents in the last round (or opening statements)
            previous_messages = []
            current_transcripts = load_jsonl(transcript_path)
            
            for record in current_transcripts:
                if record.get("round") == round_num - 1:
                    msg = f"Agent {record['agent']} ({record['stance']}, {record['model']}): {record['message']}"
                    previous_messages.append(msg)

            previous_statements = "\n\n".join(previous_messages)
            
            system_prompt = DEBATE_AGENT_SYSTEM_PROMPT.format(topic=topic_question, stance=stances[i])
            response_prompt = DEBATE_RESPONSE_PROMPT.format(previous_statements=previous_statements)
            full_prompt = f"{system_prompt}\n\n{response_prompt}"
            
            response = agent.respond(full_prompt)
            logger.log({"round": round_num, "agent": i, "stance": stances[i], "model": agent_models[i], "message": response, "type": "debate_response"})
            print(f"Agent {i} ({stances[i]}, {agent_models[i]}): {response}\n")

    # --- JUDGING PHASE ---
    print("\n" + "=" * 60)
    print("--- JUDGING ---")
    transcripts = load_jsonl(transcript_path)
    winner_id, justification = judge.pick_winner(transcripts)
    
    logger.log({"event": "verdict", "winner": winner_id, "justification": justification})
    
    print(f"WINNER: Agent {winner_id}")
    print(f"Justification: {justification}")
    
    # --- SAVE METADATA ---
    duration_seconds = time.time() - start_time
    metadata = {
        "debate_config": config,
        "topic_question": topic_question,
        "timing": {
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": round(duration_seconds, 2)
        },
        "results": {
            "winner": winner_id,
            "justification": justification,
            "transcript_file": os.path.basename(transcript_path)
        },
        "system_info": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        }
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)
        
    print("\n" + "=" * 60)
    print(f"Debate finished. Results saved in: {results_folder}")
    print(f"  - Transcript: {os.path.basename(transcript_path)}")
    print(f"  - Metadata: {os.path.basename(metadata_path)}")


if __name__ == "__main__":
    debate_configuration = get_user_config()
    run_debate(debate_configuration) 