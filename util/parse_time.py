from __future__ import annotations
import re
from datetime import time
from typing import Optional

TWELVE_HR_RE = re.compile(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$")
TWENTYFOUR_HR_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
MILITARY_RE = re.compile(r"^(\d{2})(\d{2})$")


def parse(input_str: Optional[str]) -> Optional[time]:
    if input_str is None:
        return None

    normalised = input_str.strip().lower()

    if normalised in ("noon", "midday"):
        return time(12, 0)
    if normalised == "midnight":
        return time(0, 0)

    m12 = TWELVE_HR_RE.match(normalised)
    if m12:
        hour = int(m12.group(1))
        minute = int(m12.group(2)) if m12.group(2) else 0
        period = m12.group(3)

        if hour < 1 or hour > 12 or minute > 59:
            return None

        if period == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12

        return time(hour, minute)

    m24 = TWENTYFOUR_HR_RE.match(normalised)
    if m24:
        hour = int(m24.group(1))
        minute = int(m24.group(2))
        if hour > 23 or minute > 59:
            return None
        return time(hour, minute)

    mil = MILITARY_RE.match(normalised)
    if mil:
        hour = int(mil.group(1))
        minute = int(mil.group(2))
        if hour > 23 or minute > 59:
            return None
        return time(hour, minute)

    return None
