# Enhanced Multi-Agent Game Tournament System

A flexible, extensible tournament system for LLM agents playing various games with configurable formats and visualizations.

## 🚀 New Features

### Flexible Tournament Formats
- **Single Elimination**: Traditional knockout tournament
- **Round Robin**: Every player plays every other player
- **Swiss System**: Pairings based on current standings
- **Best-of-X Matches**: LLMs face off in multiple games per round

### Generic Game Interface
- **Configurable Board Sizes**: 3x3, 4x4, 5x5, up to 10x10
- **Flexible Win Conditions**: 3-in-a-row, 4-in-a-row, or custom
- **Multiple Games**: Tic-Tac-Toe, Connect-Four (with easy expansion)
- **Extensible Design**: Easy to add new games

### Enhanced Visualizations
- **Tournament Brackets**: Visual bracket progression
- **Performance Heatmaps**: Player statistics and comparisons
- **Win Rate Trends**: Performance over time
- **Match Flow Diagrams**: Tournament progression analysis
- **Interactive Charts**: Enhanced UI with detailed metrics

## 📁 Project Structure

```
TicTacToeAgent/
├── main_enhanced.py          # Enhanced CLI interface
├── game_interface.py         # Generic game interface (IGame)
├── generic_tictactoe.py      # Configurable Tic-Tac-Toe implementation
├── connect_four.py           # Connect-Four example
├── llm_agents.py            # LLM agents for new interface
├── tournament_system.py      # Flexible tournament engine
├── enhanced_viz.py          # Enhanced visualization system
├── enhanced_logger.py       # Advanced logging with JSON storage
├── session_manager.py       # Session management utility
├── logger.py                # Tournament logging
├── ollama_utils.py          # LLM communication
└── outputs/                 # Organized output directory structure
```

## 📝 Enhanced Logging System

The system features comprehensive logging with automatic file management and organized output structure:

### Output Directory Structure
Each tournament creates a timestamped session directory with all related files:
```
outputs/
├── tournament_sing_3x3_w3_4p_20241201_143022/
│   ├── logs/
│   │   ├── moves.jsonl              # Individual game moves
│   │   └── results.jsonl            # Tournament events & results
│   ├── plots/
│   │   ├── tournament_bracket.png   # Visual tournament progression
│   │   ├── performance_heatmap.png  # Player performance analysis
│   │   └── win_rate_trends.png     # Performance trends over time
│   ├── data/
│   │   ├── tournament_config.json   # Complete tournament configuration
│   │   ├── session_metadata.json   # Session timing and metadata
│   │   └── tournament_summary.json # Final results and statistics
│   └── session_summary.json        # Complete session data overview
```

### Automatic File Naming
Session directories are automatically named with descriptive information:
- `sing` = Single Elimination, `roun` = Round Robin, `swis` = Swiss
- `3x3` = Board size
- `w3` = Win length requirement
- `4p` = Number of players
- `20241201_143022` = Timestamp

### Session Management
```bash
# List all tournament sessions
python session_manager.py list

# Analyze a specific session with detailed breakdown
python session_manager.py analyze outputs/tournament_20241201_143022

# Compare performance across multiple sessions
python session_manager.py compare outputs/session1 outputs/session2

# Export session data to different formats
python session_manager.py export outputs/session1 --output data.json --format json
python session_manager.py export outputs/session1 --output data.csv --format csv

# Clean up old sessions (dry run by default)
python session_manager.py cleanup --days 30
python session_manager.py cleanup --days 30 --no-dry-run  # Actually delete

# Regenerate visualizations for existing session
python session_manager.py analyze outputs/session1 --regenerate-viz
```

### JSON Configuration Storage
All tournament parameters are automatically saved to JSON files:
- **Complete CLI arguments**: All command-line options used
- **Tournament configuration**: Format, best-of, rounds, etc.
- **Game configuration**: Board size, win conditions, etc.
- **Model information**: List of participating models
- **Session metadata**: Timing, duration, file tracking

## 🎮 Usage Examples

### Basic Enhanced Tournament
```bash
python main_enhanced.py --models phi4 qwq
```

