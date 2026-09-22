def inr(n) -> str:
    n = round(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1e7:
        return f"{sign}Rs {n/1e7:.2f} Cr"
    if n >= 1e5:
        return f"{sign}Rs {n/1e5:.2f} L"
    return f"{sign}Rs {n:,.0f}"
