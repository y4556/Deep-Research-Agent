from typing import List, Dict, Any, Tuple
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
import asyncio
from collections import defaultdict

class SourceValidator:
    """
    Validates and cross-references facts from multiple sources
    Implements confidence scoring and credibility assessment
    """
    
    def __init__(self):
        # Domain authority scores (can be expanded with actual authority data)
        self.trusted_domains = {
            # Government and official sources
            "gov": 1.0,
            "edu": 0.95,
            "mil": 1.0,
            
            # Major news outlets
            "reuters.com": 0.9,
            "apnews.com": 0.9,
            "bloomberg.com": 0.85,
            "wsj.com": 0.85,
            "nytimes.com": 0.85,
            "ft.com": 0.85,
            "economist.com": 0.85,
            
            # Business and professional
            "linkedin.com": 0.7,
            "crunchbase.com": 0.8,
            "sec.gov": 1.0,
            "ftc.gov": 1.0,
            "justice.gov": 1.0,
            
            # Academic and research
            "scholar.google.com": 0.9,
            "researchgate.net": 0.75,
            "arxiv.org": 0.8,
            
            # Legal and regulatory
            "courtlistener.com": 0.85,
            "justia.com": 0.8,
            "law.cornell.edu": 0.9,
            
            # Financial
            "fec.gov": 1.0,
            "irs.gov": 1.0,
            "finra.org": 0.9,
            
            # International
            "un.org": 0.95,
            "who.int": 0.95,
            "worldbank.org": 0.9,
        }
        
        # Red flag indicators
        self.red_flag_keywords = [
            "investigation", "lawsuit", "fraud", "convicted", "indicted",
            "scandal", "controversy", "violation", "penalty", "sanction",
            "bankruptcy", "foreclosure", "debarred", "suspended", "censured",
            "money laundering", "corruption", "bribery", "embezzlement"
        ]
        
        # Date freshness scoring
        self.date_decay_factor = 0.1  # 10% reduction per year
    
    async def validate_facts(self, facts: List[Dict[str, Any]], 
                             search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate facts by cross-referencing with search results
        Returns validated facts with updated confidence scores
        """
        validated_facts = []
        
        for fact in facts:
            validation_result = await self._validate_single_fact(fact, search_results)
            
            if validation_result["is_valid"]:
                fact.update({
                    "verified": True,
                    "confidence": validation_result["confidence"],
                    "supporting_sources": validation_result["supporting_sources"],
                    "validation_notes": validation_result["notes"],
                    "validated_at": datetime.now().isoformat()
                })
                validated_facts.append(fact)
            else:
                # Keep fact but mark as unverified
                fact.update({
                    "verified": False,
                    "confidence": max(0.1, fact.get("confidence", 0.5) * 0.5),
                    "validation_notes": validation_result["notes"],
                    "validated_at": datetime.now().isoformat()
                })
                validated_facts.append(fact)
        
        return validated_facts
    
    async def _validate_single_fact(self, fact: Dict[str, Any], 
                                    search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a single fact against search results"""
        fact_content = fact.get("content", "").lower()
        fact_sources = fact.get("sources", [])
        
        supporting_sources = []
        confidence_scores = []
        
        # Check each source
        for source in fact_sources:
            source_credibility = self._assess_source_credibility(source)
            confidence_scores.append(source_credibility)
            
            if source_credibility > 0.6:
                supporting_sources.append({
                    "url": source,
                    "credibility": source_credibility
                })
        
        # Cross-reference with other search results
        for result in search_results:
            result_url = result.get("url", "")
            result_content = result.get("content", "").lower()
            
            # Check if result supports the fact
            if self._content_supports_fact(fact_content, result_content):
                source_credibility = self._assess_source_credibility(result_url)
                
                if source_credibility > 0.5:
                    confidence_scores.append(source_credibility)
                    supporting_sources.append({
                        "url": result_url,
                        "credibility": source_credibility,
                        "snippet": result.get("content", "")[:200]
                    })
        
        # Calculate overall confidence
        if not confidence_scores:
            return {
                "is_valid": False,
                "confidence": 0.1,
                "supporting_sources": [],
                "notes": "No credible sources found"
            }
        
        # Aggregate confidence scores
        base_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Bonus for multiple independent sources
        if len(set(s["url"] for s in supporting_sources)) >= 3:
            base_confidence = min(1.0, base_confidence * 1.2)
        elif len(set(s["url"] for s in supporting_sources)) >= 2:
            base_confidence = min(1.0, base_confidence * 1.1)
        
        # Check for contradictory information
        contradictions = self._check_contradictions(fact, search_results)
        if contradictions:
            base_confidence *= 0.7
            notes = f"Possible contradictions found: {len(contradictions)}"
        else:
            notes = "Fact verified across multiple sources"
        
        return {
            "is_valid": base_confidence >= 0.4,
            "confidence": round(base_confidence, 3),
            "supporting_sources": supporting_sources[:5],  # Limit to top 5
            "notes": notes
        }
    
    def _assess_source_credibility(self, url: str) -> float:
        """Assess credibility score of a source URL"""
        if not url:
            return 0.3
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            
            # Check exact domain match
            if domain in self.trusted_domains:
                return self.trusted_domains[domain]
            
            # Check TLD
            for tld, score in [(".gov", 1.0), (".edu", 0.95), (".mil", 1.0)]:
                if domain.endswith(tld):
                    return score
            
            # Check domain keywords
            for trusted_domain, score in self.trusted_domains.items():
                if trusted_domain in domain:
                    return score * 0.9  # Slightly lower for subdomain
            
            # Unknown source - medium credibility
            return 0.5
            
        except Exception:
            return 0.3
    
    def _content_supports_fact(self, fact_text: str, content: str) -> bool:
        """Check if content supports the fact claim"""
        # Extract key entities and concepts from fact
        fact_words = set(re.findall(r'\w+', fact_text.lower()))
        content_words = set(re.findall(r'\w+', content.lower()))
        
        # Remove common words
        stop_words = {"the", "is", "at", "which", "on", "a", "an", "as", "are", "was", "were", "been", "be", "have", "has", "had"}
        fact_words -= stop_words
        content_words -= stop_words
        
        # Calculate overlap
        overlap = len(fact_words & content_words)
        overlap_ratio = overlap / max(len(fact_words), 1)
        
        # Need at least 30% overlap to support
        return overlap_ratio >= 0.3
    
    def _check_contradictions(self, fact: Dict[str, Any], 
                             search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for contradictory information in search results"""
        # Simplified contradiction detection
        # In production, would use NLI models or more sophisticated logic
        contradictions = []
        
        fact_content = fact.get("content", "").lower()
        
        # Look for explicit negations or contradictions
        negation_patterns = [
            r"not\s+" + re.escape(fact_content[:30]),
            r"deny\s+",
            r"false\s+claim",
            r"inaccurate",
            r"disputed"
        ]
        
        for result in search_results:
            content = result.get("content", "").lower()
            
            for pattern in negation_patterns:
                if re.search(pattern, content):
                    contradictions.append({
                        "source": result.get("url", ""),
                        "type": "negation",
                        "snippet": content[:200]
                    })
        
        return contradictions
    
    def assess_date_relevance(self, date_str: str) -> float:
        """
        Assess how relevant/fresh information is based on date
        Returns multiplier (1.0 for recent, decreasing for older)
        """
        if not date_str:
            return 0.7  # Unknown date - moderate penalty
        
        try:
            # Parse various date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y"]:
                try:
                    date = datetime.strptime(date_str[:10], fmt)
                    break
                except ValueError:
                    continue
            else:
                return 0.7  # Couldn't parse - moderate penalty
            
            # Calculate age in years
            age_years = (datetime.now() - date).days / 365.25
            
            # Apply decay
            freshness = max(0.3, 1.0 - (age_years * self.date_decay_factor))
            
            return round(freshness, 2)
            
        except Exception:
            return 0.7
    
    def detect_red_flags(self, text: str) -> List[Dict[str, Any]]:
        """Detect potential red flags in text"""
        red_flags = []
        text_lower = text.lower()
        
        for keyword in self.red_flag_keywords:
            if keyword in text_lower:
                # Find context around the keyword
                match = re.search(rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}', 
                                 text_lower, re.IGNORECASE)
                
                if match:
                    red_flags.append({
                        "keyword": keyword,
                        "context": match.group(0),
                        "severity": self._assess_keyword_severity(keyword)
                    })
        
        return red_flags
    
    def _assess_keyword_severity(self, keyword: str) -> str:
        """Assess severity level of red flag keyword"""
        high_severity = ["convicted", "fraud", "indicted", "money laundering", 
                        "embezzlement", "corruption"]
        medium_severity = ["investigation", "lawsuit", "violation", "scandal"]
        
        if keyword in high_severity:
            return "high"
        elif keyword in medium_severity:
            return "medium"
        else:
            return "low"
    
    async def cross_reference_facts(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-reference facts to find connections and consistency
        Returns analysis of fact relationships
        """
        entity_mentions = defaultdict(list)
        date_timeline = []
        location_mentions = defaultdict(list)
        
        # Extract entities, dates, locations from facts
        for idx, fact in enumerate(facts):
            content = fact.get("content", "")
            
            # Simple entity extraction (in production, use NER)
            words = content.split()
            for word in words:
                if word[0].isupper() and len(word) > 2:
                    entity_mentions[word].append(idx)
            
            # Extract years (simple pattern)
            years = re.findall(r'\b(19|20)\d{2}\b', content)
            for year in years:
                date_timeline.append({
                    "year": year,
                    "fact_idx": idx,
                    "content": content[:100]
                })
        
        # Find frequently mentioned entities (potential key players)
        key_entities = {
            entity: indices 
            for entity, indices in entity_mentions.items() 
            if len(indices) >= 2
        }
        
        return {
            "key_entities": key_entities,
            "timeline_events": sorted(date_timeline, key=lambda x: x["year"]),
            "total_facts_analyzed": len(facts),
            "interconnected_facts": len(key_entities)
        }
    
    def calculate_overall_confidence(self, facts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall confidence metrics for the research"""
        if not facts:
            return {
                "average_confidence": 0.0,
                "verified_ratio": 0.0,
                "high_confidence_ratio": 0.0
            }
        
        confidences = [fact.get("confidence", 0.5) for fact in facts]
        verified_count = sum(1 for fact in facts if fact.get("verified", False))
        high_confidence_count = sum(1 for fact in facts if fact.get("confidence", 0) >= 0.8)
        
        return {
            "average_confidence": round(sum(confidences) / len(confidences), 3),
            "verified_ratio": round(verified_count / len(facts), 3),
            "high_confidence_ratio": round(high_confidence_count / len(facts), 3),
            "total_facts": len(facts),
            "verified_facts": verified_count,
            "high_confidence_facts": high_confidence_count
        }


class ContentExtractor:
    """Extract clean content from web pages and documents"""
    
    def __init__(self):
        self.content_selectors = [
            "article", "main", ".content", "#content", 
            ".article-body", ".post-content"
        ]
    
    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract main content from HTML
        Note: In production, use BeautifulSoup4
        """
        # Placeholder implementation
        # In production, implement proper HTML parsing
        return {
            "text": html[:5000],  # Simplified
            "title": "",
            "author": "",
            "date": "",
            "url": url
        }

