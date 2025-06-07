# Enhanced Multi-Agent Game Tournament System

A powerful, flexible tournament system for LLM agents with configurable games, multiple tournament formats, and comprehensive logging.

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Install Ollama** (if not already installed)
```bash
# On macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull some models for testing
ollama pull phi4:latest
ollama pull qwq:latest
ollama pull llama3.2:1b
```

3. **Verify Setup**
```bash
ollama list  # Should show your installed models
```

### Basic Usage

```bash
# Simple tournament with two models
python main_enhanced.py --models phi4:latest qwq:latest

# Round-robin tournament with best-of-3 matches
python main_enhanced.py --models phi4:latest qwq:latest llama3.2:1b --format round_robin --best-of 3

# Large board strategic play (5x5 board, need 4 in a row to win)
python main_enhanced.py --models phi4:latest qwq:latest --board-size 5 --win-length 4

# Swiss tournament with multiple rounds
python main_enhanced.py --models phi4:latest qwq:latest llama3.2:1b phi4:mini --format swiss --max-rounds 3
```

## 🎮 Key Features

### ✅ Multiple Tournament Formats
- **Single Elimination**: Traditional knockout tournament
- **Round Robin**: Every player plays every other player  
- **Swiss System**: Balanced pairing based on performance
- **Best-of-X Matches**: Configurable match lengths (1, 3, 5, 7+ games)

### ✅ Flexible Game Configuration
- **Board Sizes**: 3x3, 4x4, 5x5, up to 10x10
- **Win Conditions**: 3-in-a-row, 4-in-a-row, or custom length
- **Multiple Games**: Tic-Tac-Toe, Connect-Four (easily extensible)

### ✅ Enhanced Logging & File Management
- **Automatic File Organization**: Timestamped session directories
- **Complete Parameter Storage**: All settings saved to JSON
- **Structured Output**: Separate folders for logs, plots, and data
- **Session Management**: Tools to analyze and compare tournaments

### ✅ Rich Visualizations
- **Tournament Brackets**: Visual progression tracking
- **Performance Heatmaps**: Player statistics and comparisons
- **Win Rate Trends**: Performance over time analysis
- **Statistical Insights**: Comprehensive tournament analytics

## 📁 Output Structure

Each tournament automatically creates an organized output directory:

```
outputs/
├── tournament_sing_3x3_w3_4p_20241207_180512/
│   ├── logs/
│   │   ├── moves.jsonl              # Individual game moves
│   │   └── results.jsonl            # Tournament events & results
│   ├── plots/
│   │   ├── tournament_bracket.png   # Visual tournament progression
│   │   ├── performance_heatmap.png  # Player performance analysis
│   │   └── win_rate_trends.png     # Performance trends
│   ├── data/
│   │   ├── tournament_config.json   # Complete configuration
│   │   ├── session_metadata.json   # Session timing & info
│   │   └── tournament_summary.json # Final results & statistics
│   └── session_summary.json        # Complete session overview
```

## 🔧 Advanced Usage

### Custom Tournament Configuration
```bash
# Complex tournament with all options
python main_enhanced.py \
  --models phi4:latest qwq:latest llama3.2:1b phi4:mini \
  --format swiss \
  --best-of 3 \
  --board-size 4 \
  --win-length 3 \
  --temp 0.7 \
  --seed 42 \
  --max-rounds 5 \
  --output-dir custom_tournament
```

### Session Management
```bash
# List all tournament sessions
python session_manager.py list

# Analyze a specific session in detail
python session_manager.py analyze outputs/tournament_20241207_180512

# Compare multiple tournament sessions
python session_manager.py compare outputs/session1 outputs/session2

# Export session data to JSON/CSV
python session_manager.py export outputs/session1 --output results.json

# Clean up old sessions (older than 30 days)
python session_manager.py cleanup --days 30
```

### Quick Demo
```bash
# Run the demo to see all features
python demo_enhanced.py
```

## 📊 Command Line Options

### Required Arguments
- `--models`: List of Ollama model names (e.g., `phi4:latest qwq:latest`)

