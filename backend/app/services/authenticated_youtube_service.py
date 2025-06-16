import requests
from typing import Optional
from fastapi import APIRouter

router = APIRouter()

#get liked videos if user is authenticated
@router.get("/liked_music_videos")
def get_liked_videos(access_token: str, page_token: Optional[str]= None):
    #for response from youtube
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