import pytest
from backend.services.validation import SourceValidator

def test_source_credibility_assessment():
    """Test source credibility scoring"""
    validator = SourceValidator()
    
    # Test government source
    assert validator._assess_source_credibility("https://sec.gov/filing") >= 0.9
    
    # Test educational source
    assert validator._assess_source_credibility("https://mit.edu/research") >= 0.9
    
    # Test news source
    assert validator._assess_source_credibility("https://reuters.com/article") >= 0.85
    
    # Test unknown source
    assert validator._assess_source_credibility("https://random-blog.com") < 0.7


def test_red_flag_detection():
    """Test red flag detection"""
    validator = SourceValidator()
    
    test_text = """
    John Doe was convicted of fraud in 2019 and faced an SEC investigation.
    The company filed for bankruptcy amid money laundering allegations.
    """
    
    red_flags = validator.detect_red_flags(test_text)
    
    assert len(red_flags) > 0
    assert any("fraud" in flag["keyword"] for flag in red_flags)
    assert any("investigation" in flag["keyword"] for flag in red_flags)


def test_date_relevance_assessment():
    """Test date relevance scoring"""
    validator = SourceValidator()
    
    # Recent date should have high score
    recent_score = validator.assess_date_relevance("2024-01-01")
    assert recent_score > 0.8
    
    # Old date should have lower score
    old_score = validator.assess_date_relevance("2010-01-01")
    assert old_score < 0.7
    
    # No date should have moderate penalty
    no_date_score = validator.assess_date_relevance("")
    assert no_date_score == 0.7


@pytest.mark.asyncio
async def test_content_support_fact():
    """Test if content supports a fact"""
    validator = SourceValidator()
    
    fact = "John Doe is CEO of TechCorp"
    supporting_content = "According to the latest filing, John Doe serves as Chief Executive Officer of TechCorp"
    non_supporting_content = "The weather is nice today and birds are singing"
    
    assert validator._content_supports_fact(fact.lower(), supporting_content.lower())
    assert not validator._content_supports_fact(fact.lower(), non_supporting_content.lower())


def test_confidence_calculation():
    """Test overall confidence calculation"""
    validator = SourceValidator()
    
    test_facts = [
        {"confidence": 0.9, "verified": True},
        {"confidence": 0.8, "verified": True},
        {"confidence": 0.6, "verified": False},
        {"confidence": 0.7, "verified": True}
    ]
    
    metrics = validator.calculate_overall_confidence(test_facts)
    
    assert "average_confidence" in metrics
    assert "verified_ratio" in metrics
    assert "high_confidence_ratio" in metrics
    assert 0 <= metrics["average_confidence"] <= 1
    assert 0 <= metrics["verified_ratio"] <= 1

