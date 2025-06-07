#!/usr/bin/env python3
"""
Demo script to test the audio generation functionality.
"""

import os
import json
import tempfile
from datetime import datetime
from audio_generator import DebateAudioGenerator


def create_sample_transcript():
    """Create a sample debate transcript for testing."""
    transcript = [
        {
            "timestamp": "2024-12-07T12:00:00.000000",
            "event": "debate_start",
            "topic": "Should pineapple be an acceptable pizza topping?",
            "num_agents": 2,
            "rounds": 1,
            "model": "phi4",
            "temperature": 0.7,
            "seed": 42
        },
        {
            "timestamp": "2024-12-07T12:00:15.000000",
            "round": 0,
            "agent": 0,
            "message": "I strongly believe that pineapple belongs on pizza. The sweet and tangy flavor of pineapple creates a perfect balance with savory ingredients like ham and cheese. This combination has been enjoyed worldwide for decades.",
            "type": "opening_statement"
        },
        {
            "timestamp": "2024-12-07T12:00:30.000000",
            "round": 0,
            "agent": 1,
            "message": "I respectfully disagree. Pineapple's high water content makes pizza soggy, and the sweet flavor clashes with traditional Italian ingredients. Pizza should maintain its savory integrity without fruit interference.",
            "type": "opening_statement"
        },
        {
            "timestamp": "2024-12-07T12:00:45.000000",
            "round": 1,
            "agent": 0,
            "message": "While I understand the texture concern, modern pizza preparation techniques can address the moisture issue. Moreover, culinary evolution has always included fusion elements. Hawaiian pizza represents cultural adaptation and innovation.",
            "type": "debate_response"
        },
        {
            "timestamp": "2024-12-07T12:01:00.000000",
            "round": 1,
            "agent": 1,
            "message": "Innovation should enhance, not detract from, established culinary traditions. Pizza originated in Italy as a carefully balanced dish. Adding pineapple fundamentally alters this balance and disrespects the cultural heritage of authentic pizza.",
            "type": "debate_response"
        },
        {
            "timestamp": "2024-12-07T12:01:15.000000",
            "event": "verdict",
            "winner": "A",
            "justification": "Agent A provided more compelling arguments about culinary evolution and practical solutions to texture concerns, while acknowledging the opposition's points."
        }
    ]
    return transcript


def create_sample_metadata():
    """Create sample metadata for testing."""
    return {
        "debate_info": {
            "topic": "Should pineapple be an acceptable pizza topping?",
            "num_agents": 2,
            "rounds": 1,
            "model": "phi4",
            "temperature": 0.7,
            "seed": 42
        },
        "timing": {
            "start_time": "2024-12-07T12:00:00.000000",
            "end_time": "2024-12-07T12:01:30.000000",
            "duration_seconds": 90.0,
            "duration_human": "1m 30s"
        },
        "results": {
            "winner": "A",
            "justification": "Agent A provided more compelling arguments about culinary evolution and practical solutions to texture concerns, while acknowledging the opposition's points.",
            "total_messages": 6
        }
    }


def test_basic_tts():
    """Test basic text-to-speech functionality."""
    print("🔊 Testing basic TTS functionality...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Test basic speech
        test_text = "Hello! This is a test of the debate audio system."
        print(f"Speaking: {test_text}")
        
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ Basic TTS test successful!")
        return True
        
    except ImportError:
        print("❌ pyttsx3 not installed. Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False


def test_voice_detection():
    """Test available voices on the system."""
    print("\n🎤 Testing available voices...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if voices:
            print(f"Found {len(voices)} voice(s):")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name} ({voice.id})")
        else:
            print("No additional voices found (using default)")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice detection failed: {e}")
        return False


def test_audio_generation():
    """Test full audio generation with sample debate."""
    print("\n🎬 Testing full audio generation...")
    
    try:
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample transcript
            transcript_path = os.path.join(temp_dir, "sample_transcript.jsonl")
            transcript_data = create_sample_transcript()
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                for record in transcript_data:
                    f.write(json.dumps(record) + '\n')
            
            # Create sample metadata
            metadata_path = os.path.join(temp_dir, "sample_metadata.json")
            metadata = create_sample_metadata()
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Generate audio
            audio_dir = os.path.join(temp_dir, "audio_output")
            generator = DebateAudioGenerator()
            
            print(f"Generating audio in: {audio_dir}")
            main_file = generator.generate_audio_from_transcript(
                transcript_path, audio_dir, metadata
            )
            
            # List generated files
            if os.path.exists(audio_dir):
                audio_files = sorted(os.listdir(audio_dir))
                print(f"✅ Generated {len(audio_files)} audio file(s):")
                for file in audio_files:
                    file_path = os.path.join(audio_dir, file)
                    size_kb = os.path.getsize(file_path) / 1024
                    print(f"  - {file} ({size_kb:.1f} KB)")
            
            print("✅ Full audio generation test successful!")
            print("Note: Audio files were created in temporary directory and will be cleaned up.")
            
        return True
        
    except Exception as e:
        print(f"❌ Audio generation test failed: {e}")
        return False


def main():
    """Run all audio tests."""
    print("🎵 Debate Audio System Test Suite")
    print("=" * 40)
    
    tests = [
        ("Basic TTS", test_basic_tts),
        ("Voice Detection", test_voice_detection),
        ("Audio Generation", test_audio_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{passed+1}/{total}] {test_name}")
        print("-" * 20)
        
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Audio system is ready to use.")
        print("\nNext steps:")
        print("  1. Run a debate with --audio flag:")
        print("     python orchestrator.py --topic pineapple_pizza --num_agents 2 --rounds 1 --audio")
        print("  2. Convert existing debates:")
        print("     python convert_to_audio.py")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main() 