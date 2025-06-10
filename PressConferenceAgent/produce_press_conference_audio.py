"""
Generate an audio recording of a press conference from its transcript.
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
    records = []
    if not os.path.exists(file_path): return records
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f: records.append(json.loads(line))
    return records

def create_conference_script(transcript: list) -> str:
    """Create a formatted string script of the press conference for TTS."""
    script_lines = []
    
    # Find the event title from the first log entry
    event_title = "a press conference"
    if transcript and transcript[0].get("event") == "conference_start":
        event_title = transcript[0].get("event_details", {}).get("title", event_title)

    intro = f"Welcome to this special report on {event_title}. We now go live to the press conference."
    script_lines.append(intro)

    # Process records
    for record in transcript:
        role = record.get("role", "")
        msg = record.get("message", "")
        
        if role == "Spokesperson":
            line = f"The spokesperson says: {msg}"
        elif "Journalist" in role:
            bias = record.get('bias', 'a')
            line = f"A {bias} journalist asks: {msg}"
        elif role == "Note-Taker":
            line = f"The official meeting minutes are as follows: {msg}"
        elif role == "Summarizer":
            line = f"And finally, the executive summary of the event: {msg}"
        else:
            continue # Skip system messages
        
        script_lines.append(line)
    
    return "\n\n".join(script_lines)

def main():
    """Main function to parse arguments and generate the audio file."""
    parser = argparse.ArgumentParser(description="Generate a TTS audio file from a press conference transcript.")
    parser.add_argument("conference_folder", type=str, help="Path to the conference results folder.")
    args = parser.parse_args()

    if not os.path.isdir(args.conference_folder):
        print(f"Error: Directory not found: {args.conference_folder}", file=sys.stderr)
        sys.exit(1)

    transcript_file = os.path.join(args.conference_folder, "transcript.jsonl")
    output_audio_file = os.path.join(args.conference_folder, "conference_audio.mp3")

    print("Loading conference transcript...")
    transcript_data = load_jsonl(transcript_file)
    if not transcript_data:
        print("Error: transcript.jsonl is empty or not found.", file=sys.stderr)
        sys.exit(1)

    print("Generating conference script for audio...")
    conference_script = create_conference_script(transcript_data)
    
    print("Generating audio using gTTS... This may take a moment.")
    try:
        tts = gTTS(text=conference_script, lang='en', slow=False)
        tts.save(output_audio_file)
        print(f"\nSuccessfully saved conference audio to: {output_audio_file}")
    except Exception as e:
        print(f"\nAn error occurred while generating audio: {e}", file=sys.stderr)
        print("Please check your internet connection, as gTTS may require it.", file=sys.stderr)

if __name__ == "__main__":
    main() 