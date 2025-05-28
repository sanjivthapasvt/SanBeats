import asyncio
import datetime
import json
import requests
import os
import logging
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models import SearchResult, AudioInfo, MusicRecommendation
from isodate import parse_duration
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SanBeats API")

#Get api key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

#setting up middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#logger for logging errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#threads to execute functions asynchronously
executor = ThreadPoolExecutor(max_workers=4)

def list_videos(data: dict) -> List[SearchResult]:
    results = []
    videos_ids = [item["id"]["videoId"] for item in data["items"]]
        
    #get additional video details i.e duration
    details_url = "https://www.googleapis.com/youtube/v3/videos"
    details_params = {
        "part": "contentDetails",
        "id": ",".join(videos_ids),
        "key": YOUTUBE_API_KEY
    }
        
    detail_response = requests.get(details_url, params=details_params, timeout=30)
    detail_response.raise_for_status()
    details_data = detail_response.json()
    #lookup dict for details
    details_lookup = {item["id"]: item for item in details_data["items"]}
        
    for item in data["items"]:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        details = details_lookup.get(video_id, {})

        #parse duration from ISO format to human readable format like 4:13
        duration_iso = details.get("contentDetails",{}).get("duration", "PT0S")
        try:
            duration_full = parse_duration(duration_iso)             
            duration = format_duration(duration_full)
        except Exception:
            duration = "0:00"
        #append the results to result list
        results.append(SearchResult(
            id=video_id,
            title=snippet["title"],
            duration=duration,
            thumbnail=snippet["thumbnails"]["medium"]["url"],
            channel=snippet["channelTitle"]
        ))     
        
    return results

#funciton for getting video info from youtube and using yt-dlp to return audio only url 
def get_video_info(video_id: str) -> AudioInfo:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
        formats = info.get('formats',[])
        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        if not audio_formats:
            raise ValueError("No audio formats found")
        best_audio = max(audio_formats, key=lambda x: x.get('abr') or 0)
        duration_seconds = info.get('duration', 0)
        formatted_duration = format_duration(datetime.timedelta(seconds=duration_seconds))

        return AudioInfo(
            url=best_audio.get('url', ''),
            title = info.get('title', ''),
            duration = formatted_duration,
            format=best_audio.get('acodec', 'unknown'),
            quality=f"{best_audio.get('abr', 0)}kbps",
            thumbnail = info.get('thumbnail', ''),
        )
        
        
#function for getting audio url
def get_audio_stream_url(video_id: str) -> str:
    ydl_ops = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'prefer_ffmpeg': True,
    }
    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']        
    except Exception as e:
        logger.error(f"yt-dlp error: {str(e)}")
        return None
    

def get_channel_videos(channelId: str) -> List[SearchResult]:
    try:
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "channelId": channelId,
            "maxResults": 10,
            "order": "relevance",
            "type": "video",
            "videoCategoryId": "10",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return list_videos(data)
       
    except Exception as e:
        logger.error(f"Recommendation error {str(e)}")

def get_same_tags_videos(filtered_tags: str) -> List[SearchResult]:
    try:
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": filtered_tags,
            "maxResults": 10,
            "order": "relevance",
            "type": "video",
            "videoCategoryId": "10",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return list_videos(data)

    except Exception as e:
        logger.error(f"Recommendation error {str(e)}")


#function for returning similar videos to one being played
def get_similar_videos(video_id: str) -> List[SearchResult]:
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "key": YOUTUBE_API_KEY,
            "id": video_id
        }
        response = requests.get(url, params)
        response.raise_for_status()
        data = response.json()
        if not data.get("items"):
            return []
        items = data["items"][0]["snippet"]
        tags = items.get("tags", [])
        filtered_tags = "|".join(tag.replace(" ", "+") for tag in tags[:3]) if tags else ""
        channel_id = items["channelId"]
        channel_results = get_channel_videos(channel_id)
        tags_results = get_same_tags_videos(filtered_tags) if filtered_tags else []
        combined_results = channel_results + tags_results
        recommend_result = {}
        for video in combined_results:
            vid_id = getattr(video, "video_id", None) or getattr(video, "id", None)
            if vid_id and vid_id not in recommend_result:
                recommend_result[vid_id] = video

        return list(recommend_result.values())

    except Exception as e:
        logger.error(f"Recommendation error {str(e)}")


#function for parsing time
def format_duration(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"


#######################
#######ROUTES##########
#######################

#root path just return api name
@app.get("/")
async def root():
    return {"message": "SanBeats API"}

#Get method on /search with required query parameter and optional max results 
#for sending search videos to youtube API
@app.get('/api/search', response_model=List[SearchResult])
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
            "videoCategoryId": "10", #music category
            "order": "relevance",
        }
        
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return list_videos(data)
         
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed {str(e)}")


#GET METHOD FOR GETTING YOUTUBE AUDIO URL
@app.get("/api/info/{video_id}", response_model=AudioInfo)
async def get_audio_info(video_id: str):
    try:
        info = await asyncio.get_event_loop().run_in_executor(
            executor, get_video_info, video_id
        )
        return info
    
    except Exception as e:
        logger.error(f"Stream Info error {str(e)}")
        raise HTTPException(status_code=404, detail="Video not found")
    
#GET METHOD FOR GETTING REALTED VIEDO TO THE MUSIC BEING PLAYED
@app.get("/api/recommendation/{video_id}", response_model=List[SearchResult])
async def get_music_recommendation(video_id: str):
    try:
        recommendation = await asyncio.get_event_loop().run_in_executor(
            executor, get_similar_videos, video_id
        )
        return recommendation
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while recommending: {str(e)}")
