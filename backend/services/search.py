from langchain_community.tools import TavilySearchResults
from typing import List, Dict, Any
import asyncio
import logging
import aiohttp
from core.config import settings

logger = logging.getLogger(__name__)

class DeepSearchEngine:
    """Search engine using Tavily API with Google Custom Search fallback"""
    
    def __init__(self):
        # Primary search engine: Tavily
        self.tavily_tool = TavilySearchResults(
            max_results=5,
            api_key=settings.TAVILY_API_KEY
        )
        
        # Fallback search engine: Google Custom Search
        self.google_api_key = getattr(settings, 'GOOGLE_CUSTOM_SEARCH_API_KEY', None)
        self.google_cse_id = getattr(settings, 'GOOGLE_CSE_ID', '46f410e1fc8c44c23')
        self.google_api_url = "https://www.googleapis.com/customsearch/v1"
    
    async def execute_deep_search(self, query: str, target_entity: str) -> List[Dict[str, Any]]:
        """Execute search using Tavily API with Google Custom Search fallback"""
        # 🔍 LOG EVERY SEARCH QUERY
        logger.info("="*80)
        logger.info("🔎 SEARCH QUERY")
        logger.info(f"🎯 Target: {target_entity}")
        logger.info(f"📝 Query: {query}")
        logger.info("="*80)
        
        all_results = []
        
        # Try Tavily first (primary search engine)
        try:
            logger.info("🔍 Searching with Tavily (Primary)...")
            tavily_results = await asyncio.get_event_loop().run_in_executor(
                None, self.tavily_tool.invoke, {"query": f"{query} {target_entity}"}
            )
            processed_results = self._process_tavily_results(tavily_results, query)
            logger.info(f"✅ Tavily returned {len(processed_results)} results")
            all_results.extend(processed_results)
            
        except Exception as e:
            logger.error(f"❌ Tavily search error: {e}")
            
            # Fallback to Google Custom Search
            if self.google_api_key:
                logger.warning("🔄 Falling back to Google Custom Search...")
                try:
                    google_results = await self._search_google_custom(query, target_entity)
                    logger.info(f"✅ Google Custom Search returned {len(google_results)} results")
                    all_results.extend(google_results)
                except Exception as google_error:
                    logger.error(f"❌ Google Custom Search also failed: {google_error}")
                    raise Exception(f"Both search engines failed. Tavily: {e}, Google: {google_error}")
            else:
                logger.error("❌ No fallback search engine configured (missing GOOGLE_CUSTOM_SEARCH_API_KEY)")
                raise
        
        logger.info(f"📊 Total search results: {len(all_results)}")
        return all_results
    
    async def _search_google_custom(self, query: str, target_entity: str) -> List[Dict[str, Any]]:
        """
        Execute search using Google Custom Search API
        
        Args:
            query: Search query
            target_entity: Target entity being researched
            
        Returns:
            List of processed search results
        """
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': f"{query} {target_entity}",
            'num': 5  # Number of results (max 10 per request)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.google_api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_google_results(data, query)
                else:
                    error_text = await response.text()
                    raise Exception(f"Google Custom Search API error {response.status}: {error_text}")
    
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
    
    def _process_google_results(self, data: Dict, query: str) -> List[Dict[str, Any]]:
        """Process Google Custom Search API results"""
        processed = []
        
        items = data.get("items", [])
        for item in items:
            # Extract snippet (description)
            snippet = item.get("snippet", "")
            
            # Try to get more content from pagemap if available
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [{}])[0]
            description = metatags.get("og:description") or metatags.get("description") or snippet
            
            processed.append({
                "title": item.get("title", ""),
                "content": description,
                "url": item.get("link", ""),
                "query": query,
                "source": "google_custom_search",
                "confidence": 0.85,  # Slightly lower than Tavily but still good
                "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp
            })
        
        return processed