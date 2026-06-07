# app.py

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from llm_client import ParrotLLMClient

app = FastAPI(title="Parrot-LLM Intelligence Service", version="1.0.0")

# Enable CORS for Flutter Web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM Client
llm_client = ParrotLLMClient()

# Request Models
class LiveAdviceRequest(BaseModel):
    telemetry: Dict[str, Any] = Field(..., description="Real-time patient telemetry dictionary")
    transcript: str = Field(..., description="Accumulated transcript of the consultation")
    session_duration_seconds: int = Field(0, description="Duration in seconds since session start")

class ObservationItem(BaseModel):
    timestamp: str
    category: str
    description: str
    impactScore: float
    isPositive: bool

class SessionSummaryRequest(BaseModel):
    session_duration_seconds: int = Field(..., description="Total consultation duration in seconds")
    transcript: str = Field(..., description="Full consultation transcript")
    observations: List[ObservationItem] = Field(default=[], description="List of recorded observations")
    telemetry_summary: Dict[str, Any] = Field(default={}, description="Aggregated metrics summary")

@app.get("/health")
def health_check():
    """Health check endpoint to verify LLM server and Groq client status."""
    return {
        "status": "healthy",
        "service": "Parrot-LLM",
        "groq_configured": llm_client.client is not None
    }

@app.post("/advice")
def post_live_advice(request: LiveAdviceRequest):
    """
    Receives current telemetry + transcript and returns dynamic clinical advice 
    and recommended probing questions.
    """
    try:
        advice_res = llm_client.get_live_advice(
            telemetry=request.telemetry,
            transcript=request.transcript,
            session_duration=request.session_duration_seconds
        )
        return advice_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summary")
def post_session_summary(request: SessionSummaryRequest):
    """
    Receives full session transcript, telemetry summary, and observations checklist 
    and returns a structured post-session clinical summary.
    """
    try:
        summary_res = llm_client.get_session_summary(
            session_duration=request.session_duration_seconds,
            transcript=request.transcript,
            observations=[obs.dict() for obs in request.observations],
            telemetry_summary=request.telemetry_summary
        )
        return summary_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run server on port 8001
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
