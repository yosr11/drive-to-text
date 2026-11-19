
import os
from pathlib import Path
from dotenv import load_dotenv

# Chemin vers backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BACKEND_DIR / ".env")

GOOGLE_DRIVE_API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY")

if not GOOGLE_DRIVE_API_KEY:
    raise RuntimeError(
        "GOOGLE_DRIVE_API_KEY est absente du fichier .env"
    )

GOOGLE_DRIVE_API_BASE_URL = (
    "https://www.googleapis.com/drive/v3"
)
