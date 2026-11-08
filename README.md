# 📞 Agentic AI Voice Caller — Lead Generation & Outreach Engine

A purpose-built B2B Lead Generation & Outbound Sales Operating System engineered specifically for **Agentic AI Voice Caller & Receptionist agencies** selling to:
1. **Clinic Doctors & Hospitals** (Dentistry, Dermatology, Pediatrics, Orthopedics, IVF clinics)
2. **Chartered Accountants (CAs) & Tax Advisory Firms** (Corporate audit, GST, ITR filing)
3. **High-Inquiry Local Businesses** (Diagnostic labs, Real estate agencies, Visa/Immigration consultants)

---

## 🎯 The Core Problem & Value Proposition

Doctors and CAs **never buy generic "AI callers"** when pitched with tech buzzwords. They buy when you show them the **exact revenue leaking out of their phone lines**:

- **Clinics**: The front desk is physically managing in-person patients while phones ring constantly. Between 7:30 PM and 10:00 PM (when working professionals try to book appointments) and all day Sunday, clinics are closed. **Result: 28% to 35% of high-intent patient calls go unanswered, leaking ₹1.5L – ₹4L/month ($2,000–$5,000) in lost treatments.**
- **Chartered Accountants (CAs)**: During GST deadlines and ITR filing season, partners and staff receive 50+ calls a day asking the exact same three questions (*"Did my return get filed?", "What bank statements are pending?"*). Meanwhile, high-value corporate retainers calling for company registration get a busy tone and hire a competitor. **Result: Partners waste 3+ hours daily on repetitive queries, leaking ₹2L – ₹6L/month in lost corporate advisory fees.**

This software automatically discovers these businesses, audits their operational phone vulnerability, calculates their exact monthly lost revenue, and generates ready-to-send WhatsApp, cold email, cold call scripts, and an interactive voice demo.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Dual Lead Prospector** | Live geospatial discovery via OpenStreetMap Overpass API + High-fidelity local business generator across Mumbai, Delhi, Bangalore, Hyderabad, Pune, Dubai, London, and New York. |
| **Inbound Call Vulnerability Audit** | Algorithmic scoring (0–100) based on review volume, operating hours, after-hours closures, and lack of web booking. |
| **Revenue Leakage Calculator** | Instant calculation of monthly missed calls and lost client revenue (in ₹ INR and $ USD) tailored to vertical benchmarks. |
| **Multi-Touch Outreach Suite** | 1-click generated **WhatsApp Hook** with direct click-to-chat link, **3-Step Cold Email Sequence**, and **SDR Gatekeeper Cold Call Script**. |
| **Ready-to-Deploy Voice Prompts** | Instant system prompts tailored to the lead's exact practice, ready to paste into Vapi, Retell AI, Bland AI, or Gemini Live API. |
| **Interactive Voice Simulator** | Test-drive the voice receptionist right in your browser with spoken Audio (Text-to-Speech) and microphone voice input! |
| **1-Click CSV Export** | Export enriched leads and customized pitch copy directly into Smartlead, Instantly.ai, Apollo, or GoHighLevel. |

---

## 🛠️ Quickstart

### 1. Requirements
- Python 3.10+ (Standard library + FastAPI, Uvicorn, httpx)
- No external database needed (Uses built-in SQLite stored in `data/leads.db`)

### 2. Run the Application
```bash
# Navigate to the project folder
cd /Users/abdulshahzad/Documents/LeadsGen

# Start the server (auto-seeds 21 high-vulnerability sample leads on first run)
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📂 Project Structure

```
LeadsGen/
├── app/
│   ├── api/
│   │   └── routes.py             # FastAPI REST endpoints (CRUD, search, simulate, export)
│   ├── enrichment/
│   │   └── vulnerability.py      # Call leakage scoring & revenue loss calculation
│   ├── pitch/
│   │   ├── generator.py          # WhatsApp, cold email, SDR script & voice prompt generator
│   │   └── simulator.py          # Browser-based live voice receptionist simulator
│   ├── scrapers/
│   │   └── lead_finder.py        # OpenStreetMap & curated local business generator
│   ├── static/
│   │   ├── app.js                # Frontend UI controller (simulator, TTS, filters, drawer)
│   │   ├── index.html            # Modern Tailwind CSS dashboard
│   │   └── styles.css            # Dark mode styles & glowing cards
│   ├── config.py                 # Niche benchmarks, operating metrics & settings
│   └── database.py               # SQLite schema, queries & index management
├── data/                         # SQLite persistence directory (leads.db)
├── main.py                       # Application entrypoint & lifespan seeder
├── requirements.txt              # Python dependencies
├── run.sh                        # One-click start script
└── README.md                     # Documentation & sales playbook
```

---

## 📈 Outbound Sales Playbook (Closing Doctors & CAs)

### 🩺 Strategy for Clinic Doctors:
1. **Find high-review clinics** (60+ reviews) that close by 7:30 PM and don't have online booking.
2. **Send the WhatsApp Hook**:
   > *"Dr. Sharma, noticed Apex Dental has 240+ reviews in Bandra. We ran a brief call audit: you likely miss ~18 calls/day after 7:30 PM & Sundays (~₹1.8L in missed treatments). Can I send a 20-sec audio clip of how our AI receptionist answers as Apex Dental?"*
3. **When they reply**: Open the lead in this dashboard, click the **Live Voice Simulator**, record a 20-second screen/audio clip of the AI answering their clinic's phone, and send it over WhatsApp.
4. **Offer a 7-day Pilot**: *"Let us route your after-hours calls to the AI for 7 days. If you don't recover at least 10 booked appointments, you pay zero."*

### 📊 Strategy for Chartered Accountants (CAs):
1. **Target ahead of GST/ITR deadlines** (July, September, October, March).
2. **Hit the partner's pain**:
   > *"CA Gupta, how many times did your staff get interrupted today with 'Did my return get filed?' During tax deadlines, accounting firms leak 35% of high-value corporate inquiries because lines are constantly busy."*
3. **Offer the Document Reminder + Inbound Qualification combo**:
   - Inbound: Answers client status calls automatically from a Google Sheet / CRM.
   - Outbound: Auto-calls clients to collect pending Form 26AS, bank statements, and invoices.

---

## 🔌 Telephony & Voice AI Platform Integration

The system generates ready-to-paste system prompts in the **Voice Agent Prompt** tab of each lead:
- **Retell AI / Vapi**: Paste the generated system prompt into your Agent Persona and assign a Twilio or Plivo phone number.
- **Bland AI**: Use the prompt in your Pathway configuration.
- **Google Gemini Live API**: Use bidirectional audio streaming with `gemini-2.5-flash` or `gemini-3.8-flash` using the generated system instruction.

---

## 🔑 Optional Configuration

To enable Gemini-powered dynamic pitch writing and conversations, set your API key:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```
*(If omitted, the built-in deterministic industry template engine runs automatically with zero latency and 100% reliability).*
