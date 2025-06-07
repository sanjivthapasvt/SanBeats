import os
import sys
from dotenv import load_dotenv

#load environemnt variable depending on if it is running for ececutable or no
def load_env():
    if getattr(sys, 'frozen', False):
        # Running as bundled .exe
        dotenv_path = os.path.join(sys._MEIPASS, '.env')
    else:
        # Running as script
        dotenv_path = '.env'

    load_dotenv(dotenv_path)