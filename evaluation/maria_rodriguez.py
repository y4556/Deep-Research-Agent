from typing import Dict, List, Any
from datetime import datetime

MARIA_RODRIGUEZ_EVALUATION_PROFILE = {
    "name": "Maria Rodriguez",
    "description": "Tech startup founder with complex funding history and IP disputes",
    "category": "tech_entrepreneur",
    "difficulty": "medium",
    
    "hidden_facts": [
        {
            "id": "fact_1",
            "content": "Founded VisionTech AI in 2018, raised $12M Series A from Sequoia Capital and Andreessen Horowitz",
            "category": "professional",
            "confidence_required": 0.75,
            "search_difficulty": "medium",
            "verification_sources": ["Crunchbase", "TechCrunch", "SEC Form D"],
            "points": 15
        },
        {
            "id": "fact_2",
            "content": "Previously worked as Senior Engineer at Google from 2013-2017, left to start own company",
            "category": "professional",
            "confidence_required": 0.8,
            "search_difficulty": "medium",
            "verification_sources": ["LinkedIn", "Google employee directory", "industry publications"],
            "points": 10
        },
        {
            "id": "fact_3",
            "content": "Involved in patent infringement lawsuit with former employer ByteTech over AI algorithms (2019-2020)",
            "category": "legal",
            "confidence_required": 0.85,
            "search_difficulty": "high",
            "verification_sources": ["PACER court records", "USPTO database", "legal news"],
            "points": 25
        },
        {
            "id": "fact_4",
            "content": "Holds 8 US patents in machine learning and computer vision, filed between 2015-2021",
            "category": "professional",
            "confidence_required": 0.9,
            "search_difficulty": "medium",
            "verification_sources": ["USPTO patent database", "Google Patents"],
            "points": 15
        },
        {
            "id": "fact_5",
            "content": "Graduated from MIT with PhD in Computer Science in 2013, thesis on neural networks",
            "category": "personal",
            "confidence_required": 0.85,
            "search_difficulty": "medium",
            "verification_sources": ["MIT records", "ProQuest dissertations", "academic publications"],
            "points": 10
        },
        {
            "id": "fact_6",
            "content": "Board member of Tech Diversity Initiative, non-profit focused on women in STEM",
            "category": "professional",
            "confidence_required": 0.7,
            "search_difficulty": "low",
            "verification_sources": ["Non-profit registry", "organization website", "press releases"],
            "points": 10
        },
        {
            "id": "fact_7",
            "content": "VisionTech AI faced layoffs in Q2 2022, reducing workforce by 30% amid funding difficulties",
            "category": "professional",
            "confidence_required": 0.75,
            "search_difficulty": "high",
            "verification_sources": ["Tech news outlets", "WARN notices", "employee reports"],
            "points": 20
        }
    ],
    
    "expected_risks": [
        {
            "type": "legal_compliance",
            "severity": "medium",
            "description": "History of IP litigation with previous employer, potential for future disputes",
            "expected_confidence": 0.75
        },
        {
            "type": "financial_stability",
            "severity": "medium",
            "description": "Recent layoffs and potential funding challenges may indicate financial pressure",
            "expected_confidence": 0.7
        },
        {
            "type": "operational_continuity",
            "severity": "low",
            "description": "Workforce reduction may affect company's ability to deliver on commitments",
            "expected_confidence": 0.6
        }
    ],
    
    "evaluation_criteria": {
        "fact_discovery_rate": 0.70,  # Should find at least 70% of hidden facts
        "risk_identification_accuracy": 0.75,
        "source_validation_score": 0.80,
        "connection_mapping_completeness": 0.65,
        "confidence_scoring_accuracy": 0.75,
        "research_efficiency": 0.65
    },
    
    "scoring_weights": {
        "fact_discovery": 0.35,
        "risk_assessment": 0.25,
        "source_validation": 0.20,
        "connection_mapping": 0.15,
        "efficiency": 0.05
    }
}


