"""
Generate an audio recording of a negotiation from its transcript.
"""

import argparse
import json
import os
import sys

try:
    from gtts import gTTS
except ImportError:
    print("Error: gTTS library not found. Please run 'pip install gTTS'.", file=sys.stderr)
    sys.exit(1)

def load_jsonl(file_path: str) -> list:
    """Load records from a JSONL file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def create_negotiation_script(transcript: list) -> str:
    """Create a formatted string script of the negotiation for TTS."""
    script_lines = []
    
    scenario_name = transcript[0].get("scenario", {}).get("name", "an unknown location")
    item_name = transcript[0].get("scenario", {}).get("item_name", "an item")
    intro = f"Welcome. Let's listen in on a negotiation for {item_name} at {scenario_name}."
    script_lines.append(intro)

    for record in transcript:
        role = record.get("role", "")
        msg = record.get("message", "")
        line = ""
        
        if record.get("type") == "negotiation_turn":
            price = record.get("price")
            price_str = f"and offers ${price}" if price else ""
            line = f"The {role} says: {msg} {price_str}"
        elif record.get("event") == "deal_made":
            line = f"A deal was made at ${record.get('price')}."
        elif record.get("event") == "no_deal":
            line = "The negotiation ended with no deal."
        elif role == "Moderator":
            line = f"Finally, the moderator's analysis: {msg}"
        
        if line:
            script_lines.append(line)
    
    return "\n\n".join(script_lines)

def main():
    parser = argparse.ArgumentParser(description="Generate a TTS audio file from a negotiation transcript.")
    parser.add_argument("negotiation_folder", type=str, help="Path to the negotiation results folder.")
    args = parser.parse_args()

    folder = args.negotiation_folder
    if not os.path.isdir(folder):
        print(f"Error: Directory not found: {folder}", file=sys.stderr)
        sys.exit(1)

    transcript_file = os.path.join(folder, "transcript.jsonl")
    output_audio_file = os.path.join(folder, "negotiation_audio.mp3")

    if not os.path.exists(transcript_file):
        print(f"Error: transcript.jsonl not found in {folder}", file=sys.stderr)
        sys.exit(1)

    print("Generating audio script...")
    transcript_data = load_jsonl(transcript_file)
    script_text = create_negotiation_script(transcript_data)
    
    print("Generating audio using gTTS... This may take a moment.")
    try:
        tts = gTTS(text=script_text, lang='en', slow=False)
        tts.save(output_audio_file)
        print(f"\nSuccessfully saved negotiation audio to: {output_audio_file}")
    except Exception as e:
        print(f"\nAn error occurred during audio generation: {e}", file=sys.stderr)

if __name__ == "__main__":
    main() 