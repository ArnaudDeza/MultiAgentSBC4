"""
Main orchestrator for the multi-agent press conference system.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

from agents import (
    SpokespersonAgent, JournalistAgent, NoteTakerAgent, SummarizerAgent
)
from config import DEFAULT_MODEL, DEFAULT_TEMP, DEFAULT_SEED
from event_scenarios import list_events, get_event, list_event_keys


class JsonLogger:
    """Simple JSONL logger."""
    def __init__(self, path: str):
        self.path = path
    def log(self, record: Dict[str, Any]):
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), **record}) + '\n')

def get_user_config() -> Dict[str, Any]:
    """Interactively get press conference settings from the user."""
    print("Welcome to the Multi-Agent Press Conference Simulator!")
    print("=" * 60)
    
    list_events()
    event_keys = list_event_keys()
    while True:
        event_key = input("Choose an event key from the list: ")
        if event_key in event_keys:
            break
        print(f"Invalid key. Please choose from: {', '.join(event_keys)}")
    
    while True:
        try:
            num_journalists = int(input("Enter the number of journalists (e.g., 2 or 3): "))
            if num_journalists > 0:
                break
        except ValueError:
            print("Please enter a valid number.")

    journalists = []
    print("\nDefine each journalist's model and bias.")
    for i in range(num_journalists):
        print(f"\n--- Journalist {i} ---")
        model = input(f"Enter model for Journalist {i} (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
        bias = input(f"Enter bias for Journalist {i} (e.g., 'left-leaning', 'right-leaning', 'neutral'): ")
        journalists.append({"model": model, "bias": bias})

    print("\n--- Other Agents ---")
    spokesperson_model = input(f"Enter model for Spokesperson (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    notetaker_model = input(f"Enter model for Note-Taker (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    summarizer_model = input(f"Enter model for Summarizer (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    
    while True:
        try:
            rounds = int(input("\nEnter number of question rounds (1 question per journalist per round): "))
            if rounds > 0:
                break
        except ValueError:
            print("Please enter a valid number.")

    return {
        "event_key": event_key,
        "journalists": journalists,
        "spokesperson_model": spokesperson_model,
        "notetaker_model": notetaker_model,
        "summarizer_model": summarizer_model,
        "rounds": rounds,
        "temp": DEFAULT_TEMP,
        "seed": DEFAULT_SEED,
    }

def create_results_folder(event_key: str, num_journalists: int) -> str:
    """Create a timestamped results folder."""
    base_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(base_dir, exist_ok=True)
    folder_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_key}_{num_journalists}journalists"
    results_folder = os.path.join(base_dir, folder_name)
    os.makedirs(results_folder, exist_ok=True)
    return results_folder

def format_transcript(log_records: List[Dict[str, Any]]) -> str:
    """Formats the log records into a readable string transcript."""
    lines = []
    for record in log_records:
        role = record.get("role", "System")
        message = record.get("message", "")
        lines.append(f"{role}: {message}")
    return "\n\n".join(lines)

def run_press_conference(config: Dict[str, Any]):
    """Main function to run the simulation."""
    start_time = time.time()
    event = get_event(config["event_key"])
    results_folder = create_results_folder(config["event_key"], len(config["journalists"]))
    
    transcript_path = os.path.join(results_folder, "transcript.jsonl")
    metadata_path = os.path.join(results_folder, "metadata.json")
    minutes_path = os.path.join(results_folder, "minutes.txt")
    summary_path = os.path.join(results_folder, "summary.txt")
    
    logger = JsonLogger(transcript_path)
    logger.log({"event": "conference_start", "config": config, "event_details": event})
    
    # Initialize Agents
    spokesperson = SpokespersonAgent(config["spokesperson_model"], config["temp"], config["seed"])
    journalists = [
        JournalistAgent(j["model"], config["temp"], config["seed"] + i + 1, j["bias"])
        for i, j in enumerate(config["journalists"])
    ]
    note_taker = NoteTakerAgent(config["notetaker_model"], config["temp"], config["seed"] + 100)
    summarizer = SummarizerAgent(config["summarizer_model"], config["temp"], config["seed"] + 200)

    print("\n" + "="*60)
    print(f"Starting Press Conference: {event['title']}")
    print("="*60 + "\n")

    # 1. Opening Statement
    print("--- Spokesperson's Opening Statement ---")
    opening_statement = spokesperson.generate_opening_statement(event["details"])
    print(opening_statement)
    logger.log({"role": "Spokesperson", "message": opening_statement, "type": "opening_statement"})
    
    # 2. Q&A Rounds
    for r in range(config["rounds"]):
        print(f"\n--- Question Round {r+1} ---")
        for i, journalist in enumerate(journalists):
            transcript_str = format_transcript(logger.log_records)
            
            # Journalist asks
            print(f"\nJournalist {i} ({journalist.bias}, {journalist.model}) is asking...")
            question = journalist.generate_question(transcript_str)
            print(f"Question: {question}")
            logger.log({"role": f"Journalist {i}", "bias": journalist.bias, "model": journalist.model, "message": question, "type": "question"})
            
            # Spokesperson responds
            transcript_str = format_transcript(logger.log_records) # Update transcript
            print("\nSpokesperson is responding...")
            response = spokesperson.generate_response(event["details"], transcript_str, question)
            print(f"Response: {response}")
            logger.log({"role": "Spokesperson", "message": response, "type": "answer"})

    # 3. Note-Taker generates minutes
    print("\n" + "="*60)
    print("--- Generating Meeting Minutes ---")
    transcript_str = format_transcript(logger.log_records)
    minutes = note_taker.generate_minutes(transcript_str)
    print(minutes)
    logger.log({"role": "Note-Taker", "message": minutes, "type": "minutes"})
    with open(minutes_path, 'w', encoding='utf-8') as f:
        f.write(minutes)

    # 4. Summarizer generates summary
    print("\n" + "="*60)
    print("--- Generating Final Summary ---")
    summary = summarizer.generate_summary(minutes)
    print(summary)
    logger.log({"role": "Summarizer", "message": summary, "type": "summary"})
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    # 5. Save final metadata
    duration = time.time() - start_time
    final_metadata = {
        "config": config,
        "event": event,
        "timing": {"duration_seconds": round(duration, 2)},
        "files": {
            "transcript": os.path.basename(transcript_path),
            "metadata": os.path.basename(metadata_path),
            "minutes": os.path.basename(minutes_path),
            "summary": os.path.basename(summary_path),
        }
    }
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, indent=4)
        
    print("\n" + "="*60)
    print(f"Press conference finished. Results saved in: {results_folder}")

# Add a simple in-memory log for transcript formatting
def add_in_memory_logging(logger_class):
    original_init = logger_class.__init__
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.log_records = []
    logger_class.__init__ = new_init

    original_log = logger_class.log
    def new_log(self, record: Dict[str, Any]):
        self.log_records.append(record)
        original_log(self, record)
    logger_class.log = new_log
    return logger_class

if __name__ == "__main__":
    JsonLogger = add_in_memory_logging(JsonLogger)
    user_config = get_user_config()
    run_press_conference(user_config) 