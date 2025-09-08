# SAM.gov Search (Live API Ready) — v5

Works in two modes:

- **Demo** (`DEMO_MODE=true`) — synthetic results; no API key needed.
- **Live** (`DEMO_MODE=false`) — calls SAM.gov **Get Opportunities v2** and **Entity Information v4** with your `SAM_API_KEY`.

## 1) Where to get an API key
- Log into **SAM.gov** → Profile → **Account Details** → **Public API Key** (requires OTP).  
  Docs: open.gsa.gov (Get Opportunities) and Entity Management API pages.

## 2) Environment
- `DEMO_MODE=false`
- `SAM_API_KEY=<your key>`
- Optional: `OPPS_DAYS_BACK` (default 30), `OPPS_LIMIT` (default 25)

## 3) Live Endpoints Used
- Opportunities v2 (Production): `https://api.sam.gov/opportunities/v2/search`
  - Required: `postedFrom`, `postedTo` (mm/dd/yyyy), `api_key`
  - Filters we pass: `ncode` (NAICS), `ptype` (optional), `limit`, `offset`
- Entity Information v4 (Production): `https://api.sam.gov/entity-information/v4/entities`
  - Common params: `legalBusinessName`, `samRegistered=Yes`, `includeSections=entityRegistration,coreData`
  - `api_key` required

> Date range max is **1 year** for opportunities. We default to last **30 days** unless you override via `OPPS_DAYS_BACK`.

## 4) Run Locally
```
pip install -r requirements.txt
cp .env.example .env
# edit .env to DEMO_MODE=false and set SAM_API_KEY
python webapp.py
```

## 5) Deploy on Render (Dockerfile)
- Environment:
  - `DEMO_MODE=false`
  - `SAM_API_KEY=...`
  - *(keep your existing secret files if using Google Drive later — not required here)*

## 6) Routes
- `GET /` → form
- `POST /search` → live calls if enabled
- `POST /capture` → save PNG to /tmp
- `GET /download/<file>` → download
- `GET /files` → list /tmp
- `GET /healthz` → ok

## 7) Notes
- If rate-limited or the key is missing/invalid, the app will fall back to demo data and show a banner message.
