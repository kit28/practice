podman run --rm \
  --device nvidia.com/gpu=5 \
  --security-opt=label=disable \
  --shm-size=16g \
  -v "/data0/HDD-data/GENAI/cohere-transcribe-arabic-07-2026:/models/cohere:Z" \
  -p 8005:8000 \
  docker.io/vllm/vllm-openai:latest \
  --model /models/cohere \
  --served-model-name cohere-transcribe-arabic-07-2026 \
  --trust-remote-code
  
  
  
  
import os
import pandas as pd
from openai import OpenAI

# ==============================
# CONFIGURATION
# ==============================

AUDIO_FOLDER = "/path/to/your/wav/folder"
OUTPUT_EXCEL = "cohere_transcriptions.xlsx"

# Your Cohere vLLM server
VLLM_URL = "http://localhost:8006/v1"

MODEL_NAME = "cohere-transcribe-arabic-07-2026"

# Arabic
LANGUAGE = "ar"


# ==============================
# VLLM CLIENT
# ==============================

client = OpenAI(
    base_url=VLLM_URL,
    api_key="dummy"
)


# ==============================
# TRANSCRIPTION
# ==============================

results = []

wav_files = sorted(
    f for f in os.listdir(AUDIO_FOLDER)
    if f.lower().endswith(".wav")
)

print(f"Found {len(wav_files)} WAV files.\n")


for i, filename in enumerate(wav_files, start=1):

    file_path = os.path.join(AUDIO_FOLDER, filename)

    print(f"[{i}/{len(wav_files)}] Transcribing: {filename}")

    try:
        with open(file_path, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                model=MODEL_NAME,
                file=audio_file,
                language=LANGUAGE
            )

        text = transcription.text

        results.append({
            "filename": filename,
            "transcription": text
        })

        print("  ✓ Done")

    except Exception as e:

        print(f"  ✗ Failed: {e}")

        results.append({
            "filename": filename,
            "transcription": f"ERROR: {str(e)}"
        })


# ==============================
# SAVE TO EXCEL
# ==============================

df = pd.DataFrame(
    results,
    columns=["filename", "transcription"]
)

df.to_excel(
    OUTPUT_EXCEL,
    index=False
)

print("\n================================")
print("Transcription completed.")
print(f"Excel file: {OUTPUT_EXCEL}")
print("================================")



import torch
from transformers import AutoProcessor, CohereAsrForConditionalGeneration
from transformers.audio_utils import load_audio

# ==========================================
# Configuration
# ==========================================

MODEL_PATH = "/data0/HDD-data/GENAI/cohere-transcribe-arabic-07-2026"
AUDIO_FILE = "call.wav"

# ==========================================
# Load processor and model
# ==========================================

print("Loading processor...")

processor = AutoProcessor.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

print("Loading model...")

model = CohereAsrForConditionalGeneration.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    local_files_only=True
)

print("Model loaded.")

# ==========================================
# Load audio
# ==========================================

audio = load_audio(
    AUDIO_FILE,
    sampling_rate=16000
)

# ==========================================
# Prepare input
# ==========================================

inputs = processor(
    audio,
    sampling_rate=16000,
    return_tensors="pt",
    language="ar"
)

inputs = inputs.to(model.device, dtype=model.dtype)

# ==========================================
# Generate transcription
# ==========================================

print("Transcribing...")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=256
    )

# ==========================================
# Decode
# ==========================================

text = processor.decode(
    outputs,
    skip_special_tokens=True
)

print("\n================================")
print("TRANSCRIPTION")
print("================================")
print(text)
print("================================")
