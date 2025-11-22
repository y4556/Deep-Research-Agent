# 🎯 Architecture Quick Reference

## Visual Diagrams

### LangGraph Workflow (Actual Graph)

```bash
# Visualize the ACTUAL compiled LangGraph
python visualize_langgraph.py

# Generates:
# - ASCII diagram (always works, shows exact structure)
# - Mermaid diagram (view at mermaid.live)
# - PNG image (if graphviz installed)
```

### System Architecture Diagrams

```bash
# Generate additional architecture diagrams
pip install networkx matplotlib
python visualize_architecture.py

# Creates:
# 1. system_architecture.png - Frontend, Backend, Services, External APIs
# 2. node_model_mapping.png - Which AI model handles each node
# 3. data_flow.png - How data flows through the system
```

**Recommendation**: Start with `visualize_langgraph.py` to see the actual graph!

---

## 🔄 The 9 Nodes (in order)

| # | Node | What It Does | AI Model | Input | Output |
|---|------|--------------|----------|-------|--------|
| 1 | **Research Planner** | Creates strategic plan | Claude Opus | target_entity | research_plan |
| 2 | **Query Generator** | Generates search queries | GPT-4 | research_plan, gaps | search_queries |
| 3 | **Search Executor** | Searches Tavily/DDG | None | search_queries | raw_search_results |
| 4 | **Fact Extractor** | Extracts structured facts | Claude Sonnet | raw_results | extracted_facts |
| 5 | **Source Validator** | Validates & scores facts | None (Service) | extracted_facts | verified_facts |
| 6 | **Connection Mapper** | Maps relationships | GPT-4 | verified_facts | connections |
| 7 | **Risk Assessor** | Identifies risks | Claude Opus | facts, connections | risks_flagged |
| 8 | **Research Reflector** | Identifies gaps | Gemini Pro | all data | knowledge_gaps |
| 9 | **Report Synthesizer** | Generates report | Claude Opus | all data | final_report |

**Note:** Steps 2-8 can loop up to `max_depth` times based on Decision Point logic.

---

## 🎯 AI Model Strategy

```
📊 Task Assignment Logic:

Claude Opus (Most Capable)
├─ Planning          → Strategic thinking
├─ Risk Assessment   → Critical analysis
└─ Report Synthesis  → Quality writing

GPT-4 (Reliable & Structured)
├─ Query Generation  → Precise queries
└─ Connection Mapping → Structured extraction

Claude Sonnet (Cost-Effective)
└─ Fact Extraction   → High volume processing

Gemini Pro (Diverse Perspective)
└─ Research Reflection → Alternative viewpoint
```

---

## 🗂️ File Structure at a Glance

```
backend/core/
├─ config.py      → All settings & environment vars
├─ state.py       → ResearchState TypedDict + models
├─ models.py      → MultiModelCoordinator (4 AI models)
├─ nodes.py       → All 9 node implementations
└─ graph.py       → ResearchWorkflow orchestration

backend/services/
├─ search.py      → Tavily + DuckDuckGo integration
├─ validation.py  → SourceValidator (90+ domains)
└─ langsmith_client.py → Monitoring & tracing

backend/api/
└─ routes.py      → 5 FastAPI endpoints

frontend/
├─ app.py         → Main Streamlit app
├─ components/    → UI components (4 files)
└─ utils/         → API client wrapper
```

---

## 🔌 External Services Used

| Service | Purpose | Cost | Required? |
|---------|---------|------|-----------|
| **OpenAI** | GPT-4 for queries & connections | ~$0.50/run | ✅ Yes |
| **Anthropic** | Claude for planning & analysis | ~$0.80/run | ✅ Yes |
| **Google** | Gemini for reflection | ~$0.10/run | ✅ Yes |
| **Tavily** | Primary search engine | ~$0.05/run | ✅ Yes |
| **LangSmith** | Monitoring & debugging | Free tier | ✅ Recommended |
| **DuckDuckGo** | Fallback search | Free | No (automatic) |
| **Serper** | Alternative search | ~$0.10/run | No (optional) |

---

## 📊 ResearchState Schema

The state that flows through all nodes:

```python
{
  # What we're researching
  "target_entity": "John Doe - CEO",
  "research_session_id": "uuid",
  
  # Plan & queries
  "research_plan": ["Phase 1: ...", "Phase 2: ..."],
  "search_queries": ["query 1", "query 2", ...],
  
  # Results & findings
  "raw_search_results": [{...}, {...}],
  "extracted_facts": [{content, category, confidence}, ...],
  "verified_facts": [{...verified...}, ...],
  "connections": [{source, target, relationship}, ...],
  "risks_flagged": [{type, severity, description}, ...],
  
  # Quality metrics
  "confidence_scores": {average, verified_ratio, ...},
  
  # Control flow
  "research_depth": 2,      # Current iteration
  "max_depth": 3,           # Stop condition
  "next_step": "continue",  # or "finalize"
  "knowledge_gaps": ["Missing info about X", ...],
  "current_focus": "financial investigation",
  
  # Tracking
  "model_decisions": {...},
  "start_time": "2024-01-01T12:00:00",
  "langsmith_session_id": "trace-id"
}
```

