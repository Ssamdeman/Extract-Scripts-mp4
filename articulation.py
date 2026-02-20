import typer
import logging
import os
import time
from pathlib import Path

from config import WEAK_WORD_CONFIDENCE_THRESHOLD, PAUSE_THRESHOLD_SECONDS
from audio_utils import extract_audio_to_wav
from transcription import evaluate_transcription
from acoustics import evaluate_acoustics
from output_manager import append_to_metrics

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = typer.Typer(help="Articulation Analysis CLI")

@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="Path to the audio/video file to analyze"),
    history_file: str = typer.Option("metrics_history.json", "--history", "-h", help="Path to the JSON history file to append to")
):
    """
    Analyze speech articulation metrics from an audio or video file.
    """
    if not input_file.exists():
        typer.secho(f"Error: File '{input_file}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Starting analysis for: {input_file.name}", fg=typer.colors.CYAN, bold=True)
    start_time = time.time()
    
    # Process audio
    wav_path = None
    try:
        wav_path = extract_audio_to_wav(str(input_file))
        
        # 1. Transcription metrics (Whisper)
        typer.secho("Running transcription analysis...", fg=typer.colors.BLUE)
        transcription_metrics = evaluate_transcription(
            wav_path, 
            conf_threshold=WEAK_WORD_CONFIDENCE_THRESHOLD, 
            pause_threshold=PAUSE_THRESHOLD_SECONDS
        )
        
        # 2. Acoustic metrics (OpenSmile)
        typer.secho("Running acoustic analysis...", fg=typer.colors.BLUE)
        acoustic_metrics = evaluate_acoustics(wav_path)
        
        # 3. Merge metrics
        final_metrics = {**transcription_metrics, **acoustic_metrics}
        
        # 4. Save to history
        append_to_metrics(history_file, str(input_file.name), final_metrics)
        
        elapsed = time.time() - start_time
        typer.secho(f"\nAnalysis complete in {elapsed:.1f}s!", fg=typer.colors.GREEN, bold=True)
        
        # Display summary to terminal
        typer.secho("--- ARTICULATION SUMMARY ---", bold=True)
        typer.echo(f"Speech Rate: {final_metrics['speech_rate_sps']} syllables/sec")
        typer.echo(f"Pauses (> {PAUSE_THRESHOLD_SECONDS}s): {final_metrics['pause_count']} (avg {final_metrics['avg_pause_duration_sec']}s)")
        typer.echo(f"Jaw Mobility (F1 SD): {final_metrics['f1_variance_sd']}")
        typer.echo(f"Tongue Mobility (F2 SD): {final_metrics['f2_variance_sd']}")
        typer.echo(f"Voice Clarity (Mean HNR): {final_metrics['mean_hnr']}")
        
        weak_words = final_metrics['weak_words']
        if weak_words:
            typer.secho(f"\nWeak Words ({len(weak_words)} words below {WEAK_WORD_CONFIDENCE_THRESHOLD} conf):", fg=typer.colors.YELLOW)
            for w in weak_words[:10]: # Limit console output to 10
                typer.echo(f"  - '{w['word']}' (conf: {w['probability']:.2f}, at {w['start']:.1f}s)")
            if len(weak_words) > 10:
                typer.echo(f"  ... and {len(weak_words) - 10} more.")
        else:
            typer.secho("\nExcellent articulation! No weak words detected.", fg=typer.colors.GREEN)
            
    except Exception as e:
        typer.secho(f"\nAnalysis failed: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    finally:
        # Cleanup
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    app()