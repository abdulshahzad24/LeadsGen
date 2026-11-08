import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.config import DB_PATH
from app.enrichment.verifier import verify_lead_data

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            contact_person TEXT,
            niche TEXT NOT NULL,
            specialty TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            address TEXT,
            city TEXT,
            country TEXT DEFAULT 'India',
            rating REAL DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            opening_hours TEXT,
            has_online_booking INTEGER DEFAULT 0,
            vulnerability_score INTEGER DEFAULT 50,
            est_monthly_missed_calls INTEGER DEFAULT 0,
            est_monthly_revenue_loss_inr INTEGER DEFAULT 0,
            est_monthly_revenue_loss_usd INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            notes TEXT DEFAULT '',
            pitches TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_niche ON leads(niche)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_city ON leads(city)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_vulnerability ON leads(vulnerability_score DESC)")
    conn.commit()
    conn.close()

def row_to_lead(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    d["has_online_booking"] = bool(d.get("has_online_booking", 0))
    if d.get("pitches"):
        try:
            d["pitches"] = json.loads(d["pitches"])
        except Exception:
            d["pitches"] = {}
    else:
        d["pitches"] = {}
        
    # Attach multi-point verified audit badges
    verification = verify_lead_data(d)
    d["verification_score"] = verification["verification_score"]
    d["is_verified"] = verification["is_verified"]
    d["verification_badges"] = verification["verification_badges"]
    return d

def get_all_leads(
    niche: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    min_vulnerability: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params: List[Any] = []
    
    if niche:
        query += " AND niche = ?"
        params.append(niche)
    if status:
        query += " AND status = ?"
        params.append(status)
    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if min_vulnerability is not None:
        query += " AND vulnerability_score >= ?"
        params.append(min_vulnerability)
    if search:
        query += " AND (business_name LIKE ? OR contact_person LIKE ? OR phone LIKE ? OR address LIKE ? OR specialty LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s, s])
        
    query += " ORDER BY vulnerability_score DESC, review_count DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    leads = [row_to_lead(r) for r in rows]
    conn.close()
    return leads

def get_lead_by_id(lead_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row_to_lead(row)
    return None

def insert_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    lead_id = lead_data.get("id") or str(uuid.uuid4())
    pitches_json = json.dumps(lead_data.get("pitches", {}))
    
    cursor.execute("""
        INSERT INTO leads (
            id, business_name, contact_person, niche, specialty, phone, email,
            website, address, city, country, rating, review_count, opening_hours,
            has_online_booking, vulnerability_score, est_monthly_missed_calls,
            est_monthly_revenue_loss_inr, est_monthly_revenue_loss_usd,
            status, notes, pitches, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_id,
        lead_data.get("business_name", ""),
        lead_data.get("contact_person", ""),
        lead_data.get("niche", "clinic"),
        lead_data.get("specialty", ""),
        lead_data.get("phone", ""),
        lead_data.get("email", ""),
        lead_data.get("website", ""),
        lead_data.get("address", ""),
        lead_data.get("city", ""),
        lead_data.get("country", "India"),
        float(lead_data.get("rating", 0.0)),
        int(lead_data.get("review_count", 0)),
        lead_data.get("opening_hours", ""),
        1 if lead_data.get("has_online_booking") else 0,
        int(lead_data.get("vulnerability_score", 50)),
        int(lead_data.get("est_monthly_missed_calls", 0)),
        int(lead_data.get("est_monthly_revenue_loss_inr", 0)),
        int(lead_data.get("est_monthly_revenue_loss_usd", 0)),
        lead_data.get("status", "new"),
        lead_data.get("notes", ""),
        pitches_json,
        now,
        now
    ))
    conn.commit()
    conn.close()
    return get_lead_by_id(lead_id)

def update_lead(lead_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    fields = []
    params = []
    for k, v in updates.items():
        if k in ("id", "created_at"):
            continue
        if k == "pitches" and isinstance(v, dict):
            fields.append("pitches = ?")
            params.append(json.dumps(v))
        elif k == "has_online_booking":
            fields.append("has_online_booking = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
            
    if not fields:
        conn.close()
        return get_lead_by_id(lead_id)
        
    fields.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(lead_id)
    
    query = f"UPDATE leads SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return get_lead_by_id(lead_id)

def delete_lead(lead_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(est_monthly_revenue_loss_inr), SUM(est_monthly_missed_calls) FROM leads")
    rev_row = cursor.fetchone()
    total_loss_inr = rev_row[0] or 0
    total_missed_calls = rev_row[1] or 0
    
    cursor.execute("SELECT niche, COUNT(*) FROM leads GROUP BY niche")
    by_niche = {r[0]: r[1] for r in cursor.fetchall()}
    
    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    by_status = {r[0]: r[1] for r in cursor.fetchall()}
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE vulnerability_score >= 70")
    high_vuln_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_leads": total_leads,
        "total_missed_calls_monthly": total_missed_calls,
        "total_estimated_revenue_loss_inr": total_loss_inr,
        "total_estimated_revenue_loss_usd": round(total_loss_inr / 85),
        "high_vulnerability_leads": high_vuln_count,
        "by_niche": by_niche,
        "by_status": by_status
    }
