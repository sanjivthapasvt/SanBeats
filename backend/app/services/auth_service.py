import os
import requests
from fastapi import APIRouter
from urllib.parse import urlencode


SECRET_KEY = os.getenv("SECRET_KEY")
router = APIRouter()

#google api client id and secret from .env
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("REDIRECT_URI")


#this get method returns a url when you goto url it redirects to google login page
@router.get("/api/login/google")
async def google_login():
    scopes = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]

    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent"
    }
    
    url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
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
    data = response.json()
    access_token = data["access_token"]
    access_token_expires_in = data["expires_in"]
    refresh_token = data["refresh_token"]
    refresh_token_expires_in = data["refresh_token_expires_in"]
    
    user_info_resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_resp.json()
    
    user_data = {
        "name": user_info["name"],
        "email": user_info["email"],
        "picture": user_info["picture"],
    }

    #return user info like id, name, email and also access and refresh tokens
    return {
        "user": user_data,
        "token": {
            "access_token": access_token,
            "access_token_expires_in": access_token_expires_in,
            "refresh_token": refresh_token,
            "refresh_token_expires_in": refresh_token_expires_in,
        }
    }
