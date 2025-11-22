import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

@pytest.fixture
def sample_research_state():
    """Fixture providing a sample research state"""
    return {
        "target_entity": "Test Entity",
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
        "max_depth": 3,
        "research_session_id": "test-session",
        "start_time": "2024-01-01T00:00:00",
        "langsmith_session_id": None
    }


@pytest.fixture
def sample_facts():
    """Fixture providing sample facts"""
    return [
        {
            "id": "fact_1",
            "content": "John Doe is CEO of TechCorp",
            "category": "professional",
            "sources": ["https://example.com"],
            "confidence": 0.9,
            "verified": True
        },
        {
            "id": "fact_2",
            "content": "Previously worked at Google",
            "category": "professional",
            "sources": ["https://linkedin.com"],
            "confidence": 0.85,
            "verified": True
        }
    ]


@pytest.fixture
def sample_risks():
    """Fixture providing sample risks"""
    return [
        {
            "id": "risk_1",
            "type": "legal",
            "severity": "high",
            "description": "Pending lawsuit",
            "confidence": 0.8,
            "evidence": ["Court filing"]
        }
    ]

