# main.py

import os

import sys

import argparse

import string

import collections

import json

from datetime import datetime

import re

import warnings

import whisper

import nltk

import matplotlib.pyplot as plt

import textstat

# --- Constants ---

FILLER_WORDS = [

    'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'right',

    'basically', 'actually', 'literally', 'i mean', 'okay'

]

TOP_N_WORDS = 15

# --- NLTK Setup ---

def setup_nltk():

    """Checks for and downloads all required NLTK data packages if missing."""

    required_packages = {

        'punkt': 'tokenizers/punkt',

        'stopwords': 'corpora/stopwords',

        'punkt_tab': 'tokenizers/punkt_tab'

    }

    try:

        for pkg_id, pkg_path in required_packages.items():

            nltk.data.find(pkg_path)

    except LookupError:

        print("First-time setup: Downloading required NLTK packages...")

        for pkg_id in required_packages:

            nltk.download(pkg_id, quiet=True)

        print("NLTK setup complete.")

# Add these functions to main.py after the `calculate_readability` function

def calculate_statistics(transcript_text, filler_words_dict):

    """

    Calculates text statistics including word counts and filler word percentage.

    

    Args:

        transcript_text: The full transcript text

        filler_words_dict: Dictionary of filler words and their counts

    

    Returns:

        Dictionary with statistics

    """

    # Tokenize for total word count (including all words)

    all_tokens = nltk.word_tokenize(transcript_text.lower())

    all_words = [word for word in all_tokens if word.isalpha()]

    

    total_words = len(all_words)

    unique_words = len(set(all_words))

    total_filler_words = sum(filler_words_dict.values())

    

    # Calculate percentage

    filler_percentage = (total_filler_words / total_words * 100) if total_words > 0 else 0

    

    return {

        "total_words": total_words,

        "unique_words": unique_words,

        "total_filler_words": total_filler_words,

        "filler_word_percentage": round(filler_percentage, 2)

    }

def interpret_readability_score(score):

    """

    Provides human-readable interpretation of Flesch-Kincaid grade level.

    

    Args:

        score: Flesch-Kincaid grade level score

    

    Returns:

        String interpretation of the score

    """

    if score < 6:

        return "Elementary school level (easy to understand)"

    elif score < 9:

        return "Middle school level (accessible to most)"

    elif score < 13:

        return "High school level (standard reading level)"

    elif score < 16:

        return "College level (more complex)"

    else:

        return "Graduate level (advanced/academic)"

# --- Text Cleaning and Transcription ---

def clean_text_timestamps(raw_text_content):

    """

    Removes HH:MM:SS timestamps from the beginning of lines in a string.

    """

    pattern = re.compile(r"^\d{2}:\d{2}:\d{2}\s?")

    cleaned_lines = [pattern.sub("", line) for line in raw_text_content.splitlines()]

    return "\n".join(cleaned_lines)

def format_text_without_timestamps(result):

    """Formats the transcription result from Whisper into a clean string."""

    lines = [segment['text'].strip() for segment in result['segments']]

    return '\n'.join(lines)

def transcribe_video(video_path, model, verbose):

    """Transcribes a single video file and returns the text content."""

    if verbose:

        print(f"Transcribing: {video_path}")

    try:

        result = model.transcribe(video_path)

        return format_text_without_timestamps(result)

    except Exception as e:

        print(f"Error during transcription: {e}", file=sys.stderr)

        return None

# --- Speech Analysis Functions ---

def process_text(text_content, remove_stopwords=True):

    """Cleans and tokenizes text."""

    text = text_content.lower()

    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = nltk.word_tokenize(text)

    if remove_stopwords:

        stop_words = set(nltk.corpus.stopwords.words('english'))

        tokens = [word for word in tokens if word not in stop_words and word.isalpha()]

    return tokens

def find_filler_words(all_words):

    """Counts the occurrences of predefined filler words."""

    filler_counts = collections.Counter(word for word in all_words if word in FILLER_WORDS)

    return dict(filler_counts)

def count_word_frequency(meaningful_words):

    """Counts the frequency of each word in a list of tokens."""

    counts = collections.Counter(meaningful_words)

    return counts.most_common(TOP_N_WORDS)

def calculate_readability(text_content):

    """Calculates the Flesch-Kincaid grade level of the text."""

    return textstat.flesch_kincaid_grade(text_content)

def display_frequency_graph(frequency_data, filename, show=False):

    """Generates and displays a bar chart of the most frequent words."""

    if not show:

        return

    

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

