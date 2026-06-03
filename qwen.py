# download_models.py
from huggingface_hub import snapshot_download

# Set your desired base directory
BASE_MODEL_DIR = "/opt/models"  # Change to your preferred path

# Download Qwen3-ASR-1.7B
asr_model_path = snapshot_download(
    repo_id="Qwen/Qwen3-ASR-1.7B",
    local_dir=f"{BASE_MODEL_DIR}/qwen3-asr-1.7b",
    local_dir_use_symlinks=False,   # copies files directly, no symlinks to cache
)

# Download Qwen3-ForcedAligner-0.6B
aligner_model_path = snapshot_download(
    repo_id="Qwen/Qwen3-ForcedAligner-0.6B",
    local_dir=f"{BASE_MODEL_DIR}/qwen3-forced-aligner-0.6b",
    local_dir_use_symlinks=False,
)

print(f"ASR model saved to:     {asr_model_path}")
print(f"Aligner model saved to: {aligner_model_path}")



# transcribe.py
import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from transformers import AutoModel, AutoTokenizer

# ── Config ──────────────────────────────────────────────────────────────
BASE_MODEL_DIR   = "/opt/models"
ASR_MODEL_DIR    = f"{BASE_MODEL_DIR}/qwen3-asr-1.7b"
ALIGNER_MODEL_DIR= f"{BASE_MODEL_DIR}/qwen3-forced-aligner-0.6b"
AUDIO_FILE       = "/path/to/your/call.wav"  # <-- change this

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE == "cuda" else torch.float32
# ────────────────────────────────────────────────────────────────────────


def load_asr_pipeline(model_dir: str):
    """Load Qwen3-ASR from a local directory (no cache)."""
    processor = AutoProcessor.from_pretrained(
        model_dir,
        local_files_only=True,   # never reach out to HF Hub
    )
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_dir,
        torch_dtype=DTYPE,
        local_files_only=True,
        low_cpu_mem_usage=True,
    ).to(DEVICE)

    asr_pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=DTYPE,
        device=DEVICE,
        return_timestamps=True,         # word-level timestamps
        chunk_length_s=30,              # sliding window for long audio
        stride_length_s=[5, 5],
    )
    return asr_pipe


def load_aligner(model_dir: str):
    """Load Qwen3-ForcedAligner from a local directory (no cache)."""
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        local_files_only=True,
    )
    model = AutoModel.from_pretrained(
        model_dir,
        torch_dtype=DTYPE,
        local_files_only=True,
    ).to(DEVICE)
    model.eval()
    return model, tokenizer


def load_audio(filepath: str, target_sr: int = 16000):
    """Load a WAV file and resample to 16 kHz mono."""
    waveform, sr = torchaudio.load(filepath)
    if waveform.shape[0] > 1:                          # stereo → mono
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        waveform = resampler(waveform)
    return waveform.squeeze().numpy(), target_sr        # numpy array


def transcribe_with_timestamps(audio_file: str):
    print("Loading ASR model...")
    asr_pipe = load_asr_pipeline(ASR_MODEL_DIR)

    print("Loading audio...")
    audio_array, sample_rate = load_audio(audio_file)

    print("Transcribing...")
    result = asr_pipe(
        {"array": audio_array, "sampling_rate": sample_rate},
        generate_kwargs={"language": "en"},   # remove/change for other languages
    )

    print("\n── Full Transcript ─────────────────────────────────────────")
    print(result["text"])

    print("\n── Chunks with Timestamps ──────────────────────────────────")
    for chunk in result.get("chunks", []):
        start, end = chunk["timestamp"]
        text = chunk["text"].strip()
        print(f"  [{start:6.2f}s → {end:6.2f}s]  {text}")

    return result


