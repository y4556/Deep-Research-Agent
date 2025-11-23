from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
import asyncio
import uuid
import re
import logging
from datetime import datetime

from .state import ResearchState, Fact, RiskFlag, Connection
from .models import MultiModelCoordinator
from services.search import DeepSearchEngine
from services.validation import SourceValidator as ValidationService

logger = logging.getLogger(__name__)

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
        logger.info("~"*80)
        logger.info("📋 NODE: RESEARCH PLANNER")
        logger.info(f"🎯 Target: {state['target_entity']}")
        logger.info("~"*80)
        
        target = state["target_entity"]
        
        planning_prompt = f"""
You are conducting comprehensive due diligence research on: "{target}"

TASK: Create a strategic, multi-phase research plan that will uncover all relevant information about this entity (whether it's an individual person or an organization/company).

STEP 1 - IDENTIFY ENTITY TYPE:
First, determine if the target is:
- An INDIVIDUAL (person, executive, public figure)
- An ORGANIZATION (company, nonprofit, institution, government entity)

STEP 2 - DEVELOP CUSTOMIZED RESEARCH PLAN:

For INDIVIDUALS, investigate:
PHASE 1: CORE IDENTITY & VERIFICATION
- Full name verification and aliases
- Date of birth, nationality, residence locations
- Educational background (degrees, institutions, years)
- Professional licenses and certifications
- Digital footprint (social media, publications, interviews)

PHASE 2: PROFESSIONAL & EMPLOYMENT HISTORY
- Complete career timeline with dates
- Companies worked for (roles, tenure, achievements)
- Board memberships and advisory positions
- Business ownership stakes and partnerships
- Income sources and compensation history

PHASE 3: FINANCIAL ANALYSIS
- Personal wealth indicators and assets
- Investment portfolio and holdings
- Business interests and equity stakes
- Loans, liens, bankruptcies, tax issues
- Real estate ownership and transactions

PHASE 4: NETWORK & RELATIONSHIPS
- Family members and personal relationships
- Professional associates and mentors
- Political connections and donations
- Club memberships and social circles
- Co-investors and business partners

PHASE 5: LEGAL & REGULATORY REVIEW
- Civil litigation history (plaintiff/defendant)
- Criminal records or investigations
- Regulatory sanctions or fines
- Patent disputes or IP issues
- Divorce, custody, or family legal matters

PHASE 6: REPUTATION & RISK ASSESSMENT
- Media coverage and public perception
- Controversies, scandals, or negative press
- Conflicts of interest
- Ethical concerns or misconduct allegations
- Social media behavior and statements

For ORGANIZATIONS, investigate:
PHASE 1: CORPORATE IDENTITY & STRUCTURE
- Legal entity name, registration details, jurisdiction
- Corporate structure and ownership hierarchy
- Subsidiaries, parent companies, affiliated entities
- Business registration numbers and tax IDs
- Operating history and evolution

PHASE 2: LEADERSHIP & GOVERNANCE
- Board of directors (names, backgrounds, tenure)
- Executive team (CEO, CFO, CTO, etc.)
- Major shareholders and beneficial owners
- Changes in leadership (departures, hires)
- Governance structure and policies

PHASE 3: FINANCIAL PERFORMANCE
- Revenue, profitability, growth trends
- Funding rounds and investor information
- Financial statements and SEC filings
- Debt obligations and credit rating
- Bankruptcies, restructurings, or financial distress

PHASE 4: BUSINESS OPERATIONS
- Products/services offered and market position
- Customer base and key clients
- Supplier relationships and dependencies
- Competitive landscape and market share
- Expansion plans and strategic initiatives

PHASE 5: LEGAL & COMPLIANCE
- Regulatory licenses and permits
- Compliance with industry regulations
- Litigation history (lawsuits, settlements)
- Regulatory investigations or sanctions
- IP portfolio (patents, trademarks)

PHASE 6: REPUTATION & RISK FACTORS
- Media coverage and industry reputation
- Customer reviews and COMPLAINTS
- Employee reviews and workplace culture
- Environmental, social, governance (ESG) issues
- CONTROVERSIES, SCANDALS, or PR CRISIS

STEP 3 - PRIORITIZE INVESTIGATION AREAS:
Rank the most critical investigation areas (high, medium, low priority) based on:
- Likelihood of finding material information
- Risk exposure potential
- Relevance to due diligence objectives

===== FEW-SHOT EXAMPLES =====

EXAMPLE 1 - INDIVIDUAL:
Input: "Elon Musk"
Reasoning: Elon Musk is a high-profile individual entrepreneur. I need to investigate his multiple business interests, wealth sources, legal issues, and public controversies.
Output:
1. Verify educational background (University of Pennsylvania, Stanford dropout)
2. Document CEO roles (Tesla, SpaceX, X/Twitter) with timelines
3. Map business network (Peter Thiel, Larry Ellison, other PayPal mafia)
4. Review SEC investigations and legal settlements
5. Assess Twitter acquisition controversy and management style
6. Examine political donations and regulatory relationships
7. Investigate personal relationships and family dynamics

EXAMPLE 2 - ORGANIZATION:
Input: "FTX"
Reasoning: FTX is a cryptocurrency company. Given recent industry volatility, I must investigate financial stability, regulatory compliance, and leadership credibility.
Output:
1. Verify corporate registration (Bahamas) and entity structure
2. Identify leadership team (Sam Bankman-Fried as CEO, executives)
3. Analyze funding rounds ($2B+ raised, Sequoia, SoftBank investors)
4. Investigate regulatory licenses (CFTC, state money transmitter licenses)
5. Examine customer fund handling and segregation practices
6. Map relationships with Alameda Research (sister company)
7. Assess bankruptcy proceedings and fraud allegations


===== YOUR TASK =====

Now create a detailed, prioritized research plan for: "{target}"

REASONING (Chain of Thought):
1. Is this an individual or organization?
2. What are the Highest Risk areas to investigate?
3. What specific, actionable investigation steps should be taken?

OUTPUT FORMAT (8-10 specific investigation tasks):
1. [Specific investigation task with concrete details]
2. [Specific investigation task with concrete details]
...

Focus on: Hidden connections, undisclosed conflicts, financial irregularities, legal risks, and reputation concerns.
"""
        
        research_plan_text = await self.model_coordinator.generate_with_model(
            task_type="planning",
            prompt=planning_prompt,
            system_message="""You are a Outstanding Investigative Researcher and Due Diligence Expert with 20+ years of experience. 
You excel at uncovering hidden risks, identifying red flags, and creating comprehensive investigation strategies.
Your approach is methodical, thorough, and always produces actionable intelligence."""
        )
        
        research_plan = self._parse_research_plan(research_plan_text)
        
        logger.info(f"✅ Research Planner completed - Generated {len(research_plan)} plan items")
        
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
        logger.info("~"*80)
        logger.info("🔎 NODE: QUERY GENERATOR")
        logger.info(f"🎯 Focus: {state.get('current_focus', 'comprehensive')}")
        logger.info("~"*80)
        
        current_focus = state.get("current_focus", "comprehensive")
        previous_queries = state.get("search_queries", [])
        existing_facts = state.get("extracted_facts", [])
        knowledge_gaps = state.get("knowledge_gaps", [])
        
        query_prompt = f"""
You are generating search queries to investigate: "{state['target_entity']}"

===== CONTEXT =====
RESEARCH FOCUS: {current_focus}
PREVIOUS QUERIES: {previous_queries[-5:] if previous_queries else "None - This is the first search"}
KNOWN FACTS: {[f['content'][:100] + '...' for f in existing_facts[-3:]] if existing_facts else "No facts discovered yet"}
KNOWLEDGE GAPS: {knowledge_gaps[-3:] if knowledge_gaps else "Initial investigation phase"}

===== TASK =====
Generate 3 HIGHLY SPECIFIC search queries that will uncover NEW, VERIFIABLE information about this entity.

STEP 1 - ANALYZE WHAT WE NEED:
- What critical information is still missing?
- What facts need verification from additional sources?
- What areas have not been explored yet?
- What specific documents or records would provide authoritative data?

STEP 2 - CRAFT STRATEGIC QUERIES:
Use these advanced search strategies:

For INDIVIDUALS:
✓ Official Records: "SEC Form 4 filings [Name]", "USPTO patent inventor [Name]", "[Name] professional license [State]"
✓ Legal Documents: "[Name] lawsuit plaintiff", "[Name] vs defendant case", "[Name] settlement agreement"
✓ Business Relationships: "[Name] board member company", "[Name] investor portfolio", "[Name] co-founder startup"
✓ Educational Background: "[Name] [University] alumni", "[Name] degree [Field] [Year]", "[Name] thesis dissertation"
✓ Media & Reputation: "[Name] interview [Topic]", "[Name] controversy scandal", "[Name] [Industry] expert"
✓ Location-Specific: "[Name] [City] property records", "[Name] [State] voter registration", "[Name] [County] court records"

For ORGANIZATIONS:
✓ Corporate Records: "[Company] SEC 10-K filing", "[Company] articles of incorporation", "[Company] Delaware entity"
✓ Financial Data: "[Company] revenue 2023", "[Company] funding round Series", "[Company] IPO prospectus"
✓ Leadership: "[Company] CEO [Name]", "[Company] board of directors", "[Company] executive team"
✓ Legal/Regulatory: "[Company] FTC complaint", "[Company] class action lawsuit", "[Company] regulatory fine"
✓ Operations: "[Company] customer reviews", "[Company] Glassdoor reviews", "[Company] competitors analysis"
✓ Industry-Specific: "[Company] FDA approval", "[Company] patent portfolio", "[Company] acquisition merger"

STEP 3 - AVOID DUPLICATE QUERIES:
DO NOT repeat previous queries. FIND NEW angles to investigate.

===== FEW-SHOT EXAMPLES =====

EXAMPLE 1 - Individual (First Iteration):
Target: "Elizabeth Holmes"
Focus: Biographical verification
Previous Queries: None
Known Facts: None
Gaps: Everything unknown

Reasoning: Need to establish basic identity, education, and career foundation first.
Queries:
1. Elizabeth Holmes Stanford University dropout 2003 2004
2. Elizabeth Holmes Theranos founder CEO Silicon Valley
3. Elizabeth Holmes net worth Forbes youngest billionaire

EXAMPLE 2 - Individual (Second Iteration):
Target: "Elizabeth Holmes"
Focus: Legal and regulatory review
Previous Queries: ["Elizabeth Holmes Stanford dropout", "Theranos founder CEO"]
Known Facts: ["Dropped out of Stanford in 2004", "Founded Theranos in 2003"]
Gaps: Legal issues, fraud allegations, trial outcome

Reasoning: Basic bio established. Now need legal/criminal information.
Queries:
1. Elizabeth Holmes SEC fraud charges 2018 settlement
2. Elizabeth Holmes trial verdict guilty wire fraud
3. Elizabeth Holmes sentencing prison sentence 2022

===== YOUR TASK =====

Target Entity: "{state['target_entity']}"

REASONING (Chain of Thought):
1. Based on what we already know, what are the 3 most important gaps to fill?
2. What specific documents or records would provide authoritative verification?
3. What search queries will return the highest-quality, most credible sources?

OUTPUT (3-5 queries):
1. [Specific, targeted query with key details]
2. [Specific, targeted query with key details]
3. [Specific, targeted query with key details]

QUALITY CHECKS:
✓ Queries are specific (not generic)
✓ Queries target authoritative sources (SEC, court records, official databases)
✓ Queries AVOID DUPLICATING PREVIOUS SEARCHES
✓ Queries FILL IDENTIFIED KNOWLEDGE GAPS
✓ Queries ARE OPTIMIZED FOR SEARCH ENGINES
"""
        
        queries_text = await self.model_coordinator.generate_with_model(
            task_type="query_generation",
            prompt=query_prompt,
            system_message="""You are an elite OSINT (Open Source Intelligence) researcher and search strategist with 15+ years of experience.
Your queries consistently uncover information that others miss."""
        )
        
        logger.info(f"Raw LLM queries response:\n{queries_text[:500]}...")
        
        new_queries = self._parse_queries(queries_text)
        
        logger.info(f"✅ Query Generator completed - Generated {len(new_queries)} new queries")
        for i, q in enumerate(new_queries, 1):
            logger.info(f"   {i}. {q}")
        
        return {
            **state,
            "search_queries": state.get("search_queries", []) + new_queries
        }
    
    def _parse_queries(self, queries_text: str) -> List[str]:
        """Parse LLM response into clean search queries"""
        lines = [line.strip() for line in queries_text.split('\n') if line.strip()]
        queries = []
        
        import re
        for line in lines:
            # Match numbered lists: 1., 1), #1, etc.
            if re.match(r'^[\d\*\-\•#]+[\.\):]?\s+', line):
                # Remove the numbering/bullet
                clean_query = re.sub(r'^[\d\*\-\•#]+[\.\):]?\s+', '', line)
                # Remove quotes
                clean_query = clean_query.strip('"').strip("'").strip()
                if clean_query and len(clean_query) > 10:
                    queries.append(clean_query)
                    logger.debug(f"Parsed query: {clean_query}")
        
        # If no queries found, try splitting by common patterns
        if not queries:
            logger.warning("No queries found with standard parsing, trying alternative parsing...")
            # Look for lines that look like search queries (contain keywords)
            for line in lines:
                if any(keyword in line.lower() for keyword in ['search', 'find', 'query', 'look for', 'investigate']):
                    continue  # Skip instruction lines
                # If line is substantial and not a header, treat it as a query
                if len(line) > 15 and not line.endswith(':') and not line.isupper():
                    queries.append(line.strip('"').strip("'").strip())
                    logger.debug(f"Alternative parsed query: {line}")
        
        result = queries[:5]  # Limit to 5 queries
        logger.info(f"Total queries parsed: {len(result)}")
        return result

