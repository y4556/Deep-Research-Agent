from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
import asyncio
import uuid
import re
from datetime import datetime

from .state import ResearchState, Fact, RiskFlag, Connection
from .models import MultiModelCoordinator
from services.search import DeepSearchEngine
from services.validation import SourceValidator as ValidationService

class BaseNode:
    """Base class for all research nodes"""
    
    def __init__(self):
        self.model_coordinator = MultiModelCoordinator()
        self.node_id = self.__class__.__name__
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """Execute node logic - to be implemented by subclasses"""
        raise NotImplementedError

class ResearchPlanner(BaseNode):
    """Creates comprehensive research plan"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        target = state["target_entity"]
        
        planning_prompt = f"""
        Create a comprehensive, multi-phase research plan for: {target}
        
        Develop a strategic investigation covering these phases:
        
        PHASE 1: CORE IDENTIFICATION & VERIFICATION
        - Biographical data verification (age, education, background)
        - Professional credentials and employment history
        - Digital footprint and online presence
        
        PHASE 2: FINANCIAL & BUSINESS INVESTIGATION  
        - Company affiliations and business relationships
        - Financial interests and investment patterns
        - Regulatory compliance and legal history
        - Tax liens, bankruptcies, or financial disputes
        
        PHASE 3: NETWORK & RELATIONSHIP MAPPING
        - Professional associations and memberships
        - Personal relationships and family connections
        - Political affiliations and donations
        - Organizational board memberships
        
        PHASE 4: RISK & REPUTATION ASSESSMENT
        - Litigation history and legal controversies
        - Regulatory sanctions or investigations
        - Reputation indicators and public perception
        - Conflict of interest analysis
        
        Return a structured, actionable research plan with specific investigation areas.
        Focus on uncovering hidden connections and potential risks.
        """
        
        research_plan_text = await self.model_coordinator.generate_with_model(
            task_type="planning",
            prompt=planning_prompt,
            system_message="You are an Expert Investigative Researcher with deep expertise in due diligence and risk assessment."
        )
        
        research_plan = self._parse_research_plan(research_plan_text)
        
        return {
            **state,
            "research_plan": research_plan,
            "current_focus": research_plan[0] if research_plan else "comprehensive",
            "research_depth": state.get("research_depth", 0) + 1
        }
    
    def _parse_research_plan(self, plan_text: str) -> List[str]:
        """Parse the LLM response into a structured research plan"""
        lines = [line.strip() for line in plan_text.split('\n') if line.strip()]
        plan_items = []
        
        for line in lines:
            if line.startswith(('-', '•', 'PHASE', 'Phase', '1.', '2.', '3.', '4.')):
                clean_line = line.lstrip('-• ').split(':')[-1].strip()
                if clean_line and len(clean_line) > 10:  # Meaningful content
                    plan_items.append(clean_line)
        
        return plan_items[:8]  # Limit to top 8 items

class QueryGenerator(BaseNode):
    """Generates targeted search queries based on research context"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        current_focus = state.get("current_focus", "comprehensive")
        previous_queries = state.get("search_queries", [])
        existing_facts = state.get("extracted_facts", [])
        knowledge_gaps = state.get("knowledge_gaps", [])
        
        query_prompt = f"""
        Generate specific, actionable search queries for: {state['target_entity']}
        
        CURRENT RESEARCH FOCUS: {current_focus}
        PREVIOUS QUERIES (last 5): {previous_queries[-5:] if previous_queries else "None"}
        KNOWN FACTS: {[f['content'][:100] + '...' for f in existing_facts[-3:]] if existing_facts else "None"}
        KNOWLEDGE GAPS: {knowledge_gaps[-3:] if knowledge_gaps else "None"}
        
        Create 3-5 highly specific search queries that will uncover new, verifiable information.
        Focus on filling knowledge gaps and verifying existing information.
        
        Consider these search strategies:
        - Specific document searches (court records, SEC filings, patents)
        - Location-based searches (specific cities, regions)
        - Time-bound searches (specific years, date ranges)
        - Relationship searches (specific people, organizations)
        - Database-specific queries (professional directories, regulatory databases)
        
        Make queries precise and likely to return authoritative sources.
        """
        
        queries_text = await self.model_coordinator.generate_with_model(
            task_type="query_generation",
            prompt=query_prompt,
            system_message="You are an Expert Search Strategist skilled at crafting precise investigative queries."
        )
        
        new_queries = self._parse_queries(queries_text)
        
        return {
            **state,
            "search_queries": state.get("search_queries", []) + new_queries
        }
    
    def _parse_queries(self, queries_text: str) -> List[str]:
        """Parse LLM response into clean search queries"""
        lines = [line.strip() for line in queries_text.split('\n') if line.strip()]
        queries = []
        
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '"')):
                clean_query = line.split('.', 1)[-1].strip().lstrip('-•" ').rstrip('"')
                if clean_query and len(clean_query) > 10:
                    queries.append(clean_query)
        
        return queries[:5]  # Limit to 5 queries

