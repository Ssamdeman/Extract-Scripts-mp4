import os
import re

with open('speech_analysis.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Add hashlib
if 'import hashlib' not in c:
    c = re.sub(r'(import json\s+)', r'\1import hashlib\n\n', c, count=1)

# Add helper functions
helpers = '''def get_file_id(fpath):
    if not os.path.exists(fpath): return ""
    import hashlib
    import os
    return hashlib.md5(f"{os.path.basename(fpath)}-{os.stat(fpath).st_size}".encode()).hexdigest()

def is_speech_file_processed(out_dir, sfile, fid):
    if not os.path.exists(out_dir): return False
    import json
    import os
    for f in os.listdir(out_dir):
        if f.endswith('.json') and f.startswith('analysis_'):
            try:
                d = json.load(open(os.path.join(out_dir, f), 'r', encoding='utf-8'))
                if d.get('source_file') == sfile or d.get('file_id') == fid: return True
            except: pass
    return False

def process_and_analyze_file(file_path, model, json_path, transcript_path, is_text_file, verbose, file_id=None):'''

if 'def get_file_id' not in c:
    c = re.sub(r'def process_and_analyze_file\(.*?verbose\):', helpers, c, flags=re.DOTALL)

# Add file_id to json structure
target = r'"source_file": filename,'
rep = '"source_file": filename,\n        "file_id": file_id,'
if '"file_id": file_id' not in c:
    c = re.sub(target, rep, c)

# Replace main loop entirely starting from args.file
main_regex = r'    # For analysis mode, file is required.*?    sys\.exit\(0\)'
main_rep = '''    # Batch Processing
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
            
        print(f"\\nProcessing {fname}...")
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
    sys.exit(0)'''

if 'files_to_process = []' not in c:
    c = re.sub(main_regex, main_rep, c, flags=re.DOTALL)

with open('speech_analysis.py', 'w', encoding='utf-8') as f:
    f.write(c)
