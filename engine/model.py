"""Month-by-month interconnected simulation engine."""
from __future__ import annotations
import copy
import datetime as dt

from .calculations import compound_monthly, emi, outstanding_balance
from .house import house_cost_future, affordability, readiness_check

BUCKETS = ["emergency", "bike", "house", "long_term_wealth", "retirement_voluntary", "car", "marriage", "other"]


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def add_months(d: dt.date, n: int) -> dt.date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, 28)
    return dt.date(y, m, day)


def months_between(d1: dt.date, d2: dt.date) -> int:
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def default_state(profile: dict) -> dict:
    as_of = profile["as_of"]
    temp = profile["temporary_phase"]["expenses"]
    return {
        "as_of": as_of,
        "buckets": {b: 0.0 for b in BUCKETS},
        "epf_balance": 0.0,
        "debts": [],
        "take_home": profile["income"]["take_home_monthly"],
        "epf_employee_monthly": profile["income"]["epf_employee_monthly"],
        "expenses": dict(temp),
        "phase_switched": False,
        "bike": {
            "target": profile["goals"]["bike"]["target"],
            "done": False,
            "deadline": add_months(parse_date(as_of), profile["goals"]["bike"]["years_from_now"] * 12).isoformat(),
            "redirect_amount": 0.0,
        },
        "transactions": [],
    }


def _essential_total(expenses: dict) -> float:
    keys = ("household", "family_support", "medical")
    return sum(expenses.get(k, 0) for k in keys)


def bucket_return_rate(bucket: str, assumptions: dict, years_elapsed: float = 0.0) -> float:
    r = assumptions["instrument_returns_annual"]
    if bucket == "emergency":
        return r["liquid_debt_fund"]["value"]
    if bucket == "bike":
        return r["liquid_debt_fund"]["value"]
    if bucket == "house":
        # glide path: assume ~8yr horizon at t=0, de-risking as time passes (section 7 framework)
        years_to_target = max(0.0, 8.0 - years_elapsed)
        if years_to_target > 10:
            return r["index_fund_equity"]["value"]
        if years_to_target > 7:
            return 0.09
        if years_to_target > 4:
            return 0.085
        if years_to_target > 2:
            return 0.075
        return r["liquid_debt_fund"]["value"]
    if bucket == "long_term_wealth":
        return r["index_fund_equity"]["value"]
    if bucket == "retirement_voluntary":
        return r["ppf"]["value"]
    return r["fd"]["value"]


