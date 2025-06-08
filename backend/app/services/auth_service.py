from utils.env_loader import load_env
import os
from fastapi.security import OAuth2PasswordBearer
import requests
from jose import jwt
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, timezone
#loading .env
load_env()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#google api client id and secret from .env
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("REDIRECT_URI")


#function for creating token
# def create_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(days=7)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


#this get method returns a url when you goto url it redirects to google login page
@router.get("/login/google")
async def login_google():
    url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"response_type=code&"
    f"client_id={GOOGLE_CLIENT_ID}&"
    f"redirect_uri={GOOGLE_REDIRECT_URI}&"
    f"scope=openid%20email%20profile%20https://www.googleapis.com/auth/youtube.readonly&"
    f"access_type=offline&"
    f"prompt=consent"
)
    return{
        "url": url
    }

#this should be same url as in google cloud console authorized redirect URIs
#after /gogin/google the google automatically redirects to this url with code
#and this returns user info including id, email, name and picture
@router.get("/auth/callback")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    
    user_info_resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_resp.json()

    youtube_info_resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
        headers={"Authorization": f"Bearer {access_token}"})
    youtube_data = youtube_info_resp.json()
    
    return {
        "profile": user_info,
        "youtube": youtube_data,
    }

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=ALGORITHM)
