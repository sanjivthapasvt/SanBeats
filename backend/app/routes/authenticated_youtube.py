import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
from typing import Optional, List
from models import YoutubePlaylistResponse
from fastapi import APIRouter, HTTPException, logger
from services import get_liked_music
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)


#get liked videos if user is authenticated
@router.get("/liked_music_videos", response_model=YoutubePlaylistResponse)
async def get_liked_music_videos(access_token: str, page_token: Optional[str]= None):
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
@router.get("/playlist_user")
async def get_user_playlist(access_token: str, page_token: Optional[str] = None):
    try:
        url = "https://www.googleapis.com/youtube/v3/playlists"
        params = {
            "part": "snippet,contentDetails",
            "mine": True,
            "maxResults": 10,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    
    except Exception as e:
        logger.error(f"Get playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get Playlist error {str(e)}")