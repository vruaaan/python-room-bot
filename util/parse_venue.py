from __future__ import annotations
import json
from typing import Optional

VENUES_FILE = "venues.json"


def _load_venue_aliases() -> dict[str, str]:
    venue_map: dict[str, str] = {}
    try:
        with open(VENUES_FILE, "r", encoding="utf-8") as f:
            raw: dict[str, list[str]] = json.load(f)

        for key, alt_names in raw.items():
            key = key.strip()
            if not key:
                continue
            venue_map[key.lower()] = key
            for alt_name in alt_names:
                normalised_alt = alt_name.strip().lower()
                if normalised_alt:
                    venue_map[normalised_alt] = key
    except (OSError, json.JSONDecodeError) as e:
        print(f"Failed to load {VENUES_FILE}: {e}")
    return venue_map


_VENUE_ALIASES = _load_venue_aliases()


def parse(input_str: Optional[str]) -> Optional[str]:
    if input_str is None:
        return None
    normalised = input_str.strip().lower()
    if not normalised:
        return None
    return _VENUE_ALIASES.get(normalised)
