"""
Generate an HTML visualization of a debate from its transcript file.
"""

import argparse
import json
import os
import sys
import html

# A simple color palette for the agent avatars
AGENT_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#FED766", 
    "#8A6FDF", "#3C8DAD", "#E87EA1", "#F8A553"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debate Visualization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }}
        .debate-container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .debate-header {{
            padding: 20px;
            background-color: #f5f5f5;
            border-bottom: 1px solid #ddd;
        }}
        .debate-header h1 {{
            margin: 0;
            font-size: 1.5em;
            color: #333;
        }}
        .chat-log {{
            padding: 20px;
            max-height: 70vh;
            overflow-y: auto;
        }}
        .message {{
            display: flex;
            margin-bottom: 20px;
            align-items: flex-start;
        }}
        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1em;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .message-content {{
            background-color: #e4e6eb;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 85%;
        }}
        .meta-info {{
            font-size: 0.8em;
            color: #65676b;
            margin-bottom: 4px;
        }}
        .meta-info strong {{
            color: #050505;
        }}
        .message-text {{
            font-size: 0.95em;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .verdict {{
            padding: 20px;
            margin: 20px;
            border: 2px solid #FFD700;
            background-color: #FFFACD;
            border-radius: 8px;
        }}
        .verdict h2 {{
            margin-top: 0;
            color: #DAA520;
        }}
    </style>
</head>
<body>
    <div class="debate-container">
        <div class="debate-header">
            <h1>{topic}</h1>
        </div>
        <div class="chat-log">
            {chat_messages}
        </div>
    </div>
</body>
</html>
"""

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

def generate_html(transcript: list, metadata: dict) -> str:
    """Generates the final HTML content from the transcript data."""
    topic = metadata.get("topic_question", "Debate Topic")
    chat_messages_html = ""

    for record in transcript:
        event = record.get("event")
        msg_type = record.get("type")

        if msg_type in ["opening_statement", "debate_response"]:
            agent_id = record.get('agent', 'N/A')
            stance = record.get('stance', 'Unknown')
            model = record.get('model', 'Unknown')
            message = record.get('message', '')

            avatar_color = AGENT_COLORS[agent_id % len(AGENT_COLORS)]
            avatar_initial = f"A{agent_id}"
            
            meta_info = f"<strong>Agent {agent_id}</strong> ({html.escape(model)}) | Stance: {html.escape(stance)}"
            
            chat_messages_html += f"""
            <div class="message">
                <div class="avatar" style="background-color: {avatar_color};">{avatar_initial}</div>
                <div class="message-content">
                    <div class="meta-info">{meta_info}</div>
                    <div class="message-text">{html.escape(message)}</div>
                </div>
            </div>
            """
        elif event == "verdict":
            winner = record.get("winner", "N/A")
            justification = record.get("justification", "No justification provided.")
            
            chat_messages_html += f"""
            <div class="verdict">
                <h2>Judge's Verdict</h2>
                <p><strong>Winner:</strong> Agent {html.escape(str(winner))}</p>
                <p><strong>Justification:</strong> {html.escape(justification)}</p>
            </div>
            """
            
    return HTML_TEMPLATE.format(topic=html.escape(topic), chat_messages=chat_messages_html)


def main():
    """Main function to parse arguments and generate the HTML file."""
    parser = argparse.ArgumentParser(description="Generate an HTML visualization from a debate transcript.")
    parser.add_argument(
        "debate_folder",
        type=str,
        help="Path to the debate results folder containing transcript.jsonl and metadata.json."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.debate_folder):
        print(f"Error: The specified directory does not exist: {args.debate_folder}", file=sys.stderr)
        sys.exit(1)

    transcript_file = os.path.join(args.debate_folder, "transcript.jsonl")
    metadata_file = os.path.join(args.debate_folder, "metadata.json")
    output_html_file = os.path.join(args.debate_folder, "debate_visualization.html")

    print("Loading debate data...")
    transcript_data = load_jsonl(transcript_file)
    metadata = load_json(metadata_file)

    if not transcript_data or not metadata:
        print("Could not load necessary files. Aborting.", file=sys.stderr)
        sys.exit(1)

    print("Generating HTML visualization...")
    html_content = generate_html(transcript_data, metadata)

    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nSuccessfully created debate visualization!")
    print(f"You can open this file in your browser: {output_html_file}")


if __name__ == "__main__":
    main() 