class DeepSearchExecutor(BaseNode):
    """Executes deep search using multiple search engines"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        logger.info("~"*80)
        logger.info("🌐 NODE: DEEP SEARCH EXECUTOR")
        logger.info("📊 Executing latest queries")
        logger.info("~"*80)
        
        search_engine = DeepSearchEngine()
        all_queries = state.get("search_queries", [])
        current_queries = all_queries[-3:] if all_queries else []  # Get latest queries
        
        logger.info(f"Total queries in state: {len(all_queries)}")
        logger.info(f"Queries to execute: {current_queries}")
        
        if not current_queries:
            logger.warning("⚠️ No queries to execute! Skipping search.")
            return {
                **state,
                "raw_search_results": state.get("raw_search_results", [])
            }
        
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
                logger.error(f"❌ Search error for query '{query}': {e}")
                continue
        
        logger.info(f"✅ Deep Search completed - Retrieved {len(all_results)} total results")
        
        return {
            **state,
            "raw_search_results": state.get("raw_search_results", []) + all_results
        }

class FactExtractor(BaseNode):
    """Extracts structured facts from search results"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        logger.info("~"*80)
        logger.info("📝 NODE: FACT EXTRACTOR")
        logger.info("📊 Processing search results")
        logger.info("~"*80)
        
        recent_results = state["raw_search_results"][-10:]  # Process recent results
        existing_facts = state.get("extracted_facts", [])
        
        extracted_facts = []
        for result in recent_results:
            facts = await self._extract_facts_from_result(result, state["target_entity"])
            extracted_facts.extend(facts)
        
        # Deduplicate facts to avoid repetition
        deduplicated_facts = self._deduplicate_facts(extracted_facts, existing_facts)
        
        logger.info(f"✅ Fact Extractor completed - Extracted {len(extracted_facts)} facts, {len(deduplicated_facts)} unique")
        
        return {
            **state,
            "extracted_facts": existing_facts + deduplicated_facts
        }
    
    def _deduplicate_facts(self, new_facts: List[Dict], existing_facts: List[Dict]) -> List[Dict]:
        """Remove duplicate facts based on content similarity"""
        unique_facts = []
        all_existing_content = [f.get('content', '').lower() for f in existing_facts]
        
        for fact in new_facts:
            fact_content = fact.get('content', '').lower()
            
            # Check if fact is substantially similar to existing facts
            is_duplicate = False
            for existing_content in all_existing_content:
                # Calculate word overlap
                fact_words = set(fact_content.split())
                existing_words = set(existing_content.split())
                
                if len(fact_words) == 0:
                    continue
                    
                overlap = len(fact_words & existing_words) / len(fact_words)
                
                # If >70% word overlap or exact substring match, it's a duplicate
                if overlap > 0.7 or fact_content in existing_content or existing_content in fact_content:
                    is_duplicate = True
                    logger.debug(f"Skipping duplicate fact: {fact_content[:80]}...")
                    break
            
            if not is_duplicate:
                unique_facts.append(fact)
                all_existing_content.append(fact_content)
        
        return unique_facts
    
    async def _extract_facts_from_result(self, result: Dict, target_entity: str) -> List[Dict]:
        """Extract facts from a single search result"""
        extraction_prompt = f"""
You are extracting DETAILED, COMPLETE, verifiable facts about "{target_entity}" from a search result.

===== SOURCE DOCUMENT =====
TITLE: {result.get('title', 'N/A')}
CONTENT: {result.get('content', 'N/A')}
URL: {result.get('url', 'N/A')}

CRITICAL RULES:
1. Extract COMPLETE facts - include ALL relevant details (dates, places, amounts, names)
2. DO NOT cut facts short - include full sentences with context
3. Be SPECIFIC - "Elizabeth Holmes founded Theranos in 2003 at age 19 in Palo Alto, California" NOT "Founded a company"
4. NO DUPLICATES - if a fact is similar to something already stated, skip it
5. NO SPECULATION - only extract what is explicitly stated

CATEGORIES (choose ONE per fact):
For INDIVIDUALS: 
- Biographical (birth, age, nationality, upbringing, background)
- Education (degrees, universities, years, majors, academic achievements)
- Employment (job titles, companies, dates employed, responsibilities, achievements)
- Financial (wealth, salary, investments, assets, fundraising)
- Legal (lawsuits, charges, investigations, settlements, convictions)
- Family (spouse, children, relatives, personal relationships)
- Professional (licenses, certifications, board memberships, professional associations)

For ORGANIZATIONS:
- Corporate (founding, headquarters, legal structure, registration)
- Leadership (CEO, executives, board members, founders)
- Financial (revenue, profit, funding, valuation, financial status)
- Operations (products, services, customers, employees, market position)
- Legal (lawsuits, regulatory actions, compliance, investigations)
- Ownership (shareholders, parent companies, subsidiaries, investors)

CONFIDENCE LEVELS:
0.9-1.0: Official government records, court documents, SEC filings
0.7-0.9: Reputable news (WSJ, NYT, Reuters) with direct quotes and documentation
0.5-0.7: Industry publications, verified LinkedIn/official company profiles
0.3-0.5: Unverified claims, blogs, social media

===== EXAMPLES OF GOOD VS BAD FACTS =====

❌ BAD (too vague): "Graduated from college"
✅ GOOD (detailed): "Graduated from Stanford University with a B.A. in Chemical Engineering in 2003"

❌ BAD (incomplete): "Founded a company"
✅ GOOD (complete): "Founded Theranos in Palo Alto, California in 2003 at age 19 after dropping out of Stanford University"

❌ BAD (cut off): "Worked as CEO from..."
✅ GOOD (full detail): "Served as CEO of Theranos from 2003 to 2018, overseeing the company's growth to a $9 billion valuation at its peak in 2015"

❌ BAD (generic): "Had legal issues"
✅ GOOD (specific): "Charged by the SEC with massive fraud in March 2018, agreed to pay $500,000 penalty and relinquish voting control of Theranos, and was barred from serving as an officer or director of a public company for 10 years"

❌ BAD (vague): "Was convicted"
✅ GOOD (detailed): "Found guilty on January 3, 2022, of four counts of fraud against investors after a federal jury trial that lasted from September 2021 to January 2022"

FEW-SHOT EXAMPLES:

Example 1 (Education):
Source: "Holmes enrolled at Stanford University in 2002 to study chemical engineering but dropped out in her sophomore year to found Theranos"
→ FACT: Enrolled at Stanford University in 2002 to study chemical engineering, dropped out during sophomore year to found Theranos
→ CATEGORY: Education 
→ CONFIDENCE: 0.8

Example 2 (Employment):
Source: "She served as CEO and chairman of Theranos from its founding in 2003 until she was forced to step down as CEO in 2018 following revelations of fraud"
→ FACT: Served as CEO and Chairman of Theranos from 2003 to 2018, when she stepped down following fraud revelations
→ CATEGORY: Employment
→ CONFIDENCE: 0.9

Example 3 (Legal):
Source: "In 2022, Holmes was found guilty on four counts of defrauding investors and sentenced to 11 years and 3 months in federal prison"
→ FACT: Found guilty on four counts of defrauding investors in 2022, sentenced to 11 years and 3 months in federal prison
→ CATEGORY: Legal
→ CONFIDENCE: 0.95

Example 4 (Skip - too vague):
Source: "Some say she may have had connections to various tech executives"
→ [SKIP - Vague speculation without specific details]

===== YOUR TASK =====

Extract ALL detailed, complete, verifiable facts about "{target_entity}" from the source document above.

For EACH fact, provide:
- COMPLETE information with specific details (dates, numbers, names, places)
- Proper CATEGORY classification
- Accurate CONFIDENCE score
- Full context (not cut off mid-sentence)

OUTPUT FORMAT:
FACT: [Complete, detailed statement with all specifics]
CATEGORY: [One category from the list above]
CONFIDENCE: [0.0-1.0 based on source quality]

(Repeat for each fact found)

If NO verifiable facts found: [NO FACTS EXTRACTED]

Remember: DETAIL is key! Include dates, amounts, specific names, and full context!
"""
        
        facts_text = await self.model_coordinator.generate_with_model(
            task_type="fact_extraction",
            prompt=extraction_prompt,
            system_message="You are a forensic analyst with 20+ years experience. You distinguish fact from opinion, assess credibility, and extract precise details. You NEVER speculate - only verifiable facts."
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
                
                # Determine category with better classification
                category = "general"
                clean_lower = clean_line.lower()
                
                if any(kw in clean_lower for kw in ['born', 'birth', 'age', 'nationality', 'raised', 'grew up', 'childhood']):
                    category = "biographical"
                elif any(kw in clean_lower for kw in ['university', 'college', 'degree', 'phd', 'mba', 'graduated', 'studied', 'education', 'school']):
                    category = "education"
                elif any(kw in clean_lower for kw in ['ceo', 'cfo', 'cto', 'founder', 'co-founder', 'position', 'worked at', 'employment', 'job', 'career', 'worked for']):
                    category = "employment"
                elif any(kw in clean_lower for kw in ['lawsuit', 'court', 'legal', 'violation', 'investigation', 'charged', 'convicted', 'settled', 'sec', 'fraud', 'criminal']):
                    category = "legal"
                elif any(kw in clean_lower for kw in ['revenue', 'profit', 'funding', 'investment', 'raised', 'valuation', 'bankruptcy', 'financial', 'money', 'million', 'billion']):
                    category = "financial"
                elif any(kw in clean_lower for kw in ['married', 'spouse', 'family', 'relative', 'children', 'partner', 'husband', 'wife']):
                    category = "family"
                elif any(kw in clean_lower for kw in ['board', 'director', 'executive', 'management', 'professional', 'license', 'certification']):
                    category = "professional"
                
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
        
        # Filter for quality and completeness
        quality_facts = []
        for fact in facts:
            content = fact['content'].strip()
            
            # Quality checks
            if (len(content) < 20 or  # Too short
                len(content.split()) < 5 or  # Too few words
                content.lower().startswith(('no', 'none', 'n/a', '[skip', 'skip')) or  # Negative responses
                not content[0].isupper() or  # Doesn't start with capital
                content.count('.') > 5):  # Too many sentences (might be multiple facts)
                logger.debug(f"Skipping low-quality fact: {content[:50]}...")
                continue
            
            quality_facts.append(fact)
        
        logger.info(f"Quality filter: {len(quality_facts)}/{len(facts)} facts passed")
        
        return quality_facts[:15]  # Limit to 15 facts per extraction


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
You are conducting a comprehensive risk assessment for: "{target}" (individual OR organization)

===== CONTEXT =====
VERIFIED FACTS:
{facts_summary}

KEY CONNECTIONS:
{connections_summary}

DETECTED RED FLAGS:
{flags_summary}

===== TASK =====
Identify DISTINCT, MATERIAL risks that could impact due diligence decisions.

STEP 1 - ANALYZE THE FACTS:
- What factual evidence suggests potential problems?
- Are there patterns of concerning behavior?
- What risks are supported by hard evidence vs. speculation?

STEP 2 - CATEGORIZE RISKS:
Choose ONE category per risk (do NOT duplicate):

1. FINANCIAL: Fraud, bankruptcy, embezzlement, undisclosed liabilities, suspicious transactions, tax evasion
2. LEGAL: Active lawsuits, criminal charges, regulatory investigations, SEC violations, settlements, judgments
3. REPUTATION: Scandals, controversies, ethics violations, consistent negative press, damaged credibility
4. OPERATIONAL: Failed businesses, management turnover, workplace issues, safety violations, poor performance
5. POLITICAL: Conflicts of interest, foreign government ties, corruption allegations, undisclosed political activity

STEP 3 - ASSESS SEVERITY:
- CRITICAL: Confirmed fraud, active criminal charges, major regulatory sanctions, bankruptcy, material misrepresentation
- HIGH: Ongoing litigation, SEC investigations, significant ethical breaches, pattern of problems
- MEDIUM: Settled lawsuits, past controversies, moderate compliance issues, questionable associations
- LOW: Minor issues, old incidents (>5 years), resolved matters with no pattern

===== FEW-SHOT EXAMPLES =====

EXAMPLE 1 - Individual with Legal Risk:
Facts: "Settled SEC fraud charges for $5M in 2021", "Barred from serving as officer/director for 3 years"
Reasoning: Recent SEC action with significant penalty. This is an active restriction.
Output:
{{
  "category": "LEGAL",
  "severity": "CRITICAL",
  "title": "SEC Fraud Settlement and Officer/Director Bar",
  "description": "Settled SEC fraud charges with $5 million penalty in 2021 and barred from serving as corporate officer or director for 3 years. This represents confirmed regulatory violation with ongoing restrictions on professional activities.",
  "evidence": "SEC settlement agreement, 3-year officer/director bar",
  "confidence": 0.95
}}


EXAMPLE 2 - Individual with Reputation Risk:
Facts: "Fired from XYZ Corp for ethics violations 2019", "Multiple workplace harassment complaints", "Negative Glassdoor reviews mention hostile behavior"
Reasoning: Pattern of workplace misconduct across multiple sources.
Output:
{{
  "category": "REPUTATION",
  "severity": "HIGH",
  "title": "Termination for Ethics Violations and Harassment",
  "description": "Terminated from XYZ Corp in 2019 due to ethics violations involving multiple workplace harassment complaints. Pattern confirmed by negative employee reviews citing hostile work environment.",
  "evidence": "Termination for cause, harassment complaints, employee testimonials",
  "confidence": 0.85
}}

===== YOUR TASK =====

Assess risks for: "{target}"

REASONING (Chain of Thought):
1. What are the most serious concerns based on the facts?
2. Which risks are supported by concrete evidence?
3. What severity level is justified by the evidence?
4. Are there any duplicates or overlaps to consolidate?

OUTPUT FORMAT (5-8 DISTINCT risks maximum):
{{
  "category": "[FINANCIAL|LEGAL|REPUTATION|OPERATIONAL|POLITICAL]",
  "severity": "[CRITICAL|HIGH|MEDIUM|LOW]",
  "title": "[Specific, concise title, max 60 chars]",
  "description": "[Detailed description with specifics, dates, amounts, parties]",
  "evidence": "[List specific supporting facts]",
  "confidence": [0.0-1.0 based on evidence quality]
}}

CRITICAL RULES:
✗ NO duplicate risks (consolidate similar issues)
✗ NO speculation without evidence
✗ NO generic descriptions
✓ ONLY material risks affecting due diligence
✓ SPECIFIC details (dates, amounts, names)
✓ DISTINCT core issues
✓ HIGH confidence threshold (>0.6)
"""
        
        risk_text = await self.model_coordinator.generate_with_model(
            task_type="risk_assessment",
            prompt=risk_prompt,
            system_message="""You are a senior risk analyst and compliance expert with 25+ years at Big 4 firms, specialized in due diligence for private equity, and regulatory matters.
You are conservative but not paranoid - you flag real risks with solid evidence."""
        )
        
        return self._parse_risks(risk_text)
    
    def _parse_risks(self, text: str) -> List[Dict]:
        """Parse LLM response into structured risks with improved deduplication"""
        logger.info(f"Parsing risk text: {text[:500]}...")
        
        risks = []
        
        # Try JSON parsing first (preferred format)
        try:
            import json
            # Extract JSON objects from text
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, text, re.DOTALL)
            
            for match in json_matches:
                try:
                    risk_obj = json.loads(match)
                    if isinstance(risk_obj, dict) and 'severity' in risk_obj:
                        # Standardize
                        risks.append({
                            "id": f"risk_{uuid.uuid4().hex[:8]}",
                            "type": risk_obj.get('category', 'general').lower().replace(' ', '_'),
                            "severity": risk_obj.get('severity', 'medium').lower(),
                            "description": risk_obj.get('title', risk_obj.get('description', '')),
                            "evidence": [risk_obj.get('evidence', '')] if risk_obj.get('evidence') else [],
                            "confidence": float(risk_obj.get('confidence', 0.7)),
                            "impact": self._assess_impact(risk_obj.get('severity', 'medium').lower()),
                            "detected_at": datetime.now().isoformat()
                        })
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}, falling back to text parsing")
        
        # Fallback to line-by-line parsing if JSON failed
        if not risks:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            current_risk = None
            
            for line in lines:
                # Skip headers and empty lines
                if line.startswith('#') or len(line) < 10:
                    continue
                
                # Look for risk indicators (but be strict)
                if any(marker in line.lower() for marker in ['severity:', 'category:', 'risk:']):
                    if current_risk and current_risk.get('description'):
                        risks.append(current_risk)
                    
                    # Determine severity
                    severity = "medium"
                    if "critical" in line.lower():
                        severity = "critical"
                    elif "high" in line.lower():
                        severity = "high"
                    elif "low" in line.lower():
                        severity = "low"
                    
                    # Determine risk type from category markers
                    risk_type = "general"
                    text_lower = line.lower()
                    if "financial" in text_lower:
                        risk_type = "financial"
                    elif any(kw in text_lower for kw in ['legal', 'regulatory']):
                        risk_type = "legal_regulatory"
                    elif "reputation" in text_lower:
                        risk_type = "reputation"
                    elif "operational" in text_lower:
                        risk_type = "operational"
                    elif any(kw in text_lower for kw in ['political', 'conflict']):
                        risk_type = "political_conflict"
                    
                    # Extract confidence
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
                        "description": "",
                        "evidence": [],
                        "confidence": confidence,
                        "impact": self._assess_impact(severity),
                        "detected_at": datetime.now().isoformat()
                    }
                
                elif current_risk:
                    # Accumulate description and evidence
                    if not current_risk["description"]:
                        current_risk["description"] = line
                    elif len(current_risk["description"]) < 300:
                        current_risk["description"] += " " + line
                    else:
                        current_risk["evidence"].append(line)
            
            if current_risk and current_risk.get('description'):
                risks.append(current_risk)
        
        logger.info(f"Parsed {len(risks)} risks before deduplication")
        return risks
    
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
        """Remove duplicate or highly similar risks with aggressive deduplication"""
        if not risks:
            return []
        
        logger.info(f"Deduplicating {len(risks)} risks...")
        
        unique_risks = []
        seen_descriptions = []
        
        # Sort by confidence and severity (highest quality first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_risks = sorted(
            risks, 
            key=lambda r: (
                severity_order.get(r.get("severity", "low"), 3),
                -r.get("confidence", 0)  # Higher confidence first
            )
        )
        
        for risk in sorted_risks:
            desc = risk.get("description", "").lower().strip()
            
            # Skip if too short or generic
            if len(desc) < 20 or desc.count(' ') < 3:
                logger.debug(f"Skipping generic risk: {desc[:50]}")
                continue
            
            # Check for significant overlap with existing risks
            is_duplicate = False
            for seen_desc in seen_descriptions:
                # Multiple similarity checks
                desc_words = set(desc.split())
                seen_words = set(seen_desc.split())
                
                # Word overlap
                overlap = len(desc_words & seen_words) / max(len(desc_words), 1)
                
                # Substring check
                substring_match = (desc in seen_desc or seen_desc in desc)
                
                # Key phrase extraction (SEC, fraud, investigation, etc.)
                key_phrases = self._extract_key_phrases(desc)
                seen_phrases = self._extract_key_phrases(seen_desc)
                phrase_overlap = len(key_phrases & seen_phrases) / max(len(key_phrases), 1) if key_phrases else 0
                
                # Duplicate if:
                
                if overlap > 0.5 or substring_match or phrase_overlap > 0.7:
                    is_duplicate = True
                    logger.debug(f"Duplicate detected: '{desc[:50]}...' overlaps with '{seen_desc[:50]}...'")
                    break
            
            if not is_duplicate:
                unique_risks.append(risk)
                seen_descriptions.append(desc)
        
        logger.info(f"After deduplication: {len(unique_risks)} unique risks")
        return unique_risks
    
    def _extract_key_phrases(self, text: str) -> set:
        """Extract key phrases from risk description for better deduplication"""
        text_lower = text.lower()
        key_phrases = set()
        
        # Define important phrase patterns
        patterns = [
            r'sec\s+(?:charged|charges|investigation)',
            r'fraud(?:\s+charges)?',
            r'lawsuit(?:s)?',
            r'investigation(?:s)?',
            r'regulatory\s+(?:violation|issue)',
            r'bankruptcy',
            r'criminal\s+(?:charges|investigation)',
            r'compliance\s+(?:violation|issue)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            key_phrases.update(matches)
        
        return key_phrases
        
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
You are creating a COMPREHENSIVE EXECUTIVE SUMMARY for due diligence on: "{target_entity}" (individual OR organization)

===== RESEARCH DATA =====
METADATA:
- Research Depth: {research_depth} investigation cycles
- Verified Facts: {len(verified_facts)}
- Average Confidence: {confidence_scores.get('average_confidence', 'N/A')}
- Connections Mapped: {len(connections)}
- Risks Identified: {len(risks)} ({len(critical_risks)} critical, {len(high_risks)} high)

VERIFIED FACTS:
{facts_summary}

KEY CONNECTIONS:
{connections_summary}

RISK ASSESSMENT:
{risks_summary}

===== TASK =====
Synthesize all findings into a professional executive summary for C-level decision-makers.

STEP 1 - ANALYZE THE ENTITY:
- Is this an individual or organization?
- What is their primary role/activity?
- What is most important for decision-makers to know?

STEP 2 - STRUCTURE YOUR SUMMARY:

1. ENTITY OVERVIEW (2-3 paragraphs)
   - Core identity and background
   - Primary activities/business
   - Key milestones and timeline

2. MATERIAL FINDINGS (4-6 key points)
   - Most significant discoveries (positive and negative)
   - Patterns or trends uncovered
   - Critical relationships or connections
   - Notable achievements or controversies

3. RISK PROFILE (2-3 paragraphs)
   - Overall risk assessment (Critical/High/Medium/Low)
   - Most serious concerns requiring attention
   - Potential deal-breakers or red flags
   - Areas of uncertainty needing further investigation

4. STRATEGIC RECOMMENDATIONS (3-5 actions)
   - Proceed/Proceed with Caution/Do Not Proceed
   - Specific mitigation strategies if concerns exist
   - Additional due diligence areas to explore
   - Ongoing monitoring recommendations

5. CONFIDENCE & LIMITATIONS (1-2 paragraphs)
   - Overall confidence level in findings
   - Information gaps or incomplete areas
   - Source quality and limitations

===== YOUR TASK =====

Create executive summary for: "{target_entity}"

REASONING (Chain of Thought):
1. What is the most important information for executives to know?
2. What are the key risks vs. opportunities?
3. What is the appropriate risk level (Critical/High/Medium/Low)?
4. Should we proceed, proceed with caution, or stop?
5. What additional steps would reduce uncertainty?

OUTPUT: Professional executive summary following the 5-section structure above.

TONE & STYLE:
✓ Professional, objective, executive-level language
✓ Balanced (acknowledge both strengths and concerns)
✓ Specific (use dates, names, amounts, facts)
✓ Actionable (clear recommendations)
✓ Honest about limitations and uncertainty
✗ No speculation beyond the evidence
✗ No generic platitudes
✗ No unnecessary jargon
"""
        
        executive_summary = await self.model_coordinator.generate_with_model(
            task_type="synthesis",
            prompt=synthesis_prompt,
            system_message="""You are a Managing Director at a top-tier strategy consulting firm (McKinsey, BCG, Bain) with 30+ years synthesizing due diligence for Fortune 500 boards and private equity firms.
Your reports directly influence major business decisions. You write with clarity, precision, and executive presence."""
        )
        
        # Generate narrative story/overview
        narrative_story = await self._generate_entity_narrative(
            target_entity, facts_by_category, connections, risks
        )
        
        # Structure the final report
        final_report = {
            "executive_summary": executive_summary,
            "entity_narrative": narrative_story,  # New: Complete chronological story
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
    
    async def _generate_entity_narrative(self, target_entity: str, facts_by_category: Dict,
                                         connections: List[Dict], risks: List[Dict]) -> str:
        """Generate a chronological narrative story of the entity"""
        
        # Organize all facts chronologically
        all_facts = []
        for category, facts in facts_by_category.items():
            for fact in facts:
                all_facts.append({
                    'content': fact.get('content', ''),
                    'category': category,
                    'confidence': fact.get('confidence', 0)
                })
        
        # Format top facts
        facts_summary = "\n".join([
            f"- {fact['content']} [{fact['category']}]"
            for fact in sorted(all_facts, key=lambda x: x['confidence'], reverse=True)[:30]
        ])
        
        # Format key connections
        connections_summary = "\n".join([
            f"- Connected to {conn.get('target', 'Unknown')} ({conn.get('relationship', 'unknown')})"
            for conn in connections[:15]
        ])
        
        # Format critical events/risks
        critical_events = "\n".join([
            f"- {risk.get('description', '')}"
            for risk in risks if risk.get('severity') in ['critical', 'high']
        ][:10])
        
        narrative_prompt = f"""
You are writing a comprehensive narrative story about "{target_entity}" based on verified research findings.

===== YOUR TASK =====
Write a 3-5 paragraph chronological narrative that tells the COMPLETE STORY of this entity from beginning to present.

This is NOT a bullet-point list. This is a NARRATIVE STORY written in paragraph form.

For INDIVIDUALS: Tell their life story
- Early life, birth, family background (if known)
- Education and formative years
- Career trajectory and major achievements
- Key business ventures, companies founded/led
- Major events, scandals, legal issues (if any)
- Current status and legacy

For ORGANIZATIONS: Tell the company's story
- Founding story (who, when, where, why)
- Early years and initial products/services
- Growth trajectory, funding rounds, expansions
- Key milestones and achievements
- Major controversies, problems, or failures (if any)
- Current status and market position

===== VERIFIED FACTS =====
{facts_summary}

===== KEY CONNECTIONS =====
{connections_summary}

===== CRITICAL EVENTS =====
{critical_events}

===== EXAMPLE FORMAT (Elizabeth Holmes / Theranos) =====

Elizabeth Holmes was born in Washington, D.C. in 1984 to a family with a history of public service. She enrolled at Stanford University in 2002 to study chemical engineering, demonstrating early promise and ambition. However, in 2003 at age 19, she made the bold decision to drop out of Stanford during her sophomore year to pursue her vision of revolutionizing blood testing.

In 2003, Holmes founded Theranos in Palo Alto, California, with the ambitious goal of making blood diagnostics faster, cheaper, and more accessible using just a finger prick instead of traditional venipuncture. She served as CEO and Chairman, raising substantial venture capital funding. By 2015, Theranos reached a staggering $9 billion valuation, and Holmes was celebrated as the youngest self-made female billionaire, gracing magazine covers and earning comparisons to Steve Jobs. The company claimed its proprietary Edison device could run hundreds of tests from a single drop of blood, partnering with major pharmacy chains like Walgreens.

However, the foundation began to crumble in 2015 when investigative journalist John Carreyrou of The Wall Street Journal published exposés revealing that Theranos's technology did not work as advertised. The company was secretly using traditional blood testing equipment for most tests, and its own devices produced unreliable results that could endanger patients. This triggered regulatory investigations and the eventual unraveling of what prosecutors would call a massive fraud scheme.

In March 2018, the SEC charged Holmes with massive fraud, alleging she had misled investors about the company's technology, business relationships, and financial performance. She agreed to pay a $500,000 penalty, relinquish voting control of Theranos, and was barred from serving as an officer or director of any public company for 10 years. Theranos officially dissolved in September 2018. In June 2018, federal prosecutors brought criminal charges against Holmes for wire fraud and conspiracy to commit wire fraud.

Her criminal trial began in September 2021 and lasted until January 2022. On January 3, 2022, a federal jury found her guilty on four counts of defrauding investors out of hundreds of millions of dollars. She was acquitted on charges related to defrauding patients. In November 2022, Holmes was sentenced to 11 years and 3 months in federal prison and ordered to pay $452 million in restitution to victims. She began serving her sentence in May 2023 at a minimum-security federal prison in Bryan, Texas. The Theranos scandal has become one of the most notorious cases of Silicon Valley fraud, serving as a cautionary tale about the dangers of hype, deception, and prioritizing growth over ethics in the startup world.

===== YOUR NARRATIVE FOR "{target_entity}" =====

Write 3-5 comprehensive paragraphs telling the complete story chronologically. Include:
- Origins/founding/early life with specific dates
- Key milestones and achievements with timeline
- Major turning points and critical events
- Controversies, legal issues, or scandals (if any) with details
- Current status and overall significance

Write in NARRATIVE form (paragraphs), NOT bullet points.
Focus on CHRONOLOGY - tell the story from beginning to end.
Include SPECIFIC DETAILS: dates, amounts, names, places from the verified facts.
Make it COMPREHENSIVE yet CONCISE - capture the full arc of the story.

Begin now:
"""
        
        narrative_story = await self.model_coordinator.generate_with_model(
            task_type="synthesis",
            prompt=narrative_prompt,
            system_message="""You are an investigative journalist and biographer who has written bestselling books about major business figures and scandals.
You excel at narrative storytelling, weaving facts into compelling chronological narratives. You write with clarity, drama, and precision.
Your narratives are factual, well-sourced, and capture both successes and failures. You tell the COMPLETE story."""
        )
        
        return narrative_story
    
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