def refine_with_aligner(audio_file: str, transcript: str):
    """
    Use ForcedAligner for precise word-level alignment on the transcript.
    The aligner takes the audio + known text and returns tighter timestamps.
    """
    print("\nLoading ForcedAligner model...")
    aligner_model, aligner_tokenizer = load_aligner(ALIGNER_MODEL_DIR)

    audio_array, sample_rate = load_audio(audio_file)
    audio_tensor = torch.tensor(audio_array).unsqueeze(0).to(DEVICE)

    # Tokenise transcript
    inputs = aligner_tokenizer(
        transcript,
        return_tensors="pt",
        padding=True,
    ).to(DEVICE)

    with torch.no_grad():
        outputs = aligner_model(
            audio=audio_tensor,
            **inputs,
        )

    # `outputs` structure depends on the model head — adapt as needed
    # Typical: outputs.word_timestamps → list of {word, start, end}
    if hasattr(outputs, "word_timestamps"):
        print("\n── Forced-Aligned Word Timestamps ──────────────────────────")
        for item in outputs.word_timestamps:
            print(f"  [{item['start']:6.3f}s → {item['end']:6.3f}s]  {item['word']}")
    else:
        print("Raw aligner output:", outputs)

    return outputs


if __name__ == "__main__":
    # Step 1: ASR transcription with timestamps
    result = transcribe_with_timestamps(AUDIO_FILE)

    # Step 2 (optional): Forced alignment for tighter word timestamps
    # refine_with_aligner(AUDIO_FILE, result["text"])




#####################

# transcribe.py
import torch
import torchaudio
import librosa
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# ── Config ──────────────────────────────────────────────────────────────
BASE_MODEL_DIR    = "/opt/models"
ASR_MODEL_DIR     = f"{BASE_MODEL_DIR}/qwen3-asr-1.7b"
ALIGNER_MODEL_DIR = f"{BASE_MODEL_DIR}/qwen3-forced-aligner-0.6b"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE == "cuda" else torch.float32

# Language config — set to None for auto-detect, or "ar" / "en" to force
LANGUAGE = None   # auto-detect recommended for mixed Arabic/English calls
# ────────────────────────────────────────────────────────────────────────


def load_asr_pipeline(model_dir: str):
    """Load Qwen3-ASR from local directory, no cache."""
    print("Loading ASR model from:", model_dir)
    processor = AutoProcessor.from_pretrained(
        model_dir,
        local_files_only=True,
    )
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_dir,
        torch_dtype=DTYPE,
        local_files_only=True,
        low_cpu_mem_usage=True,
    ).to(DEVICE)

    asr_pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=DTYPE,
        device=DEVICE,
        return_timestamps=True,
        chunk_length_s=30,        # 30s windows — safe for 1–6 min audio
        stride_length_s=[4, 2],   # 4s look-back, 2s look-ahead overlap
                                  # prevents word cuts at chunk boundaries
    )
    return asr_pipe


def load_audio(filepath: str, target_sr: int = 16000) -> tuple[np.ndarray, int]:
    """
    Load WAV, resample to 16kHz mono.
    Uses librosa for robust handling of various WAV encodings.
    """
    audio_array, sr = librosa.load(filepath, sr=target_sr, mono=True)
    duration = len(audio_array) / target_sr
    print(f"Audio loaded: {duration:.1f}s  |  sample rate: {sr}Hz")
    return audio_array, sr


def detect_language_from_audio(asr_pipe, audio_array: np.ndarray, sample_rate: int) -> str:
    """
    Run a quick 10s sample through the model to detect language.
    Returns 'ar' or 'en' (or whatever Whisper-based model reports).
    """
    sample = audio_array[: sample_rate * 10]   # first 10 seconds
    result = asr_pipe(
        {"array": sample, "sampling_rate": sample_rate},
        generate_kwargs={"task": "transcribe"},   # no forced language
        return_timestamps=False,
    )
    # Qwen3-ASR (Whisper-based) exposes detected language on the model's
    # forced_decoder_ids after a forward pass — read it from the tokenizer
    # The simplest proxy: check character script in the short result
    text = result.get("text", "")
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    lang = "ar" if arabic_chars > len(text) * 0.3 else "en"
    print(f"Detected language: {lang}  (sample text: '{text[:60]}')")
    return lang


