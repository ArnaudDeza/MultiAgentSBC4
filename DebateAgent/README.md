# Multi-Agent Debate System

A Python framework for running multi-agent debates using local LLMs via Ollama. Agents engage in structured debates on topics, with a judge determining the winner based on argument quality.

## Features

- **Multi-agent debates**: Run debates with 2-8 agents using different LLM models
- **Structured rounds**: Opening statements followed by multiple debate rounds
- **Automated judging**: AI judge evaluates arguments and picks winners
- **JSONL logging**: Complete debate transcripts saved for analysis
- **Configurable parameters**: Customize models, temperature, rounds, and more
- **Error handling**: Graceful handling of model failures with retry logic

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running and has the required models:
```bash
ollama pull phi4
ollama pull gemma3:12b  # optional alternative model
```

## Usage

### Basic Usage

Run a default debate with 3 agents, 5 rounds, using phi4:
```bash
python orchestrator.py
```

### Using Predefined Topics

```bash
# Use a predefined topic by key
python orchestrator.py --topic pineapple_pizza --num_agents 3 --rounds 2

# See all available topics
python orchestrator.py --list-topics

# See just the topic keys
python orchestrator.py --list-keys
```

### Using Custom Topics

```bash
# Use any custom debate question
python orchestrator.py \
  --topic "Should AI replace human teachers in schools?" \
  --num_agents 4 \
  --rounds 3 \
  --model phi4 \
  --temp 0.8 \
  --seed 123
```

### Audio Generation

Generate audio transcripts using text-to-speech:

```bash
# Generate debate with audio
python orchestrator.py --topic pineapple_pizza --audio

# Convert existing debates to audio
python convert_to_audio.py

# Test audio system
python demo_audio.py
```

### Available Options

- `--topic`: Debate topic key or custom question (default: ai_education)
- `--num_agents`: Number of debate agents (default: 3)
- `--rounds`: Number of debate rounds (default: 5)
- `--model`: Ollama model to use (default: phi4)
- `--temp`: Generation temperature 0.0-1.0 (default: 0.7)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output`: Output location (default: auto-generated timestamped folder)
- `--audio`: Generate audio transcript using text-to-speech
- `--list-topics`: Show all available predefined topics
- `--list-keys`: Show just the topic keys

## Log Format

The system outputs JSONL logs with the following record types:

**Debate Start:**
```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "event": "debate_start",
  "topic": "The benefits and drawbacks of AI in education",
  "num_agents": 3,
  "rounds": 5,
  "model": "phi4",
  "temperature": 0.7,
  "seed": 42
}
```

**Agent Messages:**
```json
{
  "timestamp": "2024-01-15T10:30:15.000000",
  "round": 1,
  "agent": 0,
  "message": "I believe AI can revolutionize education by...",
  "type": "opening_statement"
}
```

**Final Verdict:**
```json
{
  "timestamp": "2024-01-15T10:35:00.000000",
  "event": "verdict",
  "winner": "B",
  "justification": "Agent B provided the most compelling arguments..."
}
```

## Project Structure

```
multi_agent_debate/
├── agents.py          # DebateAgent & JudgeAgent classes
├── orchestrator.py    # Main debate loop / CLI entrypoint
├── config.py          # Model nicknames & hyperparameters
├── utils.py           # JSON-logger, timestamp helper
├── ollama_utils.py    # Ollama API wrapper functions
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## How It Works

1. **Initialization**: Creates N debate agents with unique seeds
2. **Opening Statements**: Each agent presents their initial position
3. **Debate Rounds**: Agents respond to each other's arguments iteratively
4. **Judging**: A judge agent evaluates all arguments and declares a winner
5. **Logging**: All interactions are logged to JSONL for analysis

## Customization

- **Models**: Edit `config.py` to add new Ollama models
- **Prompts**: Modify agent prompts in `agents.py` and `orchestrator.py`
- **Judging**: Customize the judging logic in `JudgeAgent.pick_winner()`
- **Logging**: Extend `JsonLogger` in `utils.py` for additional formats

## Troubleshooting

**Model not found error:**
- Ensure the model is installed: `ollama pull <model_name>`
- Check available models: `ollama list`

**Connection errors:**
- Verify Ollama is running: `ollama serve`
- Check Ollama is accessible on default port 11434

**Memory issues:**
- Use smaller models (e.g., `phi4-mini` instead of `phi4`)
- Reduce `num_ctx` parameter in `config.py` 