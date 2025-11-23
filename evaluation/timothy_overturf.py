from typing import Dict, List, Any
from datetime import datetime

TIMOTHY_OVERFURT_EVALUATION_PROFILE = {
    "name": "Timothy Overturf",
    "description": "Business executive with complex financial background and hidden connections",
    "category": "business_executive",
    "difficulty": "high",
    
    "hidden_facts": [
        {
            "id": "fact_1",
            "content": "Founded three shell companies in Delaware between 2015-2018 for tax optimization",
            "category": "financial",
            "confidence_required": 0.8,
            "search_difficulty": "high",
            "verification_sources": ["SEC filings", "Delaware business registry"],
            "points": 20
        },
        {
            "id": "fact_2", 
            "content": "Was subject to SEC investigation in 2019 regarding potential insider trading violations",
            "category": "legal",
            "confidence_required": 0.9,
            "search_difficulty": "very_high",
            "verification_sources": ["SEC enforcement database", "court records"],
            "points": 30
        },
        {
            "id": "fact_3",
            "content": "Serves as undisclosed board member for offshore investment firm 'Vertex Holdings'",
            "category": "professional",
            "confidence_required": 0.7,
            "search_difficulty": "high", 
            "verification_sources": ["corporate registries", "leaked documents"],
            "points": 25
        },
        {
            "id": "fact_4",
            "content": "Linked to controversial political donations through obscure PACs in 2020 election cycle",
            "category": "political",
            "confidence_required": 0.6,
            "search_difficulty": "medium",
            "verification_sources": ["FEC filings", "PAC disclosures"],
            "points": 15
        },
        {
            "id": "fact_5",
            "content": "Has history of patent litigation involving former business partners from 2016-2017",
            "category": "legal",
            "confidence_required": 0.75,
            "search_difficulty": "medium",
            "verification_sources": ["court records", "patent database"],
            "points": 20
        }
    ],
    
    "expected_risks": [
        {
            "type": "financial_opacity",
            "severity": "high",
            "description": "Complex corporate structure with multiple shell companies",
            "expected_confidence": 0.7
        },
        {
            "type": "regulatory_compliance",
            "severity": "high", 
            "description": "History of SEC investigations and regulatory scrutiny",
            "expected_confidence": 0.8
        },
        {
            "type": "conflict_of_interest",
            "severity": "medium",
            "description": "Undisclosed board memberships and business relationships",
            "expected_confidence": 0.6
        },
        {
            "type": "reputation_risk",
            "severity": "medium",
            "description": "Association with controversial political activities",
            "expected_confidence": 0.5
        }
    ],
    
    "evaluation_criteria": {
        "fact_discovery_rate": 0.75,  # Should find at least 75% of hidden facts
        "risk_identification_accuracy": 0.8,
        "source_validation_score": 0.85,
        "connection_mapping_completeness": 0.7,
        "confidence_scoring_accuracy": 0.8,
        "research_efficiency": 0.6  # Balance of depth vs resource usage
    },
    
    "scoring_weights": {
        "fact_discovery": 0.35,
        "risk_assessment": 0.25,
        "source_validation": 0.20,
        "connection_mapping": 0.15,
        "efficiency": 0.05
    }
}

def evaluate_timothy_overturf_research(research_report: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate research performance on Timothy Overturf profile"""
    
    found_facts = research_report.get("key_findings", [])
    identified_risks = research_report.get("risk_assessment", [])
    
    # Calculate fact discovery score
    fact_score = calculate_fact_discovery_score(found_facts)
    
    # Calculate risk assessment score  
    risk_score = calculate_risk_assessment_score(identified_risks)
    
    # Calculate source validation score
    validation_score = calculate_validation_score(found_facts)
    
    # Calculate connection mapping score
    connection_score = calculate_connection_score(research_report.get("connection_network", []))
    
    # Overall score
    weights = TIMOTHY_OVERFURT_EVALUATION_PROFILE["scoring_weights"]
    overall_score = (
        fact_score * weights["fact_discovery"] +
        risk_score * weights["risk_assessment"] + 
        validation_score * weights["source_validation"] +
        connection_score * weights["connection_mapping"]
    )
    
    return {
        "overall_score": round(overall_score, 2),
        "detailed_scores": {
            "fact_discovery": round(fact_score, 2),
            "risk_assessment": round(risk_score, 2),
            "source_validation": round(validation_score, 2),
            "connection_mapping": round(connection_score, 2)
        },
        "facts_found": len(found_facts),
        "risks_identified": len(identified_risks),
        "evaluation_timestamp": datetime.now().isoformat(),
        "profile_difficulty": "high"
    }

def calculate_fact_discovery_score(found_facts: List[Dict]) -> float:
    """Calculate how many hidden facts were discovered"""
    hidden_facts = TIMOTHY_OVERFURT_EVALUATION_PROFILE["hidden_facts"]
    total_points = sum(fact["points"] for fact in hidden_facts)
    
    # Simplified scoring - in real implementation, would do semantic matching
    earned_points = min(len(found_facts) * 10, total_points)  # Placeholder
    
    return earned_points / total_points

def calculate_risk_assessment_score(identified_risks: List[Dict]) -> float:
    """Calculate risk assessment accuracy"""
    expected_risks = TIMOTHY_OVERFURT_EVALUATION_PROFILE["expected_risks"]
    
    if not identified_risks:
        return 0.0
    
    # Simplified scoring
    return min(len(identified_risks) / len(expected_risks), 1.0)

def calculate_validation_score(found_facts: List[Dict]) -> float:
    """Calculate source validation quality"""
    if not found_facts:
        return 0.0
    
    # Check for source citations
    facts_with_sources = [fact for fact in found_facts if fact.get("sources")]
    return len(facts_with_sources) / len(found_facts)

def calculate_connection_score(connections: List[Dict]) -> float:
    """Calculate connection mapping completeness"""
    if not connections:
        return 0.0
    
    return min(len(connections) / 10, 1.0) 