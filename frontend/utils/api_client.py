import requests
from typing import Dict, Any, List, Optional
import streamlit as st

class ResearchAPIClient:
    """
    Client for interacting with the Deep Research Agent API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """Handle API response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected Error: {e}")
            return None
    
    def start_research(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Start a new research session
        
        Args:
            request_data: Dictionary containing:
                - target_entity: str (required)
                - max_depth: int (optional, default=3)
                - research_focus: str (optional)
                - additional_context: dict (optional)
        
        Returns:
            Response dict with session_id and status
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/start"
            response = requests.post(
                url,
                json=request_data,
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except Exception as e:
            st.error(f"Error starting research: {e}")
            return None
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a research session
        
        Args:
            session_id: Session ID to query
        
        Returns:
            Status dict with progress, current_step, findings_count, etc.
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/status/{session_id}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error fetching status: {e}")
            return None
    
    def get_research_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get completed research report
        
        Args:
            session_id: Session ID to query
        
        Returns:
            Complete research report dict
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/report/{session_id}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error fetching report: {e}")
            return None
    
    def get_session_logs(self, session_id: str, last_n: int = 50) -> Optional[Dict[str, Any]]:
        """
        Get backend logs for a research session
        
        Args:
            session_id: Session ID to query
            last_n: Number of recent logs to retrieve
        
        Returns:
            Dict with logs list
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/logs/{session_id}?last_n={last_n}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            # Don't show error for logs, just fail silently
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all research sessions
        
        Returns:
            List of session summaries
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/sessions"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            result = self._handle_response(response)
            return result if result else []
        except Exception as e:
            st.error(f"Error listing sessions: {e}")
            return []
    
    def cancel_research(self, session_id: str) -> bool:
        """
        Cancel a research session
        
        Args:
            session_id: Session ID to cancel
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}{self.api_prefix}/research/{session_id}"
            response = requests.delete(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error cancelling research: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if API is healthy
        
        Returns:
            True if API is responding, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
