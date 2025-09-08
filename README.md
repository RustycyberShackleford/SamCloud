# SAM Mini API Demo (Flask)

This demo exposes **two endpoints** backed by the **official SAM.gov APIs**:

- `GET /search_opportunities` — query **Contract Opportunities** by **NAICS** and date window (≤ 1-year span).
- `GET /search_entity` — search **Entity Information** by name (returns UEI, status, NAICS associations, addresses, etc.).

The app requires one environment variable: **`sam_api_key`**.

---

## 1) Get Your SAM Public API Key

1. Go to https://sam.gov
2. Click **Sign In** (authenticate via login.gov).
3. After you’re back on SAM.gov, click your **name (top-right) → Account Details**.
4. Scroll to **API Keys** → **Create New Key**.
5. Copy the generated key.

> You do **not** need to register an entity to get a public API key.

---

## 2) Configure Your Environment Variable

### macOS / Linux (temporary for current shell)
```bash
export sam_api_key="PASTE_YOUR_KEY_HERE"
```

### Windows (PowerShell)
```powershell
$env:sam_api_key="PASTE_YOUR_KEY_HERE"
```

### Windows (cmd)
```bat
set sam_api_key=PASTE_YOUR_KEY_HERE
```

### Optional: `.env` (local only)
Create a file named `.env` in the project root:
```
sam_api_key=PASTE_YOUR_KEY_HERE
```
> `.env` is for local only—don’t commit real keys.

If using `.env`, it’s already supported via `python-dotenv` in `app.py`.

---

## 3) Install & Run (Local)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000/healthz` → should return `{"ok": true}`.

---

## 4) Try the Endpoints

### A) Contract Opportunities (NAICS)
**Dates must be MM/DD/YYYY and within a 1-year range.**
```bash
curl "http://localhost:5000/search_opportunities?naics=115310&from=06/10/2025&to=09/07/2025&limit=10&offset=0"
```
- `naics` — required (e.g., `115310` Forestry Support Services)
- `from` / `to` — required (MM/DD/YYYY, ≤ 1-year span)
- `limit` — optional (1–1000; default 50)
- `offset` — optional (default 0)

**Response:** fields are flattened and include `title`, `solicitationNumber`, `noticeType`, `postedDate`, `responseDeadLine`, `naics`, `setAside`, `agency`, `office`, `placeOfPerformance`, and `links`.

### B) Entity Search (by name)
```bash
curl "http://localhost:5000/search_entity?name=California%20Forestry%20Mitigation"
```
**Response:** simplified array with `legalBusinessName`, `ueiSAM`, `cageCode`, `registrationStatus`, `registrationExpirationDate`, addresses, and `naics` list.

---

## 5) Deploying on Render (or any PaaS)

- In your service settings → **Environment** → **Environment Variables**:
  - Key: `sam_api_key`
  - Value: `PASTE_YOUR_KEY_HERE`
- Start command (Render/Heroku/etc):
  - `gunicorn app:app --preload -b 0.0.0.0:$PORT`

**Procfile:**
```
web: gunicorn app:app --preload -b 0.0.0.0:$PORT
```

---

## 6) Notes & Gotchas

- **Date window**: SAM Opportunities API enforces a **≤ 1-year** posted date range.
- **Rate limits**: Public keys have daily request limits; design with pagination and caching.
- **No scraping**: Use official APIs. The UI “uiLink” in results may require roles; rely on API data.
- **Security**: Do not hardcode your API key; keep it in `sam_api_key`.

---

## 7) Extending This

- Add CSV/PDF export (for “screenshot-like” artifacts).
- Push files to Google Drive using a service account & Drive API.
- Add filters: `ptype` (notice type), `state`, `zip`, `typeOfSetAside`.