### Tournament Options
- `--format`: Tournament format (`single_elimination`, `round_robin`, `swiss`)
- `--best-of`: Games per match (1, 3, 5, 7, etc.)
- `--max-rounds`: Maximum rounds for Swiss tournaments

### Game Configuration
- `--board-size`: Board size (3-10, default: 3)
- `--win-length`: Length needed to win (default: 3)

### LLM Settings
- `--temp`: Temperature for LLM responses (0.0-2.0, default: 0.7)
- `--seed`: Random seed for reproducibility

### Output Options
- `--output-dir`: Base directory for outputs (default: outputs)
- `--session-name`: Custom session name (auto-generated if not provided)
- `--no-viz`: Skip visualization generation
- `--quick`: Minimal output for batch processing

## 🎯 Tournament Formats Explained

### Single Elimination
- **Best for**: Quick tournaments, many players
- **Characteristics**: Players eliminated after one loss, fast results
- **Use case**: Quick competitions with clear winners

### Round Robin
- **Best for**: Comprehensive skill assessment, fewer players
- **Characteristics**: Every player plays every other player
- **Use case**: Determining true skill rankings

### Swiss System
- **Best for**: Balanced tournaments with many players
- **Characteristics**: Players paired by similar performance
- **Use case**: Large tournaments without elimination

## 🎲 Game Configurations

### Board Sizes & Strategy
- **3x3**: Classic quick games (2-10 moves typically)
- **4x4**: Extended gameplay with more strategy
- **5x5+**: Deep strategic play requiring planning

### Win Length Effects
- **Win = Board Size**: Traditional rules (3-in-a-row on 3x3)
- **Win < Board Size**: More strategic with multiple winning paths
- **Large Boards**: Enable complex tactical play

## 🔍 Troubleshooting

### Common Issues

1. **"Model not found" errors**:
   ```bash
   ollama list  # Check available models
   ollama pull model_name:latest  # Pull missing models
   ```

2. **Import errors**:
   ```bash
   pip install -r requirements.txt  # Install dependencies
   ```

3. **Permission errors**:
   ```bash
   chmod +x session_manager.py  # Make scripts executable
   ```

4. **Visualization errors**:
   - Ensure matplotlib is installed: `pip install matplotlib`
   - Use `--no-viz` flag to skip visualizations if needed

### Getting Help
```bash
# See all available options
python main_enhanced.py --help

# Session manager help
python session_manager.py --help

# Check model availability
ollama list
```

## 📈 Performance Tips

1. **Start Small**: Begin with 2-3 models and small boards
2. **Use Swiss Format**: For many players, Swiss is most efficient
3. **Best-of-3**: Good balance of accuracy and speed
4. **Monitor Resources**: Large tournaments with many models can be intensive

## 🔧 Extensibility

The system is designed for easy extension:

- **Add New Games**: Implement the `IGame` interface
- **Custom Tournament Formats**: Extend `TournamentEngine`
- **Enhanced Metrics**: Add statistics to the logging system
- **Visualization Customization**: Modify `enhanced_viz.py`

See `README_ENHANCED.md` for detailed technical documentation.

## 📄 Files Overview

### Core System
- `main_enhanced.py` - Main CLI interface
- `tournament_system.py` - Tournament engine with multiple formats
- `enhanced_logger.py` - Comprehensive logging system
- `session_manager.py` - Session analysis and management tools

### Game Implementation
- `game_interface.py` - Generic game interface
- `generic_tictactoe.py` - Configurable Tic-Tac-Toe
- `connect_four.py` - Connect-Four example game
- `llm_agents.py` - LLM player agents

### Visualization & Analysis
- `enhanced_viz.py` - Tournament visualizations and analytics
- `demo_enhanced.py` - Demonstration script

### Utilities
- `ollama_utils.py` - LLM communication utilities
- `requirements.txt` - Python dependencies

---

🎉 **Ready to run tournaments!** Start with `python main_enhanced.py --models phi4:latest qwq:latest` and explore from there. 