import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# On Vercel serverless, only /tmp is writable
if os.getenv("VERCEL"):
    DATA_DIR = Path("/tmp/data")
else:
    DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "leads.db"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

NICHE_BENCHMARKS = {
    "clinic": {
        "label": "Doctor / Clinic",
        "avg_daily_inbound_calls": 65,
        "avg_missed_call_rate": 0.28,
        "conversion_rate_inbound": 0.35,
        "avg_patient_ltv_inr": 4500,
        "avg_patient_ltv_usd": 150
    },
    "ca": {
        "label": "Chartered Accountant / Tax",
        "avg_daily_inbound_calls": 45,
        "avg_missed_call_rate": 0.32,
        "conversion_rate_inbound": 0.25,
        "avg_patient_ltv_inr": 25000,
        "avg_patient_ltv_usd": 600
    },
    "diagnostic": {
        "label": "Diagnostic Lab",
        "avg_daily_inbound_calls": 90,
        "avg_missed_call_rate": 0.25,
        "conversion_rate_inbound": 0.40,
        "avg_patient_ltv_inr": 2800,
        "avg_patient_ltv_usd": 90
    },
    "real_estate": {
        "label": "Real Estate",
        "avg_daily_inbound_calls": 50,
        "avg_missed_call_rate": 0.35,
        "conversion_rate_inbound": 0.15,
        "avg_patient_ltv_inr": 75000,
        "avg_patient_ltv_usd": 1500
    },
    "visa_consultant": {
        "label": "Visa Consultant",
        "avg_daily_inbound_calls": 60,
        "avg_missed_call_rate": 0.30,
        "conversion_rate_inbound": 0.20,
        "avg_patient_ltv_inr": 40000,
        "avg_patient_ltv_usd": 1000
    }
}
