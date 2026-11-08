import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager

from app.database import init_db, get_all_leads
from app.api.routes import router as api_router
from app.scrapers.lead_finder import generate_leads_for_search

BASE_DIR = Path(__file__).resolve().parent

def ensure_initialized():
    try:
        init_db()
        existing = get_all_leads(limit=1)
        if not existing:
            seed_batches = [
                ("clinic", "Mumbai", 4),
                ("ca", "Mumbai", 4),
                ("clinic", "Delhi", 3),
                ("ca", "Delhi", 3)
            ]
            for niche, city, count in seed_batches:
                generate_leads_for_search(niche, city, count=count)
    except Exception as e:
        print(f"[Init Warning] {e}")

# Run on module import (handles serverless cold start on Vercel)
ensure_initialized()

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_initialized()
    yield

app = FastAPI(
    title="AI Caller LeadGen — Doctors & CAs",
    version="1.0.0",
    lifespan=lifespan
)

# Support both with and without /api prefix (handles Vercel route stripping)
app.include_router(api_router, prefix="/api")
app.include_router(api_router)

# Mount static folder
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
@app.get("/api")
@app.get("/api/index")
@app.get("/api/index.py")
def serve_index():
    index_file = BASE_DIR / "app" / "static" / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AI Caller LeadGen</h1>")

@app.get("/static/{file_path:path}")
def serve_static_file(file_path: str):
    target = static_dir / file_path
    if target.exists():
        return FileResponse(target)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
