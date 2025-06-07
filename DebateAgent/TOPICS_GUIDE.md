# Debate Topics System Guide

## Overview

The multi-agent debate system now supports **two ways** to specify debate topics:

1. **Predefined Topics**: Use topic keys for 56+ carefully crafted debate questions
2. **Custom Topics**: Provide any custom debate question

## 🎯 Predefined Topics

### Categories Available

- **Technology** (8 topics): AI, social media, privacy, autonomous vehicles, etc.
- **Environment** (7 topics): Nuclear energy, carbon tax, renewable energy, etc.
- **Education** (7 topics): Standardized testing, free college, remote learning, etc.
- **Healthcare** (7 topics): Universal healthcare, vaccines, mental health, etc.
- **Economics** (7 topics): UBI, wealth tax, minimum wage, automation, etc.
- **Ethics** (6 topics): Animal rights, death penalty, consciousness, etc.
- **Lifestyle** (6 topics): Pineapple pizza, daylight saving, video games, etc.
- **Sports** (4 topics): College athletes, performance drugs, esports, etc.
- **Media** (4 topics): Cancel culture, streaming, news bias, content moderation

### How to Use Predefined Topics

```bash
# Use a topic key
python orchestrator.py --topic pineapple_pizza

# See all available topics with full questions
python orchestrator.py --list-topics

# See just the topic keys for quick reference
python orchestrator.py --list-keys
```

### Popular Topic Keys

```bash
# Fun debates
python orchestrator.py --topic pineapple_pizza
python orchestrator.py --topic video_games
python orchestrator.py --topic daylight_saving

# Serious debates
python orchestrator.py --topic ai_education
python orchestrator.py --topic nuclear_energy
python orchestrator.py --topic universal_healthcare

# Controversial debates
python orchestrator.py --topic death_penalty
python orchestrator.py --topic drug_legalization
python orchestrator.py --topic cancel_culture
```

## 🆕 Custom Topics

You can still use any custom debate question:

```bash
# Custom topic examples
python orchestrator.py --topic "Should cats rule the world?"
python orchestrator.py --topic "Is cereal soup?"
python orchestrator.py --topic "Should we replace all politicians with AI?"
```

## 🔄 How It Works

The system automatically detects whether your input is:

1. **A predefined topic key** → Uses the carefully crafted question
2. **A custom question** → Uses your exact text

```python
# Example resolution:
Input: "ai_education" 
→ Output: "Should artificial intelligence replace human teachers in classrooms?"

Input: "Should robots take over?" 
→ Output: "Should robots take over?" (used as-is)
```

## 📊 Topic Statistics

- **Total Topics**: 56 predefined topics
- **Categories**: 9 different categories
- **Range**: From lighthearted (pineapple pizza) to serious (healthcare policy)
- **Quality**: Each topic is phrased as a clear, debatable question

## 🚀 Examples

### Quick Debate Session
```bash
# 2-minute debate on a fun topic
python orchestrator.py --topic pineapple_pizza --num_agents 2 --rounds 1
```

### Serious Policy Debate
```bash
# Extended debate on important policy
python orchestrator.py --topic universal_healthcare --num_agents 4 --rounds 5
```

### Custom Topic Exploration
```bash
# Debate a unique question
python orchestrator.py --topic "Should time travel be regulated by the UN?"
```

## 📁 Enhanced Results System

All debates now save to organized folders:

```
results/
└── 20241207_120000_3agents_5rounds_phi4_Should_pineapple_be_on_pizza/
    ├── transcript.jsonl      # Full debate log
    ├── metadata.json         # Run parameters & system info
    └── (auto-generated)
```

## 🛠️ Adding New Topics

To add new predefined topics, edit `topics.py`:

```python
DEBATE_TOPICS = {
    # Add your topic
    "your_topic_key": "Your debate question here?",
    # ... existing topics
}

# Add to appropriate category
TOPIC_CATEGORIES = {
    "your_category": ["your_topic_key", ...],
    # ... existing categories
}
```

## 💡 Tips

1. **Browse topics first**: Use `--list-topics` to see all options
2. **Use topic keys**: Faster than typing full questions
3. **Mix and match**: Different topics can lead to different argument styles
4. **Custom topics**: Great for testing specific scenarios
5. **Results folders**: Each debate gets its own organized folder

## 🎯 Use Cases

- **Research**: Compare how different models debate the same topic
- **Education**: Use education topics for classroom discussions
- **Entertainment**: Fun topics for casual debates
- **Analysis**: Compare argument quality across topics
- **Testing**: Custom topics for specific scenarios 