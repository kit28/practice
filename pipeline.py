import time
import uuid

def long_running_pipeline(audio_url: str) -> dict:
    print(f"Processing: {audio_url}")
    time.sleep(10)  # Simulate 10-minute job with shorter sleep (change as needed)
    return {
        "transcript": "Dummy transcript of audio",
        "analysis": "Dummy sentiment analysis result",
        "speakers": ["Speaker 1", "Speaker 2"]
    }