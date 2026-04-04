from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.orchestrator import AIOrchestrator

# 1. Initialize the FastAPI app
app = FastAPI(
    title="Agentic Phishing API Bridge", 
    description="Backend API for real-time Chrome Extension integration.",
    version="1.0"
)

# 2. Load your existing AI brain!
print("Loading AI Orchestrator into API memory...")
orchestrator = AIOrchestrator()

# 3. Define the exact format of the data we expect to receive
class ThreatRequest(BaseModel):
    url: str
    deep_scan: bool = True

# 4. A simple health-check route to ensure the server is awake
@app.get("/")
def health_check():
    return {"status": "Online", "system": "Agentic Threat Pipeline Active"}

# 5. The Main Scanning Endpoint
@app.post("/api/v1/scan")
def scan_target(request: ThreatRequest):
    try:
        # We simply pass the URL to the exact same orchestrator we built for the UI!
        result = orchestrator.run_detection(
            url=request.url,
            deep_scan=request.deep_scan
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend Engine Error: {str(e)}")