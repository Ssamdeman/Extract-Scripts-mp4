# 🎙️ Speech Analysis & Articulation Suite

A dual-purpose command-line suite that helps improve public speaking skills through transcription analysis and acoustic articulation tracking.

## ✨ Features

The suite contains two distinct tools:

**1. Speech Analysis (`speech_analysis.py`)**
- **Video & Text Support**: Analyze `.mp4`, `.mov`, `.mkv` videos or existing `.txt` transcripts
- **Automatic Transcription**: Uses Whisper AI to convert speech to text
- **Speech Statistics**: Word counts, unique words, filler word usage percentage
- **Readability Analysis**: Flesch-Kincaid grade level with interpretation
- **Filler Word Detection**: Identifies crutch words like "um," "uh," "like," "you know"
- **Word Frequency Analysis**: Top 15 most-used meaningful words
- **JSON Output**: Structured data perfect for feeding into LLMs for deeper analysis
- **Optional Visualization**: Bar chart of word frequency (opt-in with `--graph`)
- **Multiple Model Sizes**: Choose from tiny/base/small/medium/large Whisper models

**2. Articulation & Mobility Tracking (`articulation.py`)**
Tracks your physical speaking attributes and records daily metric trends (Accepts any media file: `.mp4`, `.mov`, `.mkv`, `.wav`, `.mp3`).
- **Acoustic Feature Extraction**: Uses `opensmile` to measure jaw and tongue mobility (F1/F2 Standard Deviation).
- **Voice Clarity**: Calculates Harmonics-to-Noise Ratio (HNR).
- **Speech Rate**: Syllables-per-second tracking using `faster-whisper` and `syllables`.
- **Weak Words**: Identifies mumbled or poorly articulated words based on Whisper confidence scores over active speech.
- **Progress Tracking**: Appends records directly to a single `metrics_history.json` for daily trend monitoring.

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
pip install -r requirements.txt
```

### 3. Make the script executable

```bash
chmod +x speech_analysis.py
chmod +x articulation.py
```

## 💻 Usage

### Tool 1: Speech Analysis (`speech_analysis.py`)

Primary tool for transcripts, filler words, and readability.

```bash
# Analyze a video
python speech_analysis.py video.mp4

# Analyze an existing transcript
python speech_analysis.py transcript.txt

# Show word frequency graph and use better Whisper model
python speech_analysis.py video.mp4 --graph --model small
```

**Available Flags (`speech_analysis.py`)**

| Flag                | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `--graph`           | Display word frequency bar chart                                   |
| `--output-dir PATH` | Specify output directory (default: current directory)              |
| `--model NAME`      | Choose Whisper model: tiny/base/small/medium/large (default: base) |
| `--verbose`, `-v`   | Show detailed analysis output                                      |
| `--llm-prompt`      | Print LLM prompt template (for copying to AI assistants)           |
| `--version`         | Show version number                                                |


### Tool 2: Audio Articulation Tracker (`articulation.py`)

Secondary tool for tracking physical jaw/tongue mobility and weak words. Appends all metrics to `metrics_history.json`.

```bash
# Analyze a daily video or audio file (.mp4, .mov, .mkv, .wav, .mp3)
python articulation.py video.mp4

# Track history dynamically
python articulation.py test.mp3 --history ./custom_history.json
```

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

### Step 1: Get the prompt template

```bash
python speech_analysis.py --llm-prompt
```


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
  python speech_analysis.py "$file" --output-dir ./batch_results
done
```

### Quick Analysis

```bash
# Fast analysis with tiny model
python speech_analysis.py lecture.mp4 --model tiny --output-dir ~/tmp
```

### Detailed Review

```bash
# Full verbose output with visualization
python speech_analysis.py presentation.mp4 -v --graph --model small
```

## 📄 Version

Current version: 3.0.0

## 👤 Author

Created by Samuel Damon

---

**Ready to improve your speaking skills!** 🎤✨
