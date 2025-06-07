# Rock Paper Scissors Royale 🎮✂️📄🪨

**A sophisticated multi-agent tournament system where Large Language Models compete in strategic Rock Paper Scissors matches**

Rock Paper Scissors Royale is an advanced tournament platform that pits different LLM models against each other in the classic game of Rock Paper Scissors. Unlike simple random play, this system allows LLMs to develop strategies, analyze opponent patterns, and adapt their gameplay over time.

## 🌟 Features

### Core Functionality
- **Multi-Agent LLM Competition**: Support for multiple Ollama models competing simultaneously
- **Strategic Gameplay**: LLMs receive game history and can develop adaptive strategies
- **Three Tournament Types**: Round-robin, single-elimination, and league formats
- **Comprehensive Logging**: JSONL-based logging of all matches and tournament progression
- **Rich Visualizations**: Matplotlib-powered analysis plots and statistics

### Advanced Capabilities
- **Pattern Recognition**: Agents can analyze opponent move patterns
- **Temperature Control**: Adjustable LLM creativity/randomness
- **Baseline Agents**: Random and Counter-strategy agents for comparison
- **Real-time Analysis**: Live tournament progression tracking
- **Professional Statistics**: Win rates, move frequencies, matchup analysis

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- At least 2 Ollama models downloaded

### Setup
```bash
# Clone or download the project
cd RockPaperScissors

# Install dependencies
pip install -r requirements.txt

# Verify Ollama is working and list available models
python main.py --list-models
```

### Download Ollama Models (if needed)
```bash
# Download some popular models
ollama pull phi3
ollama pull llama2
ollama pull gemma
ollama pull mistral
```

## 🚀 Quick Start

### Basic Tournament
```bash
# Run a simple league tournament with 2 models
python main.py phi3 llama2

# Add baseline agents for comparison
python main.py phi3 llama2 --add-baselines
```

### Tournament Types
```bash
# Round-robin tournament (everyone plays everyone)
python main.py phi3 llama2 gemma --tournament round-robin

# Single-elimination bracket
python main.py phi3 llama2 gemma mistral --tournament elimination

# League format (random pairings over multiple rounds)
python main.py phi3 llama2 --tournament league --rounds 20
```

### Advanced Options
```bash
# Customize LLM behavior
python main.py phi3 llama2 --temperature 0.5 --rounds 15

# Skip visualizations for headless operation
python main.py phi3 llama2 --no-viz

# Analyze existing tournament data
python main.py --analyze-only
```

## 📊 Tournament Formats

### League Tournament (Default)
- Random pairings each round
- Configurable number of total rounds
- Points-based scoring (3 for win, 1 for draw, 0 for loss)
- Progressive standings updates

### Round-Robin Tournament
- Every agent plays every other agent
- Fair and comprehensive competition
- Multiple rounds per match
- Detailed head-to-head statistics

### Single-Elimination Tournament
- Bracket-style competition
- Automatic bracket padding to power-of-2
- Sudden-death matches
- Clear elimination progression

## 📈 Visualizations

The system generates comprehensive analysis plots:

1. **Move Frequency Heatmap**: Shows each agent's preferred moves as percentages
2. **Win Rate Analysis**: Bar chart of win rates with game counts
3. **Move Matchup Matrix**: Win rates for each move vs move combination
4. **Tournament Timeline**: Progression of scores over rounds (league format)

## 🎯 Game Rules & Strategy

### Basic Rules
- **Rock** beats **Scissors**
- **Paper** beats **Rock**
- **Scissors** beats **Paper**
- Same moves result in a **Draw**

### Strategic Elements
- **Pattern Recognition**: LLMs can analyze opponent history
- **Adaptive Play**: Strategies can evolve based on experience
- **Meta-Gaming**: Advanced models may try to predict opponent predictions
- **Historical Context**: Full game history is provided to agents

## 📝 Logging & Data

### JSONL Log Format
All tournament data is stored in `data/logs/tournament.jsonl`:

```json
{"timestamp": "2024-01-01T12:00:00", "type": "tournament_start", "models": ["phi3", "llama2"], "tournament_type": "league", "rounds": 20}
{"timestamp": "2024-01-01T12:00:01", "type": "match", "match_id": "M0001", "player1": "phi3", "player2": "llama2", "move1": "rock", "move2": "paper", "result1": "loss", "result2": "win"}
{"timestamp": "2024-01-01T12:05:00", "type": "round_summary", "round": 5, "standings": {...}}
{"timestamp": "2024-01-01T12:10:00", "type": "tournament_end", "final_standings": {...}, "champion": "phi3"}
```

