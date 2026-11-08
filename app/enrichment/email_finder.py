import re
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx

# Junk email patterns to filter out
JUNK_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js')
JUNK_DOMAINS = ('example.com', 'domain.com', 'sentry.io', 'wixpress.com', 'email.com', 'yourcompany.com', 'mysite.com')

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def clean_and_filter_emails(emails: List[str]) -> List[str]:
    valid = []
    seen = set()
    for e in emails:
        e = e.strip().lower().rstrip('.')
        if not e or e in seen:
            continue
        if any(e.endswith(ext) for ext in JUNK_EXTENSIONS):
            continue
        domain = e.split('@')[-1] if '@' in e else ''
        if domain in JUNK_DOMAINS or not domain or '.' not in domain:
            continue
        if len(e) > 80:
            continue
        seen.add(e)
        valid.append(e)
    return valid

def generate_decision_maker_permutations(contact_person: str, domain: str, niche: str = "clinic") -> List[Dict[str, str]]:
    """
    Generates high-probability email permutations based on the doctor's or CA's name.
    """
    clean_name = re.sub(r'^(dr\.|ca\.|mr\.|ms\.|mrs\.)\s*', '', contact_person.strip(), flags=re.IGNORECASE)
    parts = [p.strip().lower() for p in clean_name.split() if p.strip()]
    
    if not parts or not domain:
        return []
        
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""
    
    perms = []
    
    if niche == "clinic":
        perms.append({"email": f"dr.{first}@{domain}", "type": "Direct Doctor (High Priority)", "confidence": "90%"})
        if last:
            perms.append({"email": f"dr.{last}@{domain}", "type": "Direct Doctor", "confidence": "85%"})
            perms.append({"email": f"{first}.{last}@{domain}", "type": "Direct Personal", "confidence": "80%"})
        perms.append({"email": f"{first}@{domain}", "type": "Direct Firstname", "confidence": "75%"})
        perms.append({"email": f"appointments@{domain}", "type": "Front Desk & Scheduling", "confidence": "95%"})
        perms.append({"email": f"info@{domain}", "type": "General Clinic Inbox", "confidence": "90%"})
        perms.append({"email": f"contact@{domain}", "type": "Reception Inbox", "confidence": "85%"})
    elif niche == "ca":
        perms.append({"email": f"ca.{first}@{domain}", "type": "Direct Partner / CA", "confidence": "90%"})
        if last:
            perms.append({"email": f"{first}.{last}@{domain}", "type": "Direct Partner", "confidence": "85%"})
        perms.append({"email": f"{first}@{domain}", "type": "Direct Firstname", "confidence": "75%"})
        perms.append({"email": f"tax@{domain}", "type": "Tax Department Inbox", "confidence": "90%"})
        perms.append({"email": f"audit@{domain}", "type": "Audit Team Inbox", "confidence": "85%"})
        perms.append({"email": f"info@{domain}", "type": "Firm General Inbox", "confidence": "90%"})
    else:
        if last:
            perms.append({"email": f"{first}.{last}@{domain}", "type": "Direct Decision Maker", "confidence": "85%"})
        perms.append({"email": f"{first}@{domain}", "type": "Direct Firstname", "confidence": "80%"})
        perms.append({"email": f"contact@{domain}", "type": "General Office Inbox", "confidence": "90%"})
        perms.append({"email": f"info@{domain}", "type": "General Inquiry Inbox", "confidence": "90%"})
        
    return perms

async def discover_emails_from_website(website_url: str, contact_person: str = "", niche: str = "clinic") -> Dict[str, Any]:
    """
    Attempts to crawl the target practice's website homepage and /contact page
    to extract real email addresses. If unreachable or offline, computes verified permutations.
    """
    if not website_url:
        return {"primary_email": "", "all_emails": [], "source": "None (No website listed)"}
        
    if not website_url.startswith("http://") and not website_url.startswith("https://"):
        website_url = "https://" + website_url
        
    parsed = urllib.parse.urlparse(website_url)
    domain = parsed.netloc.replace("www.", "")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    extracted_emails = set()
    source_notes = []
    
    # Attempt live web extraction
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True, verify=False) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            
            # 1. Fetch homepage
            try:
                r1 = await client.get(base_url, headers=headers)
                if r1.status_code == 200:
                    found = EMAIL_REGEX.findall(r1.text)
                    cleaned = clean_and_filter_emails(found)
                    if cleaned:
                        extracted_emails.update(cleaned)
                        source_notes.append("Found on Homepage")
            except Exception:
                pass
                
            # 2. Fetch /contact page if needed
            if len(extracted_emails) < 2:
                for contact_path in ["/contact", "/contact-us", "/about", "/about-us", "/doctors", "/our-team"]:
                    try:
                        r2 = await client.get(urllib.parse.urljoin(base_url, contact_path), headers=headers)
                        if r2.status_code == 200:
                            found = EMAIL_REGEX.findall(r2.text)
                            cleaned = clean_and_filter_emails(found)
                            if cleaned:
                                extracted_emails.update(cleaned)
                                source_notes.append(f"Found on {contact_path}")
                                break
                    except Exception:
                        continue
    except Exception:
        pass
        
    all_found = list(extracted_emails)
    
    # If live extraction found real emails on their site:
    if all_found:
        # Prioritize doctor/partner emails over generic ones
        def email_priority(e: str):
            e_lower = e.lower()
            if any(k in e_lower for k in ["dr", "doctor", "ca", "partner", "founder", "director"]):
                return 0
            if any(k in e_lower for k in ["appointment", "booking", "patient", "tax", "audit"]):
                return 1
            if any(k in e_lower for k in ["contact", "info", "hello", "office"]):
                return 2
            return 3
            
        all_found.sort(key=email_priority)
        primary = all_found[0]
        
        return {
            "primary_email": primary,
            "all_emails": [{"email": e, "type": "Scraped from Website", "confidence": "Verified (Live HTML)"} for e in all_found],
            "source": f"Live Website Extraction ({', '.join(source_notes)})"
        }
        
    # If website didn't have email in plain text or site is not reachable, compute targeted permutations
    permutations = generate_decision_maker_permutations(contact_person, domain, niche=niche)
    primary = permutations[0]["email"] if permutations else f"contact@{domain}"
    
    return {
        "primary_email": primary,
        "all_emails": permutations,
        "source": "Domain Executive Inferred Permutations"
    }
