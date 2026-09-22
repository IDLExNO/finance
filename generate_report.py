#!/usr/bin/env python3
"""Runs the engine on the base profile and produces reports/initial_report.md
(the section-27 baseline output). Re-run any time assumptions.json changes."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.io_utils import load_profile, load_assumptions, save_state, DATA
from engine.model import default_state, simulate, yearly_snapshots, house_readiness, add_months, parse_date
from engine.scenarios import salary_scenarios, house_price_scenarios, home_loan_grid, job_loss_stress
from engine.house import house_cost_future, affordability
from engine.fmt import inr

profile = load_profile()
assumptions = load_assumptions()
state = default_state(profile)
save_state(state)

MONTHS = 123  # Sep 2026 -> Dec 2036, covers calendar years 2027-2036
snaps = simulate(state, profile, assumptions, MONTHS, salary_scenario="base")
yearly_all = yearly_snapshots(snaps)
yearly = [s for s in yearly_all if 2027 <= parse_date(s["date"]).year <= 2036]

lines = []

def h(title, level=2):
    lines.append(("#" * level) + " " + title)

def p(text=""):
    lines.append(text)

h("Personal Finance Command Center -- Baseline Model", 1)
p(f"_Generated from finance/data/profile.json (USER DATA) + finance/data/assumptions.json (ASSUMPTION/ESTIMATE/PROJECTION, pending verification -- see reports/research_notes.md). As-of: {profile['as_of']}._")
p()

# --- 1. Jan 2027 budget ---
h("1. January 2027 Monthly Budget")
ne = profile["normal_phase"]["expenses"]
th = profile["income"]["take_home_monthly"]
total_exp = sum(ne.values())
surplus = th - total_exp
p("| Line | Amount |")
p("|---|---|")
p(f"| Take-home | {inr(th)} |")
p(f"| Personal/lifestyle | {inr(ne['personal'])} |")
p(f"| Household/rent | {inr(ne['household'])} |")
p(f"| Family support | {inr(ne['family_support'])} |")
p(f"| Gym | {inr(ne['gym_monthly'])} |")
p(f"| **Total expenses** | **{inr(total_exp)}** |")
p(f"| **Monthly surplus (pre-allocation)** | **{inr(surplus)}** |")
p(f"| EPF (employee, separate from take-home) | {inr(profile['income']['epf_employee_monthly'])} |")
p()
p("_Household and family-support figures use the midpoint of your given ranges (Rs 17,500 and Rs 12,500). ASSUMPTION -- override any time._")
p()

# --- 2. Emergency fund plan ---
h("2. Emergency Fund Strategy")
ess = ne["household"] + ne["family_support"]
target = max(assumptions["emergency_fund"]["initial_target_floor"], 6 * ess)
p(f"- Target: **{inr(target)}** (max of Rs 4L floor and 6x essential monthly spend of {inr(ess)})")
p("- Priority #1 in the allocation policy -- filled before bike/house/long-term contributions.")
p("- Held in savings account + liquid/short-duration debt fund (assumed blended return "
  f"{assumptions['instrument_returns_annual']['liquid_debt_fund']['value']*100:.1f}%/yr, ESTIMATE). Never counted as house money.")
emerg_month = next((s for s in snaps if s["buckets"]["emergency"] >= target - 1), None)
p(f"- Projected full at: **{emerg_month['date'] if emerg_month else 'beyond horizon'}** under the base salary scenario "
  f"(temporary-phase surplus of only ~Rs 9,000/mo through Dec 2026 slows early progress).")
p()

# --- 3. Bike plan ---
h("3. Bike Fund")
bike = profile["goals"]["bike"]
p(f"- Target: {inr(bike['target'])} (mid of Rs 3-4L range), by {state['bike']['deadline']} (~{bike['years_from_now']} years out).")
p("- Reserved dynamically each month as (remaining target) / (months left) -- runs **after** the emergency fund is topped up, "
  "since emergency is priority #1 per your rules. This means bike saving is light/zero until emergency hits target "
  f"(~{emerg_month['date'] if emerg_month else 'n/a'}), then accelerates.")
bike_month = next((s for s in snaps if s["bike_done"]), None)
p(f"- Projected bike-fund completion: **{bike_month['date'] if bike_month else 'beyond horizon'}**.")
p("- Once complete, its monthly reserve auto-redirects into the house fund (rule 9).")
p("- Held in liquid/short-duration debt instruments, not equity (horizon too short).")
p()

# --- 4. House-fund strategy ---
h("4. House-Fund Strategy")
p("- De-risking glide path applied to the house bucket's assumed return (not a literal fund switch, but the model's growth assumption): "
  "growth-oriented while >10y out, tapering to capital-preservation inside 2y of the (re-estimated) target date.")
p("- House bucket only starts receiving meaningful contributions once the emergency fund is full and/or the bike fund completes (see split below).")
split = assumptions["allocation_policy_default"]["post_emergency_split"]
p(f"- Post-emergency monthly surplus split (ASSUMPTION, overridable): House {split['house']*100:.0f}% / "
  f"Long-term wealth {split['long_term_wealth']*100:.0f}% / Voluntary retirement (PPF/NPS top-up) {split['retirement_voluntary']*100:.0f}%.")
p()

# --- 5. Investment structure ---
h("5. Investment Bucket Structure")
p("| Bucket | Purpose | Horizon | Assumed instrument | Return (annual) | Type |")
p("|---|---|---|---|---|---|")
ir = assumptions["instrument_returns_annual"]
rows = [
    ("Emergency", "6mo essential expenses buffer", "0-1y", "Savings + liquid debt fund", ir["liquid_debt_fund"]["value"], "ESTIMATE"),
    ("Bike", "Vehicle purchase ~2y out", "~2y", "Liquid/short-duration debt fund", ir["liquid_debt_fund"]["value"], "ESTIMATE"),
    ("House", "Down payment + costs, de-risking glide path", "~8y, shrinking", "Index fund -> balanced -> debt as date nears", None, "PROJECTION"),
    ("Long-term wealth", "Wealth beyond the house, longest horizon", "10y+", "Broad-market index / equity MF", ir["index_fund_equity"]["value"], "PROJECTION"),
    ("Retirement (voluntary)", "Top-up beyond mandatory EPF", "30y+", "PPF (safe) / NPS (equity-tilted option)", ir["ppf"]["value"], "FACT_PENDING_VERIFY"),
    ("EPF (mandatory)", "Retirement, employer+employee", "30y+", "EPFO-managed", ir["epf"]["value"], "FACT_PENDING_VERIFY"),
]
for name, purpose, horizon, instr, rate, typ in rows:
    rate_s = f"{rate*100:.1f}%" if rate is not None else "8.5-11% glide"
    p(f"| {name} | {purpose} | {horizon} | {instr} | {rate_s} | {typ} |")
p()
p("_None of these returns are guaranteed. Equity figures are historical-average PROJECTIONs; PPF/EPF rates are government-set and revised periodically -- flagged pending verification._")
p()

# --- 6. 2027-2036 forecast ---
h("6. Year-by-Year Forecast (2027-2036)")
p("| Year | Age | Take-home/mo | Surplus/mo | Emergency | Bike | House fund | Long-term wealth | EPF | Net worth |")
p("|---|---|---|---|---|---|---|---|---|---|")
start_age = profile["personal"]["age"]
start_year = parse_date(profile["as_of"]).year
for snap in yearly:
    yr = parse_date(snap["date"]).year
    age = start_age + (yr - start_year)
    b = snap["buckets"]
    p(f"| {yr} | {age} | {inr(snap['take_home'])} | {inr(snap['surplus'])} | {inr(b['emergency'])} | {inr(b['bike'])} | "
      f"{inr(b['house'])} | {inr(b['long_term_wealth'])} | {inr(snap['epf_balance'])} | {inr(snap['net_worth'])} |")
p()
p("_Base salary scenario (8%/yr from year 2), base allocation policy, expenses held flat in nominal terms except the 30% lifestyle share of each raise. All figures are PROJECTIONS._")
p()

# --- 7. Salary scenarios ---
h("7. Salary-Growth Scenarios (10y)")
sal = salary_scenarios(state, profile, assumptions, months=MONTHS)
p("| Scenario | Growth/yr | Take-home @Y10 | Net worth @Y10 | House-ready date (base house scenario) |")
p("|---|---|---|---|---|")
for name in ("conservative", "base", "strong"):
    d = sal[name]
    p(f"| {name.title()} | {d['growth_rate']*100:.0f}% | {inr(d['take_home_year10'])} | {inr(d['net_worth_year10'])} | {d['house_ready_date']} |")
p()

# --- 8. House price scenarios ---
h("8. House-Price Scenarios")
hp = house_price_scenarios(state, profile, assumptions, months=180)
p("| Scenario | Cost today | Appreciation/yr | Cash required @ready-date | Ready date | EMI @ready |")
p("|---|---|---|---|---|---|")
for key in ("low", "base", "high"):
    d = hp[key]
    r = d["ready"]
    if r:
        p(f"| {key.title()} | {inr(d['cost_today'])} | {d['appreciation']*100:.0f}% | {inr(r['cash_required'])} | {r['date']} | {inr(r['afford']['emi'])} ({r['afford']['flag']}) |")
    else:
        p(f"| {key.title()} | {inr(d['cost_today'])} | {d['appreciation']*100:.0f}% | -- | beyond 15y horizon | -- |")
p()
p("_Land/construction rates for Sriperumbudur/Oragadam/Thirumazhisai/Guduvanchery/Tambaram-outskirts corridors are placeholder ESTIMATEs "
  "pending live verification (see reports/research_notes.md); flood-risk due diligence must be done per-plot, not per-area._")
p()

# --- 9. Home loan scenarios ---
h("9. Home-Loan Scenarios")
base_ready = hp["base"]["ready"]
if base_ready:
    loan_amount = base_ready["loan_amount"]
    loan_ref_note = base_ready["date"]
else:
    ref_cost = house_cost_future(assumptions["house_cost_scenarios"]["base"], assumptions, 8, 0.06)
    loan_amount = ref_cost["base_cost"] * (1 - assumptions["home_loan"]["typical_down_payment_pct_of_loanable_cost"])
    loan_ref_note = "8y reference point (base case not yet affordable within 15y horizon -- see below)"
p(f"_Illustrative loan amount: {inr(loan_amount)} (base house scenario, base appreciation, at {loan_ref_note})._")
p()
p("| Rate | Tenure | EMI | Total interest | Total repayment |")
p("|---|---|---|---|---|")
for row in home_loan_grid(loan_amount, assumptions):
    p(f"| {row['rate']*100:.1f}% | {row['tenure_years']}y | {inr(row['emi'])} | {inr(row['total_interest'])} | {inr(row['total_repayment'])} |")
p()

# --- 10. Job-loss stress tests ---
h("10. Job-Loss Stress Tests")
jl = job_loss_stress(state, profile, assumptions)
p("| Unemployed | Essential burn/mo | Total burn | Emergency left after | Unmet shortfall | House-ready: baseline vs after job loss |")
p("|---|---|---|---|---|---|")
for months, d in jl.items():
    p(f"| {months} months | {inr(d['essential_monthly_burn'])} | {inr(d['total_burn'])} | {inr(d['emergency_after_pause'])} | "
      f"{inr(d['unmet_shortfall']) if d['unmet_shortfall'] else 'none'} | {d['house_ready_date_baseline']} -> {d['house_ready_date_after_recovery']} |")
p()

# --- 11. One-page monthly action plan (Jan 2027 baseline) ---
h("11. One-Page Monthly Action Plan (from Jan 2027)")
alloc_emerg = min(target, surplus)
p(f"- Salary: {inr(th)} | Essential+lifestyle expenses: {inr(total_exp)} | Surplus: {inr(surplus)}")
p(f"- Emergency contribution: up to {inr(alloc_emerg)} (until {inr(target)} target met)")
p(f"- Bike/House/long-term contribution: {inr(max(0, surplus-alloc_emerg))} (routed per priority order once emergency is full)")
p(f"- EPF (separate, already deducted): {inr(profile['income']['epf_employee_monthly'])} employee + assumed equal employer match")
p(f"- **Safe to spend this month (discretionary, beyond the Rs {ne['personal']:,} lifestyle line):** Rs 0 extra until emergency fund is full -- "
  "any extra spend now directly delays the emergency-fund/bike/house timeline shown above.")
p("- **Do not touch:** emergency fund balance, bike fund balance (once started), EPF.")
p()

h("How to keep this going")
p("- State lives in `finance/data/state.json` (git-ignored is NOT set up -- it's committed so it persists across sessions). "
  "`finance/data/profile.json` is your data; `assumptions.json` is external facts/estimates, clearly typed.")
p("- Feed transactions as plain text (see `finance/README.md`) and the engine recalculates surplus, all bucket balances, "
  "net worth, and the projected house-ready date automatically, logging every change to the transaction ledger inside state.json.")

report = "\n".join(lines)
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "initial_report.md")
with open(out_path, "w") as f:
    f.write(report + "\n")
print(f"Wrote {out_path} ({len(lines)} lines)")