class DeepSearchExecutor(BaseNode):
    """Executes deep search using multiple search engines"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        search_engine = DeepSearchEngine()
        current_queries = state["search_queries"][-3:]  # Get latest queries
        
        all_results = []
        for query in current_queries:
            try:
                results = await search_engine.execute_deep_search(
                    query=query,
                    target_entity=state["target_entity"]
                )
                all_results.extend(results)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Search error for query '{query}': {e}")
                continue
        
        return {
            **state,
            "raw_search_results": state.get("raw_search_results", []) + all_results
        }

class FactExtractor(BaseNode):
    """Extracts structured facts from search results"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        recent_results = state["raw_search_results"][-10:]  # Process recent results
        
        extracted_facts = []
        for result in recent_results:
            facts = await self._extract_facts_from_result(result, state["target_entity"])
            extracted_facts.extend(facts)
        
        return {
            **state,
            "extracted_facts": state.get("extracted_facts", []) + extracted_facts
        }
    
    async def _extract_facts_from_result(self, result: Dict, target_entity: str) -> List[Dict]:
        """Extract facts from a single search result"""
        extraction_prompt = f"""
        Extract verifiable facts about {target_entity} from this search result:
        
        TITLE: {result.get('title', 'N/A')}
        CONTENT: {result.get('content', 'N/A')}
        URL: {result.get('url', 'N/A')}
        
        Extract structured facts in these categories:
        - Personal Background (birth, education, family)
        - Professional History (jobs, positions, companies)
        - Financial Information (investments, companies, wealth indicators)
        - Legal & Regulatory (lawsuits, investigations, compliance)
        - Relationships & Associations (people, organizations, memberships)
        - Reputation & Behavior (awards, controversies, public perception)
        
        For each fact, assess:
        - Confidence level (0.0-1.0) based on source credibility
        - Specificity and verifiability
        - Relevance to comprehensive risk assessment
        
        Return only high-confidence, verifiable facts.
        """
        
        facts_text = await self.model_coordinator.generate_with_model(
            task_type="fact_extraction",
            prompt=extraction_prompt,
            system_message="You are an expert at extracting and verifying factual information from various sources."
        )
        
        return self._parse_facts(facts_text, result.get('url', 'unknown'))
    
    def _parse_facts(self, facts_text: str, source: str) -> List[Dict]:
        """Parse extracted facts into structured format"""
        facts = []
        lines = [line.strip() for line in facts_text.split('\n') if line.strip()]
        
        current_fact = None
        fact_id_counter = 0
        
        for line in lines:
            # Skip headers and empty lines
            if line.startswith('#') or len(line) < 10:
                continue
            
            # Check if this is a fact statement (starts with bullet, number, or category)
            if any(line.startswith(prefix) for prefix in ['- ', '• ', '* ', '1.', '2.', '3.', 'Fact:', 'FACT:']):
                if current_fact:  # Save previous fact
                    facts.append(current_fact)
                
                # Clean the line
                clean_line = line.lstrip('-•*123456789. ').strip()
                
                # Try to extract confidence if mentioned
                confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)%?|(\d+\.?\d*)\s*confidence', 
                                            clean_line, re.IGNORECASE)
                confidence = 0.7  # Default
                if confidence_match:
                    conf_val = confidence_match.group(1) or confidence_match.group(2)
                    confidence = float(conf_val)
                    if confidence > 1:  # Percentage
                        confidence /= 100
                
                # Determine category
                category = "general"
                if any(kw in clean_line.lower() for kw in ['financial', 'money', 'investment', 'company', 'business']):
                    category = "financial"
                elif any(kw in clean_line.lower() for kw in ['lawsuit', 'court', 'legal', 'violation', 'investigation']):
                    category = "legal"
                elif any(kw in clean_line.lower() for kw in ['ceo', 'position', 'work', 'employment', 'job']):
                    category = "professional"
                elif any(kw in clean_line.lower() for kw in ['born', 'education', 'family', 'personal']):
                    category = "personal"
                
                current_fact = {
                    "id": f"fact_{fact_id_counter}_{uuid.uuid4().hex[:8]}",
                    "content": clean_line,
                    "category": category,
                    "sources": [source],
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat(),
                    "verified": False
                }
                fact_id_counter += 1
            
            elif current_fact and not line.startswith(('Category:', 'Source:', 'Confidence:')):
                # Continue previous fact
                current_fact["content"] += " " + line
        
        # Add last fact
        if current_fact:
            facts.append(current_fact)
        
        return facts[:15]  # Limit to 15 facts per extraction


