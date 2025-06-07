# Tic-Tac-Toe Showdown

A sophisticated LLM tournament system where AI models compete in single-elimination Tic-Tac-Toe battles, complete with detailed logging, statistical analysis, and beautiful visualizations.

## 🎮 Overview

**Tic-Tac-Toe Showdown** is a competitive multi-agent system that:

- **Hosts tournaments** between different Ollama LLM models
- **Logs every move** and game result in structured JSONL format
- **Generates visualizations** including move frequency heatmaps and tournament brackets
- **Provides statistical analysis** of model performance and strategies
- **Features robust error handling** for LLM parsing and game state management

### Key Features

🤖 **Multi-Model Competition**: Pit different LLMs against each other  
📊 **Rich Analytics**: Comprehensive logging and statistical analysis  
🎨 **Beautiful Visualizations**: Heatmaps, brackets, and pattern analysis  
⚡ **Robust Architecture**: Error handling and fallback mechanisms  
🔧 **Highly Configurable**: Customizable tournaments and parameters  

## 🚀 Installation

### Prerequisites

1. **Ollama** must be installed and running
2. **Python 3.8+** is required

### Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Ensure Ollama models are available**:
```bash
ollama pull phi4
ollama pull qwq
ollama pull llama3.3
```

3. **Run a basic tournament**:
```bash
python main.py
```

## 🎯 Usage

### Basic Tournament
```bash
# Default tournament with phi4 vs qwq
python main.py
```

### Custom Model Selection
```bash
# Specify which models compete
python main.py --models phi4 qwq llama3.3 phi4-mini

# Self-play tournament
python main.py --models phi4 phi4
```

### Advanced Configuration
```bash
# Customize temperature and seed for reproducibility
python main.py --models phi4 qwq --temp 0.8 --seed 123

# Quick mode with minimal output
python main.py --quick

# Skip visualizations (useful for headless environments)
python main.py --no-viz
```

### Utility Commands
```bash
# List available Ollama models
python main.py --list-models

# Custom log file location
python main.py --logfile experiments/my_tournament.jsonl
```

## 📁 Project Structure

```
tic_tac_toe_showdown/
├── agents.py           # PlayerAgent with LLM integration
├── game_engine.py      # Board logic and game referee
├── tournament.py       # Tournament management and brackets
├── viz.py             # Matplotlib visualizations
├── main.py            # CLI entrypoint
├── logger.py          # JSONL logging utilities
├── ollama_utils.py    # Ollama API helpers
├── requirements.txt   # Python dependencies
├── README.md          # This documentation
├── logs/              # Tournament logs (auto-created)
│   └── tournament.jsonl
└── plots/             # Generated visualizations (auto-created)
    ├── move_heatmap.png
    ├── tournament_bracket.png
    └── move_patterns.png
```

## 🏆 How It Works

### Tournament Flow

1. **Bracket Creation**: Models are arranged in a single-elimination bracket (padded to power of 2)
2. **Match Execution**: Each match is a best-of-1 Tic-Tac-Toe game
3. **Move Generation**: LLMs generate moves via natural language prompts
4. **Validation**: Moves are parsed and validated with fallback mechanisms
5. **Progression**: Winners advance to the next round until a champion emerges

### Game Mechanics

- **Standard Tic-Tac-Toe**: 3×3 grid, first to get three in a row wins
- **Turn-based**: X goes first (randomly assigned per match)
- **Move Format**: LLMs respond with JSON: `{"row": 0, "col": 1}`
- **Error Handling**: Invalid moves trigger auto-correction to valid alternatives
- **Draw Handling**: Random winner selection for draws (rare in Tic-Tac-Toe)

### Logging Format

Every action is logged to JSONL with timestamps:

```json
{"timestamp": "2024-01-15T10:30:00.123456", "type": "tournament_start", "models": ["phi4", "qwq"], "rounds": 1}
{"timestamp": "2024-01-15T10:30:15.789012", "type": "move", "game_id": "R1M1", "player": "X", "move": {"row": 1, "col": 1}, "board": [["X", " ", " "], [" ", "X", " "], [" ", " ", " "]]}
{"timestamp": "2024-01-15T10:30:30.345678", "type": "result", "game_id": "R1M1", "result": "win", "winner": "X", "final_board": [...]}
```

## 📊 Visualizations

### Move Frequency Heatmap
Shows which board positions are most popular across all games:
- **Hot spots**: Frequently chosen positions (center, corners)
- **Cold spots**: Rarely selected positions
- **Strategic insights**: Reveals model preferences and patterns