---

## 🚦 Decision Point Logic

After Risk Assessor node, the workflow decides whether to continue:

```python
def should_continue_research(state):
    # Stop if max depth reached
    if depth >= max_depth:
        return "finalize"
    
    # Stop if no new facts found recently
    if recent_facts < 2:
        return "finalize"
    
    # Deep dive if critical gaps exist
    if high_priority_gaps and depth < max_depth - 1:
        return "deep_dive"
    
    # Continue if making progress
    if depth < 2 or recent_facts >= 3:
        return "continue"
    
    return "finalize"
```

---

## 🔍 Source Validation

How we assess source credibility:

```
Government (.gov, .mil)      → 1.0 (100%)
Educational (.edu)           → 0.95 (95%)
Major News (Reuters, AP)     → 0.85-0.9
Financial (SEC, FINRA)       → 0.9-1.0
Professional (LinkedIn)      → 0.7
Unknown domains              → 0.3-0.5

Red Flags Detected:
✓ fraud, investigation, lawsuit
✓ bankruptcy, sanction, violation
✓ money laundering, corruption
✓ + 15 more keywords
```

---

## ⚡ Performance Metrics

**Typical Research (Depth 3)**
- Duration: 15-25 minutes
- API Calls: 43-60 total
  - Search: 15-20 calls
  - OpenAI: 10-15 calls
  - Anthropic: 15-20 calls
  - Google: 3-5 calls
- Cost: $1.45-$3.00
- Facts Found: 10-20 verified
- Risks Identified: 3-8

**Scaling**
- Depth 1: 5-8 min, $0.50-1
- Depth 2: 10-15 min, $1-2
- Depth 3: 15-25 min, $1.50-3
- Depth 4: 25-35 min, $3-5
- Depth 5: 35-50 min, $5-8

---

## 🛠️ Key Configuration

**Environment Variables (.env)**
```bash
# Must have
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
TAVILY_API_KEY=tvly-...
LANGSMITH_API_KEY=ls__...

# Tuning
MAX_RESEARCH_DEPTH=3        # How many iterations
DEFAULT_SEARCH_RESULTS=5    # Results per query
RATE_LIMIT_REQUESTS=100     # Requests per minute
```

**Code Configuration (backend/core/config.py)**
```python
settings.MAX_RESEARCH_DEPTH      # Max iterations (3)
settings.DEFAULT_SEARCH_RESULTS  # Results/query (5)
settings.RATE_LIMIT_REQUESTS     # Rate limit (100/min)
```

---

## 🔧 Key Extension Points

**Add a New Node**
```python
# In backend/core/nodes.py
class YourNode(BaseNode):
    async def execute(self, state: ResearchState):
        # Your logic
        return updated_state

# In backend/core/graph.py
workflow.add_node("your_node", YourNode().execute)
workflow.add_edge("previous_node", "your_node")
```

**Add a New AI Model**
```python
# In backend/core/models.py
self.models["your_model"] = YourModelClass(...)
self.task_assignments["your_task"] = "your_model"
```

**Add a New Search Engine**
```python
# In backend/services/search.py
class YourSearchEngine:
    async def search(self, query): ...

# Add to DeepSearchEngine
self.your_engine = YourSearchEngine()
```

---

## 📞 Quick Commands

```bash
# Start backend
cd backend && python main.py

# Start frontend
cd frontend && streamlit run app.py

# Run tests
pytest tests/unit/

# Generate diagrams
python visualize_architecture.py

# Run evaluation
cd evaluation && python run_evaluation.py

# View API docs
# Open: http://localhost:8000/docs

# View LangSmith traces
# Open: https://smith.langchain.com
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Module not found" | Activate venv: `source venv/bin/activate` |
| LangSmith not tracing | Check `LANGCHAIN_TRACING_V2=true` in .env |
| Search rate limits | Reduce `MAX_RESEARCH_DEPTH` or add delays |
| Frontend can't connect | Ensure backend running on port 8000 |
| Out of memory | Reduce `max_depth` or `DEFAULT_SEARCH_RESULTS` |

---

## 📚 Documentation Files

- **README.md** - Complete project documentation
- **ARCHITECTURE.md** - Detailed architecture (this is the full version!)
- **IMPROVEMENT_PLAN.md** - Analysis & future improvements
- **SETUP_GUIDE.md** - Quick setup instructions
- **evaluation/README.md** - Evaluation system guide
- **tests/README.md** - Testing guide

---

## 🎓 Learning Path

1. **Understand the State** - Read `backend/core/state.py`
2. **See the Flow** - Check `backend/core/graph.py`
3. **Read One Node** - Start with `ResearchPlanner` in `nodes.py`
4. **Trace Execution** - Run a research and watch LangSmith
5. **Modify a Prompt** - Tune prompts in `nodes.py`
6. **Add a Feature** - Create a new node or service

---

**Full details in ARCHITECTURE.md**

