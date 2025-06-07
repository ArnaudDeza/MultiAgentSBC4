# Audio Features Guide

## Overview

The multi-agent debate system now includes comprehensive audio generation capabilities using **pyttsx3**, a completely offline text-to-speech engine that requires no internet connection.

## 🎵 Features

### 🔊 **Multi-Voice Support**
- Different voices for each agent (when available)
- Dedicated narrator voice for system messages
- Automatic voice assignment and cycling

### 🎬 **Structured Audio**
- Debate introduction with topic and agent information
- Separate audio segments for each phase:
  - Opening statements
  - Debate rounds
  - Final verdict
- Clear transitions between speakers

### 📁 **Organized Output**
- Audio files saved in organized folders
- Numbered segments for easy playback order
- Summary file listing all audio segments

## 🚀 Getting Started

### Installation

```bash
pip install pyttsx3
# or install all requirements
pip install -r requirements.txt
```

### Test Audio System

```bash
python demo_audio.py
```

This will test:
- Basic TTS functionality
- Available voices on your system
- Full audio generation with sample debate

## 📖 Usage Methods

### 1. Generate Audio During Debate

```bash
# Run debate with audio generation
python orchestrator.py --topic pineapple_pizza --audio --num_agents 2 --rounds 1
```

### 2. Convert Existing Debates

```bash
# Convert all existing debates
python convert_to_audio.py

# Convert specific debate folder
python convert_to_audio.py --folder results/20241207_120000_2agents_1rounds_phi4_pineapple_pizza

# Force regeneration of existing audio
python convert_to_audio.py --force

# List available debates
python convert_to_audio.py --list
```

### 3. Standalone Audio Generation

```python
from audio_generator import generate_debate_audio

# Generate audio from transcript
audio_file = generate_debate_audio(
    transcript_path="path/to/transcript.jsonl",
    output_dir="path/to/audio_output",
    metadata_path="path/to/metadata.json"  # optional
)
```

## 📂 Audio Output Structure

When audio is generated, the following structure is created:

```
debate_folder/
├── transcript.jsonl           # Original debate log
├── metadata.json             # Debate metadata
└── audio/                    # 🆕 Audio files
    ├── 01_introduction.wav   # Debate introduction
    ├── 02_opening_intro.wav  # Opening statements intro
    ├── 03_opening_agent_0.wav # Agent 0 opening
    ├── 03_opening_agent_1.wav # Agent 1 opening
    ├── 04_round_01_intro.wav # Round 1 introduction
    ├── 05_round_01_agent_0.wav # Agent 0 round 1
    ├── 05_round_01_agent_1.wav # Agent 1 round 1
    ├── 06_verdict.wav        # Final verdict
    └── audio_segments.txt    # List of all segments
```

## 🎛️ Configuration Options

### Voice Settings

```python
from audio_generator import DebateAudioGenerator

generator = DebateAudioGenerator(
    base_rate=150,              # Speaking rate (words per minute)
    base_volume=0.9,            # Volume level (0.0 to 1.0)
    pause_between_agents=1.0,   # Pause between agents (seconds)
    pause_between_rounds=2.0    # Pause between rounds (seconds)
)
```

### Available Voices

The system automatically detects and uses available voices on your system:

- **Linux**: espeak voices (various languages/accents)
- **Windows**: SAPI voices (built-in + installed)
- **macOS**: System voices (various languages)

## 🎤 Voice Assignment

- **Agent 0**: First available voice
- **Agent 1**: Second available voice (if exists)
- **Agent N**: Cycles through available voices
- **Narrator**: Always uses first voice for consistency

## 🔧 Troubleshooting

### Common Issues

**"pyttsx3 not available"**
```bash
pip install pyttsx3
```

**"No voices found"**
- Linux: Install espeak (`sudo apt-get install espeak`)
- Windows: Voices should be built-in
- macOS: Voices should be built-in

**Audio files too large**
- Reduce speaking rate: `base_rate=120`
- Limit text length (done automatically)

**Audio quality issues**
- Install additional voice packages for your OS
- Adjust volume and rate settings

### Platform-Specific Notes

**Linux (Ubuntu/Debian)**
```bash
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev
sudo apt-get install festival festvox-kallpc16k
```

**Windows**
- Uses built-in SAPI voices
- Install additional voices from Microsoft Store

**macOS**
- Uses built-in system voices
- Download additional voices in System Preferences

## 🎯 Use Cases

### 🎓 **Educational**
- Classroom demonstrations
- Accessibility for visually impaired
- Language learning (hearing debate structure)

### 🎪 **Entertainment**
- Podcast-style debate content
- Background listening
- Party entertainment with fun topics

### 🔬 **Research**
- Audio analysis of argument patterns
- Comparing debate styles across topics
- Creating audio datasets

### 📊 **Analysis**
- Listening while reviewing transcripts
- Multi-modal analysis (text + audio)
- Sharing results with non-technical audiences

## 📈 Performance

### Typical Generation Times
- **2 agents, 1 round**: ~30 seconds
- **3 agents, 3 rounds**: ~2-3 minutes
- **4 agents, 5 rounds**: ~5-8 minutes

### File Sizes
- **Per minute of audio**: ~500-800 KB (WAV format)
- **Complete debate**: 2-10 MB typical
- **Compression**: Files are uncompressed WAV for quality

## 🚀 Advanced Usage

### Batch Processing

```bash
# Convert all debates in a specific directory
python convert_to_audio.py --results-dir /path/to/debates

# Use custom audio settings
python -c "
from audio_generator import DebateAudioGenerator
generator = DebateAudioGenerator(base_rate=120, base_volume=0.8)
generator.generate_audio_from_transcript('transcript.jsonl', 'audio_out')
"
```

### Integration with Other Tools

```python
# Combine with debate analysis
import json
from audio_generator import generate_debate_audio

# Generate audio for all debates
for debate_folder in debate_folders:
    transcript = os.path.join(debate_folder, 'transcript.jsonl')
    audio_dir = os.path.join(debate_folder, 'audio')
    generate_debate_audio(transcript, audio_dir)
```

## 🎉 Fun Examples

```bash
# Quick fun debate with audio
python orchestrator.py --topic pineapple_pizza --num_agents 2 --rounds 1 --audio

# Serious policy debate with audio
python orchestrator.py --topic universal_healthcare --num_agents 3 --rounds 3 --audio

# Custom silly topic with audio
python orchestrator.py --topic "Should cats be allowed to vote?" --audio
```

The audio system transforms text debates into engaging, accessible audio content that you can listen to anywhere! 