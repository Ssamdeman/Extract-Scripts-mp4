import os

# Threshold for flagging "weak words" based on whisper word-level confidence
WEAK_WORD_CONFIDENCE_THRESHOLD = 0.70

# Minimum gap in seconds to be considered a pause
PAUSE_THRESHOLD_SECONDS = 0.4

# Expected sample rate for output wav files (opensmile standard)
TARGET_SAMPLE_RATE = 16000
