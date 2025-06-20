curl -X POST http://localhost:8001/run_pipeline \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/sample_audio.wav"}'
    
    
    curl http://localhost:8001/get_status/<job_id>