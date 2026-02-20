import os
import re

with open('speech_analysis.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Imports
c = re.sub(r'import json\n\nimport hashlib', r'import json\nimport hashlib\nfrom output_manager import append_to_metrics, get_file_id, is_file_processed', c)

# 2. Remove local get_file_id and is_speech_file_processed
c = re.sub(r'def get_file_id\(file_path\):.*?return False\n\n', '', c, flags=re.DOTALL)

# 3. Update setup_output_paths to setup_transcript_path
setup_path_old = r'def setup_output_paths\(file_path, output_dir\):.*?(?=\# \-\-\- Output Functions \-\-\-)'
setup_path_new = '''def setup_transcript_path(file_path):
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]
    transcript_path = None
    if not detect_file_type(file_path):
        transcript_dir = "transcripts"
        os.makedirs(transcript_dir, exist_ok=True)
        transcript_path = os.path.join(transcript_dir, f"{base_name}.txt")
    return transcript_path

'''
c = re.sub(setup_path_old, setup_path_new, c, flags=re.DOTALL)

# 4. process_and_analyze_file signature and JSON saving removal
proc_old = r'def process_and_analyze_file\(file_path, model, json_path, transcript_path, is_text_file, verbose, file_id=None\):.*?return analysis_results'
proc_new = '''def process_and_analyze_file(file_path, model, transcript_path, is_text_file, verbose):
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
    
    analysis_results = perform_speech_analysis(transcript_text)
    
    final_json_output = {
        "transcript": transcript_text,
        **analysis_results
    }
    
    return final_json_output'''
c = re.sub(proc_old, proc_new, c, flags=re.DOTALL)

# 5. Fix ArgumentParser arguments
args_old = r"parser\.add_argument\('--output-dir'.*?help='Output directory for results \(default: current directory\)'\)\n\n    parser\.add_argument\('--model'.*?help='Whisper model size \(default: base\)'\)\n\n    parser\.add_argument\('--verbose'.*?help='Show detailed output \(default: minimal\)'\)"
args_new = """parser.add_argument('--history', type=str, default='speech_analysis_history.json',
                       help='Output history JSON file (default: speech_analysis_history.json)')
    parser.add_argument('--model', type=str, default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size (default: base)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Disable verbose output (default: False)')"""
c = re.sub(args_old, args_new, c, flags=re.DOTALL)

# 6. Update print_minimal_output
old_min_out = r'def print_minimal_output\(filename, json_path\):.*?print\(f"\\u2192 Results: \{json_path\}"\)'
new_min_out = '''def print_minimal_output(filename, json_path):
    print(f"✓ Analyzed: {filename}\\n→ Results appended to: {json_path}")'''
c = re.sub(old_min_out, new_min_out, c, flags=re.DOTALL)

# 7. Update main batch processing logic
main_old = r'    if not args\.verbose: warnings\.filterwarnings\(\'ignore\'\).*?sys\.exit\(0\)'
main_new = '''    if args.quiet: warnings.filterwarnings('ignore')
    setup_nltk()

    if not args.quiet: print(f"Loading Whisper model '{args.model}'...")
    try:
        model = whisper.load_model(args.model)
    except Exception as e:
        print(f"Error loading Whisper model: {e}", file=sys.stderr)
        sys.exit(1)

    graphs_to_show = []
    for current_file in files_to_process:
        file_id = get_file_id(current_file)
        fname = os.path.basename(current_file)
        if is_file_processed(args.history, fname, file_id):
            print(f"Skipping '{fname}' (already processed with ID: {file_id}).")
            continue
            
        print(f"\\nProcessing {fname}...")
        is_text = detect_file_type(current_file)
        transcript_path = setup_transcript_path(current_file)
        
        analysis_results = process_and_analyze_file(
            current_file, model, transcript_path,
            is_text, not args.quiet
        )
        if analysis_results is None: continue
        
        append_to_metrics(args.history, fname, file_id, analysis_results)
        
        if not args.quiet: print_verbose_output(analysis_results, fname)
        else: print_minimal_output(fname, args.history)
        
        if args.graph: graphs_to_show.append((analysis_results['word_frequency'], fname))

    for freq, fname in graphs_to_show:
        display_frequency_graph(freq, fname, show=True)
    sys.exit(0)'''
c = re.sub(main_old, main_new, c, flags=re.DOTALL)

with open('speech_analysis.py', 'w', encoding='utf-8') as f:
    f.write(c)
