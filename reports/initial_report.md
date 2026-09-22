# Personal Finance Command Center -- Baseline Model
_Generated from finance/data/profile.json (USER DATA) + finance/data/assumptions.json (ASSUMPTION/ESTIMATE/PROJECTION, pending verification -- see reports/research_notes.md). As-of: 2026-09-22._

## 1. January 2027 Monthly Budget
| Line | Amount |
|---|---|
| Take-home | Rs 89,000 |
| Personal/lifestyle | Rs 20,000 |
| Household/rent | Rs 17,500 |
| Family support | Rs 12,500 |
| Gym | Rs 1,000 |
| **Total expenses** | **Rs 51,000** |
| **Monthly surplus (pre-allocation)** | **Rs 38,000** |
| EPF (employee, separate from take-home) | Rs 6,000 |

_Household and family-support figures use the midpoint of your given ranges (Rs 17,500 and Rs 12,500). ASSUMPTION -- override any time._

## 2. Emergency Fund Strategy
- Target: **Rs 4.00 L** (max of Rs 4L floor and 6x essential monthly spend of Rs 30,000)
- Priority #1 in the allocation policy -- filled before bike/house/long-term contributions.
- Held in savings account + liquid/short-duration debt fund (assumed blended return 6.5%/yr, ESTIMATE). Never counted as house money.
- Projected full at: **2027-10-22** under the base salary scenario (temporary-phase surplus of only ~Rs 9,000/mo through Dec 2026 slows early progress).

## 3. Bike Fund
- Target: Rs 3.50 L (mid of Rs 3-4L range), by 2028-09-22 (~2 years out).
- Reserved dynamically each month as (remaining target) / (months left) -- runs **after** the emergency fund is topped up, since emergency is priority #1 per your rules. This means bike saving is light/zero until emergency hits target (~2027-10-22), then accelerates.
- Projected bike-fund completion: **2028-08-22**.
- Once complete, its monthly reserve auto-redirects into the house fund (rule 9).
- Held in liquid/short-duration debt instruments, not equity (horizon too short).

## 4. House-Fund Strategy
- De-risking glide path applied to the house bucket's assumed return (not a literal fund switch, but the model's growth assumption): growth-oriented while >10y out, tapering to capital-preservation inside 2y of the (re-estimated) target date.
- House bucket only starts receiving meaningful contributions once the emergency fund is full and/or the bike fund completes (see split below).
- Post-emergency monthly surplus split (ASSUMPTION, overridable): House 55% / Long-term wealth 30% / Voluntary retirement (PPF/NPS top-up) 15%.

## 5. Investment Bucket Structure
| Bucket | Purpose | Horizon | Assumed instrument | Return (annual) | Type |
|---|---|---|---|---|---|
| Emergency | 6mo essential expenses buffer | 0-1y | Savings + liquid debt fund | 6.5% | ESTIMATE |
| Bike | Vehicle purchase ~2y out | ~2y | Liquid/short-duration debt fund | 6.5% | ESTIMATE |
| House | Down payment + costs, de-risking glide path | ~8y, shrinking | Index fund -> balanced -> debt as date nears | 8.5-11% glide | PROJECTION |
| Long-term wealth | Wealth beyond the house, longest horizon | 10y+ | Broad-market index / equity MF | 11.0% | PROJECTION |
| Retirement (voluntary) | Top-up beyond mandatory EPF | 30y+ | PPF (safe) / NPS (equity-tilted option) | 7.1% | FACT_PENDING_VERIFY |
| EPF (mandatory) | Retirement, employer+employee | 30y+ | EPFO-managed | 8.2% | FACT_PENDING_VERIFY |

_None of these returns are guaranteed. Equity figures are historical-average PROJECTIONs; PPF/EPF rates are government-set and revised periodically -- flagged pending verification._

## 6. Year-by-Year Forecast (2027-2036)
| Year | Age | Take-home/mo | Surplus/mo | Emergency | Bike | House fund | Long-term wealth | EPF | Net worth |
|---|---|---|---|---|---|---|---|---|---|
| 2027 | 23 | Rs 96,120 | Rs 42,984 | Rs 4.04 L | Rs 92,849 | Rs 11,946 | Rs 6,523 | Rs 1.93 L | Rs 7.12 L |
| 2028 | 24 | Rs 1.04 L | Rs 48,367 | Rs 4.31 L | Rs 3.58 L | Rs 3.20 L | Rs 96,809 | Rs 3.75 L | Rs 16.28 L |
| 2029 | 25 | Rs 1.12 L | Rs 54,180 | Rs 4.60 L | Rs 3.82 L | Rs 10.47 L | Rs 2.98 L | Rs 5.86 L | Rs 29.18 L |
| 2030 | 26 | Rs 1.21 L | Rs 60,458 | Rs 4.91 L | Rs 4.07 L | Rs 18.73 L | Rs 5.46 L | Rs 8.30 L | Rs 44.07 L |
| 2031 | 27 | Rs 1.31 L | Rs 67,239 | Rs 5.24 L | Rs 4.34 L | Rs 27.99 L | Rs 8.46 L | Rs 11.10 L | Rs 61.08 L |
| 2032 | 28 | Rs 1.41 L | Rs 74,562 | Rs 5.59 L | Rs 4.64 L | Rs 38.32 L | Rs 12.07 L | Rs 14.30 L | Rs 80.46 L |
| 2033 | 29 | Rs 1.53 L | Rs 82,471 | Rs 5.97 L | Rs 4.95 L | Rs 49.64 L | Rs 16.39 L | Rs 17.96 L | Rs 1.02 Cr |
| 2034 | 30 | Rs 1.65 L | Rs 91,013 | Rs 6.37 L | Rs 5.28 L | Rs 62.27 L | Rs 21.52 L | Rs 22.13 L | Rs 1.27 Cr |
| 2035 | 31 | Rs 1.78 L | Rs 1.00 L | Rs 6.79 L | Rs 5.63 L | Rs 76.34 L | Rs 27.56 L | Rs 26.87 L | Rs 1.55 Cr |
| 2036 | 32 | Rs 1.92 L | Rs 1.10 L | Rs 7.25 L | Rs 6.01 L | Rs 91.99 L | Rs 34.67 L | Rs 32.24 L | Rs 1.87 Cr |

