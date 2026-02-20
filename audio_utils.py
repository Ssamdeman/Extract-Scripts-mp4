import logging
import tempfile
import ffmpeg
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_audio_to_wav(input_path: str) -> str:
    """
    Extracts audio from any video or audio file and converts it 
    to a 16kHz mono WAV file suitable for opensmile and whisper.
    Returns the path to the temporary WAV file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    logger.info(f"Extracting audio from {input_path}...")
    
    # Create a temporary file with a .wav extension
    temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_fd) # Close file descriptor so ffmpeg can write to it
    
    try:
        # Run ffmpeg wrapper directly capturing standard output/error to avoid spam
        (
            ffmpeg
            .input(input_path)
            .output(temp_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
        logger.info(f"Audio extracted to temporary 16kHz WAV: {temp_path}")
        return temp_path
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode('utf8') if e.stderr else str(e)}")
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise RuntimeError("Failed to extract audio using ffmpeg")

if __name__ == "__main__":
    # Simple debug test
    logging.basicConfig(level=logging.INFO)
    print("Audio Utils Module - Ready")
