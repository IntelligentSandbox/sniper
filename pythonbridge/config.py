import os
from dotenv import load_dotenv

# TODO: Handle malformed .env files
load_dotenv()
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
