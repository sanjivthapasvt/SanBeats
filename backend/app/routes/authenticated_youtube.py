import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
from typing import Optional
from models import YoutubePlaylistResponse
from fastapi import APIRouter, HTTPException, logger
from services import get_liked_music, get_user_playlist
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)


#get liked videos if user is authenticated
@router.get("/list_user_liked_videos", response_model=YoutubePlaylistResponse)
async def list_liked_music_videos(access_token: str, page_token: Optional[str]= None):
    #for response from youtube
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            executor, get_liked_music, access_token, page_token
        )
        return result
        
    except Exception as e:
        logger.error(f"liked music error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Liked music error {str(e)}")

#get playlist if the user is authenticated
@router.get("/list_user_playlist", response_model=YoutubePlaylistResponse)
async def list_user_playlist(access_token: str, page_token: Optional[str] = None):
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            executor, get_user_playlist, access_token, page_token
        )
        return result
    
    except Exception as e:
        logger.error(f"Get playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get playlist error {str(e)}")
    
@router.post("/add_to_playlist")
def add_music_to_playlist(videoId: str, playlistId: str, access_token: str):
    try:
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "snippet": {
                "playlistId": playlistId,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": videoId,
                }
            }
        }
        
        response = requests.post(url=url, params=params, json=data, headers=headers)
        response.raise_for_status()
        
        return {
            "message": "Succesfully added video to playlist",
            "response": response.json(),
        }
        
    except Exception as e:
        logger.error(f"Add to playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Add to playlist error {str(e)}")