### Data Analysis
Load and analyze tournament data:
```python
from utils import load_tournament_data

data = load_tournament_data("data/logs/tournament.jsonl")
matches = [r for r in data if r["type"] == "match"]
print(f"Total matches: {len(matches)}")
```

## 🔧 Configuration

### Command Line Options
```
usage: main.py [-h] [--list-models] [--tournament {round-robin,elimination,league}]
               [--rounds ROUNDS] [--temperature TEMPERATURE] [--seed SEED]
               [--add-baselines] [--log-file LOG_FILE] [--no-viz] [--analyze-only]
               [models ...]

positional arguments:
  models                Ollama model names to participate

optional arguments:
  --list-models         List available Ollama models and exit
  --tournament TYPE     Tournament type (default: league)
  --rounds ROUNDS       Number of rounds per match or total rounds
  --temperature TEMP    LLM temperature (0.0-1.0, default: 0.7)
  --seed SEED          Random seed (default: 42)
  --add-baselines      Add Random and Counter baseline agents
  --log-file FILE      JSONL log file path
  --no-viz             Skip visualization generation
  --analyze-only       Only generate analysis plots from existing log
```

### Agent Types
1. **LLM Agents**: Use specified Ollama models with strategic prompts
2. **Random Agent**: Makes completely random moves (baseline)
3. **Counter Agent**: Counters opponent's most frequent move (baseline)

## 🎨 Customization

### Adding New Agent Types
Extend the `PlayerAgent` class in `agents.py`:

```python
class MyCustomAgent(PlayerAgent):
    def make_move(self, round_num, opponent_history, own_history):
        # Your custom strategy here
        return Move.ROCK
```

### Custom Tournament Formats
Extend the `TournamentManager` class in `tournament.py`:

```python
def run_my_tournament(self, agents, **kwargs):
    # Your custom tournament logic
    pass
```

## 🛡️ Error Handling

The system includes robust error handling:
- **LLM Parsing Failures**: Falls back to random moves
- **Model Unavailability**: Validates models before tournament start
- **Timeout Protection**: Graceful handling of slow responses
- **Interrupt Handling**: Clean shutdown on Ctrl+C

## 🚨 Troubleshooting

### Common Issues

**"No Ollama models found"**
```bash
# Check if Ollama is running
ollama list

# Install models if needed
ollama pull phi3
```

**"Model not found"**
```bash
# List available models
python main.py --list-models

# Use exact model names from the list
```

**"Temperature must be between 0.0 and 1.0"**
```bash
# Use valid temperature values
python main.py phi3 llama2 --temperature 0.7
```

**Visualization issues**
```bash
# Install matplotlib properly
pip install matplotlib

# Run without visualizations if needed
python main.py phi3 llama2 --no-viz
```

### Performance Tips
- Use lower temperatures (0.3-0.5) for more consistent strategies
- Reduce rounds for faster tournaments during testing
- Use `--no-viz` for automated/scripted tournaments
- Monitor system resources with many large models

## 📊 Example Tournament Analysis

Here's what a typical tournament produces:

```
🏆 LEAGUE TOURNAMENT RESULTS
============================================================
🥇 CHAMPION: phi3

📊 Final Standings:
------------------------------------------------------------
🥇  1. phi3           |  45 pts | 15- 3- 2 |  75.0% | 20 matches
🥈  2. llama2         |  38 pts | 12- 6- 2 |  60.0% | 20 matches
🥉  3. Random         |  22 pts |  7-11- 2 |  35.0% | 20 matches
     4. Counter        |  15 pts |  4-14- 2 |  20.0% | 20 matches
============================================================
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- New agent strategies
- Additional tournament formats
- Enhanced visualizations
- Performance optimizations
- Documentation improvements

## 📄 License

This project is open source. Feel free to use and modify for your needs.

## 🎯 Use Cases

- **LLM Research**: Compare reasoning capabilities across models
- **Game Theory Studies**: Analyze strategic behavior in simple games
- **Benchmarking**: Evaluate model performance in competitive scenarios
- **Educational**: Demonstrate multi-agent systems and game theory
- **Entertainment**: Fun competitions between your favorite models

---

**Ready to see which LLM will become the Rock Paper Scissors champion? Start your tournament today!** 🏆 