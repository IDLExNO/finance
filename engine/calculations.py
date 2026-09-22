"""Pure financial math. No I/O, no state -- easy to test and reuse."""
from __future__ import annotations
import math


def emi(principal: float, annual_rate: float, years: float) -> float:
    """Monthly EMI for a fully-amortizing loan."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12
    n = int(round(years * 12))
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def amortization_totals(principal: float, annual_rate: float, years: float) -> dict:
    payment = emi(principal, annual_rate, years)
    n = int(round(years * 12))
    total_paid = payment * n
    return {
        "emi": round(payment),
        "total_repayment": round(total_paid),
        "total_interest": round(total_paid - principal),
        "principal": round(principal),
        "tenure_months": n,
    }


def outstanding_balance(principal: float, annual_rate: float, years: float, months_paid: int) -> float:
    r = annual_rate / 12
    n = int(round(years * 12))
    payment = emi(principal, annual_rate, years)
    if r == 0:
        return max(0.0, principal - payment * months_paid)
    bal = principal * (1 + r) ** months_paid - payment * (((1 + r) ** months_paid - 1) / r)
    return max(0.0, bal)


def fv_lumpsum(amount: float, annual_rate: float, years: float) -> float:
    return amount * (1 + annual_rate) ** years


def fv_series_monthly(monthly_contribution: float, annual_rate: float, months: int) -> float:
    """Future value of a level monthly contribution series, contributions at month-end."""
    if months <= 0:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return monthly_contribution * months
    return monthly_contribution * (((1 + r) ** months - 1) / r)


def required_monthly_for_target(target_fv: float, annual_rate: float, months: int) -> float:
    if months <= 0:
        return target_fv
    r = annual_rate / 12
    if r == 0:
        return target_fv / months
    factor = ((1 + r) ** months - 1) / r
    return target_fv / factor if factor else target_fv


def compound_monthly(balance: float, annual_rate: float, months: int = 1) -> float:
    r = annual_rate / 12
    return balance * (1 + r) ** months
