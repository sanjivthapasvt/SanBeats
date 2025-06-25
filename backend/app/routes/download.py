import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, Response
from services.download_service import download_youtube_video
router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

@router.post("/download")
async def download_video(video_url: str, path:str, video:bool, quality:int = None):
    try:
        download = await asyncio.get_event_loop().run_in_executor(
            executor, download_youtube_video, path, video_url, video, quality
        )
        if not download:
            raise HTTPException("Something went wrong", 400)
        
        return {"message": "Download Successful"}

    except Exception as e:
        print(f"Download {str(e)}")
        raise HTTPException(status_code=404, detail="Something went wrong while downlaoding")