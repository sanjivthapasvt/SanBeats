from utils.env_loader import load_env
import os
load_env()

GOOGLE_CLIENT_ID = os.get_env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.get_env("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.get_env("REDIRECT_URI")