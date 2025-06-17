import logging
from typing import Optional
from fastapi import HTTPException, logger
import requests
from models import YoutubePlaylistResponse, PlayListItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#parse the youtube respone to match YoutbePlaylistRepsonse model
def parse_youtube_response(raw_response: dict) -> YoutubePlaylistResponse:
    try:
        items = []
        for item in raw_response.get("items", []):
            video_id = item.get("id")
            snippet = item.get("snippet")
        
            thumbnails_response = snippet.get("thumbnails", {})

            result = PlayListItem(
                id=video_id,
                title=snippet.get("title", ""),
                thumbnails=thumbnails_response,
                channelTitle=snippet.get("channelTitle", "")
            )
            items.append(result)
        next_page_token = raw_response.get("nextPageToken")
        return YoutubePlaylistResponse(items=items, nextPageToken=next_page_token)
    except Exception as e:
        logger.error(f"Parse youtube response error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parse youtube response error {str(e)}")


def get_liked_music(access_token: str, page_token: Optional[str]= None):
#for response from youtube
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "myRating": "like",
            "maxResults": 25,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        
        if page_token:
            params["pageToken"] = page_token
            
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        #filter videos with category 10(i.e music)
        filtered_music = [
            item for item in data.get("items", [])
            if item["snippet"].get("categoryId") == "10"
        ]
        
        filtered_data = {
            "items": filtered_music,
            "nextPageToken": data.get("nextPageToken")
        }
        
        parsed_response = parse_youtube_response(filtered_data)
        return parsed_response
        
    except Exception as e:
        logger.error(f"liked music error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Liked music error {str(e)}")
