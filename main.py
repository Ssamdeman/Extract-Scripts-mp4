import whisper
import sys
import os


def format_text_without_timestamps(result):
    lines = [segment['text'].strip() for segment in result['segments']]
    return '\n'.join(lines)



def transcribe_video(video_path, output_txt_path, model):
    print(f"\nTranscribing: {video_path}")
    result = model.transcribe(video_path)

   
    # Save result as .txt
    with open(output_txt_path, "w", encoding="utf-8") as f:
        formatted_text = format_text_without_timestamps(result)
        f.write(formatted_text)
    print(f"Transcription saved to: {output_txt_path}")




# def format_text_with_timestamps(result):
#     lines = []
#     for segment in result['segments']:
#         start = segment['start']
#         end = segment['end']
#         text = segment['text'].strip()
#         lines.append(f"[{start:.2f} - {end:.2f}] {text}")
#     return '\n'.join(lines)



def main():
    input_folder = "video_files"
    output_folder = "transcripts"
    supported_extensions = (".mp4", ".mov", ".mkv", ".avi")

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load Whisper model once
    model = whisper.load_model("base")

    # Iterate over all video files
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(supported_extensions):
            video_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_txt_path = os.path.join(output_folder, f"{base_name}.txt")
            transcribe_video(video_path, output_txt_path, model)

    print("\nAll transcriptions completed.")




if __name__ == "__main__":
    main()  