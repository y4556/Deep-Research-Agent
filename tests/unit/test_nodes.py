import pytest
from backend.core.nodes import (
    ResearchPlanner,
    QueryGenerator,
    FactExtractor,
    SourceValidator,
    ConnectionMapper,
    RiskAssessor,
    ResearchReflector,
    ReportSynthesizer
)
from backend.core.state import ResearchState

@pytest.mark.asyncio
async def test_research_planner():
    """Test ResearchPlanner node"""
    planner = ResearchPlanner()
    
    initial_state: ResearchState = {
        "target_entity": "John Doe",
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
    
    result = await planner.execute(initial_state)
    
    assert "research_plan" in result
    assert len(result["research_plan"]) > 0
    assert result["research_depth"] == 1


@pytest.mark.asyncio
async def test_fact_extractor_parsing():
    """Test fact extraction and parsing"""
    extractor = FactExtractor()
    
    test_text = """
    - John Doe is CEO of TechCorp since 2020 (Confidence: 0.9)
    - Previously worked at Google as Senior Engineer (Confidence: 0.85)
    - Holds MBA from Harvard Business School (Confidence: 0.95)
    """
    
    facts = extractor._parse_facts(test_text, "https://example.com")
    
    assert isinstance(facts, list)
    assert len(facts) > 0
    for fact in facts:
        assert "id" in fact
        assert "content" in fact
        assert "category" in fact
        assert "confidence" in fact


def test_parse_research_plan():
    """Test research plan parsing"""
    planner = ResearchPlanner()
    
    test_plan = """
    PHASE 1: Core Investigation
    - Biographical data verification
    - Professional credentials
    
    PHASE 2: Financial Analysis
    - Company affiliations
    - Investment patterns
    """
    
    parsed = planner._parse_research_plan(test_plan)
    
    assert isinstance(parsed, list)
    assert len(parsed) > 0


def test_query_generator_parsing():
    """Test query parsing"""
    generator = QueryGenerator()
    
    test_queries = """
    1. "John Doe CEO TechCorp"
    2. "John Doe LinkedIn profile"
    3. "TechCorp SEC filings John Doe"
    """
    
    queries = generator._parse_queries(test_queries)
    
    assert isinstance(queries, list)
    assert len(queries) > 0
    assert all(len(q) > 10 for q in queries)


# Add more tests for other nodes

