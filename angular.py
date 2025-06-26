from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os

app = FastAPI()

EXCEL_STORAGE_PATH = "./uploads/excel"  # Or wherever your Excel files are stored

@app.get("/download-excel/{job_id}")
def download_excel(job_id: str):
    # Construct file path (e.g., job_id.xlsx)
    file_path = os.path.join(EXCEL_STORAGE_PATH, f"{job_id}.xlsx")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel file not found")

    return FileResponse(
        path=file_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=f"{job_id}.xlsx"
    )