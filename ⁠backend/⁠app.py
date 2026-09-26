from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from downloader import VideoDownloader, extract_media
from ai_enhancer import AIEnhancer
import os, uuid, asyncio

app = FastAPI(title="AI Downloader API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("downloads", exist_ok=True)
app.mount("/files", StaticFiles(directory="downloads"), name="files")

class DownloadRequest(BaseModel):
    url: str
    quality: str = "4k"
    platform: str = "auto"
    enhance: bool = False

@app.post("/api/download")
async def download_endpoint(req: DownloadRequest):
    result = await extract_media(req.url, req.quality)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    
    # تحسين اختياري
    if req.enhance and result["file"].endswith(".mp4"):
        enhanced = f"downloads/enhanced_{uuid.uuid4().hex}.mp4"
        AIEnhancer.enhance_video(result["file"], enhanced)
        result["enhanced_file"] = f"/files/{os.path.basename(enhanced)}"
    
    result["download_url"] = f"/files/{os.path.basename(result['file'])}"
    return result

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
