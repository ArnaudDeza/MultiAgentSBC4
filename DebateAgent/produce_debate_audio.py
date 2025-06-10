"""
Generate an audio recording of a debate from its transcript file.

This script reads the transcript.jsonl and metadata.json from a debate
results folder, compiles a script, and uses gTTS (Google Text-to-Speech)
to create an MP3 audio file of the debate.
"""

import argparse
import json
import os
import sys

try:
    from gtts import gTTS
except ImportError:
    print("Error: The gTTS library is not installed.")
    print("Please install it by running: pip install gTTS")
    sys.exit(1)


def load_jsonl(file_path: str) -> list:
    """Load records from a JSONL file."""
    records = []
    if not os.path.exists(file_path):
        print(f"Error: Transcript file not found at {file_path}")
        return records
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_json(file_path: str) -> dict:
    """Load a standard JSON file."""
    if not os.path.exists(file_path):
        print(f"Error: Metadata file not found at {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_debate_script(transcript: list, metadata: dict) -> str:
    """
    Create a formatted string script of the entire debate for TTS.
    """
    script_lines = []
    
    # Introduction
    topic = metadata.get("topic_question", "an unknown topic")
    num_agents = metadata.get("debate_config", {}).get("num_agents", "several")
    rounds = metadata.get("debate_config", {}).get("rounds", "several")
    
    intro = f"Welcome to the debate. Today, {num_agents} agents will debate for {rounds} rounds on the topic: {topic}"
    script_lines.append(intro)
    script_lines.append("Let's begin with the opening statements.")

    # Process debate rounds
    last_round = -1
    for record in transcript:
        event_type = record.get("type")
        if event_type in ["opening_statement", "debate_response"]:
            round_num = record.get("round")
            
            # Announce new round
            if round_num != last_round:
                if round_num == 0:
                    pass # Already announced opening statements
                else:
                    script_lines.append(f"Now, for round {round_num}.")
                last_round = round_num

            agent_id = record.get('agent')
            stance = record.get('stance')
            model = record.get('model')
            message = record.get('message')
            
            line = f"Agent {agent_id}, using model {model}, arguing '{stance}', says: {message}"
            script_lines.append(line)
            
    # Verdict
    verdict_record = next((r for r in transcript if r.get("event") == "verdict"), None)
    if verdict_record:
        winner = verdict_record.get("winner")
        justification = verdict_record.get("justification")
        
        script_lines.append("The debate has concluded. The judge will now deliver the verdict.")
        script_lines.append(f"The winner is Agent {winner}.")
        script_lines.append(f"The judge's justification is as follows: {justification}")
    
    return "\n\n".join(script_lines)


def main():
    """Main function to parse arguments and generate the audio file."""
    parser = argparse.ArgumentParser(
        description="Generate a TTS audio file from a debate transcript.",
        epilog="Example: python produce_debate_audio.py results/20231027_103000_2agents_3rounds_phi4_pineapple_pizza"
    )
    parser.add_argument(
        "debate_folder",
        type=str,
        help="Path to the debate results folder containing transcript.jsonl and metadata.json."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.debate_folder):
        print(f"Error: The specified directory does not exist: {args.debate_folder}")
        sys.exit(1)

    # Define file paths
    transcript_file = os.path.join(args.debate_folder, "transcript.jsonl")
    metadata_file = os.path.join(args.debate_folder, "metadata.json")
    output_audio_file = os.path.join(args.debate_folder, "debate_audio.mp3")

    # Load data
    print("Loading debate data...")
    transcript_data = load_jsonl(transcript_file)
    metadata = load_json(metadata_file)

    if not transcript_data or not metadata:
        print("Could not load necessary files. Aborting.")
        sys.exit(1)

    # Create script
    print("Generating debate script...")
    debate_script = create_debate_script(transcript_data, metadata)
    
    # Generate audio
    print("Generating audio using gTTS. This may take a moment...")
    try:
        tts = gTTS(text=debate_script, lang='en', slow=False)
        tts.save(output_audio_file)
        print(f"\nSuccessfully saved debate audio to: {output_audio_file}")
    except Exception as e:
        print(f"\nAn error occurred while generating the audio file: {e}")
        print("Please check your internet connection, as gTTS requires it.")


if __name__ == "__main__":
    main() 