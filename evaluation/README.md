# Evaluation System

## Overview

The evaluation system tests the Deep Research Agent's performance on predefined test personas with known "hidden facts" that the agent should discover.

## Test Personas

### 1. Timothy Overturf (High Difficulty)
- **Category**: Business Executive
- **Hidden Facts**: 5 facts worth 110 points total
- **Key Challenges**: Shell companies, SEC investigation, offshore connections
- **Expected Discovery Rate**: 75%

### 2. Maria Rodriguez (Medium Difficulty)
- **Category**: Tech Entrepreneur
- **Hidden Facts**: 7 facts worth 105 points total
- **Key Challenges**: Patent disputes, funding history, layoffs
- **Expected Discovery Rate**: 70%

### 3. Blackstone Capital LLC (Very High Difficulty)
- **Category**: Investment Firm
- **Hidden Facts**: 8 facts worth 215 points total
- **Key Challenges**: Offshore structures, beneficial ownership, Paradise Papers
- **Expected Discovery Rate**: 60%

## Running Evaluations

### Quick Start

```bash
cd evaluation
python run_evaluation.py
```

### What It Does

1. Runs research on each test persona
2. Compares findings against ground truth
3. Calculates performance scores
4. Generates detailed report
5. Saves results to `results/` directory

### Expected Runtime

- **Timothy Overturf**: 15-20 minutes
- **Maria Rodriguez**: 12-15 minutes
- **Blackstone Capital**: 20-30 minutes
- **Total**: ~45-65 minutes

### Costs

Approximate API costs per full evaluation:
- OpenAI (GPT-4): $2-4
- Anthropic (Claude): $3-5
- Google (Gemini): $1-2
- Search APIs: $0.50-1
- **Total**: ~$6.50-12 per complete evaluation run

## Evaluation Metrics

### Fact Discovery Score (35-40% weight)
Measures how many hidden facts were discovered
- Points awarded for each fact found
- Weighted by difficulty
- Bonus for discovering very difficult facts

### Risk Assessment Score (25-30% weight)
Evaluates risk identification accuracy
- Did it identify expected risk types?
- Correct severity classification?
- Quality of evidence provided?

### Source Validation Score (20% weight)
Assesses quality of source verification
- Credibility of sources cited
- Cross-referencing thoroughness
- Confidence scoring accuracy

### Connection Mapping Score (15% weight)
Measures relationship mapping completeness
- Key entities identified
- Relationship types correct
- Network completeness

### Efficiency Score (2-5% weight)
Evaluates resource usage
- Time to completion
- API calls made
- Cost effectiveness

## Interpreting Results

### Overall Scores

- **90-100%**: Excellent - Agent performed exceptionally
- **80-89%**: Very Good - Strong performance with minor gaps
- **70-79%**: Good - Acceptable performance, some improvements needed
- **60-69%**: Adequate - Meets minimum requirements
- **Below 60%**: Needs Improvement - Significant issues to address

### By Difficulty

- **Very High Difficulty**: 60% is good, 70%+ is excellent
- **High Difficulty**: 70% is good, 80%+ is excellent
- **Medium Difficulty**: 75% is good, 85%+ is excellent

## Output Files

### JSON Results
```json
{
  "evaluation_run": {
    "timestamp": "2024-01-01T12:00:00",
    "total_personas": 3,
    "successful_evaluations": 3
  },
  "results": [
    {
      "profile_name": "Timothy Overturf",
      "overall_score": 0.78,
      "detailed_scores": { ... },
      "facts_found": 12,
      "risks_identified": 6,
      ...
    }
  ]
}
```

## Adding New Test Personas

### 1. Create Profile File

```python
# evaluation/your_persona.py

YOUR_PERSONA_PROFILE = {
    "name": "Person Name",
    "description": "Brief description",
    "category": "category",
    "difficulty": "medium|high|very_high",
    
    "hidden_facts": [
        {
            "id": "fact_1",
            "content": "Fact description",
            "category": "financial|legal|professional|personal",
            "confidence_required": 0.8,
            "search_difficulty": "low|medium|high|very_high",
            "verification_sources": ["source1", "source2"],
            "points": 20
        }
    ],
    
    "expected_risks": [ ... ],
    "evaluation_criteria": { ... }
}

def evaluate_your_persona_research(report):
    # Evaluation logic
    pass
```

### 2. Add to Runner

Edit `run_evaluation.py`:

```python
from your_persona import YOUR_PERSONA_PROFILE, evaluate_your_persona_research

# In EvaluationRunner.__init__:
self.test_personas.append({
    "profile": YOUR_PERSONA_PROFILE,
    "evaluator": evaluate_your_persona_research
})
```

## Best Practices

### Designing Test Personas

1. **Mix Difficulty Levels**: Include easy, medium, and hard personas
2. **Diverse Categories**: Cover individuals, companies, organizations
3. **Real-World Scenarios**: Base on actual due diligence needs
4. **Verifiable Facts**: Use facts that can actually be found online
5. **Clear Criteria**: Define explicit success metrics

### Fact Selection

- **Publicly Available**: Must be discoverable via search
- **Specific**: Clear, verifiable claims (not vague)
- **Diverse Categories**: Cover multiple investigation areas
- **Varying Difficulty**: Mix easy-to-find and deeply hidden facts
- **Point Weighting**: More points for difficult-to-discover facts

### Running Evaluations

- **Regular Cadence**: Run after major changes
- **Baseline Establishment**: Run multiple times to establish baseline
- **Track Over Time**: Monitor improvement/regression
- **Cost Monitoring**: Track API costs per evaluation
- **Compare Configurations**: Test different depth settings, models, etc.

## Troubleshooting

### Low Fact Discovery Scores

- Check search query quality (are they specific enough?)
- Review prompt engineering (are instructions clear?)
- Verify search APIs are working (rate limits, quotas)
- Increase research depth if needed

### Poor Risk Assessment

- Review risk assessment prompts
- Check if risk patterns are too generic
- Ensure evidence is being properly extracted
- Verify severity classification logic

### Source Validation Issues

- Check source credibility database completeness
- Review cross-referencing logic
- Ensure confidence scoring is calibrated
- Verify URL parsing works correctly

## Future Enhancements

- [ ] Automated regression testing
- [ ] Comparison with baseline performance
- [ ] Cost tracking and optimization
- [ ] Parallel execution of evaluations
- [ ] Web dashboard for results visualization
- [ ] Historical performance tracking
- [ ] A/B testing different configurations
- [ ] Integration with CI/CD pipeline

