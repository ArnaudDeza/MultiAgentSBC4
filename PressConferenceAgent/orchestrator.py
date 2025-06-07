"""Main orchestrator for the simulated press conference."""

import argparse
import json
import random
import sys
from typing import List, Dict, Any

import config
from utils import JsonLogger
from agents import SpokespersonAgent, JournalistAgent, NoteTakerAgent


def load_transcript(output_file: str) -> List[Dict[str, Any]]:
    """Load the transcript from the output JSONL file.
    
    Args:
        output_file: Path to the JSONL file containing the transcript
        
    Returns:
        List of records from the transcript
    """
    records = []
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except FileNotFoundError:
        print(f"Warning: Output file {output_file} not found")
    return records


def run_press_conference(num_journalists: int, model: str, temp: float, seed: int, 
                        topic: str, output: str) -> None:
    """Run the complete press conference simulation.
    
    Args:
        num_journalists: Number of journalists to simulate
        model: Ollama model name to use
        temp: Temperature setting for text generation
        seed: Random seed for reproducibility
        topic: Topic for the press conference
        output: Output file path for the transcript
    """
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Initialize logger
    logger = JsonLogger(output)
    
    # Initialize agents
    spokesperson = SpokespersonAgent(model, temp, seed)
    journalists = [JournalistAgent(i, model, temp, seed + i) for i in range(num_journalists)]
    note_taker = NoteTakerAgent(model, temp, seed)
    
    print(f"🎤 Starting Press Conference on: {topic}")
    print(f"📊 Model: {model}, Temperature: {temp}, Seed: {seed}")
    print(f"👥 Number of journalists: {num_journalists}")
    print(f"📝 Logging to: {output}")
    print("=" * 60)
    
    try:
        # Opening statement
        print("📢 Generating opening statement...")
        statement = spokesperson.opening_statement(topic)
        logger.log({"type": "opening", "text": statement})
        print(f"Spokesperson: {statement}\n")
        
        # Q&A Loop
        print("❓ Starting Q&A session...")
        for j in journalists:
            print(f"Journalist {j.id} asking question...")
            
            # Journalist asks question
            question = j.ask_question(statement)
            logger.log({"type": "question", "journalist": j.id, "text": question})
            print(f"Journalist {j.id}: {question}")
            
            # Spokesperson answers
            answer = spokesperson.answer_question(question)
            logger.log({"type": "answer", "journalist": j.id, "text": answer})
            print(f"Spokesperson: {answer}\n")
        
        # Generate summary
        print("📋 Generating meeting minutes...")
        transcript = load_transcript(output)
        minutes = note_taker.summarize(transcript)
        logger.log({"type": "minutes", "text": minutes})
        
        print("=" * 60)
        print("📋 PRESS CONFERENCE MINUTES:")
        print("=" * 60)
        print(minutes)
        print("=" * 60)
        print(f"✅ Complete transcript saved to: {output}")
        
    except Exception as e:
        print(f"❌ Error during press conference: {e}")
        # Retry once with a different seed
        try:
            print("🔄 Retrying with adjusted parameters...")
            run_press_conference(num_journalists, model, temp, seed + 1000, topic, output)
        except Exception as retry_e:
            print(f"❌ Retry failed: {retry_e}")
            sys.exit(1)


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Simulated Press Conference with Multiple Agents")
    
    parser.add_argument("--num_journalists", type=int, default=config.DEFAULT_NUM_JOURNALISTS,
                       help=f"Number of journalists (default: {config.DEFAULT_NUM_JOURNALISTS})")
    parser.add_argument("--model", type=str, default=config.DEFAULT_MODEL,
                       help=f"Ollama model to use (default: {config.DEFAULT_MODEL})")
    parser.add_argument("--temp", type=float, default=config.DEFAULT_TEMP,
                       help=f"Temperature for text generation (default: {config.DEFAULT_TEMP})")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED,
                       help=f"Random seed (default: {config.DEFAULT_SEED})")
    parser.add_argument("--topic", type=str, default="Technology Innovation",
                       help="Topic for the press conference (default: 'Technology Innovation')")
    parser.add_argument("--output", type=str, default=config.DEFAULT_OUTPUT,
                       help=f"Output JSONL file (default: {config.DEFAULT_OUTPUT})")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.num_journalists < 1:
        print("❌ Error: Number of journalists must be at least 1")
        sys.exit(1)
    
    if args.temp < 0 or args.temp > 2:
        print("❌ Error: Temperature must be between 0 and 2")
        sys.exit(1)
    
    # Run the press conference
    run_press_conference(
        num_journalists=args.num_journalists,
        model=args.model,
        temp=args.temp,
        seed=args.seed,
        topic=args.topic,
        output=args.output
    )


if __name__ == "__main__":
    main() 