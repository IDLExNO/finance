"""Natural-language transaction parsing + application to persisted state."""
from __future__ import annotations
import re
import datetime as dt

AMOUNT_RE = re.compile(
    r'(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|lakh|lac|l|thousand|k)?',
    re.IGNORECASE,
)


def parse_amount(text: str) -> float | None:
    m = AMOUNT_RE.search(text.replace(",", ""))
    if not m:
        return None
    num = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    if unit in ("crore", "cr"):
        num *= 1e7
    elif unit in ("lakh", "lac", "l"):
        num *= 1e5
    elif unit in ("thousand", "k"):
        num *= 1e3
    return num


CATEGORY_KEYWORDS = {
    "household": ["rent", "household", "housing"],
    "family_support": ["family support", "family", "parents", "mom", "mother", "dad", "father"],
    "personal": ["personal", "lifestyle", "fun"],
    "gym_monthly": ["gym"],
    "medical": ["medical", "health"],
}


def _match_category(text: str) -> str | None:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return cat
    return None


def parse_transaction(text: str) -> dict:
    """Returns a structured action dict. type is one of:
    expense_onetime, salary_set, expense_recurring_set, expense_recurring_delta,
    invest, bonus, new_emi, bike_purchase, house_plan, unknown
    """
    t = text.strip()
    tl = t.lower()
    amount = parse_amount(t)

    if re.search(r'\bsalary\b.*\b(increas|now|is|changed|became|to)\b', tl) or re.search(r'take.?home.*(is|now|increas)', tl):
        return {"type": "salary_set", "amount": amount, "raw": t}

    if "bonus" in tl:
        return {"type": "bonus", "amount": amount, "raw": t}

    if re.search(r'\bemi\b', tl) and re.search(r'(start|new)', tl):
        return {"type": "new_emi", "amount": amount, "raw": t}

    if "bike" in tl and re.search(r'(bought|purchase|buy)', tl):
        return {"type": "bike_purchase", "amount": amount, "raw": t}

    if re.search(r'\binvest', tl):
        return {"type": "invest", "amount": amount, "raw": t, "bucket": "long_term_wealth"}

    if re.search(r'\b(house|villa|plot)\b.*\bin\s+(19|20)\d{2}\b', tl) or "planning" in tl:
        year_m = re.search(r'(19|20)\d{2}', tl)
        return {"type": "house_plan", "amount": amount, "year": int(year_m.group(0)) if year_m else None, "raw": t}

    cat = _match_category(tl)
    if cat and re.search(r'(increas|now|is|changed|became|to)\b', tl):
        if re.search(r'\bby\b', tl):
            return {"type": "expense_recurring_delta", "category": cat, "amount": amount, "raw": t}
        return {"type": "expense_recurring_set", "category": cat, "amount": amount, "raw": t}

    if re.search(r'\b(spent|paid|bought)\b', tl):
        return {"type": "expense_onetime", "amount": amount, "desc": t, "raw": t}

    return {"type": "unknown", "amount": amount, "raw": t}
