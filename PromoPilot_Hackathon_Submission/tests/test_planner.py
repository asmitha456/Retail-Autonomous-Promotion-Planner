
import pandas as pd
from planner import plan_promotions, simulate

def test_planner_respects_budget_and_returns_plan():
    p = pd.read_csv("sample_data/products.csv")
    plan, summary = plan_promotions(p, marketing_budget=10000, min_margin_pct=20, target_clearance_pct=35, notes="Diwali")
    assert summary["marketing_spend"] <= 10000.01
    assert (plan["expected_profit"] >= 0).all() if not plan.empty else True

def test_simulation_changes_with_demand():
    p = pd.read_csv("sample_data/products.csv")
    plan, _ = plan_promotions(p)
    if not plan.empty:
        low = simulate(plan, 0.8)
        high = simulate(plan, 1.2)
        assert high["units"] >= low["units"]
