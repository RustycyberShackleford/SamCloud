import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)

API_KEY = os.getenv("sam_api_key")

DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")  # MM/DD/YYYY


def require_api_key():
    if not API_KEY:
        return jsonify({
            "error": "Missing API key",
            "hint": "Set environment variable sam_api_key to your SAM.gov Public API key."
        }), 500


def validate_date_param(label: str, value: str):
    if not value or not DATE_RE.match(value):
        return f"{label} must be in MM/DD/YYYY format"
    return None


def within_one_year(posted_from: str, posted_to: str):
    try:
        d1 = datetime.strptime(posted_from, "%m/%d/%Y")
        d2 = datetime.strptime(posted_to, "%m/%d/%Y")
        return (d2 - d1).days <= 366 and d1 <= d2
    except Exception:
        return False


def flatten_opportunity(item: dict) -> dict:
    return {
        "title": item.get("title"),
        "solicitationNumber": item.get("solicitationNumber"),
        "noticeType": item.get("type"),
        "postedDate": item.get("postedDate"),
        "responseDeadLine": item.get("responseDeadLine"),
        "naics": item.get("naicsCode"),
        "setAside": item.get("typeOfSetAsideDescription") or item.get("typeOfSetAside"),
        "agency": (item.get("department") or {}).get("name"),
        "office": (item.get("office") or {}).get("name"),
        "placeOfPerformance": (item.get("placeOfPerformance") or {}).get("city"),
        "state": (item.get("placeOfPerformance") or {}).get("state"),
        "zip": (item.get("placeOfPerformance") or {}).get("zip"),
        "links": item.get("links"),
    }


def flatten_entity(entity: dict) -> dict:
    reg = entity.get("entityRegistration", {})
    core = entity.get("coreData", {})
    naics = []
    for assoc in (core.get("naics") or []):
        code = assoc.get("naicsCode")
        desc = assoc.get("naicsTitle")
        if code:
            naics.append({"code": code, "title": desc})
    return {
        "legalBusinessName": reg.get("legalBusinessName") or core.get("legalBusinessName"),
        "ueiSAM": reg.get("ueiSAM") or core.get("ueiSAM"),
        "cageCode": core.get("cage"),
        "registrationStatus": reg.get("registrationStatus"),
        "registrationExpirationDate": reg.get("registrationExpirationDate"),
        "samRegistered": reg.get("samRegistered"),
        "physicalAddress": (core.get("physicalAddress") or {}),
        "mailingAddress": (core.get("mailingAddress") or {}),
        "naics": naics,
        "entityStartDate": core.get("startDate"),
        "entityEndDate": core.get("endDate"),
        "entityType": core.get("businessType"),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def health():
    return {"ok": True}


@app.route("/search_opportunities")
def search_opportunities():
    missing = require_api_key()
    if missing:
        return missing

    naics = request.args.get("naics", "").strip()
    posted_from = request.args.get("from", "").strip()
    posted_to = request.args.get("to", "").strip()

    if not naics:
        return jsonify({"error": "Missing required parameter: naics"}), 400

    err = validate_date_param("from", posted_from) or validate_date_param("to", posted_to)
    if err:
        return jsonify({"error": err}), 400

    if not within_one_year(posted_from, posted_to):
        return jsonify({"error": "postedFrom/postedTo must be within a 1-year window and from<=to"}), 400

    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 1000))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    url = "https://api.sam.gov/opportunities/v2/search"
    params = {
        "api_key": API_KEY,
        "ncode": naics,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": limit,
        "offset": offset
    }

    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        return jsonify({
            "error": "SAM Opportunities API error",
            "status": r.status_code,
            "body": r.text
        }), 502

    payload = r.json() if r.text else {}
    total = payload.get("totalRecords", 0)
    items = [flatten_opportunity(it) for it in payload.get("opportunitiesData", [])]

    return jsonify({
        "query": {"naics": naics, "from": posted_from, "to": posted_to, "limit": limit, "offset": offset},
        "totalRecords": total,
        "pageCount": len(items),
        "nextOffset": offset + limit if (offset + limit) < max(total, 0) else None,
        "results": items
    })


@app.route("/search_entity")
def search_entity():
    missing = require_api_key()
    if missing:
        return missing

    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Missing required parameter: name"}), 400

    url = "https://api.sam.gov/entity-information/v4/entities"
    params = {
        "api_key": API_KEY,
        "q": name,
        "includeSections": "entityRegistration,coreData",
        "size": 10
    }

    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        return jsonify({
            "error": "SAM Entity API error",
            "status": r.status_code,
            "body": r.text
        }), 502

    payload = r.json() if r.text else {}
    total = payload.get("totalRecords", 0)
    entities = [flatten_entity(e) for e in payload.get("entityData", [])]

    return jsonify({
        "query": {"name": name},
        "totalRecords": total,
        "results": entities
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
