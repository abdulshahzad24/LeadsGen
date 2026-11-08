import os
import json
from typing import Dict, Any, Optional
from app.config import GEMINI_API_KEY, NICHE_BENCHMARKS

def generate_personalized_pitches(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a full outreach suite:
    1. whatsapp_pitch
    2. cold_email_step1
    3. cold_email_step2
    4. cold_email_step3
    5. cold_call_script
    6. voice_agent_prompt (for Vapi / Retell / Gemini Live)
    7. sample_conversation_flow (for interactive simulator)
    """
    # Check if Gemini API is available and key is configured
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 10:
        try:
            return generate_with_gemini(lead)
        except Exception as e:
            print(f"[Warning] Gemini API call failed ({e}), falling back to deterministic template engine.")
            return generate_rule_based_pitches(lead)
    else:
        return generate_rule_based_pitches(lead)


def generate_with_gemini(lead: Dict[str, Any]) -> Dict[str, Any]:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    niche_info = NICHE_BENCHMARKS.get(lead.get("niche", "clinic"), NICHE_BENCHMARKS["clinic"])
    
    prompt = f"""
You are the world's top B2B sales copywriter & outbound strategist for an "Agentic AI Voice Caller" company.
Our product provides human-sounding 24/7 AI Voice receptionists that answer incoming phone calls instantly, book appointments/consultations directly into the CRM, handle FAQs, and follow up with leads via WhatsApp and SMS without putting callers on hold.

Target Lead Information:
- Business Name: {lead.get('business_name')}
- Contact Person: {lead.get('contact_person')}
- Niche: {lead.get('niche')} ({niche_info['label']})
- Specialty/Services: {lead.get('specialty')}
- Location: {lead.get('city')}, {lead.get('address')}
- Google Rating: {lead.get('rating')} stars ({lead.get('review_count')} reviews)
- Operating Hours: {lead.get('opening_hours')}
- Online Booking System: {'Yes' if lead.get('has_online_booking') else 'None (100% phone dependent)'}
- Vulnerability Score: {lead.get('vulnerability_score')}/100
- Estimated Monthly Missed Calls: {lead.get('est_monthly_missed_calls')} calls
- Estimated Monthly Lost Revenue: ₹{lead.get('est_monthly_revenue_loss_inr'):,} (~${lead.get('est_monthly_revenue_loss_usd'):,})

Return a strictly valid JSON object with the following exact keys:
1. "whatsapp_pitch": A concise, punchy 3-part WhatsApp message. Mention their exact clinic/firm name, their review count, the estimated missed calls after hours, and a direct CTA to hear an 18-sec audio sample. Use emojis tastefully.
2. "cold_email_step1": A high-converting cold email (Subject line + Body). Focus on the "Missed Call Leak Audit" and how their front desk gets overwhelmed.
3. "cold_email_step2": Follow-up email (sent 3 days later) with a 30-second audio demonstration proof.
4. "cold_email_step3": Breakup / 9-word closing email.
5. "cold_call_script": A complete 60-second SDR cold call script for calling their front desk/receptionist to reach the Doctor/Partner, including gatekeeper bypass and 2 objection rebuttals.
6. "voice_agent_prompt": A complete, production-ready system prompt for an AI Voice Agent (e.g. Retell / Vapi / Gemini Live) customized specifically for {lead.get('business_name')}. It should include persona, greetings, services handled, appointment booking guidelines, and FAQ answering instructions.
7. "sample_caller_dialogue": A list of 3-4 turn-by-turn conversation messages between a Caller and the AI Agent showing how gracefully it books an appointment or answers a pricing question. Each item should have "speaker" ('Caller' or 'AI Agent') and "text".

Respond ONLY with valid JSON.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )
    result = json.loads(response.text)
    return result


