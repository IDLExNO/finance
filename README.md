# Personal Finance Command Center

A persistent, interconnected financial model. State lives in `data/state.json` (git-committed
so it survives across sessions); it is never hand-edited -- only through transactions.

## Files

- `data/profile.json` -- **USER DATA**: your income, expense assumptions, goals. Edit this if a
  base fact changes (e.g. new employer, new bike target).
- `data/assumptions.json` -- **ASSUMPTION / ESTIMATE / PROJECTION / FACT_PENDING_VERIFY** external
  figures (instrument returns, home-loan rates, Chennai construction/land cost placeholders, tax
  notes). See `reports/research_notes.md` for sourcing and what still needs live verification.
- `data/state.json` -- the living model: bucket balances, EPF, debts, current expenses, transaction
  ledger. Auto-created on first run from `profile.json`.
- `engine/` -- pure calculation code (EMI/FV math, house-cost math, the month-by-month simulator,
  the natural-language transaction parser, scenario/stress-test generators).
- `generate_report.py` -- regenerates `reports/initial_report.md` (the full baseline: budget,
  emergency/bike/house plans, investment structure, 2027-2036 forecast, salary/house-price/loan
  scenarios, job-loss stress tests, one-page action plan). Re-run after changing `assumptions.json`.
- `cli.py` -- interactive transaction engine.

## Usage

Interactive:
```
python3 cli.py
> Spent Rs 8000 on a trip
> Salary increased to 105000
> dashboard
> forecast
```

One-shot (for scripting / chat-driven updates):
```
python3 cli.py "Spent Rs 8000 on a trip"
python3 cli.py dashboard
```

Supported transaction phrasings (extend `engine/transactions.py` for more):
- `Spent Rs X on <desc>` / `Bought <item> for Rs X` -- one-time expense, reduces this month's
  surplus, reports opportunity cost at 5y/10y if invested instead.
- `Salary increased to Rs X` / `Take-home is now Rs X`
- `Rent is now Rs X` / `Family support increased by Rs X` -- recurring expense set/delta
  (categories: household, family_support, personal, gym_monthly, medical)
- `Invested Rs X in <instrument>` -- adds to the long-term-wealth bucket
- `Received Rs X bonus` -- tops up emergency fund first, then splits per policy
- `New EMI Rs X` -- adds a recurring loan payment
- `Bought bike for Rs X` -- draws down the bike bucket, marks the bike goal done
- `Planning Rs X house in <year>` -- records a house-plan override note

Every transaction is logged in `state.json["transactions"]` (never overwritten) and immediately
recalculates: monthly surplus, all bucket balances, net worth, and the projected house-ready date,
by re-running the full simulation before and after.

## Modeling choices worth knowing

- **Allocation priority**: emergency fund fully first (target = max(Rs 4L, 6x essential expenses)),
  then a dynamically-recomputed bike reserve (until the 2-year bike goal is met, then that amount
  redirects to the house fund), then the remainder splits House 55% / Long-term wealth 30% /
  Voluntary retirement 15%. All overridable in `assumptions.json` -> `allocation_policy_default`.
- **Salary growth**: applied once a year (on the anniversary of `profile.json.as_of`); 30% of any
  raise is added to the personal/lifestyle expense line, 70% flows into surplus -- per your stated
  rule (`profile.json -> policy_overrides.raise_split`).
- **House affordability**: the model does NOT fix the down payment at 20%. It uses the full
  accumulated house-fund corpus as down payment (beyond required registration/legal/interiors/
  contingency cash), since a bigger down payment only ever helps the EMI. "House-ready" requires
  both the cash and an EMI that isn't flagged `unaffordable` (>35% of take-home).
- **House bucket return** glides down from equity-like (11%) toward liquid-debt (6.5%) as the
  assumed ~8-year horizon shrinks, per your de-risking framework.
- **Job-loss stress test** actually pauses income for N months (no salary, no EPF contribution,
  expenses continue) and draws down buckets in safety order (emergency -> bike -> house -> ...);
  any unmet shortfall is reported, not silently absorbed as new debt.
- Expenses are held flat in nominal terms unless you report a change -- no inflation is silently
  assumed on top of what you tell the model.

## Known simplifications / next verification steps

- Chennai land/construction per-sqft rates in `assumptions.json -> house_cost_scenarios` are
  placeholder ESTIMATEs, not live-sourced. Flood-risk is a hard filter per your rules but must be
  checked per-plot -- this model does not and cannot do that automatically.
- PPF/EPF rates and TN stamp duty/registration % are flagged `FACT_PENDING_VERIFY` -- verify before
  relying on them for a real transaction.
- Girlfriend/spouse income, inheritance, and undefined bonuses are never assumed -- only entered
  via an explicit transaction, and even then treated as optional upside, not baseline.
