"""Scenario grids: salary growth, house-price appreciation, loan rates, stress tests."""
from __future__ import annotations
import copy

from .model import simulate, house_readiness, add_months, parse_date, _essential_total
from .house import house_cost_future, affordability, readiness_check
from .calculations import amortization_totals


def salary_scenarios(state, profile, assumptions, months=120):
    out = {}
    for name in ("conservative", "base", "strong"):
        snaps = simulate(state, profile, assumptions, months, salary_scenario=name)
        r = house_readiness(snaps, profile, assumptions, "base", "base")
        out[name] = {
            "growth_rate": assumptions["salary_growth_scenarios"][name],
            "take_home_year10": snaps[-1]["take_home"],
            "net_worth_year10": snaps[-1]["net_worth"],
            "house_ready_date": r["date"] if r else "beyond 10y horizon",
        }
    return out


def house_price_scenarios(state, profile, assumptions, months=180):
    snaps = simulate(state, profile, assumptions, months, salary_scenario="base")
    out = {}
    for cost_key, appr_key in (("low", "low"), ("base", "base"), ("high", "high")):
        r = house_readiness(snaps, profile, assumptions, cost_key, appr_key)
        cost_now = house_cost_future(assumptions["house_cost_scenarios"][cost_key], assumptions, 0, 0)
        out[cost_key] = {
            "cost_today": round(cost_now["total_project_cost"]),
            "appreciation": assumptions["house_price_appreciation_scenarios"][appr_key],
            "ready": r,
        }
    return out


def home_loan_grid(loan_amount: float, assumptions, tenures=None):
    tenures = tenures or assumptions["home_loan"]["tenures_years"]
    grid = []
    for rate in assumptions["home_loan"]["stress_rates"]:
        for tenure in tenures:
            row = amortization_totals(loan_amount, rate, tenure)
            row["rate"] = rate
            row["tenure_years"] = tenure
            grid.append(row)
    return grid


def job_loss_stress(state, profile, assumptions, unemployed_months_list=(3, 6, 12), horizon_months=180):
    baseline_snaps = simulate(state, profile, assumptions, horizon_months, salary_scenario="base")
    baseline_ready = house_readiness(baseline_snaps, profile, assumptions, "base", "base")
    results = {}
    for months in unemployed_months_list:
        essential_monthly = _essential_total(state["expenses"]) or sum(state["expenses"].values()) * 0.6
        snaps = simulate(state, profile, assumptions, horizon_months, salary_scenario="base", income_pause_months=months)
        pause_end = snaps[months - 1] if months <= len(snaps) else snaps[-1]
        r = house_readiness(snaps, profile, assumptions, "base", "base")
        results[months] = {
            "essential_monthly_burn": round(essential_monthly),
            "total_burn": round(essential_monthly * months),
            "emergency_after_pause": pause_end["buckets"]["emergency"],
            "unmet_shortfall": pause_end.get("unmet_shortfall", 0),
            "house_ready_date_after_recovery": r["date"] if r else f"beyond {horizon_months//12}y horizon",
            "house_ready_date_baseline": baseline_ready["date"] if baseline_ready else f"beyond {horizon_months//12}y horizon",
        }
    return results


def market_crash_stress(state, profile, assumptions, drops=(0.20, 0.30, 0.40, 0.50), months=120):
    baseline = simulate(state, profile, assumptions, months, salary_scenario="base")[-1]
    out = {}
    for drop in drops:
        s = copy.deepcopy(state)
        # simulate crash today on equity-heavy buckets (long_term_wealth, and equity portion of house if young)
        s["buckets"]["long_term_wealth"] *= (1 - drop)
        s["buckets"]["house"] *= (1 - drop * 0.5)  # house bucket only partially equity-exposed on average
        snaps = simulate(s, profile, assumptions, months, salary_scenario="base")
        out[drop] = {
            "net_worth_10y": snaps[-1]["net_worth"],
            "net_worth_10y_baseline": baseline["net_worth"],
            "difference": snaps[-1]["net_worth"] - baseline["net_worth"],
        }
    return out


def property_appreciation_stress(state, profile, assumptions, rates=None, months=180):
    rates = rates or assumptions["stress_test_appreciation_grid"]
    snaps = simulate(state, profile, assumptions, months, salary_scenario="base")
    out = {}
    for rate in rates:
        # temporarily patch a pseudo scenario key using base cost scenario cfg with custom rate
        for snap in snaps:
            years = snap["month_index"] / 12
            cost = house_cost_future(assumptions["house_cost_scenarios"]["base"], assumptions, years, rate)
            check = readiness_check(snap["buckets"]["house"], cost, snap["take_home"],
                                     assumptions["home_loan"]["base_rate_assumption"], 20, assumptions)
            if check and check["afford"]["flag"] != "unaffordable":
                out[rate] = {"ready_date": snap["date"], "cash_required": round(check["cash_required"]), "emi": check["afford"]["emi"]}
                break
        else:
            out[rate] = {"ready_date": "beyond 15y horizon", "cash_required": None, "emi": None}
    return out


def interest_rate_stress(loan_amount: float, take_home: float, assumptions, tenure=20):
    out = {}
    for rate in assumptions["home_loan"]["stress_rates"]:
        afford = affordability(take_home, loan_amount, rate, tenure, assumptions)
        out[rate] = afford
    return out
