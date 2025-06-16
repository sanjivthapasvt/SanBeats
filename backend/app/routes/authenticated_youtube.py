import logging
import requests
from typing import Optional
from fastapi import APIRouter, HTTPException, logger

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#get liked videos if user is authenticated
@router.get("/liked_music_videos")
def get_liked_music_videos(access_token: str, page_token: Optional[str]= None):
    #for response from youtube
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "myRating": "like",
            "maxResults": 50,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        #filter videos with category 10(i.e music)
        filtered_music = [
            item for item in data.get("items", [])
            if item["snippet"].get("categoryId") == "10"
        ]
        
        return {
            "videos": filtered_music,
            "nextPageToken": data.get("nextPageToken")
        }
        
    except Exception as e:
        logger.error(f"liked music error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Liked music error {str(e)}")
