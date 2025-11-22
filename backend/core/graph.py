from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Dict, Any
import uuid
from datetime import datetime

from .state import ResearchState
from .nodes import (
    ResearchPlanner,
    QueryGenerator,
    DeepSearchExecutor, 
    FactExtractor,
    SourceValidator,
    ConnectionMapper,
    RiskAssessor,
    ResearchReflector,
    ReportSynthesizer
)
from services.langsmith_client import LangSmithClient

class ResearchWorkflow:
    """Main LangGraph workflow for deep research"""
    
    def __init__(self):
        self.graph = self._build_workflow()
        self.langsmith_client = LangSmithClient()
    
    def _build_workflow(self) -> StateGraph:
        """Build the complete research workflow"""
        workflow = StateGraph(ResearchState)
        
        # Initialize nodes
        nodes = {
            "planner": ResearchPlanner(),
            "query_generator": QueryGenerator(),
            "search_executor": DeepSearchExecutor(),
            "fact_extractor": FactExtractor(),
            "source_validator": SourceValidator(),
            "connection_mapper": ConnectionMapper(),
            "risk_assessor": RiskAssessor(),
            "research_reflector": ResearchReflector(),
            "report_synthesizer": ReportSynthesizer()
        }
        
        # Add all nodes to the graph
        for name, node in nodes.items():
            workflow.add_node(name, node.execute)
        
        # Define the workflow edges
        workflow.set_entry_point("planner")
        
        # Main research flow
        workflow.add_edge("planner", "query_generator")
        workflow.add_edge("query_generator", "search_executor")
        workflow.add_edge("search_executor", "fact_extractor")
        workflow.add_edge("fact_extractor", "source_validator")
        workflow.add_edge("source_validator", "connection_mapper")
        workflow.add_edge("connection_mapper", "risk_assessor")
        
        # Conditional routing based on research progress
        workflow.add_conditional_edges(
            "risk_assessor",
            self._should_continue_research,
            {
                "continue": "research_reflector",
                "deep_dive": "research_reflector",
                "finalize": "report_synthesizer"
            }
        )
        
        # Reflection leads back to query generation with new context
        workflow.add_edge("research_reflector", "query_generator")
        workflow.add_edge("report_synthesizer", END)
        
        return workflow.compile()
    
    def _should_continue_research(self, state: ResearchState) -> str:
        """Determine if research should continue, dive deeper, or finalize"""
        depth = state.get("research_depth", 0)
        max_depth = state.get("max_depth", 3)
        
        # Check depth limits
        if depth >= max_depth:
            return "finalize"
        
        # Check if we're still finding new information
        recent_facts = state.get("extracted_facts", [])[-5:]
        if not recent_facts or len(recent_facts) < 2:
            return "finalize"
        
        # Check knowledge gaps for deep diving
        gaps = state.get("knowledge_gaps", [])
        high_priority_gaps = [gap for gap in gaps if "high" in gap.lower() or "critical" in gap.lower()]
        
        if high_priority_gaps and depth < max_depth - 1:
            return "deep_dive"
        
        # Default to continue if we're making progress
        if depth < 2 or len(recent_facts) >= 3:
            return "continue"
        
        return "finalize"
    
    async def conduct_research(self, target_entity: str, max_depth: int = 3, **kwargs) -> Dict[str, Any]:
        """Execute the complete research workflow"""
        research_session_id = str(uuid.uuid4())
        
        initial_state: ResearchState = {
            "target_entity": target_entity,
            "research_plan": [],
            "search_queries": [],
            "raw_search_results": [],
            "extracted_facts": [],
            "verified_facts": [],
            "risks_flagged": [],
            "connections": [],
            "confidence_scores": {},
            "research_depth": 0,
            "next_step": "plan",
            "knowledge_gaps": [],
            "current_focus": "comprehensive",
            "model_decisions": {},
            "max_depth": max_depth,
            "research_session_id": research_session_id,
            "start_time": datetime.now().isoformat(),
            "langsmith_session_id": None,
            **kwargs
        }
        
        # Start LangSmith session
        langsmith_session = await self.langsmith_client.start_research_session(
            research_session_id, 
            target_entity
        )
        initial_state["langsmith_session_id"] = langsmith_session.get("session_id")
        
        try:
            # Execute the research graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Log completion to LangSmith
            await self.langsmith_client.complete_research_session(
                research_session_id,
                final_state
            )
            
            return final_state
            
        except Exception as e:
            # Log error to LangSmith
            await self.langsmith_client.error_research_session(
                research_session_id,
                str(e)
            )
            raise e