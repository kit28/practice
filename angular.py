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
    
    
from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "./uploads/bulk"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)

    return {"uploaded": saved_files}
    
    

from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import aiofiles

app = FastAPI()

BASE_UPLOAD_DIR = "./uploads"

@app.post("/upload-folder")
async def upload_folder(files: List[UploadFile] = File(...)):
    saved_files = []

    for file in files:
        # The browser sends `filename` as webkitRelativePath (e.g. "subdir/file.xlsx")
        relative_path = file.filename  
        save_path = os.path.join(BASE_UPLOAD_DIR, relative_path)

        # Create directories if needed
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save asynchronously
        async with aiofiles.open(save_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        saved_files.append(save_path)

    return {"saved": saved_files}
    
    
from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import aiofiles

app = FastAPI()

BASE_UPLOAD_DIR = "./uploads"

@app.post("/upload-folder")
async def upload_folder(files: List[UploadFile] = File(...)):
    if not files:
        return {"error": "No files uploaded"}

    # Take the root folder from the first file’s relative path
    first_file_path = files[0].filename  # e.g. "ProjectData/audio/file1.wav"
    root_folder = first_file_path.split("/")[0]  # "ProjectData"

    # Build the absolute save path for this folder
    save_folder_path = os.path.join(BASE_UPLOAD_DIR, root_folder)

    # Save all files while preserving structure
    for file in files:
        relative_path = file.filename  # "ProjectData/audio/file1.wav"
        save_path = os.path.join(BASE_UPLOAD_DIR, relative_path)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        async with aiofiles.open(save_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

    # ✅ Return the folder path for future API calls
    return {"saved_folder": save_folder_path}