class SourceValidator(BaseNode):
    """Validates facts by cross-referencing multiple sources"""
    
    def __init__(self):
        super().__init__()
        self.validator = ValidationService()
    
    async def execute(self, state: ResearchState) -> ResearchState:
        extracted_facts = state.get("extracted_facts", [])
        search_results = state.get("raw_search_results", [])
        
        if not extracted_facts:
            return state
        
        # Validate facts using the validation service
        validated_facts = await self.validator.validate_facts(
            facts=extracted_facts,
            search_results=search_results
        )
        
        # Calculate overall confidence metrics
        confidence_metrics = self.validator.calculate_overall_confidence(validated_facts)
        
        # Update state with validated facts and confidence scores
        return {
            **state,
            "verified_facts": [f for f in validated_facts if f.get("verified", False)],
            "extracted_facts": validated_facts,  # Update with validation info
            "confidence_scores": {
                **state.get("confidence_scores", {}),
                **confidence_metrics
            }
        }

class ConnectionMapper(BaseNode):
    """Maps relationships and connections between entities"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        verified_facts = state.get("verified_facts", [])
        target_entity = state["target_entity"]
        
        if not verified_facts:
            return state
        
        # Build context for LLM
        facts_summary = "\n".join([
            f"- {fact['content']}" 
            for fact in verified_facts[:20]  # Limit context
        ])
        
        connection_prompt = f"""
        Analyze these verified facts about {target_entity} and identify key relationships and connections:
        
        VERIFIED FACTS:
        {facts_summary}
        
        TASK: Identify and map connections including:
        1. People directly associated with the target (family, business partners, colleagues)
        2. Organizations/companies connected to the target
        3. Financial relationships (investors, board memberships, ownership)
        4. Political or regulatory connections
        5. Indirect connections through shared associations
        
        For each connection, assess:
        - Relationship type (family, business, financial, political, professional)
        - Strength of connection (strong/medium/weak)
        - Evidence supporting the connection
        - Potential significance for risk assessment
        
        Return ONLY connections supported by the facts provided.
        Format as JSON array of connections.
        """
        
        connections_text = await self.model_coordinator.generate_with_model(
            task_type="query_generation",  # Use GPT-4 for structured extraction
            prompt=connection_prompt,
            system_message="You are an expert at identifying relationships and connections between entities based on factual information."
        )
        
        # Parse connections
        connections = self._parse_connections(connections_text, target_entity, verified_facts)
        
        return {
            **state,
            "connections": state.get("connections", []) + connections
        }
    
    def _parse_connections(self, text: str, target: str, facts: List[Dict]) -> List[Dict]:
        """Parse LLM response into structured connections"""
        connections = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_connection = None
        
        for line in lines:
            # Look for connection indicators
            if any(indicator in line.lower() for indicator in ['connected to', 'relationship with', 'associated with', 'partner', 'member']):
                # Extract entity names (simple heuristic)
                words = line.split()
                potential_entities = [w.strip('.,;:') for w in words if w[0].isupper() and len(w) > 2]
                
                if len(potential_entities) >= 2:
                    # Determine relationship type
                    rel_type = "professional"
                    if any(kw in line.lower() for kw in ['family', 'spouse', 'relative']):
                        rel_type = "family"
                    elif any(kw in line.lower() for kw in ['investor', 'funding', 'capital', 'board']):
                        rel_type = "financial"
                    elif any(kw in line.lower() for kw in ['government', 'political', 'campaign']):
                        rel_type = "political"
                    
                    # Determine strength
                    strength = 0.6  # Default medium
                    if any(kw in line.lower() for kw in ['ceo', 'founder', 'owner', 'family']):
                        strength = 0.9
                    elif any(kw in line.lower() for kw in ['former', 'ex-', 'previously']):
                        strength = 0.4
                    
                    connections.append({
                        "id": f"conn_{uuid.uuid4().hex[:8]}",
                        "source": target,
                        "target": potential_entities[0] if potential_entities[0].lower() != target.lower() else potential_entities[1],
                        "relationship": rel_type,
                        "strength": strength,
                        "evidence": [line],
                        "discovered_at": datetime.now().isoformat()
                    })
        
        return connections[:20]  # Limit connections

class RiskAssessor(BaseNode):
    """Assesses risks and flags concerning patterns"""
    
    def __init__(self):
        super().__init__()
        self.validator = ValidationService()
    
    async def execute(self, state: ResearchState) -> ResearchState:
        verified_facts = state.get("verified_facts", [])
        connections = state.get("connections", [])
        target_entity = state["target_entity"]
        
        if not verified_facts:
            return state
        
        # Detect red flags in facts
        all_red_flags = []
        for fact in verified_facts:
            content = fact.get("content", "")
            red_flags = self.validator.detect_red_flags(content)
            
            for flag in red_flags:
                all_red_flags.append({
                    "id": f"risk_{uuid.uuid4().hex[:8]}",
                    "type": flag["keyword"].replace(" ", "_"),
                    "severity": flag["severity"],
                    "description": f"{flag['keyword'].title()} mentioned in context: {flag['context']}",
                    "evidence": [fact["content"]],
                    "confidence": fact.get("confidence", 0.5),
                    "impact": self._assess_impact(flag["severity"]),
                    "source_fact_id": fact.get("id"),
                    "detected_at": datetime.now().isoformat()
                })
        
        # Perform comprehensive risk assessment using LLM
        risk_analysis = await self._comprehensive_risk_assessment(
            target_entity, verified_facts, connections, all_red_flags
        )
        
        # Combine automated and LLM-based risks
        all_risks = all_red_flags + risk_analysis
        
        # Deduplicate and prioritize
        unique_risks = self._deduplicate_risks(all_risks)
        
        return {
            **state,
            "risks_flagged": state.get("risks_flagged", []) + unique_risks
        }
    
    async def _comprehensive_risk_assessment(self, target: str, facts: List[Dict], 
                                             connections: List[Dict], 
                                             detected_flags: List[Dict]) -> List[Dict]:
        """Use LLM for comprehensive risk assessment"""
        facts_summary = "\n".join([f"- {f['content']}" for f in facts[:15]])
        connections_summary = "\n".join([
            f"- Connected to {c['target']} ({c['relationship']})"
            for c in connections[:10]
        ])
        flags_summary = "\n".join([
            f"- {f['type']}: {f['description']}"
            for f in detected_flags[:10]
        ])
        
        risk_prompt = f"""
        Conduct a comprehensive risk assessment for: {target}
        
        VERIFIED FACTS:
        {facts_summary}
        
        KEY CONNECTIONS:
        {connections_summary}
        
        DETECTED RED FLAGS:
        {flags_summary}
        
        ASSESSMENT FRAMEWORK:
        Analyze for these risk categories:
        
        1. FINANCIAL RISKS
           - Undisclosed liabilities, bankruptcy history
           - Complex corporate structures hiding beneficial ownership
           - Unusual financial patterns or transactions
           
        2. LEGAL & REGULATORY RISKS
           - Litigation history, ongoing lawsuits
           - Regulatory violations or investigations
           - Compliance issues
           
        3. REPUTATION RISKS
           - Past controversies or scandals
           - Association with problematic entities/individuals
           - Negative media coverage patterns
           
        4. OPERATIONAL RISKS
           - Business practice concerns
           - Track record of failed ventures
           - Management stability issues
           
        5. POLITICAL/CONFLICT OF INTEREST RISKS
           - Undisclosed political connections
           - Potential conflicts of interest
           - Foreign government ties
        
        For each risk identified:
        - Categorize severity (critical/high/medium/low)
        - Provide specific evidence
        - Assess confidence level (0-1)
        - Estimate potential impact
        
        Return ONLY risks with solid factual basis.
        Format each risk clearly with severity, description, and evidence.
        """
        
        risk_text = await self.model_coordinator.generate_with_model(
            task_type="risk_assessment",
            prompt=risk_prompt,
            system_message="You are an expert risk analyst conducting due diligence investigations. Be thorough but only flag risks with solid evidence."
        )
        
        return self._parse_risks(risk_text)
    
    def _parse_risks(self, text: str) -> List[Dict]:
        """Parse LLM response into structured risks"""
        risks = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_risk = None
        
        for line in lines:
            # Look for severity indicators
            if any(severity in line.lower() for severity in ['critical', 'high', 'medium', 'low', 'severity']):
                if current_risk:
                    risks.append(current_risk)
                
                # Determine severity
                severity = "medium"
                if "critical" in line.lower():
                    severity = "critical"
                elif "high" in line.lower():
                    severity = "high"
                elif "low" in line.lower():
                    severity = "low"
                
                # Determine risk type
                risk_type = "general"
                if any(kw in line.lower() for kw in ['financial', 'bankruptcy', 'debt']):
                    risk_type = "financial"
                elif any(kw in line.lower() for kw in ['legal', 'lawsuit', 'litigation', 'regulatory']):
                    risk_type = "legal_regulatory"
                elif any(kw in line.lower() for kw in ['reputation', 'scandal', 'controversy']):
                    risk_type = "reputation"
                elif any(kw in line.lower() for kw in ['political', 'conflict']):
                    risk_type = "political"
                
                # Extract confidence if mentioned
                confidence = 0.7
                conf_match = re.search(r'confidence[:\s]+(\d+\.?\d*)%?', line, re.IGNORECASE)
                if conf_match:
                    confidence = float(conf_match.group(1))
                    if confidence > 1:
                        confidence /= 100
                
                current_risk = {
                    "id": f"risk_{uuid.uuid4().hex[:8]}",
                    "type": risk_type,
                    "severity": severity,
                    "description": line,
                    "evidence": [],
                    "confidence": confidence,
                    "impact": self._assess_impact(severity),
                    "detected_at": datetime.now().isoformat()
                }
            
            elif current_risk and line and not line.startswith('#'):
                # Add to current risk description or evidence
                if len(current_risk["description"]) < 200:
                    current_risk["description"] += " " + line
                else:
                    current_risk["evidence"].append(line)
        
        if current_risk:
            risks.append(current_risk)
        
        return risks[:15]  # Limit risks
    
    def _assess_impact(self, severity: str) -> str:
        """Assess potential impact based on severity"""
        impact_map = {
            "critical": "Significant potential for material harm to reputation, finances, or legal standing. Immediate attention required.",
            "high": "Notable concerns that could impact decision-making. Should be investigated further.",
            "medium": "Moderate concerns worthy of consideration. Monitor for developments.",
            "low": "Minor issues for awareness. Minimal immediate impact expected."
        }
        return impact_map.get(severity, "Impact assessment pending.")
    
    def _deduplicate_risks(self, risks: List[Dict]) -> List[Dict]:
        """Remove duplicate or highly similar risks"""
        if not risks:
            return []
        
        unique_risks = []
        seen_descriptions = set()
        
        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_risks = sorted(risks, key=lambda r: severity_order.get(r.get("severity", "low"), 3))
        
        for risk in sorted_risks:
            desc = risk.get("description", "").lower()
            
            # Check for significant overlap with existing risks
            is_duplicate = False
            for seen_desc in seen_descriptions:
                # Simple word overlap check
                desc_words = set(desc.split())
                seen_words = set(seen_desc.split())
                overlap = len(desc_words & seen_words) / max(len(desc_words), 1)
                
                if overlap > 0.6:  # 60% overlap = duplicate
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_risks.append(risk)
                seen_descriptions.add(desc)
        
        return unique_risks

class ResearchReflector(BaseNode):
    """Reflects on research progress and identifies knowledge gaps"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        verified_facts = state.get("verified_facts", [])
        connections = state.get("connections", [])
        risks = state.get("risks_flagged", [])
        research_plan = state.get("research_plan", [])
        target_entity = state["target_entity"]
        research_depth = state.get("research_depth", 0)
        
        # Build reflection context
        facts_summary = f"Found {len(verified_facts)} verified facts across categories: " + \
            ", ".join(set(f.get("category", "general") for f in verified_facts))
        
        connections_summary = f"Mapped {len(connections)} connections"
        risks_summary = f"Identified {len(risks)} potential risks"
        
        coverage_analysis = self._analyze_coverage(verified_facts, research_plan)
        
        reflection_prompt = f"""
        Research Progress Review for: {target_entity}
        Depth: {research_depth} iterations completed
        
        CURRENT STATUS:
        - {facts_summary}
        - {connections_summary}
        - {risks_summary}
        
        COVERAGE ANALYSIS:
        {coverage_analysis}
        
        RESEARCH PLAN ITEMS:
        {", ".join(research_plan[:5])}
        
        REFLECTION TASK:
        1. Assess information quality and comprehensiveness
        2. Identify significant knowledge gaps:
           - Missing biographical/background information
           - Incomplete financial picture
           - Unexplored professional history
           - Unclear relationships or associations
           - Unverified claims requiring deeper investigation
        
        3. Determine if additional research depth is needed:
           - Are there critical unanswered questions?
           - Do we have sufficient information for risk assessment?
           - Are there suspicious patterns requiring deeper investigation?
           - Is information from diverse, credible sources?
        
        4. Suggest specific areas for deeper investigation
        
        5. Provide a quality score (0-10) for the current research
        
        Be critical but realistic. Focus on gaps that could materially impact risk assessment.
        """
        
        reflection_text = await self.model_coordinator.generate_with_model(
            task_type="reflection",
            prompt=reflection_prompt,
            system_message="You are a senior research analyst reviewing investigation quality and identifying gaps."
        )
        
        # Parse reflection to extract knowledge gaps and next steps
        knowledge_gaps = self._extract_knowledge_gaps(reflection_text)
        quality_score = self._extract_quality_score(reflection_text)
        
        # Determine next focus area
        next_focus = self._determine_next_focus(knowledge_gaps, coverage_analysis)
        
        # Increment depth
        new_depth = research_depth + 1
        
        return {
            **state,
            "knowledge_gaps": knowledge_gaps,
            "current_focus": next_focus,
            "research_depth": new_depth,
            "model_decisions": {
                **state.get("model_decisions", {}),
                f"reflection_{new_depth}": {
                    "quality_score": quality_score,
                    "gaps_identified": len(knowledge_gaps),
                    "recommendation": reflection_text[:200]
                }
            }
        }
    
    def _analyze_coverage(self, facts: List[Dict], plan: List[str]) -> str:
        """Analyze how well we've covered the research plan"""
        if not facts:
            return "No facts discovered yet. All areas need investigation."
        
        categories_covered = set(f.get("category", "general") for f in facts)
        fact_categories = {
            "personal": ["biographical", "personal", "background", "education"],
            "professional": ["employment", "professional", "career", "position"],
            "financial": ["financial", "business", "company", "investment"],
            "legal": ["legal", "lawsuit", "regulatory", "compliance"],
            "political": ["political", "government", "campaign"]
        }
        
        coverage = []
        for cat, keywords in fact_categories.items():
            has_coverage = cat in categories_covered or \
                          any(kw in " ".join(plan).lower() for kw in keywords)
            
            status = "✓ Covered" if has_coverage else "✗ Missing"
            coverage.append(f"{cat.title()}: {status}")
        
        return "\n".join(coverage)
    
    def _extract_knowledge_gaps(self, text: str) -> List[str]:
        """Extract knowledge gaps from reflection text"""
        gaps = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        in_gaps_section = False
        for line in lines:
            if any(marker in line.lower() for marker in ['knowledge gap', 'missing', 'unclear', 'need to', 'should investigate']):
                in_gaps_section = True
            
            if in_gaps_section and (line.startswith(('-', '•', '*', '1.', '2.', '3.')) or 
                                   any(marker in line.lower() for marker in ['gap:', 'missing:', 'unclear:'])):
                clean_gap = line.lstrip('-•*123456789. ').strip()
                if len(clean_gap) > 15:  # Meaningful gap
                    gaps.append(clean_gap)
        
        return gaps[:10]  # Limit gaps
    
    def _extract_quality_score(self, text: str) -> float:
        """Extract quality score from reflection"""
        score_match = re.search(r'quality[:\s]+(\d+\.?\d*)\s*(?:/\s*10)?', text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            if score > 10:  # Normalize if out of range
                score = score / 10
            return min(10.0, score)
        
        # Default based on sentiment
        if any(word in text.lower() for word in ['excellent', 'comprehensive', 'thorough']):
            return 8.0
        elif any(word in text.lower() for word in ['adequate', 'sufficient']):
            return 6.0
        elif any(word in text.lower() for word in ['lacking', 'incomplete', 'insufficient']):
            return 4.0
        
        return 5.0  # Default middle score
    
    def _determine_next_focus(self, gaps: List[str], coverage: str) -> str:
        """Determine what to focus on next based on gaps"""
        if not gaps:
            return "comprehensive"
        
        # Analyze gap themes
        gap_text = " ".join(gaps).lower()
        
        if any(kw in gap_text for kw in ['financial', 'money', 'business', 'company']):
            return "financial investigation"
        elif any(kw in gap_text for kw in ['legal', 'lawsuit', 'regulatory', 'compliance']):
            return "legal and regulatory review"
        elif any(kw in gap_text for kw in ['connection', 'relationship', 'association']):
            return "relationship mapping"
        elif any(kw in gap_text for kw in ['background', 'history', 'biographical']):
            return "biographical deep dive"
        else:
            return "comprehensive review"

class ReportSynthesizer(BaseNode):
    """Synthesizes final research report"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        target_entity = state["target_entity"]
        verified_facts = state.get("verified_facts", [])
        connections = state.get("connections", [])
        risks = state.get("risks_flagged", [])
        confidence_scores = state.get("confidence_scores", {})
        research_depth = state.get("research_depth", 0)
        search_queries = state.get("search_queries", [])
        
        # Organize facts by category
        facts_by_category = self._organize_facts_by_category(verified_facts)
        
        # Prioritize risks by severity
        critical_risks = [r for r in risks if r.get("severity") == "critical"]
        high_risks = [r for r in risks if r.get("severity") == "high"]
        medium_risks = [r for r in risks if r.get("severity") == "medium"]
        low_risks = [r for r in risks if r.get("severity") == "low"]
        
        # Prepare context for LLM synthesis
        facts_summary = self._format_facts_summary(facts_by_category)
        connections_summary = self._format_connections_summary(connections)
        risks_summary = self._format_risks_summary(critical_risks, high_risks, medium_risks, low_risks)
        
        synthesis_prompt = f"""
        Generate a comprehensive due diligence report for: {target_entity}
        
        RESEARCH METADATA:
        - Research Depth: {research_depth} iterations
        - Total Verified Facts: {len(verified_facts)}
        - Average Confidence: {confidence_scores.get('average_confidence', 'N/A')}
        - Total Connections Mapped: {len(connections)}
        - Total Risks Identified: {len(risks)}
        
        VERIFIED FACTS BY CATEGORY:
        {facts_summary}
        
        KEY CONNECTIONS:
        {connections_summary}
        
        RISK ASSESSMENT:
        {risks_summary}
        
        SYNTHESIS TASK:
        Create a professional executive summary that includes:
        
        1. OVERVIEW
           - Brief profile of the entity
           - Key identifying information
           - Primary areas of activity
        
        2. KEY FINDINGS
           - Most significant discoveries
           - Notable patterns or trends
           - Important relationships
        
        3. RISK ASSESSMENT SUMMARY
           - Overall risk level assessment
           - Critical concerns requiring immediate attention
           - Areas of uncertainty requiring further investigation
        
        4. RECOMMENDATIONS
           - Suggested actions based on findings
           - Areas requiring additional due diligence
           - Monitoring recommendations
        
        5. CONFIDENCE & LIMITATIONS
           - Overall confidence in findings
           - Information gaps
           - Source limitations
        
        Write in a professional, objective tone suitable for executive review.
        Be factual and evidence-based. Highlight both positive and negative findings.
        Clearly distinguish between verified facts and areas of uncertainty.
        """
        
        executive_summary = await self.model_coordinator.generate_with_model(
            task_type="synthesis",
            prompt=synthesis_prompt,
            system_message="You are a senior analyst synthesizing due diligence findings into an executive report. Be thorough, objective, and professional."
        )
        
        # Structure the final report
        final_report = {
            "executive_summary": executive_summary,
            "target_entity": target_entity,
            "session_id": state.get("research_session_id"),
            "research_metadata": {
                "research_depth": research_depth,
                "total_queries_executed": len(search_queries),
                "total_facts_discovered": len(verified_facts),
                "total_verified_facts": len([f for f in verified_facts if f.get("verified", False)]),
                "total_connections": len(connections),
                "total_risks": len(risks),
                "average_confidence": confidence_scores.get("average_confidence"),
                "high_confidence_facts": confidence_scores.get("high_confidence_facts"),
                "start_time": state.get("start_time"),
                "completion_time": datetime.now().isoformat()
            },
            "key_findings_by_category": facts_by_category,
            "connection_network": connections,
            "risk_assessment": {
                "overall_risk_level": self._calculate_overall_risk_level(risks),
                "critical_risks": critical_risks,
                "high_risks": high_risks,
                "medium_risks": medium_risks,
                "low_risks": low_risks
            },
            "confidence_assessment": confidence_scores,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            **state,
            "final_report": final_report
        }
    
    def _organize_facts_by_category(self, facts: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize facts by category"""
        organized = {}
        
        for fact in facts:
            category = fact.get("category", "general")
            if category not in organized:
                organized[category] = []
            organized[category].append(fact)
        
        # Sort facts within each category by confidence
        for category in organized:
            organized[category].sort(key=lambda f: f.get("confidence", 0), reverse=True)
        
        return organized
    
    def _format_facts_summary(self, facts_by_category: Dict[str, List[Dict]]) -> str:
        """Format facts summary for LLM"""
        summary_lines = []
        
        for category, facts in facts_by_category.items():
            summary_lines.append(f"\n{category.upper()}:")
            for fact in facts[:5]:  # Top 5 per category
                confidence = fact.get("confidence", 0)
                summary_lines.append(
                    f"  - {fact['content']} (Confidence: {confidence:.2f})"
                )
        
        return "\n".join(summary_lines) if summary_lines else "No verified facts available."
    
    def _format_connections_summary(self, connections: List[Dict]) -> str:
        """Format connections summary"""
        if not connections:
            return "No significant connections mapped."
        
        # Group by relationship type
        by_type = {}
        for conn in connections:
            rel_type = conn.get("relationship", "unknown")
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(conn)
        
        summary = []
        for rel_type, conns in by_type.items():
            summary.append(f"\n{rel_type.upper()}:")
            for conn in conns[:3]:  # Top 3 per type
                summary.append(
                    f"  - {conn['source']} → {conn['target']} "
                    f"(Strength: {conn.get('strength', 0):.2f})"
                )
        
        return "\n".join(summary)
    
    def _format_risks_summary(self, critical: List, high: List, medium: List, low: List) -> str:
        """Format risks summary"""
        summary = []
        
        if critical:
            summary.append("\nCRITICAL RISKS:")
            for risk in critical[:3]:
                summary.append(f"  - {risk['description'][:150]}")
        
        if high:
            summary.append("\nHIGH RISKS:")
            for risk in high[:5]:
                summary.append(f"  - {risk['description'][:150]}")
        
        if medium:
            summary.append(f"\nMEDIUM RISKS: {len(medium)} identified")
        
        if low:
            summary.append(f"\nLOW RISKS: {len(low)} identified")
        
        if not summary:
            return "No significant risks identified."
        
        return "\n".join(summary)
    
    def _calculate_overall_risk_level(self, risks: List[Dict]) -> str:
        """Calculate overall risk level"""
        if not risks:
            return "low"
        
        critical_count = sum(1 for r in risks if r.get("severity") == "critical")
        high_count = sum(1 for r in risks if r.get("severity") == "high")
        medium_count = sum(1 for r in risks if r.get("severity") == "medium")
        
        if critical_count >= 1:
            return "critical"
        elif high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 3:
            return "medium"
        else:
            return "low"