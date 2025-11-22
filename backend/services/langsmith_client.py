from langsmith import Client
from langsmith.schemas import Run, Example
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from core.config import settings

class LangSmithClient:
    """Client for LangSmith integration and monitoring"""
    
    def __init__(self):
        self.client = Client(
            api_key=settings.LANGSMITH_API_KEY
        )
        self.project_name = settings.LANGSMITH_PROJECT
    
    async def initialize(self):
        """Initialize LangSmith client"""
        print(f"🔍 LangSmith initialized for project: {self.project_name}")
    
    async def start_research_session(self, session_id: str, target_entity: str) -> Dict[str, Any]:
        """Start a new research session in LangSmith"""
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
            print(f"LangSmith session start error: {e}")
            return {"session_id": session_id}
    
    async def log_node_execution(self, session_id: str, node_name: str, inputs: Dict, outputs: Dict):
        """Log node execution to LangSmith"""
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
            print(f"LangSmith logging error for {node_name}: {e}")
    
    async def complete_research_session(self, session_id: str, final_state: Dict[str, Any]):
        """Mark research session as completed"""
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
            print(f"✅ Research session {session_id} completed and logged to LangSmith")
            
        except Exception as e:
            print(f"LangSmith completion error: {e}")
    
    async def error_research_session(self, session_id: str, error: str):
        """Log research session error"""
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
            print(f"LangSmith error logging error: {e}")
    
    async def cleanup(self):
        """Cleanup LangSmith client"""
        print("🧹 LangSmith client cleaned up")