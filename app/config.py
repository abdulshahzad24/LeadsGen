import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "leads.db"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Industry benchmark settings for calculation of missed call losses
NICHE_BENCHMARKS = {
    "clinic": {
        "label": "Doctor / Clinic",
        "avg_daily_inbound_calls": 65,
        "avg_missed_call_rate": 0.28,  # 28% of calls missed during rush hours / after hours
        "conversion_rate_inbound": 0.35,  # 35% of callers want to book an appointment
        "avg_patient_ltv_inr": 4500,  # Consultation + prescriptions/tests/followups (INR)
        "avg_patient_ltv_usd": 150,
        "pain_points": [
            "Patients get busy tone during peak morning OPD hours",
            "No one answers phone after 7:30 PM when working patients try to book",
            "Front desk is overwhelmed juggling physical patients and ringing phones",
            "High no-show rate due to lack of automated WhatsApp / voice call reminders"
        ],
        "ai_use_cases": [
            "24/7 Appointment booking & calendar sync",
            "Pre-consultation symptom triage & doctor schedule check",
            "Automated confirmation & reminder calls 2 hours before slot",
            "Instant FAQs on doctor fees, lab report availability & clinic location"
        ]
    },
    "ca": {
        "label": "Chartered Accountant / Tax Firm",
        "avg_daily_inbound_calls": 45,
        "avg_missed_call_rate": 0.32,  # 32% missed during tax filing crunch & meetings
        "conversion_rate_inbound": 0.25,  # 25% of inquiries convert to billable clients
        "avg_patient_ltv_inr": 25000,  # Annual retainer / filing fee (INR)
        "avg_patient_ltv_usd": 600,
        "pain_points": [
            "During GST & ITR deadlines, 50+ clients call repeatedly asking 'Did my filing happen?'",
            "CAs spend 3 hours daily answering basic queries instead of doing billable audit work",
            "New high-value prospective corporate clients call, get busy tone, and hire competitor CA",
            "Repeated phone follow-ups required to collect missing documents (Form 26AS, bank statements)"
        ],
        "ai_use_cases": [
            "Filing status inquiry bot checking client PAN/GSTN status automatically",
            "Document collection reminder caller collecting bank statements & invoices",
            "New corporate consultation qualifying and scheduling for Senior Partner",
            "Instant answers to fee structure, compliance deadlines, and service offerings"
        ]
    },
    "diagnostic": {
        "label": "Diagnostic Lab / Pathology Center",
        "avg_daily_inbound_calls": 90,
        "avg_missed_call_rate": 0.25,
        "conversion_rate_inbound": 0.40,
        "avg_patient_ltv_inr": 2800,
        "avg_patient_ltv_usd": 90,
        "pain_points": [
            "Constant calls asking 'Is fasting required for my lipid profile?'",
            "Patients repeatedly calling 'Is my blood test report ready yet?'",
            "Home sample collection requests lost because lines were engaged"
        ],
        "ai_use_cases": [
            "Home collection booking with address & time slot capture",
            "Automated report dispatch via WhatsApp when ready",
            "Test preparation instruction delivery (fasting, timing, precautions)"
        ]
    },
    "real_estate": {
        "label": "Real Estate Agency / Property Broker",
        "avg_daily_inbound_calls": 50,
        "avg_missed_call_rate": 0.35,
        "conversion_rate_inbound": 0.15,
        "avg_patient_ltv_inr": 75000,
        "avg_patient_ltv_usd": 1500,
        "pain_points": [
            "Portals like 99acres/MagicBricks send leads who call immediately; delayed response loses the buyer",
            "Brokers are out showing properties and cannot attend inbound buyer calls",
            "Unqualified tire-kickers waste valuable broker phone time"
        ],
        "ai_use_cases": [
            "Instant 10-second response to portal inquiries",
            "Budget, preferred location & timeline pre-qualification",
            "Site visit scheduling directly to broker's calendar"
        ]
    },
    "visa_consultant": {
        "label": "Visa & Immigration Consultant",
        "avg_daily_inbound_calls": 60,
        "avg_missed_call_rate": 0.30,
        "conversion_rate_inbound": 0.20,
        "avg_patient_ltv_inr": 40000,
        "avg_patient_ltv_usd": 1000,
        "pain_points": [
            "Dozens of students and job seekers calling for eligibility checks",
            "Counselors spend entire day repeating basic country eligibility requirements",
            "Missed inquiries quickly call another consultant agency down the street"
        ],
        "ai_use_cases": [
            "Automated profile evaluation (education, IELTS score, budget, target country)",
            "One-on-one counselor consultation booking for qualified profiles",
            "Follow-up document reminder calls"
        ]
    }
}
