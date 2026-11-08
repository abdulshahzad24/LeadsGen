import csv
import io
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

from app.database import (
    get_all_leads, get_lead_by_id, insert_lead, update_lead,
    delete_lead, get_stats
)
from app.enrichment.vulnerability import calculate_vulnerability_and_roi
from app.enrichment.email_finder import discover_emails_from_website
from app.pitch.generator import generate_personalized_pitches
from app.pitch.simulator import simulate_voice_agent_reply
from app.scrapers.lead_finder import search_live_osm_places, generate_leads_for_search

router = APIRouter()

class LeadCreateRequest(BaseModel):
    business_name: str
    contact_person: Optional[str] = ""
    niche: str = "clinic"
    specialty: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    address: Optional[str] = ""
    city: str = "Mumbai"
    country: Optional[str] = "India"
    rating: Optional[float] = 4.5
    review_count: Optional[int] = 50
    opening_hours: Optional[str] = "Mon-Sat: 10:00 AM - 7:30 PM (Sun: Closed)"
    has_online_booking: Optional[bool] = False
    notes: Optional[str] = ""

class LeadUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class SearchLeadsRequest(BaseModel):
    niche: str = "clinic"
    city: str = "Mumbai"
    count: int = 5
    use_live_map: bool = False

class SimulateCallRequest(BaseModel):
    user_message: str
    chat_history: Optional[List[Dict[str, str]]] = []

@router.get("/stats")
def api_get_stats():
    return get_stats()

@router.get("/leads")
def api_get_leads(
    niche: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    min_vulnerability: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    leads = get_all_leads(
        niche=niche,
        status=status,
        city=city,
        search=search,
        min_vulnerability=min_vulnerability,
        limit=limit,
        offset=offset
    )
    return {"leads": leads, "count": len(leads)}

@router.get("/leads/{lead_id}")
def api_get_lead(lead_id: str):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.post("/leads")
def api_create_lead(req: LeadCreateRequest):
    lead_dict = req.model_dump()
    # Calculate vulnerability & ROI
    vuln = calculate_vulnerability_and_roi(lead_dict)
    lead_dict.update(vuln)
    
    # Generate pitches
    pitches = generate_personalized_pitches(lead_dict)
    lead_dict["pitches"] = pitches
    
    saved = insert_lead(lead_dict)
    return saved

@router.patch("/leads/{lead_id}")
def api_update_lead(lead_id: str, req: LeadUpdateRequest):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = update_lead(lead_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated

@router.delete("/leads/{lead_id}")
def api_delete_lead(lead_id: str):
    ok = delete_lead(lead_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "deleted", "id": lead_id}

@router.post("/leads/search")
async def api_search_leads(req: SearchLeadsRequest):
    if req.use_live_map:
        new_leads = await search_live_osm_places(req.niche, req.city, limit=req.count)
    else:
        new_leads = generate_leads_for_search(req.niche, req.city, count=req.count)
    return {"leads": new_leads, "count": len(new_leads)}

@router.post("/leads/{lead_id}/discover-email")
async def api_discover_email(lead_id: str):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    result = await discover_emails_from_website(
        website_url=lead.get("website", ""),
        contact_person=lead.get("contact_person", ""),
        niche=lead.get("niche", "clinic")
    )
    
    if result.get("primary_email"):
        update_lead(lead_id, {"email": result["primary_email"]})
        
    return {
        "lead_id": lead_id,
        "primary_email": result.get("primary_email"),
        "all_emails": result.get("all_emails", []),
        "source": result.get("source")
    }

@router.post("/leads/{lead_id}/regenerate-pitch")
def api_regenerate_pitch(lead_id: str):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    pitches = generate_personalized_pitches(lead)
    updated = update_lead(lead_id, {"pitches": pitches})
    return updated

@router.post("/leads/{lead_id}/simulate-call")
def api_simulate_call(lead_id: str, req: SimulateCallRequest):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    reply = simulate_voice_agent_reply(lead, req.user_message, req.chat_history)
    return {"agent_reply": reply}

@router.get("/leads/export/csv")
def api_export_csv():
    leads = get_all_leads(limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row formatted for cold outreach & CRM
    writer.writerow([
        "Lead ID", "Business Name", "Contact Person", "Niche", "Specialty",
        "Phone", "Email", "Website", "City", "Country", "Vulnerability Score",
        "Monthly Missed Calls", "Monthly Revenue Loss (INR)", "Status",
        "WhatsApp Hook", "Cold Email Subject", "Cold Email Body"
    ])
    
    for l in leads:
        pitches = l.get("pitches", {})
        email_step1 = pitches.get("cold_email_step1", {})
        writer.writerow([
            l.get("id"),
            l.get("business_name"),
            l.get("contact_person"),
            l.get("niche"),
            l.get("specialty"),
            l.get("phone"),
            l.get("email"),
            l.get("website"),
            l.get("city"),
            l.get("country"),
            l.get("vulnerability_score"),
            l.get("est_monthly_missed_calls"),
            l.get("est_monthly_revenue_loss_inr"),
            l.get("status"),
            pitches.get("whatsapp_pitch", ""),
            email_step1.get("subject", "") if isinstance(email_step1, dict) else "",
            email_step1.get("body", "") if isinstance(email_step1, dict) else ""
        ])
        
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=agentic_ai_leads.csv"}
    )

@router.post("/leads/seed")
def api_seed_leads():
    existing = get_all_leads(limit=1)
    if existing:
        return {"message": "Leads already exist", "total": len(get_all_leads(limit=1000))}
        
    # Seed top targets across clinics and CAs in Mumbai, Delhi, Bangalore
    seed_configs = [
        ("clinic", "Mumbai", 5),
        ("ca", "Mumbai", 4),
        ("clinic", "Delhi", 4),
        ("ca", "Delhi", 4),
        ("clinic", "Bangalore", 4),
        ("diagnostic", "Mumbai", 2),
        ("real_estate", "Bangalore", 2)
    ]
    total_created = 0
    for niche, city, count in seed_configs:
        created = generate_leads_for_search(niche, city, count=count)
        total_created += len(created)
        
    return {"message": f"Successfully seeded {total_created} high-vulnerability leads", "total": total_created}
