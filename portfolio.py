from __future__ import annotations
from typing import List, Tuple
import math
from datetime import datetime

# A tiny, illustrative “allocator” to make the demo look legit.
# You can extend this with risk tiers, constraints, etc.

DEFAULT_POOL = [
    ("AAPL", "growth"),
    ("MSFT", "growth"),
    ("NVDA", "growth"),
    ("VOO",  "broad_etf"),
    ("VXUS", "intl_etf"),
    ("IEF",  "bonds"),
    ("SHY",  "bonds_short"),
    ("XLE",  "sector_energy"),
    ("XLV",  "sector_health"),
]

def months_between(start: str | None, end: str | None) -> int | None:
    if not start or not end: return None
    s = datetime.fromisoformat(start)
    e = datetime.fromisoformat(end)
    return (e.year - s.year) * 12 + (e.month - s.month)

def choose_allocation(budget: int | None, horizon_months: int | None, age: int | None) -> dict:
    """
    Very basic heuristic:
    - Short horizon or older age => more bonds
    - Long horizon & younger => more growth/ETF
    """
    if not budget or budget <= 0:
        budget = 5000  # default fallback

    # weights sum to 1.0
    if horizon_months and horizon_months < 12:
        weights = {"bonds": 0.60, "broad_etf": 0.30, "growth": 0.10}
    elif age and age >= 55:
        weights = {"bonds": 0.50, "broad_etf": 0.35, "growth": 0.15}
    else:
        weights = {"broad_etf": 0.45, "growth": 0.40, "bonds": 0.15}

    # Map categories to tickers in DEFAULT_POOL
    buckets = {
        "growth": [t for t,c in DEFAULT_POOL if c=="growth"],
        "broad_etf": [t for t,c in DEFAULT_POOL if c=="broad_etf"],
        "bonds": [t for t,c in DEFAULT_POOL if c in ("bonds","bonds_short")],
    }
    return {"budget": budget, "weights": weights, "buckets": buckets}

def budget_to_lots(budget: int, per_lot: int = 500) -> int:
    return max(1, budget // per_lot)

def allocate_positions(budget: int, weights: dict, buckets: dict) -> List[Tuple[str, int]]:
    lots = budget_to_lots(budget)
    alloc = []
    # proportional lots per bucket
    for cat, w in weights.items():
        cat_lots = max(0, round(lots * w))
        tickers = buckets.get(cat, [])
        if not tickers: continue
        # round-robin distribute
        i = 0
        for _ in range(cat_lots):
            alloc.append((tickers[i % len(tickers)], 1))
            i += 1
    # merge same tickers to quantities
    merged = {}
    for t,q in alloc:
        merged[t] = merged.get(t, 0) + q
    return sorted(merged.items())