def perform_speech_analysis(text_content):

    """Runs all analysis tasks on a given text and returns the enhanced results."""

    # Calculate components

    filler_words_dict = find_filler_words(process_text(text_content, remove_stopwords=False))

    readability_score = calculate_readability(text_content)

    word_frequency = count_word_frequency(process_text(text_content, remove_stopwords=True))

    

    # Calculate statistics

    statistics = calculate_statistics(text_content, filler_words_dict)

    

    # Enhanced structure

    return {

        "statistics": statistics,

        "readability": {

            "score": round(readability_score, 2),

            "interpretation": interpret_readability_score(readability_score)

        },

        "filler_words": filler_words_dict,

        "word_frequency": word_frequency

    }

# --- File Handling ---

def detect_file_type(filepath):

    """Auto-detect if file is text or video based on extension."""

    ext = os.path.splitext(filepath)[1].lower()

    text_extensions = ['.txt', '.md', '.text']

    return ext in text_extensions

def setup_output_paths(file_path, output_dir):

    """Creates output directory and returns paths for JSON and transcript."""

    # Ensure output_dir exists

    os.makedirs(output_dir, exist_ok=True)

    

    filename = os.path.basename(file_path)

    base_name = os.path.splitext(filename)[0]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    

    # JSON always goes to output_dir

    json_path = os.path.join(output_dir, f"analysis_{base_name}_{timestamp}.json")

    

    # Transcripts subfolder only for videos

    transcript_path = None

    if not detect_file_type(file_path):

        transcript_dir = os.path.join(output_dir, "transcripts")

        os.makedirs(transcript_dir, exist_ok=True)

        transcript_path = os.path.join(transcript_dir, f"{base_name}.txt")

    

    return json_path, transcript_path

# --- Output Functions ---

def print_minimal_output(filename, json_path):

    """Print minimal output (default mode)."""

    print(f"Γ£ô Analyzed: {filename}")

    print(f"ΓåÆ Results: {json_path}")

def print_verbose_output(analysis_results, filename):

    """Print detailed analysis output."""

    print(f"\n----- Analysis for: {filename} -----")

    

    # Statistics

    stats = analysis_results['statistics']

    print(f"≡ƒôè Statistics:")

    print(f"  - Total words: {stats['total_words']}")

    print(f"  - Unique words: {stats['unique_words']}")

    print(f"  - Filler words: {stats['total_filler_words']} ({stats['filler_word_percentage']}%)")

    

    # Readability

    readability = analysis_results['readability']

    print(f"\n≡ƒôû Readability:")

    print(f"  - Score: {readability['score']} ({readability['interpretation']})")

    

    # Filler words

    fillers = analysis_results['filler_words']

    print("\n≡ƒùú∩╕Å Filler Word Breakdown:")

    if not fillers:

        print("  No common filler words found. Great job!")

    else:

        for word, count in fillers.items():

            print(f"  - '{word}': {count} times")

    

    # Word frequency

    frequencies = analysis_results['word_frequency']

    print(f"\n≡ƒôê Top {len(frequencies)} Most Used Meaningful Words:")

    for i, (word, count) in enumerate(frequencies):

        print(f"  {i+1}. '{word}': {count} times")

    print("---------------------------------------\n")

def get_llm_prompt_template():

    """Returns the LLM prompt template for speech improvement."""

    return (

        "Help me improve my speech. Here is my analysis in JSON format. "

        "It was analyzed by a speech analysis tool and contains: my full transcript, "

        "statistics (total words, unique words, filler word count and percentage), "

        "readability score with interpretation, a breakdown of which filler words I used "

        "and how many times, and the top 15 most frequently used meaningful words. "

        "Please review this data and give me specific, actionable suggestions to improve "

        "my speaking clarity, reduce filler words, and make my speech more engaging."

    )


def get_file_id(file_path):
    import hashlib
    if not os.path.exists(file_path): return ""
    return hashlib.md5(f"{os.path.basename(file_path)}-{os.stat(file_path).st_size}".encode()).hexdigest()

def is_speech_file_processed(output_dir, source_file, file_id):
    if not os.path.exists(output_dir): return False
    import json
    for f in os.listdir(output_dir):
        if f.endswith('.json') and f.startswith('analysis_'):
            try:
                data = json.load(open(os.path.join(output_dir, f), 'r', encoding='utf-8'))
                if data.get('source_file') == source_file or data.get('file_id') == file_id:
                    return True
            except: pass
    return False

