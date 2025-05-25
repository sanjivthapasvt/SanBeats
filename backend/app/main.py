import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
from isodate import parse_duration
import datetime
from typing import List
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="SanBeats API")

#Get api key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

#setting up middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#logger for logging errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#threads to execute functions asynchronously
executor = ThreadPoolExecutor(max_workers=4)

class SearchResult(BaseModel):
    id: str
    title: str
    duration: str
    thumbnail: str
    channel: str

class StreamInfo(BaseModel):
    url: str
    title: str
    duration: str
    format: str
    quality: str

#function for parsing time
def format_duration(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"


#root path just return api name
@app.get("/")
async def root():
    return {"message": "SanBeats API"}

#Get method on /search with required query parameter and optional max results 
#for sending search videos to youtube API
@app.get('/search', response_model=List[SearchResult])
async def search_youtube(
    q: str = Query(..., description="Youtube search query"),
    max_results: int = Query(10, ge=1, le=50)
):
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": q,
            "type": "video",
            "maxResults": max_results,
            "key": YOUTUBE_API_KEY,
            "videoCategoryID": "10", #music category
            "order": "relevance",
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        videos_ids = [item["id"]["videoId"] for item in data["items"]]
        
        #get additional video details i.e duration
        details_url = "https://www.googleapis.com/youtube/v3/videos"
        details_params = {
            "part": "contentDetails",
            "id": ",".join(videos_ids),
            "key": YOUTUBE_API_KEY
        }
        
        detail_response = requests.get(details_url, params=details_params)
        details_data = detail_response.json()
        #lookup dict for details
        details_lookup = {item["id"]: item for item in details_data["items"]}
        
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            details = details_lookup.get(video_id, {})

            #parse duration from ISO format to human readable format like 4:13
            duration_iso = details.get("contentDetails",{}).get("duration", "PT0S")
            duration_full = parse_duration(duration_iso)             
            duration = format_duration(duration_full)
            #append the results to result list
            results.append(SearchResult(
                id=video_id,
                title=snippet["title"],
                duration=duration,
                thumbnail=snippet["thumbnails"]["medium"]["url"],
                channel=snippet["channelTitle"]
            ))     
        
        return results
         
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed {str(e)}")

#funciton for getting video info using yt-dlp
def get_video_info(video_id: str) -> StreamInfo:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
        formats = info.get('formats',[])
        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
        
        return StreamInfo(
            url=best_audio.get('url', ''),
            title = info.get('title', ''),
            duration = info.get('duration', ''),
            format=best_audio.get('acodec', 'unknown'),
            quality=f"{best_audio.get('abr', 0)}kbps",
        )

async def stream_audio_content(stream_url: str):
    try:
        response = requests.get(stream_url, stream=True, timeout=30)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                yield chunk
    
    except Exception as e:
        logger.error(f"Streaming content error: {str(e)}")
        raise

#Get method for streaming audio
@app.get("/stream/{video_id}")
async def stream_audio(video_id: str, quality: str = "medium"):
    try:
        stream_url = await asyncio.get_event_loop().run_in_executor(
            executor, get_audio_stream_url, video_id, quality
        )
        if not stream_url:
            raise HTTPException(status_code=404, detail="Audio source not found")
       
        #stream audio
        return StreamingResponse(
            stream_audio_content(stream_url),
            media_type='audio/mpeg',
            headers={
                "Content-Disposition": f"inline; filename={video_id}.mp3",
                "Cache-Control": "no-cache",
                "Accept-Ranges": "bytes"
            }
        ) 
    except Exception as e:
        logger.error(f"Stream error {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")
        

@app.get("/info/{video_id}", response_model=StreamInfo)
async def get_stream_info(video_id: str):
    try:
        info = await asyncio.get_event_loop().run_in_executor(
            executor, get_video_info, video_id
        )
        return info
    
    except Exception as e:
        logger.error(f"Stream Info error {str(e)}")
        raise HTTPException(status_code=404, detail="Video not found")
    


def get_audio_stream_url(video_id: str, quality: str = "meduim") -> str:
    ydl_ops = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': get_quality_setting(quality),
        'prefer_ffmpeg': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
            
            #find best format
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x:x.get('abr', 0) or 0)
                return best_audio['url']
        
            return None
        
    except Exception as e:
        logger.error(f"yt-dlp error: {str(e)}")
        return None

def get_quality_setting(quality: str) -> str:
    quality_map = {
        "low": "9",   
        "medium": "5",
        "high": "0"
    }
    return quality_map.get(quality, "5")