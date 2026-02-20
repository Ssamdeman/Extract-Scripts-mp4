import logging
import syllables
from typing import Dict, Any

try:
    from faster_whisper import WhisperModel
except ImportError:
    logging.error("faster-whisper is not installed. Please install it.")

logger = logging.getLogger(__name__)

def evaluate_transcription(audio_path: str, conf_threshold: float, pause_threshold: float) -> Dict[str, Any]:
    """
    Runs faster-whisper on the audio to get text, word confidences, and timestamps.
    Calculates weak words, pause counts, average pause duration, and speech rate.
    """
    logger.info("Loading faster-whisper model ('base' via CPU to prevent CUDA errors)...")
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
    except Exception as e:
        logger.warning(f"Failed to load Whisper on CPU: {e}")
        raise e

    logger.info(f"Transcribing {audio_path}...")
    segments_generator, info = model.transcribe(audio_path, word_timestamps=True, language="en")
    
    words_data = []
    full_text = ""
    
    for segment in segments_generator:
        full_text += segment.text + " "
        for word in segment.words:
            words_data.append({
                "word": word.word.strip(),
                "start": word.start,
                "end": word.end,
                "probability": word.probability
            })

    full_text = full_text.strip()
    
    # 1. Weak Words
    weak_words = [w for w in words_data if w["probability"] < conf_threshold]
    
    # 2. Pauses
    pause_count = 0
    total_pause_duration = 0.0
    
    for i in range(1, len(words_data)):
        prev_word = words_data[i-1]
        curr_word = words_data[i]
        
        gap = curr_word["start"] - prev_word["end"]
        if gap >= pause_threshold:
            pause_count += 1
            total_pause_duration += gap
            
    avg_pause_duration = (total_pause_duration / pause_count) if pause_count > 0 else 0.0

    # 3. Speech Rate (Syllables per second of active speech)
    total_syllables = syllables.estimate(full_text)
    
    # Total duration is end of last word - start of first word
    # Active duration is total duration minus all pause > pause_threshold
    if words_data:
        total_duration = words_data[-1]["end"] - words_data[0]["start"]
        active_duration = total_duration - total_pause_duration
    else:
        active_duration = 0.0
        
    sps = (total_syllables / active_duration) if active_duration > 0 else 0.0
    
    result = {
        "text": full_text,
        "word_count": len(words_data),
        "weak_words": weak_words,
        "pause_count": pause_count,
        "avg_pause_duration_sec": round(avg_pause_duration, 3),
        "speech_rate_sps": round(sps, 2)
    }
    
    logger.info("Transcription analysis complete.")
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Transcription Module - Ready")
