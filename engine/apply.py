"""Apply a parsed transaction to state, compute before/after impact."""
from __future__ import annotations
import copy
import datetime as dt

from .model import simulate, house_readiness
from .calculations import fv_lumpsum


def _house_date(state, profile, assumptions):
    snaps = simulate(state, profile, assumptions, months=180, salary_scenario="base")
    r = house_readiness(snaps, profile, assumptions, "base", "base")
    return (r["date"] if r else None), snaps[119], snaps


def apply_transaction(state: dict, profile: dict, assumptions: dict, action: dict) -> tuple[dict, dict]:
    before_date, before_10y, before_snaps = _house_date(state, profile, assumptions)
    before_m1 = before_snaps[0]

    new_state = copy.deepcopy(state)
    amt = action.get("amount") or 0
    today = dt.date.today().isoformat()
    log_entry = {"date": today, "raw": action.get("raw"), "type": action["type"], "amount": amt}
    note = None

    if action["type"] == "expense_onetime":
        new_state["one_time_deduction"] = new_state.get("one_time_deduction", 0) + amt
        log_entry["category"] = "one_time"
    elif action["type"] == "salary_set":
        log_entry["old_take_home"] = new_state["take_home"]
        new_state["take_home"] = amt
    elif action["type"] == "expense_recurring_set":
        cat = action["category"]
        log_entry["category"] = cat
        log_entry["old_value"] = new_state["expenses"].get(cat, 0)
        new_state["expenses"][cat] = amt
    elif action["type"] == "expense_recurring_delta":
        cat = action["category"]
        log_entry["category"] = cat
        new_state["expenses"][cat] = new_state["expenses"].get(cat, 0) + amt
    elif action["type"] == "invest":
        bucket = action.get("bucket", "long_term_wealth")
        new_state["buckets"][bucket] = new_state["buckets"].get(bucket, 0) + amt
        log_entry["bucket"] = bucket
    elif action["type"] == "bonus":
        split = assumptions["allocation_policy_default"]["post_emergency_split"]
        gap = max(0, assumptions["emergency_fund"]["initial_target_floor"] - new_state["buckets"]["emergency"])
        to_emerg = min(gap, amt)
        rest = amt - to_emerg
        new_state["buckets"]["emergency"] += to_emerg
        new_state["buckets"]["house"] += rest * split["house"]
        new_state["buckets"]["long_term_wealth"] += rest * split["long_term_wealth"]
        new_state["buckets"]["retirement_voluntary"] += rest * split["retirement_voluntary"]
    elif action["type"] == "new_emi":
        new_state["debts"].append({"principal": 0, "rate": 0, "tenure_months": 999999, "start_month": 0, "emi": amt})
    elif action["type"] == "bike_purchase":
        price = amt or new_state["bike"]["target"]
        avail = new_state["buckets"]["bike"]
        shortfall = max(0, price - avail)
        new_state["buckets"]["bike"] = max(0, avail - price)
        new_state["bike"]["done"] = True
        if shortfall:
            new_state["one_time_deduction"] = new_state.get("one_time_deduction", 0) + shortfall
        note = f"Bike bucket had Rs {round(avail):,}; shortfall Rs {round(shortfall):,} taken from this month's surplus." if shortfall else None
    elif action["type"] == "house_plan":
        new_state["house_plan_override"] = {"target_price": amt, "year": action.get("year")}
    else:
        note = "Could not confidently parse this as a financial transaction -- no state change made."

    new_state["transactions"] = state.get("transactions", []) + [log_entry]

    after_date, after_10y, after_snaps = _house_date(new_state, profile, assumptions)
    after_m1 = after_snaps[0]

    impact = {
        "surplus_before": before_m1["surplus"], "surplus_after": after_m1["surplus"],
        "net_worth_10y_before": before_10y["net_worth"], "net_worth_10y_after": after_10y["net_worth"],
        "house_date_before": before_date, "house_date_after": after_date,
        "note": note,
    }
    if action["type"] == "expense_onetime" and amt:
        for label, years in (("5y", 5), ("10y", 10)):
            impact[f"opportunity_cost_{label}"] = round(fv_lumpsum(amt, assumptions["instrument_returns_annual"]["index_fund_equity"]["value"], years))
    return new_state, impact
