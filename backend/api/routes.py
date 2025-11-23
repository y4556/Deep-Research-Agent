from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import logging
from datetime import datetime

from core.graph import ResearchWorkflow
from core.state import ResearchReport
from utils.log_handler import get_session_handler

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for research sessions
research_sessions = {}

# Get global log handler
log_handler = get_session_handler()

class ResearchRequest(BaseModel):
    target_entity: str
    max_depth: int = 3
    research_focus: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None

class ResearchResponse(BaseModel):
    session_id: str
    status: str
    message: str
    report: Optional[Dict[str, Any]] = None
    progress: float = 0.0
    estimated_completion: Optional[str] = None

class ResearchStatus(BaseModel):
    session_id: str
    status: str
    progress: float
    current_step: Optional[str] = None
    findings_count: int = 0
    risks_identified: int = 0

@router.post("/research/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new deep research session"""
    session_id = str(uuid.uuid4())
    
    research_sessions[session_id] = {
        "status": "initializing",
        "progress": 0.0,
        "request": request.dict(),
        "report": None,
        "start_time": datetime.now().isoformat(),
        "current_step": "planning"
    }
    
    # Start research in background
    background_tasks.add_task(execute_research_background, session_id, request)
    
    return ResearchResponse(
        session_id=session_id,
        status="started",
        message=f"Research started for {request.target_entity}",
        progress=0.0
    )

@router.get("/research/status/{session_id}", response_model=ResearchStatus)
async def get_research_status(session_id: str):
    """Get status of a research session"""
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    session = research_sessions[session_id]
    
    return ResearchStatus(
        session_id=session_id,
        status=session["status"],
        progress=session["progress"],
        current_step=session.get("current_step"),
        findings_count=len(session.get("report", {}).get("key_findings", []) if session.get("report") else []),
        risks_identified=len(session.get("report", {}).get("risk_assessment", []) if session.get("report") else [])
    )

@router.get("/research/report/{session_id}", response_model=ResearchReport)
async def get_research_report(session_id: str):
    """Get completed research report"""
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    session = research_sessions[session_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Research not completed yet")
    
    return session["report"]

@router.get("/research/logs/{session_id}")
async def get_research_logs(session_id: str, last_n: Optional[int] = 50):
    """Get backend logs for a research session"""
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    logs = log_handler.get_logs(session_id, last_n=last_n)
    
    return {
        "session_id": session_id,
        "logs": logs,
        "total_logs": len(logs)
    }

@router.get("/research/sessions", response_model=List[Dict[str, Any]])
async def list_research_sessions():
    """List all research sessions"""
    return [
        {
            "session_id": session_id,
            "target_entity": data["request"]["target_entity"],
            "status": data["status"],
            "progress": data["progress"],
            "start_time": data["start_time"]
        }
        for session_id, data in research_sessions.items()
    ]

@router.delete("/research/{session_id}")
async def cancel_research(session_id: str):
    """Cancel a research session"""
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    research_sessions[session_id]["status"] = "cancelled"
    return {"message": "Research session cancelled"}

async def execute_research_background(session_id: str, request: ResearchRequest):
    """Execute research in background and update session status"""
    # Set session for log routing
    log_handler.set_session(session_id)
    
    try:
        logger.info("#"*80)
        logger.info(f"🚀 STARTING RESEARCH SESSION: {session_id}")
        logger.info(f"🎯 Target: {request.target_entity}")
        logger.info(f"📊 Max Depth: {request.max_depth}")
        logger.info(f"🔍 Focus: {request.research_focus}")
        logger.info("#"*80)
        
        workflow = ResearchWorkflow()
        
        # Update session status
        research_sessions[session_id].update({
            "status": "researching",
            "progress": 25.0
        })
        
        # Execute research
        final_state = await workflow.conduct_research(
            target_entity=request.target_entity,
            max_depth=request.max_depth,
            research_focus=request.research_focus,
            **(request.additional_context or {})
        )
        
        # Generate report
        report = generate_research_report(final_state)
        
        # Update session with results
        research_sessions[session_id].update({
            "status": "completed",
            "progress": 100.0,
            "report": report,
            "completion_time": datetime.now().isoformat()
        })
        
        logger.info("#"*80)
        logger.info(f"✅ RESEARCH COMPLETED: {session_id}")
        logger.info("#"*80)
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error("#"*80)
        logger.error(f"❌ RESEARCH ERROR: {session_id}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{error_traceback}")
        logger.error("#"*80)
        
        research_sessions[session_id].update({
            "status": "error",
            "error": str(e),
            "progress": 0.0
        })

def generate_research_report(final_state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive research report from final state"""
    
    # Extract risk assessment and group by severity
    risks_flagged = final_state.get("risks_flagged", [])
    risk_assessment_dict = {
        "critical_risks": [],
        "high_risks": [],
        "medium_risks": [],
        "low_risks": [],
        "overall_risk_level": "low"
    }
    
    # Group risks by severity
    for risk in risks_flagged:
        severity = risk.get("severity", "low").lower()
        if severity == "critical":
            risk_assessment_dict["critical_risks"].append(risk)
        elif severity == "high":
            risk_assessment_dict["high_risks"].append(risk)
        elif severity == "medium":
            risk_assessment_dict["medium_risks"].append(risk)
        else:
            risk_assessment_dict["low_risks"].append(risk)
    
    # Determine overall risk level
    if len(risk_assessment_dict["critical_risks"]) > 0:
        risk_assessment_dict["overall_risk_level"] = "critical"
    elif len(risk_assessment_dict["high_risks"]) > 0:
        risk_assessment_dict["overall_risk_level"] = "high"
    elif len(risk_assessment_dict["medium_risks"]) > 0:
        risk_assessment_dict["overall_risk_level"] = "medium"
    else:
        risk_assessment_dict["overall_risk_level"] = "low"
    
    # Extract executive summary and narrative from final report
    final_report = final_state.get("final_report", {})
    if isinstance(final_report, dict):
        executive_summary = final_report.get("executive_summary", "Comprehensive research report generated by Deep Research AI Agent")
        entity_narrative = final_report.get("entity_narrative", "")
    else:
        executive_summary = str(final_report)
        entity_narrative = ""
    
    # Extract metadata with proper calculations
    verified_facts = final_state.get("verified_facts", [])
    total_verified = sum(1 for f in verified_facts if isinstance(f, dict) and f.get("verified", False))
    
    # Calculate average confidence
    confidences = [f.get("confidence", 0) for f in verified_facts if isinstance(f, dict) and "confidence" in f]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    high_confidence_facts = sum(1 for c in confidences if c >= 0.8)
    
    return {
        "session_id": final_state.get("research_session_id", "unknown"),
        "target_entity": final_state["target_entity"],
        "executive_summary": executive_summary,
        "entity_narrative": entity_narrative,  # NEW: Complete chronological story
        "key_findings": verified_facts,
        "risk_assessment": risk_assessment_dict,  # Now a properly formatted dict!
        "connection_network": final_state.get("connections", []),
        "confidence_scores": final_state.get("confidence_scores", {}),
        "research_metadata": {
            "search_queries_used": final_state.get("search_queries", []),
            "sources_consulted": len(final_state.get("raw_search_results", [])),
            "research_depth": final_state.get("research_depth", 0),
            "total_facts_discovered": len(verified_facts),
            "total_verified_facts": total_verified,
            "total_risks": len(risks_flagged),
            "total_connections": len(final_state.get("connections", [])),
            "total_queries_executed": len(final_state.get("search_queries", [])),
            "average_confidence": avg_confidence,
            "high_confidence_facts": high_confidence_facts,
            "start_time": final_state.get("start_time"),
            "completion_time": datetime.now().isoformat()
        },
        "confidence_assessment": {
            "average_confidence": avg_confidence,
            "verified_ratio": total_verified / len(verified_facts) if verified_facts else 0,
            "high_confidence_ratio": high_confidence_facts / len(verified_facts) if verified_facts else 0
        },
        "generated_at": datetime.now().isoformat()
    }