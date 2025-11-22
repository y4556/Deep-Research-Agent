import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.integration
def test_start_research_endpoint():
    """Test research start endpoint"""
    pytest.skip("Integration test - requires full backend setup")
    
    response = client.post(
        "/api/v1/research/start",
        json={
            "target_entity": "Test Person",
            "max_depth": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "status" in data


@pytest.mark.integration
def test_list_sessions_endpoint():
    """Test list sessions endpoint"""
    pytest.skip("Integration test - requires full backend setup")
    
    response = client.get("/api/v1/research/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

