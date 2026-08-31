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