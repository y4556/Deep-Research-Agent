from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import add_messages
import operator
from datetime import datetime
from pydantic import BaseModel

class ResearchState(TypedDict):
    # Core Research Data
    target_entity: str
    research_plan: List[str]
    search_queries: List[str]
    raw_search_results: List[Dict[str, Any]]
    extracted_facts: List[Dict[str, Any]]
    verified_facts: List[Dict[str, Any]]
    risks_flagged: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    
    # Control Flow
    research_depth: int
    next_step: str  # "REFINE_QUERY", "FINALIZE", "DEEP_DIVE"
    knowledge_gaps: List[str]
    current_focus: str
    max_depth: int
    
    # Multi-Model Context
    model_decisions: Dict[str, Any]
    research_session_id: str
    start_time: str
    
    # LangSmith Tracing
    langsmith_session_id: Optional[str]

class Fact(BaseModel):
    id: str
    content: str
    category: str
    sources: List[str]
    confidence: float
    timestamp: str
    verified: bool = False

class RiskFlag(BaseModel):
    id: str
    type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    evidence: List[str]
    confidence: float
    impact: str

class Connection(BaseModel):
    source: str
    target: str
    relationship: str
    strength: float
    evidence: List[str]

class ResearchReport(BaseModel):
    session_id: str
    target_entity: str
    executive_summary: str
    key_findings: List[Fact]
    risk_assessment: Dict[str, Any]  # Changed from List[RiskFlag] to Dict to support frontend structure
    connection_network: List[Connection]
    confidence_scores: Dict[str, float]
    research_metadata: Dict[str, Any]
    confidence_assessment: Optional[Dict[str, float]] = None  # Added for confidence metrics
    generated_at: str