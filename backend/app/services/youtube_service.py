import datetime
import requests
import os
import logging
import yt_dlp
from fastapi import HTTPException
from models import SearchResult, AudioInfo
from isodate import parse_duration
from typing import List

#Get api key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

#logger for logging errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#function to process youtube search and return informtaion about each video
def list_videos(data: dict) -> List[SearchResult]:
    results = []
    videos_ids = []
    
    #extract video id from different api response i.e trending endpoint and search
    for item in data.get("items", []):
        vid = item.get("id")
        if isinstance(vid, dict):
            video_id = vid.get("videoId")
        else:
            video_id = vid
        if video_id:
            videos_ids.append(video_id)
        
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
    details_lookup = {}
    for item in details_data.get("items", []):
        video_id = item.get("id")
        if isinstance(video_id, str):
            details_lookup[video_id] = item
        
    for item in data["items"]:
        vid = item.get("id")
        video_id = vid.get("videoId") if isinstance(vid, dict) else vid
        
        if not video_id:
            continue
        
        snippet = item.get("snippet", {})
        details = details_lookup.get(video_id, {})

        #parse duration from ISO format to human readable format like 4:13
        duration_iso = details.get("contentDetails",{}).get("duration", "PT0S")
        try:
            duration_full = parse_duration(duration_iso)   
            if duration_full.total_seconds() < 120: #skip if duration is less than 2 min
                continue          
            duration = format_duration(duration_full)
        except Exception:
            continue
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
        'skip_download': True,
        'format': 'bestaudio',
        'extract_flat': False,
        'force_generic_extractor': False,
        'noplaylist': True,
        'cachedir': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False, process=True)
        formats = info.get('formats',[])
        audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
        if not audio_formats:
            raise ValueError("No audio formats found")
        best_audio = max(audio_formats, key=lambda x: x.get('abr') or 0)
        duration_seconds = info.get('duration', 0)
        formatted_duration = format_duration(datetime.timedelta(seconds=duration_seconds))

        return AudioInfo(
            url=best_audio['url'],
            title = info.get('title', ''),
            duration = formatted_duration,
            format=best_audio.get('acodec', 'unknown'),
            quality=f"{best_audio.get('abr', 0)}kbps",
            thumbnail = info.get('thumbnail', ''),
        )



#function forsearchiing in youtube
def get_search_result(q: str) -> List[SearchResult]:
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": q,
            "type": "video",
            "maxResults": 25,
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
    
    
#function for getting videos from the channel(helper function for music recommendation)
def get_channel_videos(channelId: str) -> List[SearchResult]:
    try:
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "channelId": channelId,
            "maxResults": 20,
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

#function for getting similar videos based on tag(helper function for music recommendation)
def get_same_tags_videos(filtered_tags: str) -> List[SearchResult]:
    try:
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": filtered_tags,
            "maxResults": 20,
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
        item = data["items"][0]
        tags = item.get("tags", [])
        filtered_tags = "|".join(tag.replace(" ", "+") for tag in tags[:3]) if tags else ""
        channel_id = item["snippet"]["channelId"]
        channel_results = get_channel_videos(channel_id)
        tags_results = get_same_tags_videos(filtered_tags)
        combined_results = channel_results + tags_results
        recommend_result = {}
        for video in combined_results:
            vid_id = getattr(video, "video_id", None) or getattr(video, "id", None)
            if vid_id and vid_id not in recommend_result:
                recommend_result[vid_id] = video
                
        return list(recommend_result.values())

    except Exception as e:
        logger.error(f"Recommendation error {str(e)}")


def get_trending_music() -> List[SearchResult]:
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "type": "video",
            "order": "viewCount",
            "chart": "mostPopular",
            "regionCode": "US",
            "videoCategoryId": "10",
            "q": "music",
            "maxResults": "25",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return list_videos(data)

    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trending music error: {str(e)}")

def get_most_viewed_music() -> List[SearchResult]:
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "type": "video",
            "q": "music",
            # "publishedAfter": "2024-06-01T00:00:00Z", #within last year
            "order": "viewCount",
            "videoCategoryId": "10",
            "maxResults": "25",
            "regionCode": "US",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return list_videos(data)
    
    except Exception as e:
        logger.error(f"Most Viewed music error {str(e)}")

#function for parsing time
def format_duration(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"
