# main.py — NYC DRAMA LIVE v2.0
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime, timedelta

app = FastAPI(title="NYC DRAMA LIVE")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_complaints(borough=None, limit=50):
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    params = {
        "$limit": limit,
        "$order": "created_date DESC"
    }
    if borough and borough != "ALL":
        params["borough"] = borough
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except:
        return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, borough: str = "ALL"):
    complaints = get_complaints(borough)
    drama = []
    for c in complaints[:20]:
        desc = c.get("descriptor", "ТАЙНА")
        addr = c.get("incident_address", "СЕКРЕТНОЕ МЕСТО")
        boro = c.get("borough", "NYC")
        time = c.get("created_date", "")[11:16]
        drama.append(f"{desc} — {addr} ({boro}) [{time}]")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "drama": drama,
        "total": len(complaints),
        "borough": borough
    })

@app.get("/api/drama")
async def api_drama(borough: str = "ALL"):
    complaints = get_complaints(borough, 10)
    return {"drama": [f"{c.get('descriptor')} — {c.get('incident_address')}" for c in complaints]}