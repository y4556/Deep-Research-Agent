import pytest
from backend.services.search import DeepSearchEngine

def test_search_engine_initialization():
    """Test search engine initialization"""
    engine = DeepSearchEngine()
    
    assert engine.tavily_tool is not None
    assert engine.ddg_search is not None


def test_tavily_results_processing():
    """Test processing of Tavily search results"""
    engine = DeepSearchEngine()
    
    mock_results = [
        {
            "title": "Test Article",
            "content": "Test content about research",
            "url": "https://example.com/article"
        }
    ]
    
    processed = engine._process_tavily_results(mock_results, "test query")
    
    assert len(processed) == 1
    assert processed[0]["title"] == "Test Article"
    assert processed[0]["query"] == "test query"
    assert processed[0]["source"] == "tavily"
    assert "confidence" in processed[0]


# Note: Actual search tests would require API keys or mocking
# These are basic structural tests

