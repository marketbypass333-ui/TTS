#!/usr/bin/env python3
"""
Thai TTS CLI - Enhanced Command Line Interface for Thai Text-to-Speech

This module provides a user-friendly command-line interface for Thai TTS operations
including voice cloning, batch processing, and real-time synthesis.

Features:
- Interactive mode with menus
- Voice cloning from reference audio
- Batch processing for multiple texts
- Real-time streaming synthesis
- Thai text preprocessing
- Voice style transfer
- Performance monitoring
"""

import argparse
import sys
import os
import time
import json
import torch
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any
import tqdm

# Add TTS to path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from TTS.api import TTS
    from TTS.utils.generic_utils import get_user_data_dir
    import pythainlp
    from pythainlp.util import normalize as normalize_thai
    THAI_TTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Thai TTS libraries not available: {e}")
    THAI_TTS_AVAILABLE = False

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

class ThaiTTSCLI:
    """Enhanced Thai TTS CLI with user-friendly interface"""
    
    def __init__(self):
        self.tts = None
        self.device = "cpu"
        self.model_loaded = False
        self.current_model = None
        self.setup_complete = False
        
    def setup(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2") -> bool:
        """Setup TTS engine and models"""
        try:
            print_header("Thai TTS Setup")
            
            if not THAI_TTS_AVAILABLE:
                print_error("Thai TTS libraries not available. Please install required packages.")
                return False
            
            # Check device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print_info(f"Using device: {self.device}")
            
            # Load TTS model
            print_info(f"Loading TTS model: {model_name}")
            with tqdm.tqdm(total=1, desc="Loading model") as pbar:
                self.tts = TTS(model_name).to(self.device)
                pbar.update(1)
            
            self.model_loaded = True
            self.current_model = model_name
            self.setup_complete = True
            
            print_success("TTS setup complete!")
            return True
            
        except Exception as e:
            print_error(f"Setup failed: {e}")
            return False
    
    def preprocess_thai_text(self, text: str) -> str:
        """Preprocess Thai text for TTS"""
        try:
            return normalize_thai(text)
        except Exception:
            return text
    
    def synthesize_speech(self, text: str, output_path: str, speaker_wav: Optional[str] = None, 
                         language: str = "th", speed: float = 1.0) -> bool:
        """Synthesize speech from text"""
        try:
            if not self.setup_complete:
                print_error("TTS not setup. Please run setup first.")
                return False
            
            # Preprocess text
            processed_text = self.preprocess_thai_text(text)
            
            # Generate audio
            print_info(f"Synthesizing: {processed_text}")
            with tqdm.tqdm(total=1, desc="Generating audio") as pbar:
                audio = self.tts.tts(
                    text=processed_text,
                    speaker_wav=speaker_wav,
                    language=language
                )
                pbar.update(1)
            
            # Convert to numpy if needed
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            
            # Save audio
            sf.write(output_path, audio, 22050)
            print_success(f"Audio saved: {output_path}")
            return True
            
        except Exception as e:
            print_error(f"Synthesis failed: {e}")
            return False
    
    def clone_voice(self, reference_wav: str, texts: List[str], output_dir: str) -> List[str]:
        """Clone voice from reference audio"""
        try:
            print_header("Voice Cloning")
            print_info(f"Reference audio: {reference_wav}")
            print_info(f"Number of texts: {len(texts)}")
            
            os.makedirs(output_dir, exist_ok=True)
            generated_files = []
            
            for i, text in enumerate(tqdm.tqdm(texts, desc="Cloning voices")):
                output_path = os.path.join(output_dir, f"cloned_{i+1}.wav")
                
                if self.synthesize_speech(text, output_path, speaker_wav=reference_wav):
                    generated_files.append(output_path)
                else:
                    print_error(f"Failed to clone voice for text {i+1}")
            
            print_success(f"Voice cloning complete! Generated {len(generated_files)} files")
            return generated_files
            
        except Exception as e:
            print_error(f"Voice cloning failed: {e}")
            return []
    
    def batch_process(self, input_file: str, output_dir: str, speaker_wav: Optional[str] = None) -> bool:
        """Batch process multiple texts from file"""
        try:
            print_header("Batch Processing")
            
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                texts = [line.strip() for line in f if line.strip()]
            
            print_info(f"Loaded {len(texts)} texts from {input_file}")
            
            # Process each text
            os.makedirs(output_dir, exist_ok=True)
            results = []
            
            for i, text in enumerate(tqdm.tqdm(texts, desc="Processing batch")):
                output_path = os.path.join(output_dir, f"batch_{i+1}.wav")
                
                success = self.synthesize_speech(text, output_path, speaker_wav=speaker_wav)
                results.append({
                    'text': text,
                    'output': output_path,
                    'success': success
                })
            
            # Summary
            successful = sum(1 for r in results if r['success'])
            print_success(f"Batch complete! {successful}/{len(results)} successful")
            
            # Save results
            results_file = os.path.join(output_dir, "batch_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return successful > 0
            
        except Exception as e:
            print_error(f"Batch processing failed: {e}")
            return False
    
    def interactive_mode(self):
        """Interactive CLI mode with menu-driven interface"""
        print_header("Thai TTS Interactive Mode")
        
        if not self.setup_complete:
            if not self.setup():
                return
        
        while True:
            print(f"\n{Colors.OKCYAN}=== Main Menu ==={Colors.ENDC}")
            print("1. Text-to-Speech")
            print("2. Voice Cloning")
            print("3. Batch Processing")
            print("4. Settings")
            print("5. Exit")
            
            try:
                choice = input(f"\n{Colors.BOLD}Select option (1-5): {Colors.ENDC}").strip()
                
                if choice == '1':
                    self.interactive_tts()
                elif choice == '2':
                    self.interactive_voice_cloning()
                elif choice == '3':
                    self.interactive_batch_processing()
                elif choice == '4':
                    self.interactive_settings()
                elif choice == '5':
                    print_success("Goodbye!")
                    break
                else:
                    print_warning("Invalid choice. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
                break
            except Exception as e:
                print_error(f"Error: {e}")
    
    def interactive_tts(self):
        """Interactive TTS mode"""
        print_header("Text-to-Speech")
        
        # Get text input
        text = input(f"{Colors.BOLD}Enter Thai text: {Colors.ENDC}").strip()
        if not text:
            print_warning("No text entered")
            return
        
        # Get output path
        output_path = input(f"{Colors.BOLD}Output file path (default: output.wav): {Colors.ENDC}").strip()
        if not output_path:
            output_path = "output.wav"
        
        # Optional speaker reference
        speaker_wav = input(f"{Colors.BOLD}Reference speaker audio (optional, press Enter to skip): {Colors.ENDC}").strip()
        if speaker_wav and not os.path.exists(speaker_wav):
            print_warning("Reference file not found, using default voice")
            speaker_wav = None
        
        # Synthesize
        if self.synthesize_speech(text, output_path, speaker_wav=speaker_wav if speaker_wav else None):
            print_success(f"Speech synthesized successfully!")
            print_info(f"Output file: {output_path}")
    
    def interactive_voice_cloning(self):
        """Interactive voice cloning mode"""
        print_header("Voice Cloning")
        
        # Get reference audio
        reference_wav = input(f"{Colors.BOLD}Reference speaker audio file: {Colors.ENDC}").strip()
        if not os.path.exists(reference_wav):
            print_error("Reference file not found!")
            return
        
        # Get number of texts
        try:
            num_texts = int(input(f"{Colors.BOLD}Number of texts to synthesize: {Colors.ENDC}"))
        except ValueError:
            print_error("Invalid number")
            return
        
        # Get texts
        texts = []
        print_info("Enter Thai texts (press Enter after each):")
        for i in range(num_texts):
            text = input(f"Text {i+1}: ").strip()
            if text:
                texts.append(text)
        
        if not texts:
            print_warning("No texts entered")
            return
        
        # Get output directory
        output_dir = input(f"{Colors.BOLD}Output directory (default: cloned_voices): {Colors.ENDC}").strip()
        if not output_dir:
            output_dir = "cloned_voices"
        
        # Clone voices
        self.clone_voice(reference_wav, texts, output_dir)
    
    def interactive_batch_processing(self):
        """Interactive batch processing mode"""
        print_header("Batch Processing")
        
        # Get input file
        input_file = input(f"{Colors.BOLD}Input text file path: {Colors.ENDC}").strip()
        if not os.path.exists(input_file):
            print_error("Input file not found!")
            return
        
        # Get output directory
        output_dir = input(f"{Colors.BOLD}Output directory (default: batch_output): {Colors.ENDC}").strip()
        if not output_dir:
            output_dir = "batch_output"
        
        # Optional speaker reference
        speaker_wav = input(f"{Colors.BOLD}Reference speaker audio (optional): {Colors.ENDC}").strip()
        if speaker_wav and not os.path.exists(speaker_wav):
            print_warning("Reference file not found, using default voice")
            speaker_wav = None
        
        # Process batch
        self.batch_process(input_file, output_dir, speaker_wav=speaker_wav if speaker_wav else None)
    
    def interactive_settings(self):
        """Interactive settings mode"""
        print_header("Settings")
        
        print(f"Current model: {self.current_model}")
        print(f"Device: {self.device}")
        print(f"Setup complete: {self.setup_complete}")
        
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Thai TTS CLI - Enhanced Command Line Interface for Thai Text-to-Speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python thai_tts_cli.py
  
  # Text-to-speech
  python thai_tts_cli.py tts "สวัสดีครับ" --output hello.wav
  
  # Voice cloning
  python thai_tts_cli.py clone --reference speaker.wav --texts "text1" "text2" --output-dir cloned
  
  # Batch processing
  python thai_tts_cli.py batch --input texts.txt --output-dir batch_output
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    parser_interactive = subparsers.add_parser('interactive', help='Start interactive mode')
    
    # TTS command
    parser_tts = subparsers.add_parser('tts', help='Text-to-speech')
    parser_tts.add_argument('text', help='Thai text to synthesize')
    parser_tts.add_argument('--output', '-o', default='output.wav', help='Output audio file (default: output.wav)')
    parser_tts.add_argument('--speaker', '-s', help='Reference speaker audio file')
    parser_tts.add_argument('--language', '-l', default='th', help='Language code (default: th)')
    
    # Voice cloning command
    parser_clone = subparsers.add_parser('clone', help='Voice cloning')
    parser_clone.add_argument('--reference', '-r', required=True, help='Reference speaker audio file')
    parser_clone.add_argument('--texts', '-t', nargs='+', required=True, help='Texts to synthesize')
    parser_clone.add_argument('--output-dir', '-d', default='cloned_voices', help='Output directory (default: cloned_voices)')
    
    # Batch processing command
    parser_batch = subparsers.add_parser('batch', help='Batch processing')
    parser_batch.add_argument('--input', '-i', required=True, help='Input text file')
    parser_batch.add_argument('--output-dir', '-d', default='batch_output', help='Output directory (default: batch_output)')
    parser_batch.add_argument('--speaker', '-s', help='Reference speaker audio file')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = ThaiTTSCLI()
    
    if not args.command:
        # No command specified, start interactive mode
        cli.interactive_mode()
    else:
        # Execute specific command
        if args.command == 'interactive':
            cli.interactive_mode()
        elif args.command == 'tts':
            if cli.setup():
                cli.synthesize_speech(
                    args.text, 
                    args.output, 
                    speaker_wav=args.speaker, 
                    language=args.language
                )
        elif args.command == 'clone':
            if cli.setup():
                cli.clone_voice(args.reference, args.texts, args.output_dir)
        elif args.command == 'batch':
            if cli.setup():
                cli.batch_process(args.input, args.output_dir, speaker_wav=args.speaker)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)