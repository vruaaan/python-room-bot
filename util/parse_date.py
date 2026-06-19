from __future__ import annotations
import re
from datetime import date, timedelta
from typing import Optional

DAY_ALIASES = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# "15th of june" / "15 jun" OR "june 15th" / "jun 15"
DATE_MONTH_RE = re.compile(
    r"^(?:(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(\w+)|(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?)$"
)

# numeric dates: 15-06-2026, 15/06/26, 15062026
ISO_DATE_RE = re.compile(r"^(\d{2})[/\-]?(\d{2})[/\-]?(\d{4}|\d{2})$")


def _check_day_map(text: str) -> Optional[int]:
    return DAY_ALIASES.get(text)


def _check_month_map(text: str) -> Optional[int]:
    if text is None or len(text) < 3:
        return None
    return MONTH_ALIASES.get(text[:3])


def _next_or_same(today: date, target_dow: int) -> date:
    days_ahead = (target_dow - today.weekday()) % 7
    return today + timedelta(days=days_ahead)


def _next(today: date, target_dow: int) -> date:
    days_ahead = (target_dow - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def parse(input_str: Optional[str]) -> Optional[date]:
    if input_str is None:
        return None

    normalised = input_str.strip().lower()
    today = date.today()

    if normalised in ("today", "tdy", "tonight"):
        return today
    if normalised in ("tomorrow", "tmr", "tmrw"):
        return today + timedelta(days=1)

    if normalised.startswith("next "):
        extra_weeks = 0
        remaining = normalised
        while remaining.startswith("next "):
            extra_weeks += 1
            remaining = remaining[5:].strip()
        dow = _check_day_map(remaining)
        if dow is None:
            return None
        base = _next(today, dow)
        return base + timedelta(weeks=extra_weeks - 1)

    dow = _check_day_map(normalised)
    if dow is not None:
        return _next_or_same(today, dow)

    dm = DATE_MONTH_RE.match(normalised)
    if dm:
        if dm.group(1) is not None:
            day_str, month_str = dm.group(1), dm.group(2)
        else:
            month_str, day_str = dm.group(3), dm.group(4)
        month = _check_month_map(month_str)
        if month is None:
            return None
        day = int(day_str)
        try:
            candidate = date(today.year, month, day)
        except ValueError:
            return None
        if candidate < today:
            candidate = candidate.replace(year=candidate.year + 1)
        return candidate

    iso = ISO_DATE_RE.match(normalised)
    if iso:
        day = int(iso.group(1))
        month = int(iso.group(2))
        year_str = iso.group(3)
        year = 2000 + int(year_str) if len(year_str) == 2 else int(year_str)
        try:
            return date(year, month, day)
        except ValueError:
            return None

    return None