### Tournament Bracket
Visual representation of the tournament progression:
- **Participant flow**: Shows how models advance through rounds
- **Match results**: Winner indicators and progression paths
- **Final champion**: Clear identification of the tournament winner

### Move Pattern Analysis
Separate analysis for X and O players:
- **Positional preferences**: Different strategies for first/second player
- **Comparative analysis**: Side-by-side heatmaps
- **Strategic differences**: How opening vs. responding moves differ

## 🔧 Customization

### Adding New Models

1. **Install the model in Ollama**:
```bash
ollama pull your-new-model
```

2. **Add to tournament**:
```bash
python main.py --models phi4 qwq your-new-model
```

### Custom Agent Behavior

Modify `agents.py` to customize how LLMs are prompted:

```python
# In PlayerAgent.get_move()
prompt = f"""Custom prompt for {symbol} player:
Current board: {board_str}
Your strategic instruction here...
"""
```

### Tournament Rules

Adjust tournament mechanics in `tournament.py`:

```python
# Change bracket generation
def create_custom_bracket(models):
    # Your custom seeding logic
    pass

# Modify advancement rules
def handle_draw(model1, model2):
    # Your tiebreaker logic
    pass
```

### Visualization Themes

Customize visualizations in `viz.py`:

```python
# Change color schemes
move_counts_plot = ax.imshow(move_counts, cmap='viridis')  # Different colormap

# Modify styling
ax.set_title('My Custom Tournament', fontsize=20, color='blue')
```

## 📈 Performance Analysis

### Statistical Insights

The system automatically generates:

- **Win rates by model**: Overall performance metrics
- **Games played**: Tournament participation tracking  
- **Move preferences**: Strategic pattern analysis
- **Position popularity**: Board location statistics

### Analyzing Results

```python
import json

# Load tournament log
with open('logs/tournament.jsonl', 'r') as f:
    records = [json.loads(line) for line in f]

# Analyze move patterns
moves = [r for r in records if r['type'] == 'move']
center_moves = [m for m in moves if m['move']['row'] == 1 and m['move']['col'] == 1]
print(f"Center moves: {len(center_moves)}/{len(moves)} ({len(center_moves)/len(moves):.1%})")

# Model performance
results = [r for r in records if r['type'] == 'result']
winners = [r['winner'] for r in results if r['winner']]
```

## 🐛 Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'ollama'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem**: Models not responding or timing out
```bash
# Solution: Check Ollama is running
ollama list
ollama serve  # If not running
```

**Problem**: Invalid move parsing
- **Built-in handling**: System automatically finds valid alternatives
- **Logging**: Check logs for parsing details
- **Adjustment**: Modify prompts in `agents.py` for clearer instructions

**Problem**: Visualization errors
```bash
# Solution: Install display dependencies
pip install matplotlib
# For headless environments:
python main.py --no-viz
```

### Debug Mode

Enable detailed logging by modifying `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Advanced Usage

### Batch Tournaments

Run multiple tournaments for statistical significance:

```bash
# Shell script for multiple runs
for i in {1..10}; do
    python main.py --seed $i --logfile logs/tournament_$i.jsonl
done
```

### Model Comparison Studies

```bash
# Test temperature effects
python main.py --models phi4 phi4 --temp 0.1 --logfile logs/low_temp.jsonl
python main.py --models phi4 phi4 --temp 1.5 --logfile logs/high_temp.jsonl

# Compare different model combinations
python main.py --models phi4 qwq --logfile logs/phi4_vs_qwq.jsonl
python main.py --models llama3.3 qwq --logfile logs/llama_vs_qwq.jsonl
```

### Integration with Research

The JSONL logs are perfect for research analysis:

```python
import pandas as pd
import seaborn as sns

# Convert to DataFrame for analysis
df = pd.read_json('logs/tournament.jsonl', lines=True)
move_df = df[df['type'] == 'move']

# Statistical analysis
sns.heatmap(move_counts, annot=True)
plt.title('Move Distribution Analysis')
plt.show()
```

## 🤝 Contributing

We welcome contributions! Areas for enhancement:

- **New game variants**: Different board sizes, rules
- **Advanced agents**: Minimax, neural network players
- **Enhanced visualizations**: 3D plots, animations
- **Performance optimizations**: Parallel tournaments
- **UI improvements**: Web interface, real-time viewing

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- **Ollama team** for the excellent LLM serving platform
- **Matplotlib** for powerful visualization capabilities
- **Pydantic** for robust data validation
- **The LLM community** for advancing AI capabilities

---

Ready to see which AI reigns supreme in Tic-Tac-Toe? Start your tournament today! 🏆 