def generate_rule_based_pitches(lead: Dict[str, Any]) -> Dict[str, Any]:
    niche = lead.get("niche", "clinic")
    name = lead.get("business_name", "your business")
    person = lead.get("contact_person") or ("Doctor" if niche == "clinic" else "Sir/Ma'am")
    specialty = lead.get("specialty") or ("healthcare" if niche == "clinic" else "professional services")
    city = lead.get("city", "your city")
    reviews = lead.get("review_count", 50)
    rating = lead.get("rating", 4.5)
    hours = lead.get("opening_hours", "regular office hours")
    missed_calls = lead.get("est_monthly_missed_calls", 380)
    loss_inr = f"{lead.get('est_monthly_revenue_loss_inr', 180000):,}"
    loss_usd = f"{lead.get('est_monthly_revenue_loss_usd', 2200):,}"

    if niche == "clinic":
        salutation = f"{person}" if "Dr." in person else f"Dr. {person}"
        
        whatsapp = (
            f"Hello {salutation} 👋\n\n"
            f"Noticed {name} has a stellar {rating}★ rating ({reviews}+ reviews in {city})! 🏥\n\n"
            f"We ran a brief inquiry flow audit on clinics in {city}. Because {name} closes around {hours}, "
            f"an estimated *~{round(missed_calls/26)} patient calls go unanswered daily* (especially between 7:30 PM - 10 PM & Sundays) "
            f"— leaking ~*₹{loss_inr}/month* in missed consultations.\n\n"
            f"We deployed a 24/7 Voice AI Receptionist for doctors that answers in 2 rings, answers {specialty} queries, and books appointments straight into your calendar.\n\n"
            f"Can I send you a 20-second WhatsApp voice note of how our AI answers as {name}'s receptionist?"
        )

        email_1_subject = f"Quick question regarding after-hours calls at {name}"
        email_1_body = f"""Dear {salutation},

I was looking at {name}'s profile in {city} — congratulations on building such a strong patient reputation ({reviews}+ reviews).

When analyzing appointment volume for {specialty} clinics, we found that 28% to 34% of patient calls ring out unanswered:
1. During the morning OPD rush when your front desk is checking in physical patients.
2. In the evening after {hours} when patients get home from work and want to book.
3. Over weekends when the clinic is closed.

For a clinic of your volume, that represents roughly ~{missed_calls} missed inquiries every month — or roughly ₹{loss_inr} in patient appointments lost to nearby clinics.

We built an Agentic Voice AI Receptionist specifically for healthcare practices. It answers instantly (no hold music), speaks fluent Hindi & English, triages patient concerns, and books appointments directly into your clinic calendar or WhatsApp.

Would you be open to listening to a 30-second live test call of the AI answering as {name}'s front desk?

Best regards,
LeadGen Voice AI Team
"""

        email_2_subject = f"Audio demo for {name} (as promised)"
        email_2_body = f"""Hi {salutation},

Following up on my previous note. Rather than explain how the AI works, I put together a quick 30-second simulation of our Voice AI answering a patient booking request for {name}.

Here is what it handles effortlessly:
• Inquires: "What time does Dr. see patients for {specialty}?"
• Books: Collects patient name, symptom, preferred slot, and sends instant WhatsApp confirmation.
• Zero hold times: Can handle 10 patient calls simultaneously without a busy tone.

Would you have 5 minutes this Thursday or Friday for a quick 1-click test call from your phone?

Warmly,
LeadGen Voice AI Team
"""

        email_3_subject = f"Closing the file for {name}?"
        email_3_body = f"""Hi {salutation},

I haven't heard back, so I assume automated 24/7 patient call handling and recovering missed appointment revenue isn't a top priority for {name} right now.

If you change your mind when patient rush picks up, feel free to reply here.

Wishing you and your practice continued success!

Best regards,
LeadGen Voice AI Team
"""

        cold_call_script = f"""[Cold Call Script for Calling {name}]

Target: Receptionist / Front Desk (Gatekeeper) -> Doctor / Practice Head

[Phase 1: Gatekeeper Bypass]
SDR: "Hi, good morning! I was trying to check your appointment schedule on your number yesterday around 8 PM after the clinic closed, but it went to voicemail. Who handles patient inquiries when the front desk is busy or closed?"
Receptionist: "That's handled during clinic hours only / You can speak with Dr. {person}."
SDR: "Understood! The reason I ask is we just set up an automated 24/7 Voice AI for a top {specialty} clinic down in {city} that answers calls after 7 PM and books appointments directly so front-desk staff aren't overwhelmed with 50 ringing phones while managing patients. Is Dr. {person} in between consultations for 60 seconds?"

[Phase 2: If Doctor gets on the phone]
SDR: "Dr. {person}, thank you for taking 30 seconds. I saw {name} has {reviews}+ five-star reviews. We built an AI voice caller that answers whenever your reception lines are busy or closed, answers {specialty} questions, and books patients directly into your calendar. We estimated you might be losing 15-20 calls a day after 7 PM. I don't want to sell you anything right now — could I just trigger a 30-second test call to your mobile so you can hear how the AI talks?"

[Objection Handling]
• "We already have a full-time receptionist":
  "That's fantastic! Our AI doesn't replace them — it acts as their backup so when they're drawing blood or checking in a patient, the caller doesn't hear a busy tone. What happens to calls coming in on Sunday?"
• "Send an email":
  "Happy to send an email! What's your direct WhatsApp so I can also text you the 20-second audio clip of the AI answering as {name}?"
"""

        voice_prompt = f"""You are the official 24/7 AI Receptionist for '{name}', located in {city}.
Your persona is warm, highly professional, polite, and reassuring.
You specialize in patient appointment scheduling and information for: {specialty}.

Operating Hours: {hours}.
Doctor / Practice Lead: {salutation}.

Your core responsibilities:
1. Greet the patient warmly: "Thank you for calling {name}. My name is Maya, your digital assistant. How may I assist you today?"
2. When a patient asks to book an appointment:
   - Politely ask for their full name, contact number, and the main reason for visit.
   - Ask for their preferred day and morning or evening slot.
   - Confirm: "I have requested your appointment for [Day] at [Time]. You will receive an instant confirmation SMS and WhatsApp."
3. If they ask about fees or doctor availability:
   - Provide standard consultation details courteously.
   - For emergency symptoms, instruct them to visit the nearest emergency room immediately.
4. Keep answers concise, natural, and friendly. Do not speak in long monologues."""

        dialogue = [
            {"speaker": "Caller", "text": f"Hi, I want to book an appointment for {specialty} tomorrow evening. Is the doctor available?"},
            {"speaker": "AI Agent", "text": f"Hello! Yes, {salutation} has open consultation slots tomorrow between 5:30 PM and 7:00 PM at {name}. May I know your full name and contact number to reserve your slot?"},
            {"speaker": "Caller", "text": "My name is Priya Mehta, phone is 98765 43210."},
            {"speaker": "AI Agent", "text": f"Thank you, Priya! I have scheduled you for tomorrow at 6:00 PM with {salutation}. A confirmation with location directions has just been sent to your WhatsApp. Is there anything else I can help you with?"}
        ]

    elif niche == "ca":
        salutation = f"{person}" if "CA" in person else f"CA {person}"
        whatsapp = (
            f"Hello {salutation} 📊\n\n"
            f"Reaching out from {city}. Noticed {name}'s strong reputation in {specialty} ({reviews}+ reviews).\n\n"
            f"During GST, TDS, and ITR filing deadlines, our audit shows accounting firms lose *35% of high-ticket inbound client calls* because phone lines are constantly engaged with repeat queries ('Did my ITR get filed?', 'What documents do I need?').\n\n"
            f"That's an estimated *₹{loss_inr}/month in lost corporate retainer clients* who called, got a busy signal, and hired another CA down the street.\n\n"
            f"We deployed an Agentic Voice AI that answers {name}'s calls 24/7, answers routine filing status queries automatically, and qualifies high-value corporate clients before booking them on your calendar.\n\n"
            f"Open to hearing a 25-second audio clip of how it handles tax client inquiries?"
        )

        email_1_subject = f"Tax season phone volume & missed corporate leads at {name}"
        email_1_body = f"""Dear {salutation},

With upcoming compliance deadlines, I know your team is likely fielding 50+ phone calls a day — most asking the exact same three questions:
1. "Has my ITR / GST return been uploaded?"
2. "What bank statements are still pending from my side?"
3. "Can I speak to CA {person} for 2 minutes?"

Every hour spent answering routine status calls is an hour taken away from high-value audit work and tax planning. Even worse, new corporate prospects calling for annual retainers get a busy tone and dial another firm.

We built an Agentic Voice AI specifically for Chartered Accountants and Tax Firms:
• It syncs with your client status sheet and answers client status calls in 2 rings.
• It conducts automated document collection reminder calls before deadline days.
• It pre-qualifies new company registration & GST audit prospects and schedules them on your calendar.

Would you be open to an 8-minute demo to see how we saved a peer firm in {city} 35 hours of phone interruptions every week?

Warm regards,
LeadGen Voice AI Team
"""

        email_2_subject = f"Quick 30s audio sample for {name}"
        email_2_body = f"""Hi {salutation},

Quick follow up — I wanted to share a 30-second audio preview of how our Voice AI handles a corporate tax inquiry for {name}:

Caller: "Hi, I just started a private limited company and need GST registration and monthly bookkeeping. What are your charges?"
AI Voice: "Hello! Congratulations on your new company. {name} specializes in private limited incorporation, GST filing, and ROC compliance. CA {person} offers a dedicated corporate advisory consultation. May I take your email and company name to book a 15-minute briefing call?"

It qualifies them, captures budget, and books it straight to your calendar.

Would Thursday at 4 PM work for a quick 5-minute call?

Best,
LeadGen Voice AI Team
"""

        email_3_subject = f"Permission to close your file, {salutation}?"
        email_3_body = f"""Hi {salutation},

Assuming you're completely tied up with tax audits and client filings right now.

I'll pause outreach for now. If you ever want to eliminate repetitive phone calls and never miss a high-ticket corporate inquiry at {name}, feel free to reach back out.

All the best with this quarter's filings!

Best,
LeadGen Voice AI Team
"""

        cold_call_script = f"""[Cold Call Script for Calling {name}]

Target: Junior Accountant / Office Admin -> Managing Partner / CA

[Phase 1: Gatekeeper Bypass]
SDR: "Hi, good afternoon! I'm calling for CA {person}. Is he/she currently in a client audit meeting or at their desk?"
Admin: "They are in a meeting. May I know what this is regarding?"
SDR: "Sure! We build the automated voice system for tax firms in {city} that handles all the repetitive 'What documents do I need to send?' and 'Is my GST filed?' calls during filing season so the partners don't get interrupted 30 times a day. Who manages your client communication workflow during peak tax deadlines?"

[Phase 2: Partner Pitch]
SDR: "{salutation}, I know you're super busy so I'll keep this under 45 seconds. We estimated {name} receives about 40-50 calls daily during peak tax weeks. When your staff is swamped, high-value corporate clients looking for annual audit retainers get a busy line. We built an AI Voice assistant that answers your firm's phones 24/7, answers routine filing status, and books qualified business clients right into your calendar. Can I trigger a 20-second test call to your mobile right now so you can hear how realistic it sounds?"
"""

        voice_prompt = f"""You are the senior front-office AI Associate for '{name}', an established Chartered Accountancy and Tax Advisory firm in {city}.
Your persona is articulate, highly knowledgeable in finance and tax terminologies, courteous, and crisp.
Specialties handled: {specialty}.
Firm Partner: {salutation}.
Hours: {hours}.

Instructions:
1. Greet: "Thank you for calling {name}. I am Aryan, your client advisory assistant. How may I direct your inquiry today?"
2. If an existing client is inquiring about their return or document status:
   - Ask for their Firm / Client Name and registered phone number.
   - Inform them that their file is under review by the compliance team and an update is dispatched via email/WhatsApp.
3. If a prospective client calls for new company incorporation, GST audit, or tax consulting:
   - Inquire about their business entity type (Proprietorship, LLP, Pvt Ltd).
   - Offer to schedule a consultation with {salutation}.
4. Maintain high corporate polish and confidentiality."""

        dialogue = [
            {"speaker": "Caller", "text": f"Hello, we have a newly registered tech startup in {city} and need end-to-end GST filing and annual audit. Do you take on new clients?"},
            {"speaker": "AI Agent", "text": f"Hello! Yes, absolutely. {name} specializes in startup accounting, GST compliance, and statutory audit for technology companies. To arrange a consultation with {salutation}, may I know your company name and your email address?"},
            {"speaker": "Caller", "text": "Our company is NexaFlow Technologies, and my email is rohit@nexaflow.io."},
            {"speaker": "AI Agent", "text": "Splendid, Rohit! I have noted NexaFlow Technologies. I can schedule a 20-minute onboarding call with our Senior Partner tomorrow at 3:30 PM or 5:00 PM. Which works best for you?"}
        ]

    else:
        # Generic High-Inquiry Business (Diagnostic lab, real estate, visa, etc.)
        whatsapp = (
            f"Hello {person} 👋\n\n"
            f"Noticed {name} gets heavy inquiry traffic in {city} ({reviews}+ reviews).\n\n"
            f"For businesses handling high daily calls, our studies show *over 30% of callers hang up if they get a busy tone or wait more than 3 rings* — leaking estimated *₹{loss_inr}/month* to competitors.\n\n"
            f"We created an Agentic AI Voice caller that picks up in 2 seconds, answers complex FAQs, pre-qualifies buyers, and books meetings 24/7.\n\n"
            f"Could I share a 15-second voice sample tailored to {name}?"
        )
        email_1_subject = f"Instant inquiry response for {name}"
        email_1_body = f"Hi {person},\n\nWe noticed {name} receives high daily inquiry volumes for {specialty}. Our 24/7 Voice AI answers every call instantly, books appointments, and stops lead leakage.\n\nWould you like a 30s audio sample?"
        email_2_subject = f"Audio test for {name}"
        email_2_body = f"Hi {person},\n\nFollowing up with a quick audio preview of our AI voice agent for {name}."
        email_3_subject = f"Closing file for {name}"
        email_3_body = f"Hi {person},\n\nAssuming this isn't a priority right now. Reach out anytime if you need 24/7 call automation."
        cold_call_script = f"SDR: 'Hi, I'm calling from LeadGen AI. We built an AI voice assistant that handles peak inquiry calls for {name} so you never miss a client...'"
        voice_prompt = f"You are the 24/7 AI Voice Representative for {name} in {city} handling inquiries for {specialty}."
        dialogue = [
            {"speaker": "Caller", "text": f"Hi, I have a quick question about your services at {name}."},
            {"speaker": "AI Agent", "text": f"Hello! I would be glad to help you with {specialty}. What specific details can I provide for you today?"}
        ]

    return {
        "whatsapp_pitch": whatsapp,
        "cold_email_step1": {"subject": email_1_subject, "body": email_1_body},
        "cold_email_step2": {"subject": email_2_subject, "body": email_2_body},
        "cold_email_step3": {"subject": email_3_subject, "body": email_3_body},
        "cold_call_script": cold_call_script,
        "voice_agent_prompt": voice_prompt,
        "sample_caller_dialogue": dialogue
    }
