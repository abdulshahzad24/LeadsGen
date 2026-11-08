import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from main import app
from app.database import init_db

# Ensure DB schema is initialized on serverless cold start
try:
    init_db()
except Exception as e:
    print(f"[Vercel Init] {e}")
