from typing import Dict, Any, List
from app.config import GEMINI_API_KEY

def simulate_voice_agent_reply(lead: Dict[str, Any], user_message: str, chat_history: List[Dict[str, str]]) -> str:
    """
    Simulates a live conversational turn between a caller (patient or tax client)
    and the customized AI Receptionist for this specific lead.
    """
    niche = lead.get("niche", "clinic")
    name = lead.get("business_name", "Our Clinic/Firm")
    contact = lead.get("contact_person", "the doctor/partner")
    specialty = lead.get("specialty", "our services")
    city = lead.get("city", "the city")
    hours = lead.get("opening_hours", "10:00 AM to 7:00 PM")
    
    # Try Gemini if key is available
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 10:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            system_instruction = f"""
You are the voice-based AI receptionist for '{name}' in {city}.
Specialty: {specialty}.
Lead/Doctor: {contact}.
Hours: {hours}.

Respond as a natural, friendly, efficient phone receptionist.
Keep your response short (1 to 3 sentences max) so it sounds like spoken phone dialogue.
Never break character. Never output markdown formatting or asterisks.
Book appointments, answer questions about timings/fees, or take messages for {contact}.
"""
            contents = []
            for m in chat_history[-6:]:
                role = "user" if m.get("role") == "user" else "model"
                contents.append(f"{role}: {m.get('text', '')}")
            contents.append(f"user: {user_message}")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="\n".join(contents),
                config={"system_instruction": system_instruction, "temperature": 0.4}
            )
            return response.text.strip().replace("*", "")
        except Exception as e:
            print(f"[Simulator] Gemini fallback: {e}")

    # Deterministic conversational responder
    msg = user_message.lower()
    
    if any(k in msg for k in ["hello", "hi", "hey", "good morning", "good evening"]):
        if niche == "clinic":
            return f"Hello, thank you for calling {name}. My name is Maya, the digital receptionist. Are you looking to schedule an appointment with {contact} today?"
        elif niche == "ca":
            return f"Good day, thank you for calling {name}. I am Aryan, client advisory assistant. How may I direct your tax or corporate compliance query?"
        else:
            return f"Hello, thank you for contacting {name}. How can I assist you with {specialty} today?"
            
    if any(k in msg for k in ["appointment", "book", "slot", "schedule", "consultation", "timing"]):
        if niche == "clinic":
            return f"Certainly! {contact} has open consultation slots tomorrow at 11:30 AM or in the evening at 6:00 PM. Which timing suits you best, and may I take your full name?"
        elif niche == "ca":
            return f"I can arrange a consultation with {contact} for your business. We have open advisory slots tomorrow at 3:30 PM. Would you like me to reserve that for you?"
        else:
            return f"I would be glad to book a session for you. Would tomorrow afternoon work for your schedule?"
            
    if any(k in msg for k in ["fee", "price", "cost", "charge", "rate"]):
        if niche == "clinic":
            return f"The standard initial consultation with {contact} is 800 rupees, which includes a comprehensive diagnostic assessment and 7 days of complimentary follow-up."
        elif niche == "ca":
            return f"Our corporate consultation fee is 2,500 rupees, which is fully adjusted against your retainer if you proceed with our annual compliance packages. May I book a briefing for you?"
        else:
            return f"Our service packages start with an initial assessment. May I note your email so I can send over our detailed transparent fee schedule?"

    if any(k in msg for k in ["location", "address", "where", "reach"]):
        return f"{name} is conveniently located at {lead.get('address', city)}. We have ample visitor parking available. Shall I text you the Google Maps location link on WhatsApp?"

    if any(k in msg for k in ["tomorrow", "today", "pm", "am", "clock", "yes", "sure", "ok", "my name is"]):
        return f"Perfect, I have registered your details for {contact}. A calendar invite and SMS confirmation with directions has just been dispatched. Is there anything else you'd like to ask before your visit?"

    if niche == "clinic":
        return f"Understood. I have logged that note for {contact}'s nursing desk. May I confirm your best callback number so the clinic team can confirm your record?"
    else:
        return f"Thank you for sharing those details. I've logged your requirement for {contact}. Our team will review your file and reach out shortly. Have a wonderful day!"
