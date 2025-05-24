from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
from isodate import parse_duration
from typing import List, Optional
import requests
import os
import logging

app = FastAPI(title="SabBeats API")

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
            duration = parse_duration(duration_iso)             
            
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