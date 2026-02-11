import os
import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Import STT adapter from backend/stt
try:
    from backend.stt.adapters import get_adapter
    from backend.stt.audio_converter import normalize_audio
except ImportError:
    sys.path.append(str(current_dir / 'backend'))
    from stt.adapters import get_adapter
    from stt.audio_converter import normalize_audio
    from stt.adapters import get_adapter
    from stt.audio_converter import normalize_audio

# Force pydub to use local ffmpeg if available
from pydub import AudioSegment
local_ffmpeg = os.path.join(current_dir, "ffmpeg.exe")
if os.path.exists(local_ffmpeg):
    AudioSegment.converter = local_ffmpeg
    print(f"[Config] Using local ffmpeg: {local_ffmpeg}")

def convert_stt_to_json(input_dir: str, output_json: str):
    """
    Reads audio files, transcribes them, and saves to JSON.
    """
    input_path = Path(input_dir)
    output_path = Path(output_json)
    
    if not input_path.exists():
        print(f"Error: Input '{input_dir}' does not exist.")
        return

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Initializing STT Adapter (CPU Mode)...")
    try:
        adapter = get_adapter("whisper", model_size="medium", device="cpu", compute_type="int8")
    except Exception as e:
        print(f"Error initializing STT adapter: {e}")
        sys.exit(1) # Fail explicitly

    results = []
    audio_extensions = {".wav", ".mp3", ".m4a", ".flac"}
    
    if input_path.is_file():
        files = [input_path]
    else:
        # Directory: Recursive search
        files = [f for f in input_path.rglob("*") if f.suffix.lower() in audio_extensions]
    
    if not files:
        print(f"No audio files found in '{input_dir}'.")
        return

    print(f"Found {len(files)} audio files. Starting transcription...")

    for i, file_path in enumerate(files, 1):
        print(f"Processing [{i}/{len(files)}]: {file_path.name}")
        
        try:
            # 1. Normalize
            norm_result = normalize_audio(str(file_path))
            target_audio = norm_result["normalized_path"]
            
            # 2. Transcribe
            stt_result = adapter.transcribe(target_audio)
            
            item = {
                "id": i,
                "filename": file_path.name,
                "utterance": stt_result.text_raw if not stt_result.error else "",
                "stt_meta": {
                    "confidence": stt_result.confidence,
                    "latency_ms": stt_result.latency_ms,
                    "error": stt_result.error
                }
            }
            results.append(item)
            print(f"  - Utterance: {item['utterance']}")

        except Exception as e:
            print(f"  - Failed to process {file_path.name}: {e}")
            results.append({
                "id": i,
                "filename": file_path.name,
                "utterance": "",
                "error": str(e)
            })

    # Save to JSON
    try:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully saved {len(results)} items to '{output_json}'")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    INPUT_AUDIO_DIR = "data/test_audio/01_general/김동국_일반1.m4a"
    OUTPUT_JSON_FILE = "poc/data/stt_output.json"
    
    if not os.path.exists(INPUT_AUDIO_DIR):
        print(f"Directory not found: {INPUT_AUDIO_DIR}")
        print("Please ensure your audio files are in this folder.")
    else:
        convert_stt_to_json(INPUT_AUDIO_DIR, OUTPUT_JSON_FILE)
