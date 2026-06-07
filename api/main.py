from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import re
import os
from typing import Optional

print("🚀 Loading Ujenzi API...")

app = FastAPI(title="Ujenzi API", description="Open data for journalists", version="1.0")
print("✅ Ujenzi API starting up...")
@app.on_event("startup")
async def startup_event():
    print("✅ API ready, endpoints registered: /, /docs, /api/projects, /api/debt")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

print("✅ FastAPI app created")

def load_json(filename):
    """Load JSON from the root directory (where sludge_report.json and bailout.json live)"""
    # Try current directory first (Render root)
    if os.path.exists(filename):
        print(f"✅ Found {filename} in current directory")
        with open(filename, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    # Try parent directory (if running from inside api folder)
    parent_path = os.path.join("..", filename)
    if os.path.exists(parent_path):
        print(f"✅ Found {filename} in parent directory")
        with open(parent_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    print(f"❌ Could not find {filename}")
    return None

@app.get("/test")
def test():
    """Test endpoint to verify API is running"""
    return {"status": "API is alive", "message": "Ujenzi API is working"}

@app.get("/api/projects")
def get_projects(
    min_billion: Optional[float] = Query(None, description="Minimum budget in billions"),
    max_billion: Optional[float] = Query(None, description="Maximum budget in billions"),
    ministry: Optional[str] = Query(None, description="Ministry name (partial match)"),
    county: Optional[str] = Query(None, description="County name (partial match)"),
    status_contains: Optional[str] = Query(None, description="Filter by status keyword"),
    limit: int = Query(50, description="Max results")
):
    print("📍 /api/projects endpoint called")
    data = load_json("sludge_report.json")
    if not data:
        return {"error": "sludge_report.json not found. Please ensure the file exists in the root directory."}
    
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
    print("📍 /api/debt endpoint called")
    data = load_json("bailout.json")
    if not data:
        return {"error": "bailout.json not found. Please ensure the file exists in the root directory."}
    return data

@app.get("/")
def root():
    print("📍 / endpoint called")
    return {
        "name": "Ujenzi Open API", 
        "version": "1.0", 
        "endpoints": [
            "/test", 
            "/api/projects", 
            "/api/debt", 
            "/docs"
        ]
    }

print("✅ Ujenzi API ready to start")