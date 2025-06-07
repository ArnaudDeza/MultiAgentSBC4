# Rock Paper Scissors Royale - Enhanced Logging & Analytics System

## 📊 **Comprehensive Data Logging**

The enhanced logging system captures extensive tournament data for sophisticated analysis and visualization.

### **Log Record Types**

#### 1. Tournament Start (`tournament_start`)
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "type": "tournament_start",
  "models": ["phi3", "llama2", "gemma"],
  "num_participants": 3,
  "tournament_type": "round_robin",
  "rounds": 10,
  "temperature": 0.7,
  "seed": 42,
  "expected_total_matches": 3
}
```

#### 2. Match Start (`match_start`)
```json
{
  "timestamp": "2024-01-01T12:00:05",
  "type": "match_start",
  "match_id": "RR001_phi3_vs_llama2",
  "player1": "phi3",
  "player2": "llama2",
  "rounds_in_match": 10,
  "match_number": 1
}
```

#### 3. Individual Round (`match`)
```json
{
  "timestamp": "2024-01-01T12:00:06",
  "type": "match",
  "match_id": "M0001",
  "player1": "phi3",
  "player2": "llama2",
  "move1": "rock",
  "move2": "paper",
  "result1": "loss",
  "result2": "win"
}
```

#### 4. Match End (`match_end`) - **NEW ENHANCED RECORD**
```json
{
  "timestamp": "2024-01-01T12:01:30",
  "type": "match_end",
  "match_id": "RR001_phi3_vs_llama2",
  "player1": "phi3",
  "player2": "llama2",
  "winner": "llama2",
  "final_score": "6-4",
  "player1_score": 4,
  "player2_score": 6,
  "draws": 0,
  "total_rounds": 10,
  "player1_win_rate": 0.4,
  "player2_win_rate": 0.6,
  "player1_move_frequency": {"rock": 3, "paper": 4, "scissors": 3},
  "player2_move_frequency": {"rock": 2, "paper": 5, "scissors": 3},
  "move_sequences": [
    {"round": 1, "player1_move": "rock", "player2_move": "paper"},
    {"round": 2, "player1_move": "scissors", "player2_move": "rock"},
    ...
  ],
  "player1_streaks": {
    "longest_win_streak": 2,
    "longest_loss_streak": 3,
    "current_streak": -1,
    "streak_type": "loss"
  },
  "player2_streaks": {
    "longest_win_streak": 3,
    "longest_loss_streak": 2,
    "current_streak": 1,
    "streak_type": "win"
  },
  "match_duration_seconds": 85.2
}
```

#### 5. Agent Analysis (`agent_analysis`) - **NEW RECORD TYPE**
```json
{
  "timestamp": "2024-01-01T12:05:00",
  "type": "agent_analysis",
  "agent_name": "phi3",
  "total_matches": 3,
  "overall_win_rate": 0.67,
  "favorite_move": "paper",
  "move_entropy": 0.95,
  "adaptability_score": 0.73,
  "consistency_rating": "high"
}
```

#### 6. Head-to-Head (`head_to_head`) - **NEW RECORD TYPE**
```json
{
  "timestamp": "2024-01-01T12:05:05",
  "type": "head_to_head",
  "player1": "phi3",
  "player2": "llama2",
  "total_encounters": 15,
  "player1_dominance": 0.6,
  "move_countering_effectiveness": 0.45,
  "pattern_recognition_success": 0.78
}
```

#### 7. Enhanced Tournament End (`tournament_end`)
```json
{
  "timestamp": "2024-01-01T12:15:00",
  "type": "tournament_end",
  "tournament_start_time": "2024-01-01T12:00:00",
  "tournament_end_time": "2024-01-01T12:15:00",
  "tournament_duration_seconds": 900,
  "final_standings": {...},
  "champion": "phi3",
  "total_participants": 3,
  "total_matches_played": 3,
  "matches_per_participant": 1.0
}
```

## 🔍 **Advanced Analytics Engine**

### **TournamentAnalyzer Class**

The `TournamentAnalyzer` class provides comprehensive data analysis capabilities:

```python
from utils import load_tournament_data, TournamentAnalyzer

# Load and analyze tournament data
data = load_tournament_data("data/logs/tournament.jsonl")
analyzer = TournamentAnalyzer(data)

# Get detailed agent statistics
agent_stats = analyzer.get_agent_statistics("phi3")
print(f"Win Rate: {agent_stats['match_win_rate']:.1%}")
print(f"Move Distribution: {agent_stats['move_distribution']}")

# Head-to-head analysis
h2h = analyzer.get_head_to_head_analysis("phi3", "llama2")
print(f"Head-to-head record: {h2h['agent1_wins']}-{h2h['agent2_wins']}")

