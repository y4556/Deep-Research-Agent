# Tests

## Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── unit/                 # Unit tests (fast, no external dependencies)
│   ├── test_nodes.py
│   ├── test_validation.py
│   └── test_search.py
├── integration/          # Integration tests (require backend services)
│   ├── test_workflow.py
│   └── test_api.py
└── e2e/                  # End-to-end tests (require full system)
    └── test_full_research.py
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/ -m integration
```

### With Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Specific Test File
```bash
pytest tests/unit/test_validation.py
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (default)
- `@pytest.mark.integration` - Integration tests (require services)
- `@pytest.mark.e2e` - End-to-end tests (require full system)
- `@pytest.mark.asyncio` - Async tests

## Writing Tests

### Unit Test Example
```python
def test_source_credibility():
    validator = SourceValidator()
    score = validator._assess_source_credibility("https://sec.gov")
    assert score >= 0.9
```

### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow():
    workflow = ResearchWorkflow()
    result = await workflow.conduct_research("Test Entity", max_depth=1)
    assert result["research_depth"] >= 1
```

## Notes

- Integration and E2E tests are skipped by default (require API keys)
- Use fixtures from `conftest.py` for common test data
- Mock external API calls in unit tests

