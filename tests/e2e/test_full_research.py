import pytest
import asyncio
from backend.core.graph import ResearchWorkflow

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_research_cycle():
    """
    End-to-end test of complete research cycle
    Requires all API keys and services to be running
    """
    pytest.skip("E2E test - requires full environment and API keys")
    
    workflow = ResearchWorkflow()
    
    # Run full research on a test entity
    result = await workflow.conduct_research(
        target_entity="Test Entity - Known Person",
        max_depth=3
    )
    
    # Verify all expected outputs
    assert result is not None
    assert len(result.get("verified_facts", [])) > 0
    assert len(result.get("search_queries", [])) > 0
    assert result.get("research_depth", 0) >= 3
    
    # Check report generation
    assert "final_report" in result
    report = result["final_report"]
    
    assert "executive_summary" in report
    assert "key_findings_by_category" in report
    assert "risk_assessment" in report
    assert "connection_network" in report


@pytest.mark.e2e
def test_api_to_frontend_integration():
    """Test full stack integration from API to frontend"""
    pytest.skip("E2E test - requires both backend and frontend running")
    
    # This would test:
    # 1. Frontend starts research via API
    # 2. Backend processes research
    # 3. Frontend polls for updates
    # 4. Frontend displays results
    pass

