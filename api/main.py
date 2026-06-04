from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from typing import Optional

app = FastAPI(title="Ujenzi API", description="Open data for journalists", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@app.get("/api/projects")
def get_projects(
    min_billion: Optional[float] = Query(None, description="Minimum budget in billions"),
    max_billion: Optional[float] = Query(None, description="Maximum budget in billions"),
    ministry: Optional[str] = Query(None, description="Ministry name (partial match)"),
    county: Optional[str] = Query(None, description="County name (partial match)"),
    status_contains: Optional[str] = Query(None, description="Filter by status keyword"),
    limit: int = Query(50, description="Max results")
):
    data = load_json("sludge_report.json")
    if not data:
        return {"error": "Data not available"}
    projects = data.get("projects", [])
    results = []
    for p in projects:
        budget_val = 0
        if p.get("allocated"):
            match = re.search(r'(\d+(?:\.\d+)?)', p["allocated"])
            if match:
                budget_val = float(match.group(1))
        if min_billion is not None and budget_val < min_billion:
            continue
        if max_billion is not None and budget_val > max_billion:
            continue
        if ministry and ministry.lower() not in p.get("ministry", "").lower():
            continue
        if county and county.lower() not in p.get("county", "").lower():
            continue
        if status_contains and status_contains.lower() not in p.get("status", "").lower():
            continue
        results.append({
            "name": p.get("name"),
            "allocated": p.get("allocated"),
            "status": p.get("status"),
            "ministry": p.get("ministry"),
            "county": p.get("county"),
            "latitude": p.get("lat"),
            "longitude": p.get("lng")
        })
        if len(results) >= limit:
            break
    return {"total": len(results), "projects": results, "source": data.get("source")}

@app.get("/api/debt")
def get_debt():
    data = load_json("bailout.json")
    if not data:
        return {"error": "Debt data not available"}
    return data

@app.get("/")
def root():
    return {"name": "Ujenzi Open API", "version": "1.0", "endpoints": ["/api/projects", "/api/debt"], "docs": "/docs"}
