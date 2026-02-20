# 🎙️ Speech Analysis & Articulation Suite - Windows Guide

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

- **Python 3.8+**: Ensure "Add Python to PATH" is checked during installation.
- **FFmpeg**: Required for audio processing.

### FFmpeg Installation for Windows
1.  **Using Winget (Recommended)**:
    Open PowerShell and run:
    ```powershell
    winget install "FFmpeg (Essentials Build)"
    ```
    *Restart your terminal after installation.*


## 🚀 Installation

### 1. Set up Python environment

Open PowerShell or Command Prompt in the project folder:

```powershell
# Create virtual environment
python -m venv mp4-script

# Activate virtual environment
.\mp4-script\Scripts\activate
```

> **Note:** If you see an error about scripts being disabled, run this in PowerShell as Administrator:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 💻 Usage

Run the tool specifically using the `python` command.

### Tool 1: Speech Analysis (`speech_analysis.py`)

Primary tool for transcripts, filler words, and readability.

```powershell
# Analyze a video file
python speech_analysis.py video.mp4

# Analyze an existing transcript
python speech_analysis.py transcript.txt

# Show word frequency graph & better Whisper model
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

```powershell
# Analyze a daily video or audio file (.mp4, .mov, .mkv, .wav, .mp3)
python articulation.py video.mp4

# Track history dynamically
python articulation.py test.mp3 --history .\custom_history.json
```

## 📊 Output

### Console Output
```
✓ Analyzed: video.mp4
→ Results: analysis_video_2025-10-13_14-30-00.json
```

The tool creates a JSON file containing the full analysis (transcription, filler word counts, readability scores, etc.).

## 🤖 Using with LLMs

Generate a prompt to use with ChatGPT or Claude to get feedback on your speech:

```powershell
python speech_analysis.py --llm-prompt
```

## 🔧 Troubleshooting

### "python is not recognized"
Ensure Python is added to your PATH. Reinstall Python and check the "Add Python to PATH" box at the bottom of the installer.

### "ffmpeg not found" or "FileNotFoundError"
FFmpeg is likely not in your PATH. Open a new terminal and type `ffmpeg -version`. If it errors, check the [Requirements](#requirements) section above to install it.

### NLTK Errors
The script attempts to download necessary NLTK data automatically. If it fails, you can run:

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```
