# Quick Usage Guide

## 🚀 Getting Started (30 seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure you have models in Ollama
ollama pull phi4:latest
ollama pull qwq:latest

# 3. Run your first tournament
python main_enhanced.py --models phi4:latest qwq:latest
```

## 🎮 Common Commands

```bash
# Basic 2-player tournament
python main_enhanced.py --models phi4:latest qwq:latest

# Round robin with 3 players  
python main_enhanced.py --models phi4:latest qwq:latest llama3.2:1b --format round_robin

# Best-of-3 matches
python main_enhanced.py --models phi4:latest qwq:latest --best-of 3

# Larger board (5x5, need 4 in a row)
python main_enhanced.py --models phi4:latest qwq:latest --board-size 5 --win-length 4

# Swiss tournament with 4+ players
python main_enhanced.py --models phi4:latest qwq:latest llama3.2:1b phi4:mini --format swiss --max-rounds 3

# Quick demo
python demo_enhanced.py
```

## 📁 Session Management

```bash
# List all tournaments
python session_manager.py list

# Analyze a tournament
python session_manager.py analyze outputs/tournament_20241207_180512

# Compare tournaments
python session_manager.py compare outputs/session1 outputs/session2
```

## 🔧 Options Reference

### Tournament Formats
- `--format single_elimination` (default)
- `--format round_robin` 
- `--format swiss`

### Game Settings
- `--board-size 3` (default, can be 3-10)
- `--win-length 3` (default, usually same as board size)
- `--best-of 1` (default, can be 1,3,5,7+)

### Output
- `--output-dir outputs` (default)
- `--session-name custom_name` (auto-generated if not provided)
- `--no-viz` (skip visualizations)
- `--quick` (minimal output)

---

📖 **For full documentation**: See `README.md` or `README_ENHANCED.md` 