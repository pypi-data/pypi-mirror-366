# Whisper Turbo

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-M1%20%7C%20M2%20%7C%20M3-green.svg)](https://www.apple.com/mac/)
[![PyPI version](https://img.shields.io/pypi/v/whisper-turbo.svg)](https://pypi.org/project/whisper-turbo/)

High-performance Whisper transcription using MLX for Apple Silicon, featuring Turbo v3 for blazing-fast speech-to-text.

## Features

- 🚀 Optimized for Apple Silicon (M1/M2/M3) using MLX framework
- ⚡ Supports Whisper Turbo v3 for fast, high-quality transcription
- 🎯 Automatic language detection
- 📝 Word-level timestamps
- 🔧 Handles various audio formats (AAC, MP3, MP4, WAV, etc.)
- 📡 Optional API posting functionality
- 💾 Save transcriptions to JSON format

## Installation

### From PyPI

```bash
pip install whisper-turbo
```

### From Source

```bash
git clone https://github.com/xbattlax/whisper-turbo.git
cd whisper-turbo
pip install -e .
```

## Quick Start

```bash
# Transcribe with Turbo v3 (fastest, recommended)
whisper-turbo your_audio.mp3 --model turbo-v3 --output result.json

# Or use as a Python module
from whisper_turbo import MLXWhisperTranscriber

transcriber = MLXWhisperTranscriber(model_name="turbo-v3")
text, segments = transcriber.transcribe_file("audio.mp3")
print(text)
```

### Requirements
- Python 3.8+
- Apple Silicon Mac (M1/M2/M3)
- ~2GB disk space for model download


## Usage

### Command Line Usage

```bash
# Basic transcription
whisper-turbo audio.mp3

# Use Whisper Turbo v3 (fastest, high quality)
whisper-turbo audio.mp3 --model turbo-v3

# Use other models
whisper-turbo audio.mp3 --model large-v3
whisper-turbo audio.mp3 --model medium
whisper-turbo audio.mp3 --model base

# Save output to file
whisper-turbo audio.mp3 --model turbo-v3 --output transcription.json

# Disable API posting
whisper-turbo audio.mp3 --model turbo-v3 --no-api

# Custom API endpoint
whisper-turbo audio.mp3 --api-endpoint https://your-api.com/transcript

# Enable SSL verification
whisper-turbo audio.mp3 --verify-ssl
```

### Python API Usage

```python
from whisper_turbo import MLXWhisperTranscriber

# Initialize transcriber
transcriber = MLXWhisperTranscriber(
    model_name="turbo-v3",
    api_enabled=False  # Disable API posting
)

# Transcribe audio file
text, segments = transcriber.transcribe_file("path/to/audio.mp3")

# Print full transcription
print("Full text:", text)

# Print segments with timestamps
for segment in segments:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

## Available Models

- `turbo-v3` / `turbo` - Whisper Large v3 Turbo (fastest, recommended)
- `large-v3` / `large` - Whisper Large v3 
- `medium` - Medium model (balanced speed/quality)
- `small` - Small model (faster, good quality)
- `base` - Base model (very fast, decent quality)
- `tiny` - Tiny model (fastest, lower quality)

## API Format

When API posting is enabled, the script posts transcriptions in the following format:

```json
{
  "external_call_ref": "session-uuid",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "is_final": true,
      "speaker_id": "speaker_0"
    }
  ],
  "transcription": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Hello, welcome to the meeting",
      "is_final": true
    }
  ]
}
```

## Output Format

Saved transcriptions include:

```json
{
  "file": "audio.mp3",
  "session_id": "uuid",
  "timestamp": "2024-01-15T10:30:45",
  "model": "turbo-v3",
  "device": "Apple Silicon (MLX)",
  "full_text": "Complete transcription text...",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Segment text",
      "is_final": true
    }
  ]
}
```

## Performance

On Apple Silicon (M1/M2/M3), MLX Whisper provides:
- Hardware-accelerated transcription using Metal
- Efficient memory usage
- Fast model loading and inference
- Typical processing: ~20-30 seconds for 5-minute audio with Turbo v3

## Example

```bash
# Transcribe a meeting recording with Turbo v3
whisper-turbo ~/Downloads/meeting.mp4 --model turbo-v3 --output meeting_transcript.json

# Output
🔧 Loading MLX Whisper model 'turbo-v3' on Apple Silicon...
✅ MLX Whisper ready with model: turbo-v3
✅ MLX Whisper model loaded successfully
🎧 Processing audio file: ~/Downloads/meeting.mp4
🚀 Using Apple MLX framework for optimal Metal performance
🤖 Using MLX model: mlx-community/whisper-large-v3-turbo
Detected language: English
✅ MLX Transcription complete in 23.45s
📝 Text length: 5420 characters
📊 Segments: 125
🔧 Used device: Apple Silicon (MLX)
💾 Saved transcription to: meeting_transcript.json
```

## Troubleshooting

### Installation Issues
- Ensure you're on an Apple Silicon Mac (M1/M2/M3)
- Update pip: `pip install --upgrade pip`
- Install in a virtual environment if conflicts occur

### Performance Tips
- Use `turbo-v3` model for best speed/quality balance
- Close other applications to free up memory
- For very long audio files, consider splitting them

### Common Issues
- **Import Error**: Ensure `mlx-whisper` is installed
- **Memory Error**: Try a smaller model (base, small)
- **Audio Format Error**: Convert to supported format (MP3, WAV)

## Development

### Setting up for development

```bash
# Clone the repository
git clone https://github.com/xbattlax/whisper-turbo.git
cd whisper-turbo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black whisper_turbo/

# Lint code
flake8 whisper_turbo/
```

### Building for PyPI

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to TestPyPI (for testing)
twine upload -r testpypi dist/*

# Upload to PyPI (for release)
twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MLX Whisper](https://github.com/ml-explore/mlx-whisper) team for the excellent MLX implementation
- OpenAI for the original [Whisper](https://github.com/openai/whisper) model
- Apple for the [MLX](https://github.com/ml-explore/mlx) framework

## Citation

If you use this tool in your research or project, please consider citing:

```bibtex
@software{whisper_turbo,
  author = {Nathan Metzger},
  title = {Whisper Turbo: High-performance Whisper transcription for Apple Silicon},
  year = {2024},
  url = {https://github.com/xbattlax/whisper-turbo}
}
```