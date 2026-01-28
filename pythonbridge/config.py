import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")


def load_environment():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    if not GITHUB_APP_ID:
        raise ValueError("GITHUB_APP_ID is not set")
    if not GITHUB_APP_PRIVATE_KEY:
        raise ValueError("GITHUB_APP_PRIVATE_KEY is not set")
