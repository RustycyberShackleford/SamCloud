
import base64, os, time, datetime as dt
from flask import Flask, render_template, request, jsonify, send_file, flash
from dotenv import load_dotenv
from sam_api import search_opportunities_by_naics, search_entities_by_name
from sam_api import SamApiError

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/search")
def search():
    search_type = request.form.get("searchType","entity_name")
    query = request.form.get("query","").strip()
    demo = os.getenv("DEMO_MODE","true").lower() == "true"
    api_key = os.getenv("SAM_API_KEY","").strip()

    context = {"query": query, "demo": demo, "search_type": search_type, "live": False, "error": None}

    try:
        if not demo and api_key:
            if search_type == "entity_name":
                context["entity_results"] = search_entities_by_name(query, api_key)
                context["opportunity_results"] = []
            else:
                days_back = int(os.getenv("OPPS_DAYS_BACK","30"))
                limit = int(os.getenv("OPPS_LIMIT","25"))
                context["opportunity_results"] = search_opportunities_by_naics(query, api_key, days_back=days_back, limit=limit)
                context["entity_results"] = []
            context["live"] = True
        else:
            # Fallback demo
            if search_type == "entity_name":
                from sam_demo import demo_entity_results
                context["entity_results"] = demo_entity_results(query)
                context["opportunity_results"] = []
            else:
                from sam_demo import demo_opportunities_by_naics
                context["opportunity_results"] = demo_opportunities_by_naics(query)
                context["entity_results"] = []
    except SamApiError as e:
        context["error"] = str(e)
    except Exception as e:
        context["error"] = f"Unexpected error: {e}"

    return render_template("results.html", **context)

@app.post("/capture")
def capture():
    import base64, os, time
    from flask import request, jsonify
    data_url = request.form.get("imageData","")
    name = request.form.get("name","query").strip().replace(" ", "_")
    if not data_url.startswith("data:image/png;base64,"):
        return jsonify({"ok": False, "error": "Invalid image data"}), 400
    b64 = data_url.split(",",1)[1]
    raw = base64.b64decode(b64)
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"samgov_result_{name}_{ts}.png"
    path = os.path.join("/tmp", fname)
    with open(path, "wb") as f:
        f.write(raw)
    return jsonify({"ok": True, "filename": fname})

@app.get("/download/<path:fname>")
def download(fname):
    full = os.path.join("/tmp", fname)
    if not os.path.exists(full):
        return "Not found", 404
    return send_file(full, mimetype="image/png", as_attachment=True, download_name=fname)

@app.get("/files")
def list_files():
    entries = []
    for fn in os.listdir("/tmp"):
        p = os.path.join("/tmp", fn)
        if os.path.isfile(p):
            entries.append({"name": fn, "bytes": os.path.getsize(p)})
    return {"files": entries}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