def format_timestamp(seconds: float) -> str:
    """Convert float seconds → MM:SS.mmm string."""
    minutes = int(seconds // 60)
    secs    = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def transcribe(audio_file: str, language: str = None):
    """
    Full pipeline:
      1. Load audio
      2. Auto-detect language if not forced
      3. Transcribe with word-level timestamps
      4. Print clean output with MM:SS timestamps
    """
    asr_pipe = load_asr_pipeline(ASR_MODEL_DIR)
    audio_array, sample_rate = load_audio(audio_file)

    # ── Language resolution ────────────────────────────────────────────
    lang = language
    if lang is None:
        lang = detect_language_from_audio(asr_pipe, audio_array, sample_rate)

    print(f"Transcribing in language: '{lang}' ...")

    # ── Transcription ──────────────────────────────────────────────────
    generate_kwargs = {
        "task": "transcribe",
        "language": lang,
    }
    if lang == "ar":
        # Keep Arabic numerals as Arabic-Indic (٠١٢...) or normalise to Western
        # Set to True to normalise to Western digits (0 1 2 ...) — easier for downstream
        generate_kwargs["normalize"] = True

    result = asr_pipe(
        {"array": audio_array, "sampling_rate": sample_rate},
        generate_kwargs=generate_kwargs,
    )

    # ── Output ─────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("FULL TRANSCRIPT")
    print("═" * 60)
    print(result["text"])

    print("\n" + "═" * 60)
    print("SEGMENTS WITH TIMESTAMPS")
    print("═" * 60)

    chunks = result.get("chunks", [])
    if not chunks:
        print("(no timestamp chunks returned)")
    else:
        for chunk in chunks:
            start, end = chunk["timestamp"]
            # end can be None on the last chunk if audio ends mid-window
            end_str = format_timestamp(end) if end is not None else "??:??.???"
            text    = chunk["text"].strip()
            print(f"  [{format_timestamp(start)} → {end_str}]  {text}")

    # ── Summary ────────────────────────────────────────────────────────
    total_duration = len(audio_array) / sample_rate
    print(f"\nCall duration : {format_timestamp(total_duration)}")
    print(f"Total segments: {len(chunks)}")
    print(f"Language used : {lang}")

    return result


# ── Entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    audio_path = sys.argv[1] if len(sys.argv) > 1 else "/path/to/call.wav"

    # Options:
    #   language=None  → auto-detect (recommended for mixed Arabic/English)
    #   language="ar"  → force Arabic
    #   language="en"  → force English
    result = transcribe(audio_path, language=LANGUAGE)
    
    
    
    
    
###########%%%%%%%#####


# transcribe.py
import torch
from qwen_asr import Qwen3ASRModel

# ── Config ───────────────────────────────────────────────────────────
BASE_MODEL_DIR = "/mnt/newdrive/models"
ASR_MODEL_DIR  = f"{BASE_MODEL_DIR}/Qwen/Qwen3-ASR-1.7B"
ALIGNER_DIR    = f"{BASE_MODEL_DIR}/Qwen/Qwen3-ForcedAligner-0.6B"

AUDIO_FILE     = "/mnt/newdrive/qwen_asr/1st.wav"   # change as needed
# ─────────────────────────────────────────────────────────────────────


def load_model():
    print("Loading Qwen3-ASR model...")
    model = Qwen3ASRModel.from_pretrained(
        ASR_MODEL_DIR,
        dtype=torch.bfloat16,
        device_map="cuda:0",
        max_inference_batch_size=32,
        max_new_tokens=256,
        forced_aligner=ALIGNER_DIR,          # loads aligner from local path
        forced_aligner_kwargs=dict(
            dtype=torch.bfloat16,
            device_map="cuda:0",
        ),
    )
    return model


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs    = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def transcribe(audio_file: str):
    model = load_model()

    print(f"Transcribing: {audio_file}")
    results = model.transcribe(
        audio=[audio_file],
        language=["Arabic"],    # or "English", or None for auto-detect
        return_time_stamps=True,
    )

    for r in results:
        print("\n" + "═" * 60)
        print(f"Language  : {r.language}")
        print(f"Transcript: {r.text}")
        print("\nTimestamps:")
        for ts in r.time_stamps:
            start = format_timestamp(ts[0])
            end   = format_timestamp(ts[1])
            word  = ts[2]
            print(f"  [{start} → {end}]  {word}")

    return results


if __name__ == "__main__":
    import sys
    audio = sys.argv[1] if len(sys.argv) > 1 else AUDIO_FILE
    transcribe(audio)

