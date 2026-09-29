
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import math
import pandas as pd

@dataclass
class Plan:
    product_id: str
    product: str
    category: str
    discount_pct: float
    duration_days: int
    audience: str
    mechanism: str
    expected_units: int
    expected_revenue: float
    expected_profit: float
    inventory_cleared_pct: float
    marketing_cost: float
    score: float
    confidence: float
    rationale: List[str]

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

def infer_inputs(products: pd.DataFrame, notes: str = "") -> Dict[str, Any]:
    """Extracts/infers campaign context with explicit confidence."""
    notes_l = (notes or "").lower()
    season = "General"
    for key, val in [
        ("diwali", "Diwali"), ("christmas", "Christmas"),
        ("summer", "Summer"), ("back to school", "Back-to-School"),
        ("new year", "New Year"), ("festive", "Festive")
    ]:
        if key in notes_l:
            season = val
            break
    geography = "All"
    for g in ["north", "south", "east", "west", "metro", "tier-2"]:
        if g in notes_l:
            geography = g.title()
            break
    confidence = 0.92 if notes.strip() else 0.78
    return {
        "season": season,
        "geography": geography,
        "confidence": confidence,
        "notes_used": bool(notes.strip())
    }

def _candidate(product, discount, audience, mechanism, duration, market_factor=1.0):
    price = float(product["price"])
    cost = float(product["cost"])
    inv = int(product["inventory"])
    base_daily = float(product["base_daily_sales"])
    elasticity = float(product["discount_elasticity"])
    margin_min = float(product["min_margin_pct"])
    demand = base_daily * duration
    lift = 1 + elasticity * (discount / 10.0) * market_factor
    expected_units = min(inv, max(1, int(round(demand * lift))))
    sell_price = price * (1 - discount/100)
    unit_profit = sell_price - cost
    revenue = expected_units * sell_price
    profit = expected_units * unit_profit
    clear = expected_units / inv * 100
    marketing_cost = 0.0
    # simple audience/mechanism cost model
    if mechanism == "Targeted coupon":
        marketing_cost = 0.012 * revenue
    elif mechanism == "Bundle":
        marketing_cost = 0.008 * revenue
    else:
        marketing_cost = 0.005 * revenue
    score = profit + 0.25 * revenue * min(clear/100, 1.0)
    reasons = []
    if clear >= 40: reasons.append(f"clears ~{clear:.0f}% of available inventory")
    if discount <= 15: reasons.append("keeps discount within a controlled range")
    if unit_profit / price * 100 >= margin_min: reasons.append("meets minimum margin constraint")
    if audience != "All customers": reasons.append(f"focuses on {audience.lower()}")
    return Plan(
        product_id=str(product["product_id"]),
        product=str(product["product"]),
        category=str(product["category"]),
        discount_pct=float(discount),
        duration_days=int(duration),
        audience=audience,
        mechanism=mechanism,
        expected_units=expected_units,
        expected_revenue=round(revenue,2),
        expected_profit=round(profit-marketing_cost,2),
        inventory_cleared_pct=round(clear,1),
        marketing_cost=round(marketing_cost,2),
        score=round(score,2),
        confidence=0.90 if unit_profit / price * 100 >= margin_min else 0.45,
        rationale=reasons
    )

def plan_promotions(products: pd.DataFrame, marketing_budget: float = 10000,
                    min_margin_pct: float = 20, target_clearance_pct: float = 35,
                    notes: str = "") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Deterministic agentic planner:
    1) validates/infers inputs
    2) generates candidate actions
    3) filters hard constraints
    4) scores candidates
    5) selects a portfolio under budget
    6) simulates expected outcomes
    """
    required = ["product_id","product","category","price","cost","inventory",
                "base_daily_sales","discount_elasticity","min_margin_pct","segment"]
    missing = [c for c in required if c not in products.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    context = infer_inputs(products, notes)
    rows = []
    audiences = ["All customers", "Loyal customers", "Price-sensitive", "High-value"]
    mechanisms = ["Targeted coupon", "Bundle", "Flash sale"]
    durations = [3, 5, 7]
    discounts = [5, 10, 15, 20, 25]

    for _, p in products.iterrows():
        # Keep products that can satisfy the margin floor at at least one discount.
        for d in discounts:
            sell_margin = (float(p["price"])*(1-d/100)-float(p["cost"])) / float(p["price"]) * 100
            if sell_margin < max(min_margin_pct, float(p["min_margin_pct"])):
                continue
            for aud in audiences:
                for mech in mechanisms:
                    for dur in durations:
                        c = _candidate(p, d, aud, mech, dur)
                        if c.inventory_cleared_pct >= target_clearance_pct or c.expected_profit > 0:
                            rows.append(c)

    # Select at most one campaign per product, maximizing profit + clearance,
    # while keeping total marketing cost within budget.
    rows.sort(key=lambda x: (x.score, x.expected_profit), reverse=True)
    selected = []
    used_products = set()
    budget = 0.0
    for c in rows:
        if c.product_id in used_products:
            continue
        if budget + c.marketing_cost <= marketing_budget:
            selected.append(c)
            used_products.add(c.product_id)
            budget += c.marketing_cost

    # If nothing selected, explain why.
    result = pd.DataFrame([asdict(x) for x in selected])
    if result.empty:
        result = pd.DataFrame(columns=["product_id","product","category","discount_pct",
            "duration_days","audience","mechanism","expected_units","expected_revenue",
            "expected_profit","inventory_cleared_pct","marketing_cost","score","confidence","rationale"])

    total_profit = float(result["expected_profit"].sum()) if not result.empty else 0
    total_revenue = float(result["expected_revenue"].sum()) if not result.empty else 0
    total_clear = float(result["inventory_cleared_pct"].mean()) if not result.empty else 0
    summary = {
        "context": context,
        "campaigns": len(result),
        "revenue": round(total_revenue,2),
        "profit": round(total_profit,2),
        "marketing_spend": round(budget,2),
        "avg_inventory_clearance_pct": round(total_clear,1),
        "constraints": {
            "min_margin_pct": min_margin_pct,
            "marketing_budget": marketing_budget,
            "target_clearance_pct": target_clearance_pct
        },
        "decision_trace": [
            "Inputs validated and campaign context inferred",
            "Candidate discounts, durations, mechanisms and audiences generated",
            "Candidates violating the margin floor removed",
            "Candidates ranked on expected profit and inventory clearance",
            "Portfolio selected under marketing-budget constraint",
            "Scenario simulation calculated from demand elasticity"
        ]
    }
    return result, summary

def simulate(plan_df: pd.DataFrame, demand_multiplier: float = 1.0) -> Dict[str, float]:
    if plan_df is None or plan_df.empty:
        return {"revenue": 0, "profit": 0, "units": 0}
    units = (plan_df["expected_units"] * demand_multiplier).round().astype(int)
    revenue = (units * (plan_df["expected_revenue"]/plan_df["expected_units"]).replace([math.inf, -math.inf], 0)).sum()
    # Keep costs roughly proportional to units
    unit_profit = (plan_df["expected_profit"] / plan_df["expected_units"]).replace([math.inf, -math.inf], 0)
    profit = (units * unit_profit).sum()
    return {"revenue": round(float(revenue),2), "profit": round(float(profit),2), "units": int(units.sum())}
