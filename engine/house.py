"""House cost / affordability calculations."""
from __future__ import annotations
from .calculations import emi


def house_cost_today(scenario_cfg: dict, assumptions: dict) -> dict:
    land = scenario_cfg["plot_sqft"] * scenario_cfg["land_rate_per_sqft"]
    construction = scenario_cfg["construction_sqft"] * scenario_cfg["construction_rate_per_sqft"]
    interiors = scenario_cfg["interiors_furniture"]
    base_cost = land + construction  # the "financeable" portion (land + building)
    reg_pct = assumptions["stamp_duty_registration_pct_tn"]["value"]
    legal_pct = assumptions["legal_brokerage_pct"]["value"]
    reg_legal = base_cost * (reg_pct + legal_pct)
    contingency_pct = assumptions["contingency_pct"]["value"]
    pre_contingency = base_cost + reg_legal + interiors
    contingency = pre_contingency * contingency_pct
    total_project_cost = pre_contingency + contingency
    return {
        "land": land, "construction": construction, "base_cost": base_cost,
        "reg_legal": reg_legal, "interiors": interiors, "contingency": contingency,
        "total_project_cost": total_project_cost,
    }


def house_cost_future(scenario_cfg: dict, assumptions: dict, years_from_now: float, appreciation_rate: float) -> dict:
    today = house_cost_today(scenario_cfg, assumptions)
    factor = (1 + appreciation_rate) ** years_from_now
    scaled = {k: v * factor for k, v in today.items()}
    scaled.update({"years_from_now": years_from_now, "appreciation_rate": appreciation_rate})
    return scaled


def readiness_check(house_balance: float, cost_future: dict, take_home: float, annual_rate: float,
                     tenure_years: float, assumptions: dict) -> dict | None:
    """Uses the FULL accumulated house corpus as down payment (beyond fixed cash costs), since a
    bigger down payment only ever helps EMI affordability. Returns None if the minimum required
    down payment isn't met yet."""
    other_costs = cost_future["reg_legal"] + cost_future["interiors"] + cost_future["contingency"]
    available_for_down = max(0.0, house_balance - other_costs)
    min_down_pct = assumptions["home_loan"]["typical_down_payment_pct_of_loanable_cost"]
    min_down = cost_future["base_cost"] * min_down_pct
    if available_for_down < min_down:
        return None
    down_payment = min(available_for_down, cost_future["base_cost"])
    loan_amount = max(0.0, cost_future["base_cost"] - down_payment)
    afford = affordability(take_home, loan_amount, annual_rate, tenure_years, assumptions)
    return {
        "down_payment": down_payment, "loan_amount": loan_amount, "afford": afford,
        "cash_required": down_payment + other_costs, "other_costs": other_costs,
    }


def affordability(take_home_monthly: float, loan_amount: float, annual_rate: float, tenure_years: float, assumptions: dict) -> dict:
    payment = emi(loan_amount, annual_rate, tenure_years)
    pct = payment / take_home_monthly if take_home_monthly else float("inf")
    pref = assumptions["home_loan"]["preferred_emi_pct_of_takehome"]
    upper = assumptions["home_loan"]["upper_limit_emi_pct_of_takehome"]
    if pct <= pref:
        flag = "comfortable"
    elif pct <= upper:
        flag = "stretched"
    else:
        flag = "unaffordable"
    return {"emi": round(payment), "emi_pct_of_takehome": round(pct * 100, 1), "flag": flag}
