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
