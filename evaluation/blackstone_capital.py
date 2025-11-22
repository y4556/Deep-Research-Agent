from typing import Dict, List, Any
from datetime import datetime

BLACKSTONE_CAPITAL_EVALUATION_PROFILE = {
    "name": "Blackstone Capital LLC",
    "description": "Private investment firm with complex offshore structure and regulatory concerns",
    "category": "investment_firm",
    "difficulty": "very_high",
    
    "hidden_facts": [
        {
            "id": "fact_1",
            "content": "Registered in Delaware in 2012, managing approximately $850M in assets as of 2023",
            "category": "financial",
            "confidence_required": 0.8,
            "search_difficulty": "high",
            "verification_sources": ["Delaware SOS", "SEC Form ADV", "industry databases"],
            "points": 15
        },
        {
            "id": "fact_2",
            "content": "Principal owners: James Mitchell (60%), Sarah Chen (25%), and Cayman Islands trust (15%)",
            "category": "financial",
            "confidence_required": 0.85,
            "search_difficulty": "very_high",
            "verification_sources": ["SEC filings", "beneficial ownership reports", "offshore registries"],
            "points": 30
        },
        {
            "id": "fact_3",
            "content": "Received SEC enforcement action in 2020 for failure to disclose conflicts of interest, paid $2.5M fine",
            "category": "legal",
            "confidence_required": 0.9,
            "search_difficulty": "high",
            "verification_sources": ["SEC enforcement releases", "FINRA records", "legal news"],
            "points": 35
        },
        {
            "id": "fact_4",
            "content": "Operates subsidiaries in British Virgin Islands and Luxembourg for tax optimization purposes",
            "category": "financial",
            "confidence_required": 0.75,
            "search_difficulty": "very_high",
            "verification_sources": ["Offshore registries", "ICIJ databases", "corporate filings"],
            "points": 30
        },
        {
            "id": "fact_5",
            "content": "James Mitchell was previously barred from investment advisory role by FINRA in 2008 (later overturned)",
            "category": "professional",
            "confidence_required": 0.85,
            "search_difficulty": "very_high",
            "verification_sources": ["FINRA BrokerCheck", "regulatory archives", "court records"],
            "points": 35
        },
        {
            "id": "fact_6",
            "content": "Major investments in renewable energy sector, particularly solar and wind projects in emerging markets",
            "category": "financial",
            "confidence_required": 0.7,
            "search_difficulty": "medium",
            "verification_sources": ["Investment databases", "company announcements", "industry reports"],
            "points": 10
        },
        {
            "id": "fact_7",
            "content": "Named in Paradise Papers leak (2017) for offshore tax arrangements, though no illegal activity proven",
            "category": "legal",
            "confidence_required": 0.9,
            "search_difficulty": "very_high",
            "verification_sources": ["ICIJ Paradise Papers database", "investigative journalism", "legal analysis"],
            "points": 40
        },
        {
            "id": "fact_8",
            "content": "Filed lawsuit against former client in 2021 over disputed fees, settled out of court",
            "category": "legal",
            "confidence_required": 0.75,
            "search_difficulty": "high",
            "verification_sources": ["Court records", "legal filings", "settlement agreements"],
            "points": 20
        }
    ],
    
    "expected_risks": [
        {
            "type": "regulatory_compliance",
            "severity": "high",
            "description": "History of SEC enforcement action indicating compliance weaknesses",
            "expected_confidence": 0.85
        },
        {
            "type": "financial_opacity",
            "severity": "high",
            "description": "Complex offshore structure with entities in tax havens raises transparency concerns",
            "expected_confidence": 0.75
        },
        {
            "type": "reputation_risk",
            "severity": "high",
            "description": "Association with Paradise Papers and past regulatory issues",
            "expected_confidence": 0.80
        },
        {
            "type": "leadership_concerns",
            "severity": "medium",
            "description": "Principal owner has history of regulatory issues (though later resolved)",
            "expected_confidence": 0.70
        },
        {
            "type": "litigation_exposure",
            "severity": "medium",
            "description": "History of client disputes and legal actions",
            "expected_confidence": 0.65
        }
    ],
    
    "evaluation_criteria": {
        "fact_discovery_rate": 0.60,  # High difficulty - 60% is good
        "risk_identification_accuracy": 0.85,  # Should catch major risks
        "source_validation_score": 0.90,  # Must validate carefully for this profile
        "connection_mapping_completeness": 0.70,
        "confidence_scoring_accuracy": 0.85,  # Critical for regulatory issues
        "research_efficiency": 0.50  # Will take time to uncover
    },
    
    "scoring_weights": {
        "fact_discovery": 0.40,  # Most important for difficult profile
        "risk_assessment": 0.30,  # Critical for compliance
        "source_validation": 0.20,
        "connection_mapping": 0.08,
        "efficiency": 0.02  # Less important for complex investigations
    }
}


