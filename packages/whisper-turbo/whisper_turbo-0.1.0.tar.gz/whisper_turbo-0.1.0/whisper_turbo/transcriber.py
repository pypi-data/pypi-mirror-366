#!/usr/bin/env python3
"""
MLX Whisper transcription for Apple Silicon
Using Apple's MLX framework for optimal Metal performance
"""

import argparse
import json
import time
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

import requests
from tqdm import tqdm

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)


class MLXWhisperTranscriber:
    """MLX Whisper transcription optimized for Apple Silicon"""
    
    def __init__(
        self,
        model_name: str = "base",
        api_endpoint: str = "https://localhost:8083/transcript",
        api_enabled: bool = True,
        verify_ssl: bool = False
    ):
        self.model_name = model_name
        self.api_endpoint = api_endpoint
        self.api_enabled = api_enabled
        self.verify_ssl = verify_ssl
        self.session_id = str(uuid.uuid4())
        
        print(f"🔧 Loading MLX Whisper model '{model_name}' on Apple Silicon...")
        self._load_model()
        print("✅ MLX Whisper model loaded successfully")
        
    def _load_model(self):
        """Load MLX Whisper model"""
        try:
            import mlx_whisper
            # MLX Whisper loads the model automatically on first use
            self.mlx_whisper = mlx_whisper
            print(f"✅ MLX Whisper ready with model: {self.model_name}")
        except ImportError as e:
            print(f"❌ MLX Whisper import failed: {e}")
            raise
        
    def transcribe_file(self, audio_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Transcribe audio file using MLX Whisper
        
        Returns:
            tuple: (full_text, segments_list)
        """
        print(f"🎧 Processing audio file: {audio_path}")
        print(f"🚀 Using Apple MLX framework for optimal Metal performance")
        
        start_time = time.time()
        
        try:
            # Map model names to MLX Whisper format
            model_mapping = {
                "tiny": "mlx-community/whisper-tiny-mlx",
                "base": "mlx-community/whisper-base-mlx", 
                "small": "mlx-community/whisper-small-mlx",
                "medium": "mlx-community/whisper-medium-mlx",
                "large": "mlx-community/whisper-large-v3-mlx",
                "large-v3": "mlx-community/whisper-large-v3-mlx",
                "turbo": "mlx-community/whisper-large-v3-turbo",
                "turbo-v3": "mlx-community/whisper-large-v3-turbo"
            }
            
            mlx_model_name = model_mapping.get(self.model_name, "mlx-community/whisper-base-mlx")
            print(f"🤖 Using MLX model: {mlx_model_name}")
            
            # Transcribe with MLX Whisper
            result = self.mlx_whisper.transcribe(
                audio_path,
                path_or_hf_repo=mlx_model_name,
                verbose=False,
                word_timestamps=True,
                temperature=0.0,
                no_speech_threshold=0.6,
                logprob_threshold=-1.0,
                compression_ratio_threshold=2.4,
                condition_on_previous_text=False,  # Prevent repetition loops
                initial_prompt="This is a French business meeting discussion."
            )
            
        except Exception as e:
            print(f"❌ MLX Whisper transcription failed: {e}")
            raise
        
        processing_time = time.time() - start_time
        
        # Extract text and segments
        full_text = result["text"].strip()
        segments = self._convert_segments(result["segments"])
        
        print(f"✅ MLX Transcription complete in {processing_time:.2f}s")
        print(f"📝 Text length: {len(full_text)} characters")
        print(f"📊 Segments: {len(segments)}")
        print(f"🔧 Used device: Apple Silicon (MLX)")
        
        # Post to API if enabled
        if self.api_enabled and full_text:
            self._post_to_api(segments, full_text, processing_time)
        
        return full_text, segments
    
    def _convert_segments(self, whisper_segments: List[Dict]) -> List[Dict[str, Any]]:
        """Convert MLX Whisper segments to our format and clean repetitions"""
        segments = []
        
        for seg in whisper_segments:
            text = seg["text"].strip()
            # Clean up repetitive text
            text = self._clean_repetitive_text(text)
            
            if text:  # Only add non-empty segments
                segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": text,
                    "is_final": True
                })
        
        return segments
    
    def _clean_repetitive_text(self, text: str) -> str:
        """Clean up repetitive text patterns"""
        import re
        
        # Remove excessive repetition of same phrase
        words = text.split()
        if len(words) > 10:
            # Check if more than 70% of words are the same
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            if word_counts:
                max_count = max(word_counts.values())
                if max_count > len(words) * 0.7:  # If one word appears >70% of the time
                    # Find the most common word and limit its repetition
                    most_common_word = max(word_counts, key=word_counts.get)
                    # Replace excessive repetition with just a few instances
                    pattern = rf'(\b{re.escape(most_common_word)}\b(\s*,\s*\b{re.escape(most_common_word)}\b)*)'
                    text = re.sub(pattern, most_common_word, text)
        
        return text
    
    def _post_to_api(self, segments: List[Dict[str, Any]], full_text: str, processing_time: float):
        """Post transcription to API matching expected format"""
        if not segments:
            return
        
        # Create API payload
        payload = {
            "external_call_ref": self.session_id,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "is_final": seg["is_final"],
                    "speaker_id": "speaker_0"
                }
                for seg in segments
            ],
            "transcription": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                    "is_final": seg["is_final"]
                }
                for seg in segments
            ]
        }
        
        print(f"📡 Posting to API: {self.api_endpoint}")
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json"
                },
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code in (200, 201):
                print(f"✅ API post successful: {response.status_code}")
            else:
                print(f"❌ API post failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ API post error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="MLX Whisper transcription for Apple Silicon"
    )
    
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to audio/video file to transcribe"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v3", "turbo", "turbo-v3"],
        help="Whisper model size"
    )
    
    parser.add_argument(
        "--api-endpoint",
        type=str,
        default="https://localhost:8083/transcript",
        help="API endpoint for posting transcriptions"
    )
    
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable API posting"
    )
    
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="Verify SSL certificates"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Save transcription to file"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.audio_file).exists():
        print(f"❌ Error: Audio file not found: {args.audio_file}")
        return
    
    # Create transcriber
    transcriber = MLXWhisperTranscriber(
        model_name=args.model,
        api_endpoint=args.api_endpoint,
        api_enabled=not args.no_api,
        verify_ssl=args.verify_ssl
    )
    
    # Transcribe file
    try:
        full_text, segments = transcriber.transcribe_file(args.audio_file)
        
        print(f"\n📄 TRANSCRIPTION:")
        print(f"{'='*50}")
        print(full_text[:500] + "..." if len(full_text) > 500 else full_text)
        print(f"{'='*50}")
        
        # Save output if requested
        if args.output:
            output_data = {
                "file": args.audio_file,
                "session_id": transcriber.session_id,
                "timestamp": datetime.now().isoformat(),
                "model": args.model,
                "device": "Apple Silicon (MLX)",
                "full_text": full_text,
                "segments": segments
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved transcription to: {args.output}")
            
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise


if __name__ == "__main__":
    main()