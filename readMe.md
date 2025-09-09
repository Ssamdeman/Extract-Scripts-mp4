# 🎙️ Video Speech Analysis Tool

A Python tool that automatically transcribes video files using OpenAI's Whisper and analyzes the speech to help improve public speaking skills.

## ✨ Features

- **Batch Transcription**: Supports `.mp4`, `.mov`, `.mkv`, and other common video formats.
- **Word Frequency Analysis**: Identifies and counts the most-used words in your speech.
- **Visual Feedback**: Generates a bar chart of top words for a clear visual overview.
- **Filler Word Detection**: Catches crutch words like "um," "uh," "like," and "you know."
- **Readability Score**: Calculates the Flesch-Kincaid grade level to assess complexity.
- **Dual-Mode Operation**: Run as a simple transcriber or a full speech analyzer.

## 📁 Folder Structure

speech_analyzer/
├── video_files/ # Drop your video files here
├── transcripts/ # Transcribed .txt files are saved here
├── main.py # The main script
└── README.md # This file

## 🚀 How to Use

1.  **Clone or create this folder.**

2.  **Set up a Python virtual environment.**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies.**

    ```bash
    pip install --upgrade pip
    pip install openai-whisper nltk matplotlib textstat
    ```

    _Note: The first time you run the script, `nltk` will automatically download required data packages._

4.  **Add your videos.**

    - Place your video files inside the `video_files/` directory.

5.  **Run the script.**

    - **For transcription only:**

      ```bash
      python main.py
      ```

    - **For transcription AND speech analysis:**
      ```bash
      python main.py --word_analysis
      ```

6.  **Get your results.**
    - Plain text transcripts will appear in the `transcripts/` folder.
    - If using analysis mode, a report will be printed in your terminal and a word frequency graph will be displayed.

## 📌 Notes

- **System Requirement**: You must have **FFmpeg** installed on your system for Whisper to process video files.
- **Whisper Model**: The script uses the `"base"` model by default for a balance of speed and accuracy. This can be changed in `main.py`.
- **Graph Behavior**: When running an analysis, the script will pause to display each graph. Simply close the graph window to continue to the next file.