def evaluate_blackstone_capital_research(research_report: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate research performance on Blackstone Capital profile"""
    
    found_facts = research_report.get("key_findings", [])
    identified_risks = research_report.get("risk_assessment", {})
    connections = research_report.get("connection_network", [])
    
    # Calculate scores
    fact_score = _calculate_fact_discovery_score(found_facts)
    risk_score = _calculate_risk_assessment_score(identified_risks)
    validation_score = _calculate_validation_score(found_facts)
    connection_score = _calculate_connection_score(connections)
    
    # Overall score with weights
    weights = BLACKSTONE_CAPITAL_EVALUATION_PROFILE["scoring_weights"]
    overall_score = (
        fact_score * weights["fact_discovery"] +
        risk_score * weights["risk_assessment"] +
        validation_score * weights["source_validation"] +
        connection_score * weights["connection_mapping"]
    )
    
    # Detailed analysis
    critical_facts_found = _check_critical_facts(found_facts)
    
    return {
        "overall_score": round(overall_score, 2),
        "detailed_scores": {
            "fact_discovery": round(fact_score, 2),
            "risk_assessment": round(risk_score, 2),
            "source_validation": round(validation_score, 2),
            "connection_mapping": round(connection_score, 2)
        },
        "facts_found": len(found_facts),
        "risks_identified": _count_risks(identified_risks),
        "critical_facts_discovered": critical_facts_found,
        "evaluation_timestamp": datetime.now().isoformat(),
        "profile_difficulty": "very_high",
        "profile_name": "Blackstone Capital LLC",
        "difficulty_note": "This is a very challenging profile with deeply hidden information"
    }


def _calculate_fact_discovery_score(found_facts: List[Dict]) -> float:
    """Calculate fact discovery score - weighted by difficulty"""
    hidden_facts = BLACKSTONE_CAPITAL_EVALUATION_PROFILE["hidden_facts"]
    total_points = sum(fact["points"] for fact in hidden_facts)
    
    # Keyword matching for key facts (simplified - use semantic matching in production)
    earned_points = 0
    keywords_map = {
        0: ["delaware", "2012", "850m", "assets"],
        1: ["james mitchell", "sarah chen", "cayman", "owners", "60%"],
        2: ["sec", "enforcement", "2020", "2.5m", "conflicts"],
        3: ["british virgin islands", "luxembourg", "subsidiaries", "offshore"],
        4: ["mitchell", "finra", "barred", "2008"],
        5: ["renewable", "solar", "wind", "investments"],
        6: ["paradise papers", "2017", "icij", "leak"],
        7: ["lawsuit", "2021", "fees", "settled"]
    }
    
    for fact in found_facts:
        content_lower = fact.get("content", "").lower()
        for idx, keywords in keywords_map.items():
            # Need more keyword matches for complex facts
            matches = sum(1 for kw in keywords if kw in content_lower)
            if matches >= 2:  # Require multiple keyword matches
                earned_points += hidden_facts[idx]["points"]
                break
    
    # Bonus for high-difficulty facts
    very_high_difficulty_facts = [f for f in hidden_facts if f["search_difficulty"] == "very_high"]
    very_high_points = sum(f["points"] for f in very_high_difficulty_facts)
    
    if earned_points >= very_high_points * 0.3:  # Found 30% of very hard facts
        earned_points *= 1.2  # 20% bonus
    
    return min(earned_points / total_points, 1.0)


def _calculate_risk_assessment_score(identified_risks: Dict) -> float:
    """Calculate risk assessment accuracy"""
    expected_risks = BLACKSTONE_CAPITAL_EVALUATION_PROFILE["expected_risks"]
    
    all_risks = (
        identified_risks.get("critical_risks", []) +
        identified_risks.get("high_risks", []) +
        identified_risks.get("medium_risks", []) +
        identified_risks.get("low_risks", [])
    )
    
    if not all_risks:
        return 0.0
    
    # Check for specific expected risk types
    risk_type_matches = 0
    for expected_risk in expected_risks:
        expected_type = expected_risk["type"]
        # Check if this risk type was identified
        for identified_risk in all_risks:
            identified_type = identified_risk.get("type", "")
            if expected_type in identified_type or identified_type in expected_type:
                risk_type_matches += 1
                break
    
    type_score = risk_type_matches / len(expected_risks)
    
    # Check severity alignment (high/critical risks should be flagged as such)
    high_severity_expected = sum(1 for r in expected_risks if r["severity"] in ["high", "critical"])
    high_severity_found = len(identified_risks.get("critical_risks", [])) + len(identified_risks.get("high_risks", []))
    
    severity_score = min(high_severity_found / max(high_severity_expected, 1), 1.0)
    
    return (type_score * 0.7 + severity_score * 0.3)


def _calculate_validation_score(found_facts: List[Dict]) -> float:
    """Calculate source validation quality - critical for this profile"""
    if not found_facts:
        return 0.0
    
    # Check for credible sources (should be high for regulatory/legal facts)
    credible_source_domains = [
        "sec.gov", "finra.org", "icij.org", "gov", "court", "legal"
    ]
    
    facts_with_credible_sources = 0
    facts_with_high_confidence = 0
    
    for fact in found_facts:
        sources = fact.get("sources", [])
        if sources:
            # Check if any source is from credible domain
            if any(any(domain in str(src).lower() for domain in credible_source_domains) for src in sources):
                facts_with_credible_sources += 1
        
        # Check confidence scores
        if fact.get("confidence", 0) >= 0.8:
            facts_with_high_confidence += 1
    
    credible_ratio = facts_with_credible_sources / len(found_facts)
    high_conf_ratio = facts_with_high_confidence / len(found_facts)
    
    return (credible_ratio * 0.6 + high_conf_ratio * 0.4)


def _calculate_connection_score(connections: List[Dict]) -> float:
    """Calculate connection mapping completeness"""
    if not connections:
        return 0.0
    
    # Expected connections
    expected_entities = [
        "james mitchell", "sarah chen", "cayman", "bvi", "luxembourg",
        "sec", "finra", "renewable", "solar"
    ]
    
    found_entities = set()
    for conn in connections:
        target = conn.get("target", "").lower()
        source = conn.get("source", "").lower()
        found_entities.add(target)
        found_entities.add(source)
    
    matches = sum(1 for entity in expected_entities 
                 if any(entity in found.lower() for found in found_entities))
    
    return min(matches / len(expected_entities), 1.0)


def _check_critical_facts(found_facts: List[Dict]) -> List[str]:
    """Identify which critical facts were discovered"""
    critical_keywords = {
        "SEC Enforcement": ["sec", "enforcement", "2020", "fine"],
        "Paradise Papers": ["paradise papers", "icij", "offshore leak"],
        "Beneficial Ownership": ["cayman", "trust", "owners", "mitchell", "chen"],
        "FINRA Issues": ["finra", "barred", "mitchell", "2008"]
    }
    
    discovered = []
    for critical_fact, keywords in critical_keywords.items():
        for fact in found_facts:
            content = fact.get("content", "").lower()
            if sum(1 for kw in keywords if kw in content) >= 2:
                discovered.append(critical_fact)
                break
    
    return discovered


def _count_risks(risk_assessment: Dict) -> int:
    """Count total risks identified"""
    return sum([
        len(risk_assessment.get("critical_risks", [])),
        len(risk_assessment.get("high_risks", [])),
        len(risk_assessment.get("medium_risks", [])),
        len(risk_assessment.get("low_risks", []))
    ])

