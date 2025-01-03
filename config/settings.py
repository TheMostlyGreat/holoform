# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from a .env file

ARC_BASE_URL = os.getenv("ARC_BASE_URL", "http://localhost:9099")
LM_BASE_URL = os.getenv("LM_BASE_URL", f"{ARC_BASE_URL}/v1")
DEFAULT_USER_ID = os.getenv("USER_ID", "0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
TOKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')  # Get token from root project directory
