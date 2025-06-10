"""
Generate an HTML visualization of a negotiation from its transcript.
"""

import argparse
import json
import os
import sys
import html

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Negotiation Visualization</title>
    <style>
        body {{ font-family: sans-serif; background-color: #eef2f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; background: #fff; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ padding: 20px; background: #4a5568; color: white; border-top-left-radius: 10px; border-top-right-radius: 10px; }}
        .header h1 {{ margin: 0; font-size: 1.6em; }}
        .header p {{ margin: 5px 0 0; opacity: 0.8; }}
        .chat-log {{ padding: 20px; max-height: 60vh; overflow-y: auto; }}
        .message {{ display: flex; margin-bottom: 20px; }}
        .message.buyer .msg-content {{ background: #dbeafe; }}
        .message.seller .msg-content {{ background: #dcfce7; }}
        .message.seller {{ flex-direction: row-reverse; }}
        .message.seller .msg-content {{ text-align: right; }}
        .avatar {{ width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; flex-shrink: 0; }}
        .buyer .avatar {{ background: #3b82f6; margin-right: 15px; }}
        .seller .avatar {{ background: #16a34a; margin-left: 15px; }}
        .msg-content {{ padding: 12px 18px; border-radius: 18px; max-width: 75%; }}
        .text {{ line-height: 1.5; }}
        .price-tag {{ font-weight: bold; color: #1e293b; margin-top: 8px; font-size: 1.1em; }}
        .outcome {{ padding: 20px; text-align: center; font-size: 1.5em; font-weight: bold; }}
        .deal {{ color: #16a34a; background: #f0fdf4; }}
        .no-deal {{ color: #dc2626; background: #fef2f2; }}
        .summary {{ padding: 20px; border-top: 1px solid #e2e8f0; }}
        .summary h2 {{ margin-top: 0; color: #4a5568; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>{item_name}</h1><p>A negotiation at {scenario_name}</p></div>
        <div class="chat-log">{chat_messages}</div>
        <div class="outcome {outcome_class}">{outcome_text}</div>
        <div class="summary"><h2>Moderator's Analysis</h2><div>{analysis}</div></div>
    </div>
</body>
</html>
"""

def load_jsonl(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def load_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_html(transcript: list, metadata: dict, summary_text: str) -> str:
    scenario = metadata.get("scenario", {})
    chat_html = ""
    for record in transcript:
        role = record.get("role", "").lower()
        if record.get("type") == "negotiation_turn":
            price = record.get("price")
            price_tag = f"<div class='price-tag'>Offer: ${price}</div>" if price else ""
            chat_html += f"""
            <div class="message {role}">
                <div class="avatar">{role[0].upper()}</div>
                <div class="msg-content">
                    <div class="text">{html.escape(record.get("message"))}</div>
                    {price_tag}
                </div>
            </div>"""
    
    outcome = metadata.get("outcome", {})
    outcome_class = "deal" if outcome.get("deal_made") else "no-deal"
    outcome_text = f"Deal Made at ${outcome.get('final_price')}!" if outcome.get("deal_made") else "No Deal Reached"
    
    return HTML_TEMPLATE.format(
        item_name=html.escape(scenario.get("item_name", "")),
        scenario_name=html.escape(scenario.get("name", "")),
        chat_messages=chat_html,
        outcome_class=outcome_class,
        outcome_text=outcome_text,
        analysis=html.escape(summary_text).replace('\n', '<br>')
    )

def main():
    parser = argparse.ArgumentParser(description="Generate an HTML visualization of a negotiation.")
    parser.add_argument("negotiation_folder", type=str, help="Path to the results folder.")
    args = parser.parse_args()

    folder = args.negotiation_folder
    if not os.path.isdir(folder):
        print(f"Error: Directory not found: {folder}", file=sys.stderr)
        sys.exit(1)

    files = {
        "transcript": os.path.join(folder, "transcript.jsonl"),
        "metadata": os.path.join(folder, "metadata.json"),
        "summary": os.path.join(folder, "summary.md")
    }
    
    if not all(os.path.exists(f) for f in files.values()):
        print(f"Error: Missing one or more required files in {folder}", file=sys.stderr)
        sys.exit(1)

    print("Generating HTML visualization...")
    transcript_data = load_jsonl(files["transcript"])
    metadata = load_json(files["metadata"])
    summary_data = load_text(files["summary"])
    
    html_content = generate_html(transcript_data, metadata, summary_data)

    output_file = os.path.join(folder, "negotiation_visualization.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nSuccessfully created visualization: {output_file}")

if __name__ == "__main__":
    main() 