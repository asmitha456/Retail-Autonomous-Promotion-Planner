# PromoPilot — Autonomous Promotion Planner

## Hackathon prototype
PromoPilot is an explainable, constraint-aware promotion planning agent for retail. It converts product, inventory, pricing, margin and customer-segment data into an executable promotion portfolio.

### Problem
Promotion planning requires balancing:
- revenue and profit
- minimum margin
- inventory clearance
- marketing budget
- customer segments
- competitor/seasonal context
- campaign duration and mechanism

### Solution
**Sense → Reason → Constrain → Simulate → Recommend**

1. Validate structured inputs and infer campaign context.
2. Generate promotion candidates across products, discounts, duration, audiences and mechanisms.
3. Apply hard business constraints.
4. Rank feasible candidates using expected profit + inventory clearance.
5. Select a portfolio within budget.
6. Simulate demand upside/downside.
7. Show the decision trace and confidence so business users can audit the recommendation.

### Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, usually `http://localhost:8501`.

### Run tests
```bash
pytest -q
```

### Docker
```bash
docker build -t promopilot .
docker run -p 8501:8501 promopilot
```

## Input schema
CSV columns:
`product_id, product, category, price, cost, inventory, base_daily_sales, discount_elasticity, min_margin_pct, segment`

## Demo scenario
Use the bundled sample CSV and context:
> Diwali festive campaign for India. Prioritize inventory clearance without damaging margin.

Then change the demand multiplier from 0.8x to 1.2x to show how expected units, revenue and profit change.

## Architecture
```text
              ┌──────────────────────┐
CSV / Context │ Inventory / Price    │
─────────────►│ Cost / Elasticity    │
              └──────────┬───────────┘
                         ▼
                 ┌───────────────┐
                 │ Sense Agent   │
                 │ validate +    │
                 │ infer context │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ Candidate     │
                 │ Generator     │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ Constraint    │
                 │ Engine        │
                 │ margin/budget │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ Optimizer     │
                 │ profit +      │
                 │ clearance    │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ Simulator     │
                 │ what-if       │
                 └───────┬───────┘
                         ▼
                 Explainable plan
```

## Why it is agentic
The prototype decomposes the task into decision stages rather than producing a single opaque answer. Each stage leaves an auditable trace and the planner can adapt to changing constraints and context.

## Production roadmap
- Connect ERP/inventory APIs and competitor-price feeds.
- Add LLM extraction for unstructured briefs and policy documents.
- Add ML demand forecasting and causal promotion uplift.
- Add geographic/store-level optimization.
- Add approval workflow and post-campaign learning loop.
- Add guardrails for price floors, legal claims and brand rules.
