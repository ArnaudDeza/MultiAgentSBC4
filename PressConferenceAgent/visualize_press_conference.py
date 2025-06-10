"""
Generate an HTML visualization of a press conference from its transcript file.
"""

import argparse
import json
import os
import sys
import html

SPOKESPERSON_COLOR = "#007BFF"
JOURNALIST_COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FED766", "#8A6FDF"]
SYSTEM_COLOR = "#6c757d"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Press Conference Visualization</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ padding: 25px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .header h1 {{ margin: 0; font-size: 1.8em; color: #343a40; }}
        .chat-log {{ padding: 20px; max-height: 70vh; overflow-y: auto; }}
        .message {{ display: flex; margin-bottom: 20px; }}
        .avatar {{ width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 15px; flex-shrink: 0; }}
        .msg-content {{ background: #e9ecef; padding: 12px 18px; border-radius: 18px; max-width: 85%; }}
        .meta {{ font-size: 0.85em; color: #6c757d; margin-bottom: 5px; }}
        .meta strong {{ color: #212529; }}
        .text {{ font-size: 0.98em; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }}
        .final-docs {{ padding: 25px; background-color: #f8f9fa; border-top: 1px solid #ddd; }}
        .doc-box {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-top: 15px; }}
        .doc-box h2 {{ margin-top: 0; font-size: 1.3em; color: #007BFF; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>{title}</h1></div>
        <div class="chat-log">{chat_messages}</div>
        <div class="final-docs">
            <div class="doc-box"><h2>Meeting Minutes</h2><div class="text">{minutes}</div></div>
            <div class="doc-box"><h2>Final Summary</h2><div class="text">{summary}</div></div>
        </div>
    </div>
</body>
</html>
"""

def load_jsonl(file_path: str) -> list:
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f: records.append(json.loads(line))
    return records

def load_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(transcript: list, metadata: dict) -> str:
    """Generates the final HTML content."""
    title = metadata.get("event", {}).get("title", "Press Conference")
    chat_html = ""
    minutes = ""
    summary = ""

    for record in transcript:
        role = record.get("role", "System")
        msg = record.get("message", "")
        msg_type = record.get("type")

        if msg_type in ["opening_statement", "question", "answer"]:
            avatar_initial = "?"
            color = SYSTEM_COLOR
            meta_info = f"<strong>{html.escape(role)}</strong>"

            if role == "Spokesperson":
                avatar_initial = "S"
                color = SPOKESPERSON_COLOR
            elif "Journalist" in role:
                j_id = int(role.split(" ")[1])
                avatar_initial = f"J{j_id}"
                color = JOURNALIST_COLORS[j_id % len(JOURNALIST_COLORS)]
                meta_info += f" ({html.escape(record.get('bias', ''))})"

            chat_html += f"""
            <div class="message">
                <div class="avatar" style="background-color: {color};">{avatar_initial}</div>
                <div class="msg-content">
                    <div class="meta">{meta_info}</div>
                    <div class="text">{html.escape(msg)}</div>
                </div>
            </div>
            """
        elif msg_type == "minutes":
            minutes = html.escape(msg)
        elif msg_type == "summary":
            summary = html.escape(msg)
            
    return HTML_TEMPLATE.format(title=html.escape(title), chat_messages=chat_html, minutes=minutes, summary=summary)

def main():
    parser = argparse.ArgumentParser(description="Generate an HTML visualization of a press conference.")
    parser.add_argument("conference_folder", type=str, help="Path to the results folder.")
    args = parser.parse_args()

    if not os.path.isdir(args.conference_folder):
        print(f"Error: Directory not found: {args.conference_folder}", file=sys.stderr)
        sys.exit(1)

    transcript_file = os.path.join(args.conference_folder, "transcript.jsonl")
    metadata_file = os.path.join(args.conference_folder, "metadata.json")
    output_html_file = os.path.join(args.conference_folder, "conference_visualization.html")

    print("Loading conference data...")
    if not all(os.path.exists(f) for f in [transcript_file, metadata_file]):
        print("Error: Missing transcript.jsonl or metadata.json.", file=sys.stderr)
        sys.exit(1)
        
    transcript_data = load_jsonl(transcript_file)
    metadata = load_json(metadata_file)

    print("Generating HTML visualization...")
    html_content = generate_html(transcript_data, metadata)

    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nSuccessfully created visualization: {output_html_file}")

if __name__ == "__main__":
    main() 