
import streamlit as st
import pandas as pd
import numpy as np
from planner import plan_promotions, simulate

st.set_page_config(page_title="PromoPilot", page_icon="🚀", layout="wide")

st.title("🚀 PromoPilot — Autonomous Promotion Planner")
st.caption("Constraint-aware promotion planning with explainable decisions and what-if simulation.")

with st.sidebar:
    st.header("Campaign constraints")
    budget = st.number_input("Marketing budget (₹)", min_value=500.0, value=10000.0, step=500.0)
    min_margin = st.slider("Minimum margin (%)", 5, 50, 20)
    clearance = st.slider("Target inventory clearance (%)", 10, 100, 35)
    notes = st.text_area("Business context", "Diwali festive campaign for India. Prioritize inventory clearance without damaging margin.")
    uploaded = st.file_uploader("Upload product CSV", type=["csv"])

if uploaded:
    products = pd.read_csv(uploaded)
else:
    products = pd.read_csv("sample_data/products.csv")

st.subheader("1. Inputs")
st.dataframe(products, use_container_width=True, hide_index=True)

if st.button("✨ Generate autonomous promotion plan", type="primary", use_container_width=True):
    with st.spinner("Agent is validating inputs, generating candidates, applying constraints and simulating demand..."):
        plan, summary = plan_promotions(products, budget, min_margin, clearance, notes)
    st.session_state["plan"] = plan
    st.session_state["summary"] = summary

if "plan" in st.session_state:
    plan = st.session_state["plan"]
    summary = st.session_state["summary"]

    st.subheader("2. Agent decision")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Campaigns", summary["campaigns"])
    c2.metric("Expected revenue", f"₹{summary['revenue']:,.0f}")
    c3.metric("Expected profit", f"₹{summary['profit']:,.0f}")
    c4.metric("Budget used", f"₹{summary['marketing_spend']:,.0f}")

    st.info(f"Context inferred: **{summary['context']['season']}** | Geography: **{summary['context']['geography']}** | Input confidence: **{summary['context']['confidence']*100:.0f}%**")

    if plan.empty:
        st.warning("No feasible campaign met the current constraints. Increase budget or relax the margin/clearance target.")
    else:
        display_cols = ["product","category","discount_pct","duration_days","audience","mechanism",
                        "expected_units","expected_revenue","expected_profit","inventory_cleared_pct","confidence"]
        st.dataframe(plan[display_cols].rename(columns={
            "discount_pct":"Discount %","duration_days":"Days","audience":"Audience",
            "mechanism":"Mechanism","expected_units":"Units","expected_revenue":"Revenue ₹",
            "expected_profit":"Profit ₹","inventory_cleared_pct":"Inventory cleared %",
            "confidence":"Confidence"}), use_container_width=True, hide_index=True)

        st.subheader("3. Decision trace")
        for i, step in enumerate(summary["decision_trace"], 1):
            st.write(f"**{i}.** {step}")

        st.subheader("4. What-if simulation")
        demand = st.slider("Demand multiplier", 0.60, 1.60, 1.00, 0.05)
        sim = simulate(plan, demand)
        a,b,c = st.columns(3)
        a.metric("Simulated units", f"{sim['units']:,}")
        b.metric("Simulated revenue", f"₹{sim['revenue']:,.0f}")
        c.metric("Simulated profit", f"₹{sim['profit']:,.0f}")

        st.download_button("Download promotion plan CSV",
                           plan.to_csv(index=False).encode("utf-8"),
                           "promotion_plan.csv", "text/csv")
else:
    st.markdown("""
### How the prototype works
**Sense → Reason → Constrain → Simulate → Recommend**

- **Sense:** reads inventory, pricing, costs, elasticity and customer segments.
- **Reason:** generates multiple discount/duration/mechanism/audience combinations.
- **Constrain:** removes options below minimum margin and keeps spend under budget.
- **Simulate:** estimates units, revenue and profit under demand scenarios.
- **Recommend:** returns an auditable plan with confidence and rationale.
""")
