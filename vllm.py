podman run --name cohere-audio-build \
  --security-opt=label=disable \
  -it \
  --entrypoint /bin/bash \
  localhost/vllm-openai-cohere:latest


root@xxxxx:/workspace#

python -c "import vllm; print(vllm.__version__)"


uv pip install --system "vllm[audio]==0.19.0"


podman commit cohere-audio-build localhost/vllm-openai-cohere:audio

podman rm cohere-audio-build


podman run --rm \
  --name cohere-asr \
  --device nvidia.com/gpu=5 \
  --security-opt=label=disable \
  --shm-size=16g \
  -v "/data0/HDD-data/GENAI/cohere-transcribe-arabic-07-2026:/models/cohere:Z" \
  -p 8006:8000 \
  localhost/vllm-openai-cohere:audio \
  --model /models/cohere \
  --served-model-name cohere-transcribe-arabic-07-2026 \
  --trust-remote-code



podman run --rm \
  --name cohere-asr \
  --device nvidia.com/gpu=5 \
  --security-opt=label=disable \
  --shm-size=16g \
  -v "/data0/HDD-data/GENAI/cohere-transcribe-arabic-07-2026:/models/cohere:Z" \
  -p 8006:8000 \
  --entrypoint vllm \
  localhost/vllm-openai-cohere:audio \
  serve /models/cohere \
  --served-model-name cohere-transcribe-arabic-07-2026 \
  --trust-remote-code
