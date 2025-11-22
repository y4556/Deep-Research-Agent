from langchain_community.tools import TavilySearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from typing import List, Dict, Any
import asyncio
from core.config import settings

class DeepSearchEngine:
    """Integrates multiple search engines for comprehensive research"""
    
    def __init__(self):
        self.tavily_tool = TavilySearchResults(
            max_results=3,
            api_key=settings.TAVILY_API_KEY
        )
        self.ddg_search = DuckDuckGoSearchAPIWrapper()
    
    async def execute_deep_search(self, query: str, target_entity: str) -> List[Dict[str, Any]]:
        """Execute search using multiple engines"""
        all_results = []
        
        try:
            # Tavily Search (primary)
            tavily_results = await asyncio.get_event_loop().run_in_executor(
                None, self.tavily_tool.invoke, {"query": f"{query} {target_entity}"}
            )
            all_results.extend(self._process_tavily_results(tavily_results, query))
            
        except Exception as e:
            print(f"Tavily search error: {e}")
        
        try:
            # DuckDuckGo as fallback
            ddg_results = await asyncio.get_event_loop().run_in_executor(
                None, self.ddg_search.run, f"{query} {target_entity}"
            )
            all_results.extend(self._process_ddg_results(ddg_results, query))
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return all_results
    
    def _process_tavily_results(self, results: List[Dict], query: str) -> List[Dict[str, Any]]:
        """Process Tavily search results"""
        processed = []
        for result in results:
            processed.append({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "query": query,
                "source": "tavily",
                "confidence": 0.8,
                "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp
            })
        return processed
    
    def _process_ddg_results(self, results: str, query: str) -> List[Dict[str, Any]]:
        """Process DuckDuckGo search results"""
        # DDG returns string, need to parse
        return []  # Implementation for parsing DDG results