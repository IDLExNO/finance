#!/usr/bin/env python3
"""Interactive REPL: feed plain-English transactions, get compact recalculated impact.
Run: python3 finance/cli.py
Commands: 'dashboard', 'forecast', 'how am i doing', 'quit'. Anything else is parsed as a transaction.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.io_utils import load_profile, load_assumptions, load_state, save_state
from engine.transactions import parse_transaction
from engine.apply import apply_transaction
from engine.model import simulate, yearly_snapshots, house_readiness
from engine.fmt import inr

profile = load_profile()
assumptions = load_assumptions()


def dashboard(state):
    snaps = simulate(state, profile, assumptions, 1, salary_scenario="base")
    snap = snaps[0]
    r = house_readiness(simulate(state, profile, assumptions, 180, salary_scenario="base"), profile, assumptions, "base", "base")
    print(f"Take-home: {inr(snap['take_home'])} | Expenses: {inr(snap['expenses_total'])} | Surplus: {inr(snap['surplus'])}")
    b = snap["buckets"]
    print(f"Emergency: {inr(b['emergency'])}/{inr(snap['emergency_target'])} | Bike: {inr(b['bike'])} | House: {inr(b['house'])} | "
          f"Long-term: {inr(b['long_term_wealth'])} | EPF: {inr(snap['epf_balance'])}")
    print(f"Net worth: {inr(snap['net_worth'])} | Debt: {inr(snap['debt_outstanding'])}")
    print(f"House-ready (base scenario): {r['date'] if r else 'beyond 15y horizon'}")


def process_one(state, text):
    """Used both by the REPL and by one-shot CLI invocation (`cli.py "Spent Rs 500 on food"`)."""
    if text.lower() in ("dashboard", "how am i doing", "how am i doing?"):
        dashboard(state)
        return state
    if text.lower() == "forecast":
        snaps = simulate(state, profile, assumptions, 123, salary_scenario="base")
        for s in yearly_snapshots(snaps):
            print(f"{s['date'][:7]}: net worth {inr(s['net_worth'])}, house fund {inr(s['buckets']['house'])}")
        return state

    action = parse_transaction(text)
    if action["type"] == "unknown" or action.get("amount") is None:
        print(f"Updated: could not confidently parse amount/type from: {text!r} -- no change made.")
        return state
    new_state, impact = apply_transaction(state, profile, assumptions, action)
    save_state(new_state)
    print(f"Updated ({action['type']}): {text}")
    print(f"Monthly surplus: {inr(impact['surplus_before'])} -> {inr(impact['surplus_after'])}")
    print(f"Net worth (10y): {inr(impact['net_worth_10y_before'])} -> {inr(impact['net_worth_10y_after'])}")
    print(f"House-ready date: {impact['house_date_before']} -> {impact['house_date_after']}")
    if "opportunity_cost_5y" in impact:
        print(f"Opportunity cost if invested instead: {inr(impact['opportunity_cost_5y'])} in 5y, {inr(impact['opportunity_cost_10y'])} in 10y")
    if impact.get("note"):
        print(impact["note"])
    return new_state


def main():
    state = load_state()
    if len(sys.argv) > 1:
        process_one(state, " ".join(sys.argv[1:]))
        return
    print("Personal Finance Command Center. Type a transaction, or 'dashboard' / 'forecast' / 'quit'.")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if not text:
            continue
        if text.lower() in ("quit", "exit"):
            break
        state = process_one(state, text)


if __name__ == "__main__":
    main()
