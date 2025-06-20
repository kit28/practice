from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
from pipeline import long_running_pipeline

app = FastAPI()

# Simulated in-memory store (replace with Redis/DB for production)
job_results: Dict[str, dict] = {}
job_status: Dict[str, str] = {}

# Request model
class PipelineRequest(BaseModel):
    audio_url: str

# Response for run_pipeline
class JobResponse(BaseModel):
    job_id: str

# Response for get_status
class StatusResponse(BaseModel):
    status: str
    result: dict | None = None
    error: str | None = None

# Background task function
def run_pipeline_task(audio_url: str, job_id: str):
    try:
        job_status[job_id] = "processing"
        result = long_running_pipeline(audio_url)
        job_results[job_id] = result
        job_status[job_id] = "success"
    except Exception as e:
        job_status[job_id] = "failed"
        job_results[job_id] = {"error": str(e)}

# Endpoint to start pipeline
@app.post("/run_pipeline", response_model=JobResponse)
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    job_status[job_id] = "queued"
    background_tasks.add_task(run_pipeline_task, request.audio_url, job_id)
    return {"job_id": job_id}

# Endpoint to check pipeline status
@app.get("/get_status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    status = job_status.get(job_id)
    if not status:
        return {"status": "not_found", "result": None, "error": "Invalid job ID"}

    if status == "success":
        return {"status": status, "result": job_results[job_id]}
    elif status == "failed":
        return {"status": status, "result": None, "error": job_results[job_id].get("error")}
    else:
        return {"status": status, "result": None}