# src/api/app.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn
from src.inference.predictor import Predictor
from datetime import datetime
import uuid

app = FastAPI(
    title="ML Pipeline Template API",
    description="ML Pipeline Template API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load predictor on startup
predictor = None

@app.on_event("startup")
async def startup_event():
    global predictor
    predictor = Predictor()

# Request/Response Models
class TargetRequest(BaseModel):
    domain: str = Field(..., description="Stock ticker (e.g. AAPL)")
    technology_stack: Optional[List[str]] = Field(default=[], description="Known technologies")
    company_name: Optional[str] = Field(default="", description="Company name")
    endpoints: Optional[List[str]] = Field(default=[], description="Known endpoints")
    auth_required: Optional[bool] = Field(default=False, description="Authentication required")
    
    class Config:
        schema_extra = {
            "example": {
                "domain": "AAPL",
                "technology_stack": ["React", "Node.js", "PostgreSQL"],
                "company_name": "Example Corp",
                "endpoints": ["/api/users", "/api/products"],
                "auth_required": True
            }
        }

class Prediction(BaseModel):
    record_type: str
    probability: float
    confidence: str
    priority: int

class AnalysisResponse(BaseModel):
    target: str
    analysis_timestamp: str
    predictions: List[Prediction]
    chain_predictions: List[Dict]
    risk_score: float
    recommendations: List[str]
    test_strategy: Dict

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "ML Pipeline Template API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "batch": "/api/v1/batch",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": predictor is not None
    }

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_target(request: TargetRequest):
    """Analyze a company and predict stock events"""
    
    try:
        target_info = request.dict()
        results = predictor.analyze_target(target_info)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batch")
async def batch_analyze(targets: List[TargetRequest], background_tasks: BackgroundTasks):
    """Analyze multiple companies at once"""
    
    job_id = str(uuid.uuid4())
    
    # Process in background
    background_tasks.add_task(process_batch, job_id, targets)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "targets_count": len(targets),
        "message": f"Batch job started with {len(targets)} targets"
    }

async def process_batch(job_id: str, targets: List[TargetRequest]):
    """Process batch analysis in background"""
    # Implementation for batch processing
    pass

@app.get("/api/v1/job/{job_id}")
async def get_job_status(job_id: str):
    """Get status of batch job"""
    # Implementation for job status
    return {"job_id": job_id, "status": "completed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