def simulate(state: dict, profile: dict, assumptions: dict, months: int,
             salary_scenario: str = "base", custom_growth: dict | None = None,
             policy: dict | None = None, income_pause_months: int = 0) -> list[dict]:
    """Project forward `months` months from state['as_of']. Returns monthly snapshots.
    Does not mutate the input state."""
    s = copy.deepcopy(state)
    as_of = parse_date(s["as_of"])
    normal_start = parse_date(profile["normal_phase"]["start"])
    normal_expenses = profile["normal_phase"]["expenses"]
    growth_rate = assumptions["salary_growth_scenarios"].get(salary_scenario, salary_scenario if isinstance(salary_scenario, float) else 0.08)
    split = (policy or assumptions["allocation_policy_default"])["post_emergency_split"]
    raise_lifestyle_pct = profile["policy_overrides"]["raise_split"]["lifestyle_pct"]
    emergency_floor = assumptions["emergency_fund"]["initial_target_floor"]
    epf_rate = assumptions["instrument_returns_annual"]["epf"]["value"]
    bike_deadline_idx = months_between(as_of, parse_date(s["bike"]["deadline"]))

    snapshots = []
    for m in range(1, months + 1):
        date = add_months(as_of, m)
        years_elapsed = m / 12

        if not s["phase_switched"] and date >= normal_start:
            s["expenses"] = dict(normal_expenses)
            s["phase_switched"] = True

        # annual salary growth (anniversary of as_of)
        if m % 12 == 0:
            rate = custom_growth.get(date.year, growth_rate) if custom_growth else growth_rate
            delta = s["take_home"] * rate
            s["expenses"]["personal"] = s["expenses"].get("personal", 0) + delta * raise_lifestyle_pct
            s["take_home"] += delta
            s["epf_employee_monthly"] *= (1 + rate)

        total_expenses = sum(s["expenses"].values())
        emi_total = 0.0
        for loan in s["debts"]:
            if m - loan["start_month"] < loan["tenure_months"]:
                emi_total += loan["emi"]
        income_this_month = 0.0 if m <= income_pause_months else s["take_home"]
        surplus = income_this_month - total_expenses - emi_total
        if m == 1 and s.get("one_time_deduction"):
            surplus -= s["one_time_deduction"]
            s["one_time_deduction"] = 0

        # grow existing bucket balances first
        for b in BUCKETS:
            rate = bucket_return_rate(b, assumptions, years_elapsed)
            s["buckets"][b] = compound_monthly(s["buckets"][b], rate, 1)
        if m <= income_pause_months:
            s["epf_balance"] = compound_monthly(s["epf_balance"], epf_rate, 1)  # no contributions while unemployed
        else:
            s["epf_balance"] = compound_monthly(s["epf_balance"], epf_rate, 1) + 2 * s["epf_employee_monthly"]

        remaining = surplus
        if remaining < 0:
            # unemployment/shortfall: draw down buckets in safety-first order to cover the gap
            need = -remaining
            for b in ("emergency", "bike", "house", "long_term_wealth", "retirement_voluntary", "car", "marriage", "other"):
                draw = min(need, s["buckets"][b])
                s["buckets"][b] -= draw
                need -= draw
                if need <= 0:
                    break
            s["unmet_shortfall"] = s.get("unmet_shortfall", 0) + max(0.0, need)
            remaining = 0.0
        else:
            ess = _essential_total(s["expenses"])
            emergency_target = max(emergency_floor, 6 * ess) if ess else emergency_floor
            gap = max(0.0, emergency_target - s["buckets"]["emergency"])
            alloc_emerg = min(gap, remaining)
            s["buckets"]["emergency"] += alloc_emerg
            remaining -= alloc_emerg

            if not s["bike"]["done"]:
                months_left = max(1, bike_deadline_idx - m)
                gap_bike = max(0.0, s["bike"]["target"] - s["buckets"]["bike"])
                if gap_bike <= 0:
                    s["bike"]["done"] = True
                else:
                    required = gap_bike / months_left
                    alloc_bike = min(required, remaining)
                    s["buckets"]["bike"] += alloc_bike
                    remaining -= alloc_bike
                    if s["buckets"]["bike"] >= s["bike"]["target"] - 1:
                        s["bike"]["done"] = True
                        s["bike"]["redirect_amount"] = required

            house_add = remaining * split["house"]
            if s["bike"]["done"]:
                house_add += s["bike"]["redirect_amount"]
            s["buckets"]["house"] += house_add
            s["buckets"]["long_term_wealth"] += remaining * split["long_term_wealth"]
            s["buckets"]["retirement_voluntary"] += remaining * split["retirement_voluntary"]

        ess_for_target = _essential_total(s["expenses"])
        emergency_target = max(emergency_floor, 6 * ess_for_target) if ess_for_target else emergency_floor

        debt_outstanding = sum(
            outstanding_balance(l["principal"], l["rate"], l["tenure_months"] / 12, max(0, m - l["start_month"]))
            for l in s["debts"] if m >= l["start_month"]
        )
        net_worth = sum(s["buckets"].values()) + s["epf_balance"] - debt_outstanding

        snapshots.append({
            "month_index": m, "date": date.isoformat(), "take_home": round(s["take_home"]),
            "expenses_total": round(total_expenses), "emi_total": round(emi_total),
            "surplus": round(surplus), "buckets": {k: round(v) for k, v in s["buckets"].items()},
            "epf_balance": round(s["epf_balance"]), "debt_outstanding": round(debt_outstanding),
            "net_worth": round(net_worth), "bike_done": s["bike"]["done"],
            "emergency_target": round(emergency_target),
            "unmet_shortfall": round(s.get("unmet_shortfall", 0)),
        })
    return snapshots


def yearly_snapshots(monthly: list[dict]) -> list[dict]:
    """One snapshot per calendar year (the last month recorded within that year)."""
    by_year = {}
    for snap in monthly:
        year = parse_date(snap["date"]).year
        by_year[year] = snap
    return [by_year[y] for y in sorted(by_year)]


def house_readiness(monthly: list[dict], profile: dict, assumptions: dict,
                     cost_scenario_key: str, appreciation_key: str,
                     rate_key: str = None) -> dict | None:
    cfg = assumptions["house_cost_scenarios"][cost_scenario_key]
    appr = assumptions["house_price_appreciation_scenarios"][appreciation_key]
    base_rate = assumptions["home_loan"]["base_rate_assumption"]
    for snap in monthly:
        years = snap["month_index"] / 12
        cost = house_cost_future(cfg, assumptions, years, appr)
        check = readiness_check(snap["buckets"]["house"], cost, snap["take_home"], base_rate, 20, assumptions)
        if check and check["afford"]["flag"] != "unaffordable":
            return {"date": snap["date"], "month_index": snap["month_index"], "cost": cost,
                     "down_payment": check["down_payment"], "loan_amount": check["loan_amount"],
                     "cash_required": check["cash_required"], "afford": check["afford"],
                     "house_balance": snap["buckets"]["house"]}
    return None
