#!/usr/bin/env python3
"""
Standalone script to convert existing debate transcripts to audio.
"""

import os
import sys
import argparse
import glob
from audio_generator import generate_debate_audio


def find_debate_folders(base_dir: str = "results") -> list:
    """Find all debate result folders."""
    if not os.path.exists(base_dir):
        return []
    
    folders = []
    for item in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, item)
        if os.path.isdir(folder_path):
            # Check if it contains transcript.jsonl
            transcript_path = os.path.join(folder_path, "transcript.jsonl")
            if os.path.exists(transcript_path):
                folders.append(folder_path)
    
    return sorted(folders)


def convert_single_debate(debate_folder: str, force_regenerate: bool = False) -> bool:
    """
    Convert a single debate to audio.
    
    Args:
        debate_folder: Path to debate results folder
        force_regenerate: Whether to regenerate if audio already exists
        
    Returns:
        True if successful, False otherwise
    """
    transcript_path = os.path.join(debate_folder, "transcript.jsonl")
    metadata_path = os.path.join(debate_folder, "metadata.json")
    audio_dir = os.path.join(debate_folder, "audio")
    
    # Check if files exist
    if not os.path.exists(transcript_path):
        print(f"❌ No transcript found in {debate_folder}")
        return False
    
    # Check if audio already exists
    if os.path.exists(audio_dir) and not force_regenerate:
        print(f"⏭️  Audio already exists for {os.path.basename(debate_folder)} (use --force to regenerate)")
        return True
    
    print(f"🔊 Converting {os.path.basename(debate_folder)} to audio...")
    
    try:
        main_audio_file = generate_debate_audio(
            transcript_path, 
            audio_dir, 
            metadata_path if os.path.exists(metadata_path) else None
        )
        print(f"✅ Successfully generated audio for {os.path.basename(debate_folder)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate audio for {os.path.basename(debate_folder)}: {e}")
        return False


def convert_all_debates(base_dir: str = "results", force_regenerate: bool = False) -> None:
    """Convert all debates in the results directory to audio."""
    debate_folders = find_debate_folders(base_dir)
    
    if not debate_folders:
        print(f"No debate folders found in {base_dir}")
        return
    
    print(f"Found {len(debate_folders)} debate(s) to convert:")
    for folder in debate_folders:
        print(f"  - {os.path.basename(folder)}")
    
    print("\nStarting conversion...")
    print("=" * 50)
    
    successful = 0
    for folder in debate_folders:
        if convert_single_debate(folder, force_regenerate):
            successful += 1
        print()
    
    print("=" * 50)
    print(f"Conversion complete: {successful}/{len(debate_folders)} successful")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert debate transcripts to audio using text-to-speech",
        epilog="Examples:\n"
               "  python convert_to_audio.py                    # Convert all debates\n"
               "  python convert_to_audio.py --folder path/to/debate  # Convert specific debate\n"
               "  python convert_to_audio.py --force            # Regenerate existing audio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--folder",
        type=str,
        help="Convert specific debate folder (default: convert all in results/)"
    )
    
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Base results directory (default: results)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if audio already exists"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available debate folders and exit"
    )
    
    args = parser.parse_args()
    
    # List available debates
    if args.list:
        debate_folders = find_debate_folders(args.results_dir)
        if debate_folders:
            print(f"Available debate folders in {args.results_dir}:")
            for i, folder in enumerate(debate_folders, 1):
                folder_name = os.path.basename(folder)
                audio_dir = os.path.join(folder, "audio")
                has_audio = "✅" if os.path.exists(audio_dir) else "❌"
                print(f"  {i:2d}. {folder_name} {has_audio}")
            print(f"\nTotal: {len(debate_folders)} debates")
            print("✅ = has audio, ❌ = no audio")
        else:
            print(f"No debate folders found in {args.results_dir}")
        return
    
    # Convert specific folder
    if args.folder:
        if not os.path.exists(args.folder):
            print(f"❌ Folder not found: {args.folder}")
            sys.exit(1)
        
        if convert_single_debate(args.folder, args.force):
            print("✅ Conversion successful!")
        else:
            print("❌ Conversion failed!")
            sys.exit(1)
    else:
        # Convert all debates
        convert_all_debates(args.results_dir, args.force)


if __name__ == "__main__":
    main() 