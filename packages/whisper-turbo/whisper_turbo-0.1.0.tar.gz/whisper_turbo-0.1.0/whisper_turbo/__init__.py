"""
Whisper Turbo - High-performance Whisper transcription for Apple Silicon

A fast, efficient audio transcription tool using MLX Whisper, optimized for Apple Silicon Macs.
Supports Whisper Turbo v3 for the best speed and quality.
"""

__version__ = "0.1.0"
__author__ = "Nathan Metzger"
__email__ = "nathan.metzger@voxtria.com"

from .transcriber import MLXWhisperTranscriber

__all__ = ["MLXWhisperTranscriber"]