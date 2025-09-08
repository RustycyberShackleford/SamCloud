
import os, requests, datetime as dt

OPPS_URL = "https://api.sam.gov/opportunities/v2/search"
ENTITY_URL = "https://api.sam.gov/entity-information/v4/entities"

class SamApiError(Exception):
    pass

def _date_str(d: dt.date) -> str:
    return d.strftime("%m/%d/%Y")

def search_opportunities_by_naics(naics: str, api_key: str, *, days_back: int = 30, limit: int = 25, offset: int = 0):
    naics = (naics or "").strip()
    if not naics.isdigit():
        return []

    today = dt.date.today()
    posted_to = _date_str(today)
    posted_from = _date_str(today - dt.timedelta(days=days_back))

    params = {
        "api_key": api_key,
        "ncode": naics,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": str(limit),
        "offset": str(offset)
    }
    # Optional: restrict to solicitations + combined synopsis
    # params["ptype"] = ["o","k"]  # multi not supported in simple dict; could send twice

    r = requests.get(OPPS_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise SamApiError(f"Opportunities API error {r.status_code}: {r.text[:500]}")
    data = r.json()
    items = data.get("opportunitiesData", []) or data.get("data", []) or []
    results = []
    for it in items:
        results.append({
            "solicitation": it.get("solicitationNumber") or it.get("solicitation"),
            "title": it.get("title"),
            "agency": it.get("fullParentPathName") or it.get("department"),
            "response_due": it.get("responseDeadLine") or it.get("reponseDeadLine") or "",
            "set_aside": it.get("setAside") or it.get("setAsideCode"),
            "naics": it.get("naicsCode") or "",
            "psc": it.get("classificationCode") or "",
            "status": "Active" if (it.get("active") in ("Yes","YES", True)) else "Archived"
        })
    return results

def search_entities_by_name(name: str, api_key: str, limit: int = 10, offset: int = 0):
    name = (name or "").strip()
    if not name:
        return []
    params = {
        "api_key": api_key,
        "legalBusinessName": name,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration,coreData",
        "page": str(offset),  # some versions use 'page' with size=
        "size": str(limit)
    }
    r = requests.get(ENTITY_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise SamApiError(f"Entity API error {r.status_code}: {r.text[:500]}")
    data = r.json()
    entities = data.get("entityData") or data.get("results") or data.get("data") or []
    out = []
    for e in entities:
        reg = (e.get("entityRegistration") or {})
        core = (e.get("coreData") or {})
        name_val = reg.get("legalBusinessName") or core.get("entityInformation", {}).get("legalBusinessName") or name
        uei = reg.get("ueiSAM") or core.get("entityInformation", {}).get("ueiSAM")
        address = core.get("physicalAddress", {}) if isinstance(core, dict) else {}
        addr_str = ", ".join([
            (address.get("city") or ""),
            (address.get("stateOrProvince") or address.get("state") or "" )
        ]).strip(", ")
        status = reg.get("status") or reg.get("registrationStatus") or ""
        out.append({
            "name": name_val,
            "uei": uei,
            "cage": core.get("entityInformation", {}).get("cageCode"),
            "status": status,
            "address": addr_str
        })
    return out
