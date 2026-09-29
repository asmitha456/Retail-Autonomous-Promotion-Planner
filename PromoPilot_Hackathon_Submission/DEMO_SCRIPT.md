# 3-minute demo script — PromoPilot

## 0:00–0:20 — Hook
“Retail promotions look simple, but every discount is a constrained decision. We need to clear inventory without destroying margin, stay inside a marketing budget, and target the right customers. PromoPilot turns that into an autonomous, explainable planning workflow.”

## 0:20–0:45 — Inputs
“Here is our product dataset: inventory, price, cost, daily demand, discount elasticity, minimum margin and customer segment. I also give the agent a business brief: Diwali campaign, prioritize inventory clearance without damaging margin.”

## 0:45–1:20 — Generate
“I set a ₹10,000 marketing budget and a 20% minimum margin. When I click Generate, the planner validates the inputs, infers the campaign context, creates candidate combinations of product, discount, duration, audience and mechanism, then filters out infeasible options.”

Point at:
- selected products
- discount
- duration
- audience
- mechanism
- expected profit
- inventory clearance

## 1:20–1:55 — Explainability
“This is important: the system is not a black-box chatbot. It exposes a decision trace: inputs were validated, candidates generated, margin constraints applied, the portfolio was optimized under budget, and expected outcomes were simulated. Each recommendation also carries confidence and rationale.”

## 1:55–2:30 — What-if simulation
“Now I can stress-test the campaign. At 0.8x demand, I see a downside scenario. At 1.2x, I see the upside. This gives the business user a simple way to understand sensitivity before launch.”

## 2:30–2:50 — Export
“I can download the recommended promotion portfolio as CSV for the next workflow.”

## 2:50–3:10 — Close
“PromoPilot is built around a simple principle: Sense the business context, reason over alternatives, enforce constraints, simulate outcomes, and recommend an auditable plan. The prototype is deliberately modular so the deterministic baseline can be upgraded with LLM extraction, ML demand forecasting and live enterprise data.”
