import logging
import numpy as np
from typing import Dict, Any

try:
    import opensmile
    import pandas as pd
except ImportError:
    logging.error("opensmile or pandas not installed.")

logger = logging.getLogger(__name__)

def evaluate_acoustics(audio_path: str) -> Dict[str, float]:
    """
    Extracts acoustic features using OpenSMILE (eGeMAPSv02).
    Calculates F1/F2 Standard Deviation (jaw/tongue mobility) and Mean HNR (voice clarity).
    Filters out non-voiced frames before calculating variance.
    """
    logger.info("Initializing OpenSMILE feature extractor (eGeMAPS Low-Level Descriptors)...")
    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
    )
    
    logger.info(f"Processing acoustics for {audio_path}...")
    df = smile.process_file(audio_path)
    
    # Fields of interest in eGeMAPS
    # F0semitoneFrom27.5Hz_sma3nz - Pitch (we use this to detect voiced frames)
    # F1frequency_sma3nz - Formant 1 frequency
    # F2frequency_sma3nz - Formant 2 frequency
    # HarmonicToNoiseRatio_sma3nz - Harmonics-to-Noise Ratio
    
    f0_col = "F0semitoneFrom27.5Hz_sma3nz"
    f1_col = "F1frequency_sma3nz"
    f2_col = "F2frequency_sma3nz"
    hnr_col = "HarmonicToNoiseRatio_sma3nz"
    
    # Filter voiced frames: frames where F0 (pitch) > 0 and F1/F2 > 0
    # Unvoiced frames usually have 0 or very low values for F1/F2 in opensmile
    voiced_mask = (df[f0_col] > 0) & (df[f1_col] > 0) & (df[f2_col] > 0)
    voiced_df = df[voiced_mask]
    
    if len(voiced_df) == 0:
        logger.warning("No voiced frames found in the audio! Returning zeros.")
        return {
            "f1_variance_sd": 0.0,
            "f2_variance_sd": 0.0,
            "mean_hnr": 0.0
        }
        
    f1_sd = float(np.std(voiced_df[f1_col]))
    f2_sd = float(np.std(voiced_df[f2_col]))
    mean_hnr = float(np.mean(voiced_df[hnr_col]))
    
    result = {
        "f1_variance_sd": round(f1_sd, 2),
        "f2_variance_sd": round(f2_sd, 2),
        "mean_hnr": round(mean_hnr, 2)
    }
    
    logger.info(f"Acoustic evaluation complete. F1 SD: {result['f1_variance_sd']}, HNR: {result['mean_hnr']}")
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Acoustics Module - Ready")
