# 🎙️ Speech Analysis Tool

A command-line tool that transcribes video/audio files using OpenAI's Whisper and analyzes speech patterns to help improve public speaking skills.

## ✨ Features

- **Video & Text Support**: Analyze `.mp4`, `.mov`, `.mkv` videos or existing `.txt` transcripts
- **Automatic Transcription**: Uses Whisper AI to convert speech to text
- **Speech Statistics**: Word counts, unique words, filler word usage percentage
- **Readability Analysis**: Flesch-Kincaid grade level with interpretation
- **Filler Word Detection**: Identifies crutch words like "um," "uh," "like," "you know"
- **Word Frequency Analysis**: Top 15 most-used meaningful words
- **JSON Output**: Structured data perfect for feeding into LLMs for deeper analysis
- **Optional Visualization**: Bar chart of word frequency (opt-in with `--graph`)
- **Multiple Model Sizes**: Choose from tiny/base/small/medium/large Whisper models

## 📋 Requirements

- Python 3.8+
- FFmpeg (for video processing)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Set up Python environment

```bash
cd /path/to/project
python3 -m venv mp4-script
source mp4-script/bin/activate  # On Windows: mp4-script\Scripts\activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install openai-whisper nltk matplotlib textstat
```

### 3. Make the script executable

```bash
chmod +x main.py
```

### 4. Create command-line tool (optional but recommended)

```bash
# Create wrapper script
cat > speech_analysis << 'EOF'
#!/bin/bash
source /full/path/to/mp4-script/bin/activate
python /full/path/to/main.py "$@"
EOF

chmod +x speech_analysis

# Create symlink in user bin
mkdir -p ~/.local/bin
ln -sf /full/path/to/speech_analysis ~/.local/bin/speech_analysis

# Add to PATH (add this to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

## 💻 Usage

### Basic Usage

```bash
# Analyze a video
speech_analysis video.mp4

# Analyze an existing transcript
speech_analysis transcript.txt
```

### Advanced Options

```bash
# Show word frequency graph
speech_analysis video.mp4 --graph

# Use better Whisper model
speech_analysis video.mp4 --model small

# Verbose output with details
speech_analysis video.mp4 --verbose

# Custom output directory
speech_analysis video.mp4 --output-dir ~/analysis_results

# Combine options
speech_analysis speech.mp4 --model medium --graph -v --output-dir ./results
```

### Available Flags

| Flag                | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `--graph`           | Display word frequency bar chart                                   |
| `--output-dir PATH` | Specify output directory (default: current directory)              |
| `--model NAME`      | Choose Whisper model: tiny/base/small/medium/large (default: base) |
| `--verbose`, `-v`   | Show detailed analysis output                                      |
| `--version`         | Show version number                                                |

## 📊 Output

### Console Output (Minimal by default)

```
✓ Analyzed: video.mp4
→ Results: analysis_video_2025-10-13_14-30-00.json
```

### JSON Structure

The tool always creates a JSON file with complete analysis:

```json
{
  "source_file": "video.mp4",
  "transcript": "Full transcription text here...",
  "statistics": {
    "total_words": 1250,
    "unique_words": 342,
    "total_filler_words": 22,
    "filler_word_percentage": 1.76
  },
  "readability": {
    "score": 8.5,
    "interpretation": "Middle school level (accessible to most)"
  },
  "filler_words": {
    "um": 5,
    "like": 12,
    "uh": 3,
    "you know": 2
  },
  "word_frequency": [
    ["important", 15],
    ["discussion", 12],
    ["topic", 10],
    ["understand", 8],
    ["example", 7]
  ]
}
```

### Readability Score Interpretation

- **< 6**: Elementary school level (easy to understand)
- **6-9**: Middle school level (accessible to most)
- **9-13**: High school level (standard reading level)
- **13-16**: College level (more complex)
- **16+**: Graduate level (advanced/academic)

## 🤖 Using with LLMs for Improvement

Take your JSON output and use this prompt with Claude, ChatGPT, or any LLM:

```
Help me improve my speech. Here is my analysis in JSON format. It was analyzed by a speech analysis tool and contains: my full transcript, statistics (total words, unique words, filler word count and percentage), readability score with interpretation, a breakdown of which filler words I used and how many times, and the top 15 most frequently used meaningful words. Please review this data and give me specific, actionable suggestions to improve my speaking clarity, reduce filler words, and make my speech more engaging.

[paste your JSON here]
```

## 📁 File Organization

```
project/
├── main.py              # Main script
├── speech_analysis      # Wrapper script
├── mp4-script/          # Virtual environment
│   └── bin/activate
├── transcripts/         # Video transcripts (auto-created)
└── analysis_*.json      # Analysis results
```

## 🔧 Troubleshooting

### "Command not found: speech_analysis"

Make sure `~/.local/bin` is in your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### FFmpeg not found

Install FFmpeg:

- **Mac**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/)

### NLTK data missing

The script auto-downloads required data on first run, but you can manually install:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
```

## 📝 Notes

- **First run**: NLTK will download required language data automatically
- **Model sizes**: Larger models are more accurate but slower
  - `tiny`: Fastest, least accurate
  - `base`: Good balance (default)
  - `small/medium/large`: Better accuracy, slower
- **Text files**: Automatically removes timestamps in format `HH:MM:SS`
- **Transcripts**: Saved to `transcripts/` subfolder (only for videos)

## 🎯 Examples

### Batch Processing

```bash
# Analyze multiple files
for file in *.mp4; do
  speech_analysis "$file" --output-dir ./batch_results
done
```

### Quick Analysis

```bash
# Fast analysis with tiny model
speech_analysis lecture.mp4 --model tiny --output-dir ~/tmp
```

### Detailed Review

```bash
# Full verbose output with visualization
speech_analysis presentation.mp4 -v --graph --model small
```

## 📄 Version

Current version: 2.0.0

## 👤 Author

Created by sultansamid

---

**Ready to improve your speaking skills!** 🎤✨