def evaluate_maria_rodriguez_research(research_report: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate research performance on Maria Rodriguez profile"""
    
    found_facts = research_report.get("key_findings", [])
    identified_risks = research_report.get("risk_assessment", {})
    
    # Calculate scores
    fact_score = _calculate_fact_discovery_score(found_facts)
    risk_score = _calculate_risk_assessment_score(identified_risks)
    validation_score = _calculate_validation_score(found_facts)
    connection_score = _calculate_connection_score(research_report.get("connection_network", []))
    
    # Overall score
    weights = MARIA_RODRIGUEZ_EVALUATION_PROFILE["scoring_weights"]
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
        "risks_identified": _count_risks(identified_risks),
        "evaluation_timestamp": datetime.now().isoformat(),
        "profile_difficulty": "medium",
        "profile_name": "Maria Rodriguez"
    }


def _calculate_fact_discovery_score(found_facts: List[Dict]) -> float:
    """Calculate fact discovery score"""
    hidden_facts = MARIA_RODRIGUEZ_EVALUATION_PROFILE["hidden_facts"]
    total_points = sum(fact["points"] for fact in hidden_facts)
    
    # Simple keyword matching for evaluation (enhance with semantic similarity in production)
    earned_points = 0
    keywords_map = {
        0: ["visiontech", "series a", "sequoia", "12m"],
        1: ["google", "engineer", "2013", "2017"],
        2: ["patent", "infringement", "bytetech", "lawsuit"],
        3: ["8 patents", "uspto", "machine learning"],
        4: ["mit", "phd", "computer science", "2013"],
        5: ["board member", "diversity", "stem"],
        6: ["layoffs", "2022", "30%", "funding"]
    }
    
    for fact in found_facts:
        content_lower = fact.get("content", "").lower()
        for idx, keywords in keywords_map.items():
            if any(kw in content_lower for kw in keywords):
                earned_points += hidden_facts[idx]["points"]
                break
    
    return min(earned_points / total_points, 1.0)


def _calculate_risk_assessment_score(identified_risks: Dict) -> float:
    """Calculate risk assessment accuracy"""
    expected_risks = MARIA_RODRIGUEZ_EVALUATION_PROFILE["expected_risks"]
    
    all_risks = (
        identified_risks.get("critical_risks", []) +
        identified_risks.get("high_risks", []) +
        identified_risks.get("medium_risks", []) +
        identified_risks.get("low_risks", [])
    )
    
    if not all_risks:
        return 0.0
    
    # Check if expected risk types were identified
    expected_types = {r["type"] for r in expected_risks}
    identified_types = {r.get("type", "") for r in all_risks}
    
    overlap = len(expected_types & identified_types)
    return overlap / len(expected_types) if expected_types else 0.5


def _calculate_validation_score(found_facts: List[Dict]) -> float:
    """Calculate source validation quality"""
    if not found_facts:
        return 0.0
    
    facts_with_sources = [f for f in found_facts if f.get("sources") and len(f.get("sources", [])) > 0]
    verified_facts = [f for f in found_facts if f.get("verified", False)]
    
    source_score = len(facts_with_sources) / len(found_facts)
    verified_score = len(verified_facts) / len(found_facts)
    
    return (source_score + verified_score) / 2


def _calculate_connection_score(connections: List[Dict]) -> float:
    """Calculate connection mapping completeness"""
    if not connections:
        return 0.0
    
    # Expected connections: Google, VisionTech AI, ByteTech, investors, Tech Diversity Initiative
    expected_entities = ["google", "visiontech", "bytetech", "sequoia", "andreessen", "diversity"]
    
    found_entities = set()
    for conn in connections:
        target = conn.get("target", "").lower()
        source = conn.get("source", "").lower()
        found_entities.add(target)
        found_entities.add(source)
    
    # Count matches
    matches = sum(1 for entity in expected_entities if any(entity in found for found in found_entities))
    
    return min(matches / len(expected_entities), 1.0)


def _count_risks(risk_assessment: Dict) -> int:
    """Count total risks identified"""
    return sum([
        len(risk_assessment.get("critical_risks", [])),
        len(risk_assessment.get("high_risks", [])),
        len(risk_assessment.get("medium_risks", [])),
        len(risk_assessment.get("low_risks", []))
    ])

