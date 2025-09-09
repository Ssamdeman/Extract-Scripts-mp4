# main.py

import os
import sys
import argparse
import string
import collections

import whisper
import nltk
import matplotlib.pyplot as plt
import textstat

# --- Constants ---
# Common filler words and crutch phrases for public speaking
FILLER_WORDS = [
    'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'right', 
    'basically', 'actually', 'literally', 'i mean', 'okay'
]
# Number of top words to display in the graph and report
TOP_N_WORDS = 15


# --- NLTK Setup (Corrected and more robust) ---
def setup_nltk():
    """Checks for and downloads all required NLTK data packages if missing."""
    # List of required NLTK packages
    required_packages = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'punkt_tab': 'tokenizers/punkt_tab' # Added this required package
    }
    
    try:
        for pkg_id, pkg_path in required_packages.items():
            nltk.data.find(pkg_path)
    except LookupError:
        print("First-time setup: Downloading required NLTK packages...")
        for pkg_id in required_packages:
            nltk.download(pkg_id, quiet=True)
        print("NLTK setup complete.")


        
# --- Original Transcription Functions (from your code) ---
def format_text_without_timestamps(result):
    """Formats the transcription result into a clean string without timestamps."""
    lines = [segment['text'].strip() for segment in result['segments']]
    return '\n'.join(lines)

def transcribe_video(video_path, output_txt_path, model):
    """Transcribes a single video file and saves the result to a text file."""
    print(f"\nTranscribing: {video_path}")
    try:
        result = model.transcribe(video_path)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            formatted_text = format_text_without_timestamps(result)
            f.write(formatted_text)
        print(f"Transcription saved to: {output_txt_path}")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")


# --- New Speech Analysis Functions ---
def process_text(text_content, remove_stopwords=True):
    """
    Cleans and tokenizes text. Converts to lowercase, removes punctuation,
    and optionally removes common stop words.
    """
    # 1. Convert to lowercase
    text = text_content.lower()
    
    # 2. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 3. Tokenize (split into words)
    tokens = nltk.word_tokenize(text)
    
    # 4. Optionally remove stop words
    if remove_stopwords:
        stop_words = set(nltk.corpus.stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words and word.isalpha()]
        
    return tokens

def find_filler_words(all_words):
    """Counts the occurrences of predefined filler words."""
    filler_counts = collections.Counter(word for word in all_words if word in FILLER_WORDS)
    return filler_counts

def count_word_frequency(meaningful_words):
    """Counts the frequency of each word in a list of tokens."""
    counts = collections.Counter(meaningful_words)
    return counts.most_common(TOP_N_WORDS)

def calculate_readability(text_content):
    """Calculates the Flesch-Kincaid grade level of the text."""
    return textstat.flesch_kincaid_grade(text_content)

def display_frequency_graph(frequency_data, filename):
    """Generates and displays a bar chart of the most frequent words."""
    if not frequency_data:
        print("Cannot generate graph: No meaningful words found after filtering.")
        return
        
    words, counts = zip(*frequency_data)
    
    plt.figure(figsize=(12, 7))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel("Words", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.title(f"Top {TOP_N_WORDS} Most Frequent Words in '{filename}'", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def perform_speech_analysis(text_content, filename):
    """The main orchestrator for running all analysis tasks on a given text."""
    print(f"\n----- Analysis for: {os.path.basename(filename)} -----")

    # 1. Calculate Readability
    readability_score = calculate_readability(text_content)
    print(f"📊 Readability (Flesch-Kincaid Grade Level): {readability_score:.2f}")
    if readability_score > 12:
        print("   (Suggestion: Simplify language and sentence structure for a broader audience.)")
    elif readability_score < 7:
        print("   (Suggestion: Language is very simple and easy to follow.)")
    else:
        print("   (Suggestion: Language is suitable for a general audience.)")


    # 2. Process text for word counting
    all_words = process_text(text_content, remove_stopwords=False)
    meaningful_words = process_text(text_content, remove_stopwords=True)

    # 3. Find and count filler words
    filler_word_counts = find_filler_words(all_words)
    print("\n🗣️ Filler Word Analysis:")
    if not filler_word_counts:
        print("  No common filler words found. Great job!")
    else:
        for word, count in filler_word_counts.items():
            print(f"  - '{word}': Used {count} times")

    # 4. Count frequency of meaningful words
    word_frequencies = count_word_frequency(meaningful_words)
    print(f"\n📈 Top {len(word_frequencies)} Most Used Meaningful Words:")
    for i, (word, count) in enumerate(word_frequencies):
        print(f"  {i+1}. '{word}': Used {count} times")

    # 5. Display the graph
    display_frequency_graph(word_frequencies, filename)

    print("---------------------------------------\n")


# --- Main Execution Logic ---
def main():
    """Main function to handle command-line arguments and run the program."""
    parser = argparse.ArgumentParser(description="Transcribe videos and optionally analyze the speech.")
    parser.add_argument(
        '--word_analysis', 
        action='store_true',
        help="Run word frequency and speech analysis on the transcripts."
    )
    args = parser.parse_args()

    # Define input and output directories and supported video formats
    input_folder = "video_files"
    output_folder = "transcripts"
    supported_extensions = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".wmv")

    # Create folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Perform one-time setup for NLTK if needed
    setup_nltk()

    # Load Whisper model once
    print("Loading Whisper model (this may take a moment)...")
    try:
        model = whisper.load_model("base")
        print("Whisper model loaded.")
    except Exception as e:
        print(f"Error loading whisper model: {e}")
        print("Please ensure you have whisper installed and a stable internet connection for the first download.")
        return

    # Iterate over all video files
    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_extensions)]
    if not video_files:
        print(f"No video files found in the '{input_folder}' directory. Please add videos and try again.")
        return

    for filename in video_files:
        video_path = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]
        output_txt_path = os.path.join(output_folder, f"{base_name}.txt")
        
        # Always run transcription
        transcribe_video(video_path, output_txt_path, model)

        # If the analysis flag is set, run the analysis
        if args.word_analysis:
            try:
                with open(output_txt_path, "r", encoding="utf-8") as f:
                    transcript_text = f.read()

                if transcript_text.strip():
                    perform_speech_analysis(transcript_text, filename)
                else:
                    print(f"Skipping analysis for {filename}: transcript is empty.")
            except FileNotFoundError:
                print(f"Could not find transcript file for analysis: {output_txt_path}")


    print("\nAll tasks completed.")

if __name__ == "__main__":
    main()