# Move effectiveness analysis
effectiveness = analyzer.get_move_effectiveness_matrix()
print(f"Rock vs Paper win rate: {effectiveness['rock']['paper']['win_rate']:.1%}")
```

### **Key Analytics Methods**

1. **`get_agent_statistics(agent_name)`**
   - Round-level and match-level performance
   - Move frequency and distribution analysis
   - Opponent diversity metrics
   - Experience indicators

2. **`get_head_to_head_analysis(agent1, agent2)`**
   - Direct matchup statistics
   - Win rate comparisons
   - Detailed round-by-round history

3. **`get_move_effectiveness_matrix()`**
   - Global move vs move win rates
   - Statistical significance indicators
   - Total encounter counts

4. **`get_tournament_summary()`**
   - Overall tournament metadata
   - Global statistics and trends
   - Configuration tracking

## 📈 **Advanced Visualization System**

### **Three-Tier Visualization Approach**

#### **1. Basic Analysis Plots** (`basic_tournament_analysis.png`)
- **Move Frequency Heatmap**: Agent-specific move preferences
- **Round vs Match Win Rates**: Dual performance comparison
- **Enhanced Move Effectiveness Matrix**: Tactical analysis with encounter counts
- **Tournament Statistics Dashboard**: Comprehensive overview with visual bars

#### **2. Advanced Analysis Plots** (`advanced_tournament_analysis.png`)
- **Agent Performance Ranking**: Horizontal bar chart with gradient colors
- **Head-to-Head Win Rate Matrix**: Inter-agent dominance patterns
- **Move Distribution Pie Charts**: Individual agent strategies (for ≤4 agents)
- **Tournament Timeline**: Score progression over rounds

#### **3. Agent Comparison Plots** (`agent_comparison_analysis.png`)
- **Multi-Metric Comparison**: Normalized performance across dimensions
- **Move Preference Scatter Plot**: Strategic positioning analysis
- **Performance vs Experience**: Correlation visualization
- **Agent Statistics Table**: Professional summary table

### **Visualization Features**

- **High-Resolution Output**: 300 DPI PNG files for publication quality
- **Professional Styling**: Consistent color schemes and typography
- **Interactive Elements**: Hover information and detailed annotations
- **Adaptive Layouts**: Responsive to different numbers of participants
- **Statistical Overlays**: Confidence intervals and significance indicators

## 🎯 **Key Enhancements**

### **1. Match-Level Analysis**
- Complete move sequences captured
- Streak detection and analysis
- Match duration tracking
- Performance pattern identification

### **2. Strategic Insights**
- Move effectiveness matrices
- Counter-strategy success rates
- Adaptation measurement
- Pattern recognition assessment

### **3. Tournament Intelligence**
- Real-time performance tracking
- Predictive analytics foundation
- Comparative benchmarking
- Historical trend analysis

### **4. Professional Reporting**
- Publication-ready visualizations
- Comprehensive statistical summaries
- Executive dashboard views
- Research-grade documentation

## 📊 **Data Export Capabilities**

### **JSONL Format Benefits**
- **Streaming Analytics**: Process large tournaments incrementally
- **Version Control Friendly**: Line-by-line git diffs
- **Tool Compatibility**: Easy import into pandas, R, or other analytics tools
- **Compression Efficient**: Excellent compression ratios for storage

### **Analysis Workflows**

```python
# Load and analyze
analyzer = TournamentAnalyzer(load_tournament_data())

# Generate all visualizations
create_visualization_plots(analyzer.data, "output/")

# Export summary statistics
summary = analyzer.get_tournament_summary()
with open("tournament_report.json", "w") as f:
    json.dump(summary, f, indent=2)

# Generate agent reports
for agent in analyzer.agents:
    agent_report = analyzer.get_agent_statistics(agent)
    with open(f"reports/{agent}_analysis.json", "w") as f:
        json.dump(agent_report, f, indent=2)
```

## 🔮 **Research Applications**

This enhanced logging system enables sophisticated research into:

- **LLM Strategic Reasoning**: How different models approach game theory
- **Pattern Recognition Capabilities**: Adaptation to opponent behavior
- **Temperature Effects**: Impact of randomness on strategic play
- **Model Comparison**: Objective performance benchmarking
- **Emergent Strategies**: Discovery of novel tactical approaches

The system provides a solid foundation for academic research into LLM capabilities in strategic environments.

---

**The enhanced logging system transforms Rock Paper Scissors Royale from a simple game into a comprehensive research platform for studying LLM strategic behavior!** 🚀 