### Different Tournament Formats
```bash
# Round Robin with best-of-3 matches
python main_enhanced.py --models phi4 qwq llama3.3 --format round_robin --best-of 3

# Swiss tournament with 6 rounds
python main_enhanced.py --models phi4:latest mistral:latest mistral-small:latest llama3.2:1b --format swiss --max-rounds 3
```

### Different Game Configurations
```bash
# Large board Tic-Tac-Toe (5x5, need 4 in a row)
python main_enhanced.py --models phi4 qwq --board-size 5 --win-length 4

# Quick games with smaller board
python main_enhanced.py --models phi4 qwq --board-size 3 --win-length 3 --quick
```

### Advanced Options
```bash
# Custom tournament with all options
python main_enhanced.py \
  --models phi4 qwq llama3.3 phi4-mini \
  --format swiss \
  --best-of 3 \
  --board-size 4 \
  --win-length 3 \
  --temp 0.8 \
  --seed 123 \
  --max-rounds 5 \
  --output-dir custom_plots
```

## 🎯 Tournament Formats

### Single Elimination
- Traditional knockout tournament
- Fastest format for many players
- Clear bracket progression
- Eliminates players after one loss

### Round Robin
- Every player plays every other player
- Most comprehensive format
- Best for determining true skill ranking
- Takes longer with many players

### Swiss System
- Players paired by similar performance
- Avoids rematches when possible
- Good balance of speed and accuracy
- Popular in chess tournaments

## 🎲 Game Configurations

### Board Sizes
- **3x3**: Classic Tic-Tac-Toe
- **4x4**: Extended gameplay
- **5x5**: Strategic depth
- **Custom**: Up to 10x10

### Win Conditions
- **3-in-a-row**: Quick games
- **4-in-a-row**: Balanced strategy
- **Custom**: Match board size or set independently

### Best-of-X Matches
- **Best-of-1**: Quick elimination
- **Best-of-3**: Reduces luck factor
- **Best-of-5**: Tournament standard
- **Best-of-7**: Championship format

## 📊 Enhanced Visualizations

### Tournament Brackets
- Visual representation of tournament progression
- Color-coded winners and losers
- Match scores and details
- Format-specific layouts

### Performance Metrics
- Win rate distributions
- Points progression over time
- Game efficiency analysis
- Head-to-head comparisons

### Statistical Analysis
- Rolling win rates
- Performance trends
- Player rankings
- Tournament statistics

## 🔧 Extensibility

### Adding New Games

1. **Implement IGame Interface**:
```python
class MyGame(IGame):
    def make_move(self, move, player): ...
    def is_valid_move(self, move, player): ...
    def is_game_over(self): ...
    def get_state(self): ...
    def get_valid_moves(self, player): ...
    def copy(self): ...
    def display(self): ...
    def get_game_config(self): ...
```

2. **Create Game Factory**:
```python
def create_my_game_factory(config):
    def factory():
        return MyGame(config)
    return factory
```

3. **Update Agent Prompts** (in `llm_agents.py`):
```python
def _create_my_game_prompt(self, game_state, player_id, game, valid_moves):
    # Game-specific prompt for LLM
    return prompt
```

### Adding Tournament Formats

Extend `TournamentEngine` with new format methods:
```python
def _run_my_format(self) -> Dict[str, Any]:
    # Implement custom tournament logic
    pass
```

## 📝 Enhanced Logging System

The system features comprehensive logging with automatic file management and organized output structure:

### Output Directory Structure
Each tournament creates a timestamped session directory with all related files:
```
outputs/
├── tournament_sing_3x3_w3_4p_20241201_143022/
│   ├── logs/
│   │   ├── moves.jsonl              # Individual game moves
│   │   └── results.jsonl            # Tournament events & results
│   ├── plots/
│   │   ├── tournament_bracket.png   # Visual tournament progression
│   │   ├── performance_heatmap.png  # Player performance analysis
│   │   └── win_rate_trends.png     # Performance trends over time
│   ├── data/
│   │   ├── tournament_config.json   # Complete tournament configuration
│   │   ├── session_metadata.json   # Session timing and metadata
│   │   └── tournament_summary.json # Final results and statistics
│   └── session_summary.json        # Complete session data overview
```

