
from datetime import datetime, timedelta

def demo_entity_results(name: str):
    n = (name or '').strip() or 'Example Co'
    return [
        {"name": f"{n} Holdings LLC", "uei": "UEI123456789", "cage": "1A2B3", "status":"Active", "address":"Chico, CA"},
        {"name": f"{n} Services Inc",   "uei": "UEI987654321", "cage": "9Z8Y7", "status":"Inactive", "address":"Redding, CA"}
    ]

def demo_opportunities_by_naics(naics: str):
    code = (naics or "").strip() or "541512"
    today = datetime.utcnow().date()
    return [
        {
            "solicitation": f"NAVY-{code}-R-001",
            "title": f"Services under NAICS {code} - Customer Engagement Platform",
            "agency": "Department of the Navy",
            "response_due": (today + timedelta(days=14)).isoformat(),
            "set_aside": "Total Small Business",
            "naics": code,
            "psc": "D399",
            "status": "Active"
        },
        {
            "solicitation": f"USAF-{code}-R-014",
            "title": f"Enterprise Integration and Data Orchestration ({code})",
            "agency": "Department of the Air Force",
            "response_due": (today + timedelta(days=21)).isoformat(),
            "set_aside": "None",
            "naics": code,
            "psc": "D304",
            "status": "Active"
        }
    ]
