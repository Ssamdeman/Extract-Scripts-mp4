import streamlit as st
import os
import json
import time
import random
from pathlib import Path

# Importers from the existing backend
from audio_utils import extract_audio_to_wav
from transcription import evaluate_transcription
from acoustics import evaluate_acoustics
from output_manager import append_to_metrics, get_file_id, is_file_processed
import config

st.set_page_config(
    page_title="ARTICULATION ANALYZER", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- BRUTALIST MINIMAL DESIGN SYSTEM INJECTION ---
st.markdown("""
<style>
/* Font Imports */
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* Hide Defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Base Theme */
.stApp {
    background-color: #050505;
    color: #E0E0E0;
    font-family: 'JetBrains Mono', monospace;
}

/* Typography */
h1, h2, h3 {
    font-family: 'Oswald', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
h1 {
    font-size: 5rem !important;
    font-weight: 700 !important;
    color: #FFFFFF;
    border-bottom: 8px solid #FF3300;
    padding-bottom: 0px;
    line-height: 1.1;
    margin-bottom: 2rem !important;
    margin-top: -3rem !important;
}
p {
    font-size: 1rem;
    color: #888888;
}

/* Uploader Overlay */
[data-testid="stFileUploader"] {
    border: 4px solid #333333 !important;
    border-radius: 0px !important;
    background-color: #0A0A0A !important;
    padding: 3rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #FFFFFF !important;
}
[data-testid="stFileUploader"] small {
    display: none; /* Hide 'Limit 200MB per file' */
}
[data-testid="stFileUploadDropzone"] {
    color: #FFFFFF !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 0px !important;
    border: 4px solid #FF3300 !important;
    background-color: #FF3300 !important;
    color: #000000 !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    padding: 1.5rem !important;
    transition: all 0.1s ease;
    box-shadow: 4px 4px 0px #000000;
}
.stButton > button:hover {
    background-color: #000000 !important;
    color: #FF3300 !important;
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px #FF3300;
}
.stButton > button:active {
    transform: translate(2px, 2px);
    box-shadow: 0px 0px 0px #FF3300;
}

/* Expander/Containers */
[data-testid="stExpander"] {
    border: 2px solid #333 !important;
    background-color: #0A0A0A !important;
    border-radius: 0px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Oswald', sans-serif !important;
    color: #FFF !important;
    font-size: 1.2rem;
    text-transform: uppercase;
}

/* Spinners/Loading */
.stSpinner {
    color: #FF3300 !important;
}

/* Alerts / Banners */
[data-testid="stAlert"] {
    border-radius: 0px !important;
    border-left: 8px solid #FF3300 !important;
    background-color: #1A1A1A !important;
    color: #FFF !important;
}
[data-testid="stAlert"] div {
    color: #FFF !important;
}

/* JSON Output Truncation Logic via CSS */
.json-preview {
    max-height: 250px;
    overflow-y: hidden;
    position: relative;
    border: 2px solid #333;
    padding: 1rem;
    background: #000;
    margin-bottom: 1rem;
}
.json-preview::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100px;
    background: linear-gradient(transparent, #050505);
}

/* Center Loading State */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    padding: 3rem;
    text-align: center;
    border: 4px dashed #333;
    margin: 2rem 0;
}
.loading-text {
    font-family: 'Oswald', sans-serif !important;
    font-size: 2.5rem !important;
    color: #FF3300;
    text-transform: uppercase;
    animation: pulse 1s infinite alternate;
}
@keyframes pulse {
    0% { opacity: 0.3; transform: scale(0.98); }
    100% { opacity: 1; transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1>ARTICULATION<br>ANALYZER</h1>", unsafe_allow_html=True)
st.markdown("<p>DROP IN RAW AUDIO. GET TRUTH.</p>", unsafe_allow_html=True)

# --- DIRECTORIES ---
RESOURCES_DIR = Path("resources/articulations")
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = "metrics_history.json"

# --- UPLOADER ---
uploaded_file = st.file_uploader("UPLOAD MEDIA", type=["m4a", "mp4", "mov", "mkv", "wav"])

if uploaded_file is not None:
    # 1. Save uploaded file to resources/articulations
    file_path = RESOURCES_DIR / uploaded_file.name
    
    # Check if we should render analyze button
    st.write("---")
    
    if st.button("EXECUTE ANALYSIS", use_container_width=True):
        # Save bytes
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Determine Loading Message
        loading_msg = "INITIATING EXTRACTION SEQUENCE..."
        if os.path.exists("loading_messages.txt"):
            with open("loading_messages.txt", "r") as lf:
                msgs = [L.strip() for L in lf if L.strip()]
                if msgs:
                    loading_msg = random.choice(msgs)
                    
        # Initiate pipeline
        loading_placeholder = st.empty()
        loading_placeholder.markdown(f'<div class="loading-container"><div class="loading-text">{loading_msg}</div></div>', unsafe_allow_html=True)
        time.sleep(0.1)  # Brief pause to ensure UI renders before blocking thread
        
        start_time = time.time()
        file_id = get_file_id(str(file_path))
        
        # Check history
        if is_file_processed(HISTORY_FILE, uploaded_file.name, file_id):
            loading_placeholder.empty()
            st.warning(f"FILE '{uploaded_file.name}' ALREADY ANALYZED. CHECK HISTORY.")
        else:
            wav_path = None
            try:
                # Audio pass
                wav_path = extract_audio_to_wav(str(file_path))
                
                # Compute
                transcription_metrics = evaluate_transcription(
                    wav_path,
                    conf_threshold=config.WEAK_WORD_CONFIDENCE_THRESHOLD,
                    pause_threshold=config.PAUSE_THRESHOLD_SECONDS
                )
                acoustic_metrics = evaluate_acoustics(wav_path)
                
                # Merge dictionaries strictly
                final_metrics = {**transcription_metrics, **acoustic_metrics}
                
                # Dispatch to JSON history
                append_to_metrics(HISTORY_FILE, uploaded_file.name, file_id, final_metrics)
                
                elapsed = time.time() - start_time
                loading_placeholder.empty()
                st.success(f"ANALYSIS COMPLETE IN {elapsed:.2f}s")
                
                # Render JSON payload
                st.markdown("### SYSTEM OUTPUT")
                
                # Generate a truncated raw string view, then an expander
                json_str = json.dumps(final_metrics, indent=2)
                
                # Copy JSON requirement via download_button above output
                st.download_button(
                    label="DOWNLOAD / COPY JSON",
                    data=json_str,
                    file_name=f"ARTICULATION_{file_id}.json",
                    mime="application/json"
                )
                
                truncated_json = "\n".join(json_str.splitlines()[:15])
                
                st.markdown(f'<div class="json-preview"><pre style="color: #0f0; margin: 0;">{truncated_json}</pre></div>', unsafe_allow_html=True)
                
                with st.expander("VIEW FULL PAYLOAD"):
                    st.json(final_metrics)
                    
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"CRITICAL FAILURE: {str(e)}")
            finally:
                # Strict disk hygiene
                if wav_path and os.path.exists(wav_path):
                    os.remove(wav_path)
