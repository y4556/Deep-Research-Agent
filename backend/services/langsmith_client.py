from langsmith import Client
from langsmith.schemas import Run, Example
from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime
from core.config import settings

logger = logging.getLogger(__name__)

class LangSmithClient:
    """Client for LangSmith integration and monitoring"""
    
    def __init__(self):
        self.enabled = bool(settings.LANGSMITH_API_KEY and settings.LANGCHAIN_TRACING_V2)
        if self.enabled:
            self.client = Client(api_key=settings.LANGSMITH_API_KEY)
            self.project_name = settings.LANGSMITH_PROJECT
        else:
            self.client = None
            self.project_name = None
    
    async def initialize(self):
        """Initialize LangSmith client"""
        if not self.enabled:
            logger.info("🔍 LangSmith is disabled (no API key or tracing disabled)")
            return
        logger.info(f"🔍 LangSmith initialized for project: {self.project_name}")
    
    async def start_research_session(self, session_id: str, target_entity: str) -> Dict[str, Any]:
        """Start a new research session in LangSmith"""
        if not self.enabled:
            return {"session_id": session_id}
        try:
            session_data = {
                "session_id": session_id,
                "target_entity": target_entity,
                "start_time": datetime.now().isoformat(),
                "project": self.project_name
            }
            
            # Create a parent run for the entire research session
            parent_run = Run(
                name="Deep Research Session",
                run_type="chain",
                inputs={"target_entity": target_entity, "session_id": session_id},
                session_name=session_id,
                project_name=self.project_name
            )
            
            return session_data
            
        except Exception as e:
            logger.warning(f"LangSmith session start error: {e}")
            return {"session_id": session_id}
    
    async def log_node_execution(self, session_id: str, node_name: str, inputs: Dict, outputs: Dict):
        """Log node execution to LangSmith"""
        if not self.enabled:
            return
        try:
            run = Run(
                name=f"Research Node: {node_name}",
                run_type="tool",
                inputs=inputs,
                outputs=outputs,
                session_name=session_id,
                project_name=self.project_name
            )
            
            self.client.create_run(run)
            
        except Exception as e:
            logger.warning(f"LangSmith logging error for {node_name}: {e}")
    
    async def complete_research_session(self, session_id: str, final_state: Dict[str, Any]):
        """Mark research session as completed"""
        if not self.enabled:
            return
        try:
            # Log final results
            run = Run(
                name="Research Session Complete",
                run_type="chain",
                inputs={"session_id": session_id},
                outputs={"final_state": final_state},
                session_name=session_id,
                project_name=self.project_name
            )
            
            self.client.create_run(run)
            logger.info(f"✅ Research session {session_id} completed and logged to LangSmith")
            
        except Exception as e:
            logger.warning(f"LangSmith completion error: {e}")
    
    async def error_research_session(self, session_id: str, error: str):
        """Log research session error"""
        if not self.enabled:
            return
        try:
            run = Run(
                name="Research Session Error",
                run_type="chain",
                inputs={"session_id": session_id},
                outputs={"error": error},
                session_name=session_id,
                project_name=self.project_name
            )
            
            self.client.create_run(run)
            
        except Exception as e:
            logger.warning(f"LangSmith error logging error: {e}")
    
    async def cleanup(self):
        """Cleanup LangSmith client"""
        if not self.enabled:
            return
        logger.info("🧹 LangSmith client cleaned up")