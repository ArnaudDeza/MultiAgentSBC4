"""
Audio generation for multi-agent debate transcripts using pyttsx3.
"""

import pyttsx3
import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class DebateAudioGenerator:
    """Generate audio transcripts of debates using text-to-speech."""
    
    def __init__(self, 
                 base_rate: int = 150,
                 base_volume: float = 0.9,
                 pause_between_agents: float = 1.0,
                 pause_between_rounds: float = 2.0):
        """
        Initialize the audio generator.
        
        Args:
            base_rate: Base speaking rate (words per minute)
            base_volume: Base volume level (0.0 to 1.0)
            pause_between_agents: Pause between agent responses (seconds)
            pause_between_rounds: Pause between debate rounds (seconds)
        """
        self.base_rate = base_rate
        self.base_volume = base_volume
        self.pause_between_agents = pause_between_agents
        self.pause_between_rounds = pause_between_rounds
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        
        # Get available voices
        self.voices = self.engine.getProperty('voices')
        self.voice_assignments = {}
        
        # Configure default voice settings
        self.engine.setProperty('rate', base_rate)
        self.engine.setProperty('volume', base_volume)
    
    def assign_voices(self, num_agents: int) -> Dict[int, str]:
        """
        Assign different voices to agents if available.
        
        Args:
            num_agents: Number of agents in the debate
            
        Returns:
            Dictionary mapping agent IDs to voice descriptions
        """
        if not self.voices:
            return {i: "Default Voice" for i in range(num_agents)}
        
        assignments = {}
        for i in range(num_agents):
            if i < len(self.voices):
                voice = self.voices[i]
                assignments[i] = f"Voice {i+1}"
                # Store the voice ID for later use
                self.voice_assignments[i] = voice.id
            else:
                # Cycle through available voices
                voice_idx = i % len(self.voices)
                voice = self.voices[voice_idx]
                assignments[i] = f"Voice {voice_idx+1} (recycled)"
                self.voice_assignments[i] = voice.id
        
        return assignments
    
    def set_voice_for_agent(self, agent_id: int) -> None:
        """Set the TTS voice for a specific agent."""
        if agent_id in self.voice_assignments:
            self.engine.setProperty('voice', self.voice_assignments[agent_id])
    
    def set_narrator_voice(self) -> None:
        """Set voice for narrator (system messages)."""
        # Use the first available voice or default
        if self.voices:
            self.engine.setProperty('voice', self.voices[0].id)
    
    def clean_text_for_tts(self, text: str) -> str:
        """
        Clean text to make it more suitable for TTS.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text suitable for TTS
        """
        # Remove or replace problematic characters
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('...', ' pause ')
        text = text.replace('--', ' dash ')
        text = text.replace('*', '')
        text = text.replace('#', 'number ')
        
        # Clean up multiple spaces
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Limit length for better TTS processing
        if len(text) > 1000:
            # Try to break at sentence boundaries
            sentences = text.split('. ')
            if len(sentences) > 1:
                text = '. '.join(sentences[:3]) + '.'
            else:
                text = text[:1000] + "..."
        
        return text
    
    def speak_with_pause(self, text: str, pause_after: float = 0) -> None:
        """
        Speak text and add pause.
        
        Args:
            text: Text to speak
            pause_after: Pause duration after speaking (seconds)
        """
        cleaned_text = self.clean_text_for_tts(text)
        self.engine.say(cleaned_text)
        self.engine.runAndWait()
        
        if pause_after > 0:
            time.sleep(pause_after)
    
    def save_audio_segment(self, text: str, output_file: str) -> None:
        """
        Save text as audio file.
        
        Args:
            text: Text to convert
            output_file: Output file path
        """
        cleaned_text = self.clean_text_for_tts(text)
        self.engine.save_to_file(cleaned_text, output_file)
        self.engine.runAndWait()
    
    def generate_debate_intro(self, topic: str, num_agents: int, rounds: int, model: str) -> str:
        """Generate introduction text for the debate."""
        voice_assignments = self.assign_voices(num_agents)
        
        intro = f"""
        Welcome to the Multi-Agent Debate System.
        
        Today's topic is: {topic}
        
        We have {num_agents} AI agents participating in this debate, 
        powered by the {model} language model.
        
        The debate will consist of {rounds} rounds, with opening statements followed by structured arguments.
        
        Voice assignments are as follows:
        """
        
        for agent_id, voice_desc in voice_assignments.items():
            intro += f" Agent {agent_id} will use {voice_desc}."
        
        intro += " Let's begin the debate!"
        
        return intro
    
    def generate_audio_from_transcript(self, 
                                     transcript_path: str, 
                                     output_dir: str,
                                     metadata: Optional[Dict] = None) -> str:
        """
        Generate complete audio from debate transcript.
        
        Args:
            transcript_path: Path to JSONL transcript file
            output_dir: Directory to save audio files
            metadata: Optional metadata dictionary
            
        Returns:
            Path to the main audio file
        """
        # Load transcript
        transcript = self.load_transcript(transcript_path)
        
        if not transcript:
            raise ValueError("No transcript data found")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract debate info
        debate_info = self.extract_debate_info(transcript, metadata)
        
        # Generate introduction
        self.set_narrator_voice()
        intro_text = self.generate_debate_intro(
            debate_info['topic'],
            debate_info['num_agents'], 
            debate_info['rounds'],
            debate_info['model']
        )
        
        # Save introduction
        intro_file = os.path.join(output_dir, "01_introduction.wav")
        self.save_audio_segment(intro_text, intro_file)
        print(f"Generated: {intro_file}")
        
        # Process transcript by sections
        audio_files = [intro_file]
        
        # Opening statements
        opening_files = self.generate_opening_statements_audio(transcript, output_dir)
        audio_files.extend(opening_files)
        
        # Debate rounds
        round_files = self.generate_rounds_audio(transcript, output_dir)
        audio_files.extend(round_files)
        
        # Verdict
        verdict_file = self.generate_verdict_audio(transcript, output_dir)
        if verdict_file:
            audio_files.append(verdict_file)
        
        # Generate summary file listing all segments
        summary_file = os.path.join(output_dir, "audio_segments.txt")
        with open(summary_file, 'w') as f:
            f.write("Debate Audio Segments:\n")
            f.write("=" * 30 + "\n\n")
            for i, file_path in enumerate(audio_files, 1):
                filename = os.path.basename(file_path)
                f.write(f"{i:2d}. {filename}\n")
        
        print(f"Generated {len(audio_files)} audio segments")
        print(f"Audio files saved to: {output_dir}")
        print(f"Segment list: {summary_file}")
        
        return audio_files[0]  # Return introduction file as main reference
    
    def load_transcript(self, transcript_path: str) -> List[Dict[str, Any]]:
        """Load transcript from JSONL file."""
        transcript = []
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        transcript.append(json.loads(line))
        except FileNotFoundError:
            print(f"Transcript file not found: {transcript_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing transcript: {e}")
            return []
        
        return transcript
    
    def extract_debate_info(self, transcript: List[Dict], metadata: Optional[Dict] = None) -> Dict:
        """Extract debate information from transcript or metadata."""
        # Try to get info from metadata first
        if metadata and 'debate_info' in metadata:
            return metadata['debate_info']
        
        # Fall back to extracting from transcript
        debate_start = next((record for record in transcript if record.get('event') == 'debate_start'), {})
        
        return {
            'topic': debate_start.get('topic', 'Unknown Topic'),
            'num_agents': debate_start.get('num_agents', 2),
            'rounds': debate_start.get('rounds', 3),
            'model': debate_start.get('model', 'Unknown Model')
        }
    
    def generate_opening_statements_audio(self, transcript: List[Dict], output_dir: str) -> List[str]:
        """Generate audio for opening statements."""
        opening_statements = [
            record for record in transcript 
            if record.get('type') == 'opening_statement'
        ]
        
        if not opening_statements:
            return []
        
        audio_files = []
        
        # Narrator introduction
        self.set_narrator_voice()
        narrator_text = "Now, let's hear the opening statements from each agent."
        narrator_file = os.path.join(output_dir, "02_opening_intro.wav")
        self.save_audio_segment(narrator_text, narrator_file)
        audio_files.append(narrator_file)
        
        # Individual opening statements
        for i, statement in enumerate(sorted(opening_statements, key=lambda x: x.get('agent', 0))):
            agent_id = statement.get('agent', 0)
            message = statement.get('message', '')
            
            # Set voice for this agent
            self.set_voice_for_agent(agent_id)
            
            # Create agent intro
            agent_intro = f"Agent {agent_id} opening statement:"
            statement_text = f"{agent_intro} {message}"
            
            filename = f"03_opening_agent_{agent_id}.wav"
            file_path = os.path.join(output_dir, filename)
            self.save_audio_segment(statement_text, file_path)
            audio_files.append(file_path)
            print(f"Generated: {filename}")
        
        return audio_files
    
    def generate_rounds_audio(self, transcript: List[Dict], output_dir: str) -> List[str]:
        """Generate audio for debate rounds."""
        debate_responses = [
            record for record in transcript 
            if record.get('type') == 'debate_response'
        ]
        
        if not debate_responses:
            return []
        
        audio_files = []
        
        # Group by rounds
        rounds = {}
        for response in debate_responses:
            round_num = response.get('round', 1)
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(response)
        
        for round_num in sorted(rounds.keys()):
            # Round introduction
            self.set_narrator_voice()
            round_intro = f"Round {round_num} of the debate."
            intro_filename = f"04_round_{round_num:02d}_intro.wav"
            intro_file = os.path.join(output_dir, intro_filename)
            self.save_audio_segment(round_intro, intro_file)
            audio_files.append(intro_file)
            
            # Agent responses in this round
            round_responses = sorted(rounds[round_num], key=lambda x: x.get('agent', 0))
            
            for response in round_responses:
                agent_id = response.get('agent', 0)
                message = response.get('message', '')
                
                # Set voice for this agent
                self.set_voice_for_agent(agent_id)
                
                agent_intro = f"Agent {agent_id}:"
                response_text = f"{agent_intro} {message}"
                
                filename = f"05_round_{round_num:02d}_agent_{agent_id}.wav"
                file_path = os.path.join(output_dir, filename)
                self.save_audio_segment(response_text, file_path)
                audio_files.append(file_path)
                print(f"Generated: {filename}")
        
        return audio_files
    
    def generate_verdict_audio(self, transcript: List[Dict], output_dir: str) -> Optional[str]:
        """Generate audio for the final verdict."""
        verdict_record = next((record for record in transcript if record.get('event') == 'verdict'), None)
        
        if not verdict_record:
            return None
        
        winner = verdict_record.get('winner', 'Unknown')
        justification = verdict_record.get('justification', 'No justification provided.')
        
        self.set_narrator_voice()
        verdict_text = f"""
        The debate has concluded. 
        
        After careful consideration of all arguments, the judge has reached a decision.
        
        The winner is Agent {winner}.
        
        Judge's justification: {justification}
        
        Thank you for listening to this multi-agent debate.
        """
        
        filename = "06_verdict.wav"
        file_path = os.path.join(output_dir, filename)
        self.save_audio_segment(verdict_text, file_path)
        print(f"Generated: {filename}")
        
        return file_path


# Standalone functions for easy use
def generate_debate_audio(transcript_path: str, 
                         output_dir: str,
                         metadata_path: Optional[str] = None) -> str:
    """
    Generate audio for a debate transcript.
    
    Args:
        transcript_path: Path to the JSONL transcript
        output_dir: Directory to save audio files
        metadata_path: Optional path to metadata JSON file
        
    Returns:
        Path to the main audio file
    """
    # Load metadata if provided
    metadata = None
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse metadata file: {metadata_path}")
    
    # Generate audio
    generator = DebateAudioGenerator()
    return generator.generate_audio_from_transcript(transcript_path, output_dir, metadata)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python audio_generator.py <transcript_path> <output_dir> [metadata_path]")
        print("Example: python audio_generator.py transcript.jsonl ./audio_output metadata.json")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    output_dir = sys.argv[2]
    metadata_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        main_file = generate_debate_audio(transcript_path, output_dir, metadata_path)
        print(f"\n✅ Audio generation complete!")
        print(f"Main audio file: {main_file}")
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        sys.exit(1) 