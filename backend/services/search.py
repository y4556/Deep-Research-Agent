from langchain_community.tools import TavilySearchResults
from typing import List, Dict, Any
import asyncio
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class DeepSearchEngine:
    """Search engine using Tavily API"""
    
    def __init__(self):
        # Use Tavily as primary search engine
        self.tavily_tool = TavilySearchResults(
            max_results=5,
            api_key=settings.TAVILY_API_KEY
        )
    
    async def execute_deep_search(self, query: str, target_entity: str) -> List[Dict[str, Any]]:
        """Execute search using Tavily API"""
        # 🔍 LOG EVERY SEARCH QUERY
        logger.info("="*80)
        logger.info("🔎 SEARCH QUERY")
        logger.info(f"🎯 Target: {target_entity}")
        logger.info(f"📝 Query: {query}")
        logger.info("="*80)
        
        all_results = []
        
        try:
            logger.info("🔍 Searching with Tavily...")
            tavily_results = await asyncio.get_event_loop().run_in_executor(
                None, self.tavily_tool.invoke, {"query": f"{query} {target_entity}"}
            )
            processed_results = self._process_tavily_results(tavily_results, query)
            logger.info(f"✅ Tavily returned {len(processed_results)} results")
            all_results.extend(processed_results)
            
        except Exception as e:
            logger.error(f"❌ Tavily search error: {e}")
            raise
        
        logger.info(f"📊 Total search results: {len(all_results)}")
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
                "confidence": 0.9,  # Tavily provides high-quality results
                "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp
            })
        return processed