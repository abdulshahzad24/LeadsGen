import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.database import init_db, get_all_leads
from app.api.routes import router as api_router
from app.scrapers.lead_finder import generate_leads_for_search

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()
    
    # Check if DB is empty, auto-seed realistic leads for immediate demo
    existing = get_all_leads(limit=1)
    if not existing:
        print("[Startup] Seeding initial high-vulnerability leads for Clinics, CAs & High-Inquiry practices...")
        seed_batches = [
            ("clinic", "Mumbai", 4),
            ("ca", "Mumbai", 4),
            ("clinic", "Delhi", 3),
            ("ca", "Delhi", 3),
            ("clinic", "Bangalore", 3),
            ("diagnostic", "Mumbai", 2),
            ("real_estate", "Bangalore", 2)
        ]
        total_seeded = 0
        for niche, city, count in seed_batches:
            leads = generate_leads_for_search(niche, city, count=count)
            total_seeded += len(leads)
        print(f"[Startup] Initialized {total_seeded} leads ready for outreach.")
        
    yield

app = FastAPI(
    title="Agentic AI Caller — High-Ticket Lead Generation OS",
    description="Targeting Clinic Doctors, Chartered Accountants & High-Inquiry Practices with Automated Vulnerability Audits & Custom Voice Demos",
    version="1.0.0",
    lifespan=lifespan
)

# API routes
app.include_router(api_router, prefix="/api")

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

@app.get("/")
def serve_index():
    return FileResponse(BASE_DIR / "app" / "static" / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
