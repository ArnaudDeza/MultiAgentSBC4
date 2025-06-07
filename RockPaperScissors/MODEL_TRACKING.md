# Rock Paper Scissors Royale - Enhanced Model Tracking System

## 🎯 **Clear LLM Model Identification**

The enhanced logging system now provides comprehensive tracking of LLM models throughout tournaments, ensuring clear identification and performance analysis.

### **🔧 Model Identification Strategy**

#### **Agent Naming Convention**
- **Format**: `{model_name}({instance_name})`
- **Examples**: 
  - `llama2(Alpha)` - Llama2 model, instance "Alpha"
  - `phi3(Beta)` - Phi3 model, instance "Beta"
  - `gemma(Gamma)` - Gemma model, instance "Gamma"
  - `random(Baseline)` - Random baseline agent

#### **Automatic Model Extraction**
The system automatically extracts base model names from agent identifiers:
```python
# Agent name: "llama2(Alpha)" → Base model: "llama2"
# Agent name: "phi3(Beta)" → Base model: "phi3"
```

### **📊 Tournament Start Logging**

**Enhanced tournament_start record includes:**
```json
{
  "type": "tournament_start",
  "agent_names": ["llama2(Alpha)", "phi3(Beta)", "gemma(Gamma)"],
  "models": ["llama2", "phi3", "gemma"],
  "unique_models": ["llama2", "phi3", "gemma"],
  "num_participants": 3,
  "num_unique_models": 3,
  "model_metadata": {
    "llama2(Alpha)": {
      "model": "llama2",
      "temperature": 0.7,
      "agent_type": "LLMAgent"
    },
    "phi3(Beta)": {
      "model": "phi3", 
      "temperature": 0.8,
      "agent_type": "LLMAgent"
    }
  }
}
```

**Key Fields:**
- `agent_names`: Full agent identifiers for tracking
- `models`: Base model names extracted from agents
- `unique_models`: Deduplicated list of participating models
- `model_metadata`: Detailed configuration per agent

### **⚔️ Match-Level Model Tracking**

#### **Match Start Records**
```json
{
  "type": "match_start",
  "match_id": "RR001_llama2(Alpha)_vs_phi3(Beta)",
  "player1": "llama2(Alpha)",
  "player2": "phi3(Beta)",
  "player1_model": "llama2",
  "player2_model": "phi3",
  "player1_temperature": 0.7,
  "player2_temperature": 0.8,
  "model_matchup": "llama2_vs_phi3",
  "is_same_model": false
}
```

#### **Match End Records with Model Performance**
```json
{
  "type": "match_end", 
  "player1_model": "llama2",
  "player2_model": "phi3",
  "model_matchup": "llama2_vs_phi3",
  "winner_model": "llama2",
  "is_same_model": false,
  "model_performance": {
    "llama2": {
      "score": 8,
      "win_rate": 0.8,
      "move_distribution": {
        "rock": 0.4, "paper": 0.3, "scissors": 0.3
      }
    },
    "phi3": {
      "score": 2,
      "win_rate": 0.2,
      "move_distribution": {
        "rock": 0.33, "paper": 0.33, "scissors": 0.34
      }
    }
  }
}
```

### **🤖 Model Performance Analytics**

#### **Comprehensive Model Statistics**
The `TournamentAnalyzer.get_model_performance_summary()` provides:

```python
{
  "llama2": {
    "total_matches": 4,
    "wins": 3,
    "losses": 1, 
    "draws": 0,
    "match_win_rate": 0.75,
    "total_rounds": 40,
    "rounds_won": 28,
    "round_win_rate": 0.70,
    "same_model_matches": 1,     # vs other llama2 instances
    "cross_model_matches": 3,    # vs different models
    "opponents_faced": ["phi3", "gemma", "random"],
    "opponent_diversity": 3,
    "average_match_duration": 45.2,
    "total_duration": 180.8
  }
}
```

#### **Analysis Capabilities**

1. **Model vs Model Performance**
   - Track win rates between specific model types
   - Identify model strengths and weaknesses
   - Compare cross-model vs same-model performance

2. **Configuration Impact Analysis**
   - Temperature effects on performance
   - Seed consistency validation
   - Parameter optimization insights

3. **Strategic Pattern Analysis**
   - Model-specific move preferences
   - Adaptation capabilities per model
   - Pattern recognition effectiveness

### **🎯 Research Applications**

#### **LLM Capability Studies**
- **Strategic Reasoning**: Compare how different models approach game theory
- **Pattern Recognition**: Measure adaptation to opponent behavior over time
- **Temperature Effects**: Analyze creativity vs consistency trade-offs
- **Model Scaling**: Compare performance across model sizes

#### **Competitive Analysis**
- **Head-to-Head Rankings**: Direct model comparisons
- **Meta-Game Evolution**: How strategies evolve against specific opponents
- **Robustness Testing**: Performance against various opponent types

### **📈 Visualization & Reporting**

The enhanced system generates model-focused visualizations:

1. **Model Performance Heatmaps**: Win rates between model pairs
2. **Temperature Impact Charts**: Performance vs configuration
3. **Strategic Preference Maps**: Model-specific move distributions
4. **Adaptation Timeline**: Learning curves over multiple matches

### **🔍 Usage Examples**

#### **Basic Model Tracking**
```python
from utils import load_tournament_data, TournamentAnalyzer

# Load tournament data
data = load_tournament_data("tournament.jsonl")
analyzer = TournamentAnalyzer(data)

# Get model performance summary
model_stats = analyzer.get_model_performance_summary()

# Analyze specific model
llama_performance = model_stats["llama2"]
print(f"Llama2 win rate: {llama_performance['match_win_rate']:.1%}")
print(f"Opponents faced: {llama_performance['opponents_faced']}")
```

#### **Tournament Configuration**
```python
# Create agents with clear model identification
agents = [
    create_agent("llama2", temperature=0.7, name="llama2(Strategic)"),
    create_agent("phi3", temperature=0.8, name="phi3(Creative)"), 
    create_agent("gemma", temperature=0.6, name="gemma(Conservative)")
]

# Run tournament with enhanced logging
tournament = TournamentManager()
results = tournament.run_round_robin(agents, rounds_per_match=15)
```

### **✅ Validation & Testing**

The system includes comprehensive testing:
- Mock tournament generation with realistic model data
- Analytics validation across different model types
- Edge case handling (same models, missing metadata)
- Performance metric accuracy verification

### **🚀 Production Readiness**

**Features for GPU Node Deployment:**
- Automatic model detection from Ollama
- Robust error handling for LLM failures
- Scalable logging for large tournaments
- Memory-efficient data structures
- Real-time analytics generation

**Integration Points:**
- Direct integration with Ollama model queries
- Automatic temperature and seed tracking
- Match timing and performance monitoring
- Comprehensive error logging and recovery

---

**The enhanced model tracking system provides unprecedented visibility into LLM strategic behavior, enabling sophisticated research and analysis of AI decision-making in competitive environments! 🎯** 