_Base salary scenario (8%/yr from year 2), base allocation policy, expenses held flat in nominal terms except the 30% lifestyle share of each raise. All figures are PROJECTIONS._

## 7. Salary-Growth Scenarios (10y)
| Scenario | Growth/yr | Take-home @Y10 | Net worth @Y10 | House-ready date (base house scenario) |
|---|---|---|---|---|
| Conservative | 5% | Rs 1.45 L | Rs 1.63 Cr | beyond 10y horizon |
| Base | 8% | Rs 1.92 L | Rs 1.87 Cr | 2035-09-22 |
| Strong | 10% | Rs 2.31 L | Rs 2.05 Cr | 2034-09-22 |

## 8. House-Price Scenarios
| Scenario | Cost today | Appreciation/yr | Cash required @ready-date | Ready date | EMI @ready |
|---|---|---|---|---|---|
| Low | Rs 65.05 L | 4% | Rs 31.33 L | 2032-04-22 | Rs 43,079 (stretched) |
| Base | Rs 85.13 L | 6% | Rs 72.63 L | 2035-09-22 | Rs 61,790 (stretched) |
| High | Rs 1.17 Cr | 8% | -- | beyond 15y horizon | -- |

_Land/construction rates for Sriperumbudur/Oragadam/Thirumazhisai/Guduvanchery/Tambaram-outskirts corridors are placeholder ESTIMATEs pending live verification (see reports/research_notes.md); flood-risk due diligence must be done per-plot, not per-area._

## 9. Home-Loan Scenarios
_Illustrative loan amount: Rs 71.20 L (base house scenario, base appreciation, at 2035-09-22)._

| Rate | Tenure | EMI | Total interest | Total repayment |
|---|---|---|---|---|
| 7.5% | 15y | Rs 66,005 | Rs 47.61 L | Rs 1.19 Cr |
| 7.5% | 20y | Rs 57,359 | Rs 66.46 L | Rs 1.38 Cr |
| 7.5% | 25y | Rs 52,617 | Rs 86.65 L | Rs 1.58 Cr |
| 8.0% | 15y | Rs 68,044 | Rs 51.28 L | Rs 1.22 Cr |
| 8.0% | 20y | Rs 59,556 | Rs 71.73 L | Rs 1.43 Cr |
| 8.0% | 25y | Rs 54,954 | Rs 93.66 L | Rs 1.65 Cr |
| 8.5% | 15y | Rs 70,115 | Rs 55.01 L | Rs 1.26 Cr |
| 8.5% | 20y | Rs 61,790 | Rs 77.10 L | Rs 1.48 Cr |
| 8.5% | 25y | Rs 57,333 | Rs 1.01 Cr | Rs 1.72 Cr |
| 9.0% | 15y | Rs 72,217 | Rs 58.79 L | Rs 1.30 Cr |
| 9.0% | 20y | Rs 64,062 | Rs 82.55 L | Rs 1.54 Cr |
| 9.0% | 25y | Rs 59,752 | Rs 1.08 Cr | Rs 1.79 Cr |
| 10.0% | 15y | Rs 76,514 | Rs 66.52 L | Rs 1.38 Cr |
| 10.0% | 20y | Rs 68,711 | Rs 93.70 L | Rs 1.65 Cr |
| 10.0% | 25y | Rs 64,701 | Rs 1.23 Cr | Rs 1.94 Cr |

## 10. Job-Loss Stress Tests
| Unemployed | Essential burn/mo | Total burn | Emergency left after | Unmet shortfall | House-ready: baseline vs after job loss |
|---|---|---|---|---|---|
| 3 months | Rs 70,000 | Rs 2.10 L | Rs 0 | Rs 2.40 L | 2035-09-22 -> 2035-09-22 |
| 6 months | Rs 70,000 | Rs 4.20 L | Rs 0 | Rs 3.93 L | 2035-09-22 -> 2036-02-22 |
| 12 months | Rs 70,000 | Rs 8.40 L | Rs 0 | Rs 7.01 L | 2035-09-22 -> 2037-09-22 |

## 11. One-Page Monthly Action Plan (from Jan 2027)
- Salary: Rs 89,000 | Essential+lifestyle expenses: Rs 51,000 | Surplus: Rs 38,000
- Emergency contribution: up to Rs 38,000 (until Rs 4.00 L target met)
- Bike/House/long-term contribution: Rs 0 (routed per priority order once emergency is full)
- EPF (separate, already deducted): Rs 6,000 employee + assumed equal employer match
- **Safe to spend this month (discretionary, beyond the Rs 20,000 lifestyle line):** Rs 0 extra until emergency fund is full -- any extra spend now directly delays the emergency-fund/bike/house timeline shown above.
- **Do not touch:** emergency fund balance, bike fund balance (once started), EPF.

## How to keep this going
- State lives in `finance/data/state.json` (git-ignored is NOT set up -- it's committed so it persists across sessions). `finance/data/profile.json` is your data; `assumptions.json` is external facts/estimates, clearly typed.
- Feed transactions as plain text (see `finance/README.md`) and the engine recalculates surplus, all bucket balances, net worth, and the projected house-ready date automatically, logging every change to the transaction ledger inside state.json.