def process_and_analyze_file(file_path, model, json_path, transcript_path, is_text_file, verbose, file_id=None):

    """

    Processes a single file (video or text) and outputs the analysis.

    Returns: dict with analysis results or None on error

    """

    filename = os.path.basename(file_path)

    transcript_text = ""

    if is_text_file:

        if verbose:

            print(f"Analyzing text file: {file_path}")

        try:

            with open(file_path, "r", encoding="utf-8") as f:

                raw_text = f.read()

            transcript_text = clean_text_timestamps(raw_text)

        except Exception as e:

            print(f"Error reading text file: {e}", file=sys.stderr)

            return None

    else:

        transcript_text = transcribe_video(file_path, model, verbose)

        if transcript_text and transcript_path:

            with open(transcript_path, "w", encoding="utf-8") as f:

                f.write(transcript_text)

            if verbose:

                print(f"Transcription saved to: {transcript_path}")

    if not transcript_text or not transcript_text.strip():

        print("Error: No text to analyze.", file=sys.stderr)

        return None

    

    # Perform analysis

    analysis_results = perform_speech_analysis(transcript_text)

    

    # Build enhanced JSON structure

    final_json_output = {

        "source_file": filename,
        "file_id": file_id,

        "transcript": transcript_text,

        **analysis_results  # Spreads: statistics, readability, filler_words, word_frequency

    }

    

    try:

        with open(json_path, "w", encoding="utf-8") as f:

            json.dump(final_json_output, f, indent=4)

    except Exception as e:

        print(f"Error saving JSON: {e}", file=sys.stderr)

        return None

    

    return analysis_results

def main():

    """Main function to handle command-line arguments and run the program."""

    parser = argparse.ArgumentParser(

        description="Analyze speech from video or text files",

        epilog="Example: speech_analysis video.mp4 --graph --output-dir ./results"

    )

    

    # Positional argument (now optional)

    parser.add_argument('file', nargs='?', help='Video or text file to analyze')

    

    # Optional flags

    parser.add_argument('--graph', action='store_true',

                       help='Display frequency graph (default: no graph)')

    parser.add_argument('--output-dir', type=str, default='.',

                       help='Output directory for results (default: current directory)')

    parser.add_argument('--model', type=str, default='base',

                       choices=['tiny', 'base', 'small', 'medium', 'large'],

                       help='Whisper model size (default: base)')

    parser.add_argument('--verbose', '-v', action='store_true',

                       help='Show detailed output (default: minimal)')

    parser.add_argument('--llm-prompt', action='store_true',

                       help='Print LLM prompt template for speech improvement')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.2')

    

    args = parser.parse_args()

    

    # Handle --llm-prompt flag (no file needed)

    if args.llm_prompt:

        print(get_llm_prompt_template())

        sys.exit(0)

    

    # Batch Processing
    valid_exts = {'.mp4', '.mov', '.mkv', '.wav', '.mp3', '.m4a', '.txt', '.md', '.text'}
    files_to_process = []
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        files_to_process.append(args.file)
    else:
        default_dir = os.path.join("resources", "speech_analysis")
        print(f"No explicit file provided. Scanning directory: {default_dir}")
        if os.path.exists(default_dir) and os.path.isdir(default_dir):
            for f in os.listdir(default_dir):
                f_path = os.path.join(default_dir, f)
                if os.path.isfile(f_path) and os.path.splitext(f_path)[1].lower() in valid_exts:
                    files_to_process.append(f_path)
        if not files_to_process:
            print(f"No valid media files found.", file=sys.stderr)
            sys.exit(0)

    if not args.verbose: warnings.filterwarnings('ignore')
    setup_nltk()

    if args.verbose: print(f"Loading Whisper model '{args.model}'...")
    try:
        model = whisper.load_model(args.model)
    except Exception as e:
        print(f"Error loading Whisper model: {e}", file=sys.stderr)
        sys.exit(1)

    graphs_to_show = []
    for current_file in files_to_process:
        file_id = get_file_id(current_file)
        fname = os.path.basename(current_file)
        if is_speech_file_processed(args.output_dir, fname, file_id):
            print(f"Skipping '{fname}' (already processed with ID: {file_id}).")
            continue
            
        print(f"\nProcessing {fname}...")
        is_text = detect_file_type(current_file)
        json_path, transcript_path = setup_output_paths(current_file, args.output_dir)
        
        analysis_results = process_and_analyze_file(
            current_file, model, json_path, transcript_path,
            is_text, args.verbose, file_id
        )
        if analysis_results is None: continue
        
        if args.verbose: print_verbose_output(analysis_results, fname)
        else: print_minimal_output(fname, json_path)
        
        if args.graph: graphs_to_show.append((analysis_results['word_frequency'], fname))

    for freq, fname in graphs_to_show:
        display_frequency_graph(freq, fname, show=True)
    sys.exit(0)

if __name__ == "__main__":

    main()

