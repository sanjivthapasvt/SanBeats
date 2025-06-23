import requests
import os
import logging

from fastapi import HTTPException
from isodate import parse_duration
from typing import List

from services.format_service import format_duration
from cache.audio_cache import get_cached_audio_info, extract_audio_url_and_info
from models import SearchResult, AudioInfo

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

#funciton for getting audio url
def get_audio_info(video_id: str) -> AudioInfo:
    if cached := get_cached_audio_info(video_id):
        return cached
    try:
        return extract_audio_url_and_info(video_id)

    except Exception as e:
        logger.error(f"Error while gettting audio info {str(e)}")
        raise

        
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