### Session Management
```bash
# List all tournament sessions
python session_manager.py list

# Analyze a specific session with detailed breakdown
python session_manager.py analyze outputs/tournament_20241201_143022

# Compare performance across multiple sessions
python session_manager.py compare outputs/session1 outputs/session2

# Export session data to different formats
python session_manager.py export outputs/session1 --output data.json

# Clean up old sessions (older than 30 days)
python session_manager.py cleanup --days 30
```

## 🎨 Visualization Customization

### Matplotlib Styling
```python
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.size'] = 12
```

### Custom Metrics
Add new statistics to tournament results:
```python
def calculate_custom_metric(standings):
    # Custom performance calculation
    return metric_value
```

## 📈 Performance Features

### Best-of-X Match Benefits
- **Reduced Variance**: Multiple games per match reduce random outcomes
- **True Skill Assessment**: Better differentiation between player abilities
- **Strategic Adaptation**: Players can adjust strategy between games
- **Tournament Integrity**: More reliable championship determination

### Swiss Tournament Advantages
- **Balanced Competition**: Players face opponents of similar skill
- **No Early Elimination**: All players play full tournament
- **Efficient Pairing**: Avoids repeated matchups
- **Scalable**: Works well with any number of players

## 🛠️ Configuration Options

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--models` | phi4, qwq | LLM models to compete |
| `--format` | single_elimination | Tournament format |
| `--best-of` | 1 | Games per match (auto-adjusted to odd) |
| `--board-size` | 3 | Game board size (NxN) |
| `--win-length` | 3 | Pieces in a row to win |
| `--temp` | 0.7 | LLM temperature |
| `--seed` | 42 | Random seed |
| `--max-rounds` | 10 | Swiss tournament rounds |
| `--output-dir` | plots | Visualization directory |

### Game Configuration
```python
GameConfig(
    board_size=5,      # 5x5 board
    win_length=4,      # Need 4 in a row
    num_players=2,     # Two players
    max_moves=100      # Max moves before draw
)
```

### Tournament Configuration
```python
TournamentConfig(
    format=TournamentFormat.ROUND_ROBIN,
    best_of=3,         # Best of 3 games
    shuffle_players=True,
    seed=42,
    max_rounds=8       # For Swiss
)
```

## 🔍 Analysis Features

### Statistical Insights
- Win rates by player and opponent
- Performance trends over tournament
- Game length analysis
- Move pattern analysis

### Visual Analytics
- Tournament progression trees
- Performance correlation matrices
- Win rate distribution histograms
- Time-series performance plots

## 🚀 Getting Started

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run Enhanced Tournament**:
```bash
python main_enhanced.py --models phi4 qwq --format round_robin --best-of 3
```

3. **View Results**:
- Check terminal output for standings
- Open `plots/` directory for visualizations
- Review `logs/enhanced_tournament.jsonl` for detailed logs

## 🎯 Future Enhancements

### Planned Features
- [ ] Double elimination tournaments
- [ ] Gomoku/Five-in-a-Row implementation
- [ ] Interactive web dashboard
- [ ] Real-time tournament streaming
- [ ] ELO rating system
- [ ] Multi-threaded parallel matches

### Extensibility Roadmap
- [ ] Plugin system for games
- [ ] Custom scoring systems
- [ ] Tournament templates
- [ ] AI vs Human modes
- [ ] Team tournaments

## 📝 Example Tournament Scenarios

### Scenario 1: LLM Model Comparison
```bash
python main_enhanced.py \
  --models phi4 qwq llama3.3 phi4-mini \
  --format round_robin \
  --best-of 5 \
  --board-size 3
```

### Scenario 2: Strategic Depth Analysis
```bash
python main_enhanced.py \
  --models phi4 qwq \
  --format swiss \
  --board-size 5 \
  --win-length 4 \
  --best-of 3 \
  --max-rounds 10
```

### Scenario 3: Quick Assessment
```bash
python main_enhanced.py \
  --models phi4 qwq llama3.3 \
  --format single_elimination \
  --quick \
  --no-viz
```

This enhanced system provides a comprehensive platform for evaluating LLM capabilities across different game scenarios while maintaining extensibility for future games and tournament formats. 