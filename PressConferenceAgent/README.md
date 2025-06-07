# Simulated Press Conference Demo

A multi-agent system that simulates a press conference where a spokesperson fields questions from multiple journalists, and a note-taker produces meeting minutes.

## Overview

This project demonstrates a sophisticated multi-agent interaction where:
- A **SpokespersonAgent** gives opening statements and answers questions
- Multiple **JournalistAgents** ask insightful questions based on the opening statement  
- A **NoteTakerAgent** summarizes the entire Q&A session into concise meeting minutes

All interactions are logged in JSONL format with timestamps for analysis and replay.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have Ollama installed and running with the desired models:
```bash
ollama pull phi4
```

## Usage

### Basic Usage
```bash
python orchestrator.py --topic "AI Ethics"
```

### Advanced Usage
```bash
python orchestrator.py \
  --num_journalists 3 \
  --model phi4 \
  --temp 0.6 \
  --seed 123 \
  --topic "AI Ethics" \
  --output demo_press.jsonl
```

### Command Line Arguments

- `--num_journalists`: Number of journalists to simulate (default: 4)
- `--model`: Ollama model to use (default: "phi4")
- `--temp`: Temperature for text generation (default: 0.7)
- `--seed`: Random seed for reproducibility (default: 42)
- `--topic`: Topic for the press conference (default: "Technology Innovation")
- `--output`: Output JSONL file path (default: "press_log.jsonl")

## Output Format

The system generates a JSONL file where each line contains a JSON object with these fields:

- `timestamp`: ISO timestamp when the record was created
- `type`: Record type, one of:
  - `"opening"`: Spokesperson's opening statement
  - `"question"`: Question from a journalist
  - `"answer"`: Spokesperson's answer to a question
  - `"minutes"`: Final meeting minutes summary
- `text`: The actual content (statement, question, answer, or summary)
- `journalist`: Journalist ID (only present for question/answer records)

### Example Output Records

```json
{"timestamp": "2024-01-15T10:30:00.123456", "type": "opening", "text": "Welcome to today's press conference on AI Ethics..."}
{"timestamp": "2024-01-15T10:30:15.789012", "type": "question", "journalist": 0, "text": "What measures are being taken to ensure AI transparency?"}
{"timestamp": "2024-01-15T10:30:30.345678", "type": "answer", "journalist": 0, "text": "We are implementing several transparency initiatives..."}
{"timestamp": "2024-01-15T10:32:00.901234", "type": "minutes", "text": "• Key points discussed included AI transparency measures..."}
```

## Viewing the Results

After running the simulation, you can:

1. **View the minutes**: The final summary is printed to the console
2. **Analyze the full transcript**: Open the JSONL file to see the complete conversation flow
3. **Process programmatically**: Load the JSONL file in Python for further analysis

```python
import json

# Load and analyze the transcript
with open('press_log.jsonl', 'r') as f:
    records = [json.loads(line) for line in f]

# Filter by record type
questions = [r for r in records if r['type'] == 'question']
answers = [r for r in records if r['type'] == 'answer']
minutes = [r for r in records if r['type'] == 'minutes']
```

## Project Structure

- `config.py`: Configuration constants and model settings
- `utils.py`: JSON logging and timestamp utilities
- `agents.py`: Agent class definitions (Spokesperson, Journalist, NoteTaker)
- `orchestrator.py`: Main simulation logic and CLI interface
- `ollama_utils.py`: Ollama API interaction utilities
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Error Handling

The system includes robust error handling:
- Automatic retry with adjusted parameters if initial run fails
- Graceful handling of missing output files
- Validation of command-line arguments
- Clear error messages with suggested fixes

## Customization

You can easily customize the simulation by:
- Modifying prompts in `agents.py`
- Adjusting default parameters in `config.py`
- Adding new agent types or behaviors
- Implementing different summarization strategies 