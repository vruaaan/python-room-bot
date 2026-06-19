from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from typing import Optional, Any


@dataclass
class Reservation:
    tele_handle: str
    chat_id: str
    venue: str
    date_start: date
    time_start: time
    date_end: date
    time_end: time
    id: Optional[str] = field(default=None, repr=False)

    # ── datetime helpers ──────────────────────────────────────────────────────

    def start_dt(self) -> datetime:
        return datetime.combine(self.date_start, self.time_start)

    def end_dt(self) -> datetime:
        return datetime.combine(self.date_end, self.time_end)

    def duration_hours(self) -> float:
        delta = self.end_dt() - self.start_dt()
        return delta.total_seconds() / 3600

    # ── domain logic ──────────────────────────────────────────────────────────

    def clashing(self, other: "Reservation") -> bool:
        """True when two reservations share a venue and their times overlap."""
        return (
            other.venue == self.venue
            and self.start_dt() < other.end_dt()
            and other.start_dt() < self.end_dt()
        )

    def passed(self, now: datetime) -> bool:
        return self.end_dt() <= now

    def matches(self, venue: str, d: date, start: time, end: time) -> bool:
        return (
            self.venue == venue
            and self.date_start == d
            and self.time_start == start
            and self.time_end == end
        )

    # ── Firestore serialisation ───────────────────────────────────────────────

    def to_payload(self) -> dict[str, Any]:
        return {
            "telehandle": self.tele_handle,
            "chatId": self.chat_id,
            "venue": self.venue,
            "date_start": self.date_start.isoformat(),
            "time_start": self.time_start.strftime("%H:%M"),
            "date_end": self.date_end.isoformat(),
            "time_end": self.time_end.strftime("%H:%M"),
            "duration": self.duration_hours(),
            "createdAt": SERVER_TIMESTAMP,
        }

    @staticmethod
    def from_doc(doc) -> "Reservation":
        d = doc.to_dict()
        r = Reservation(
            tele_handle=d["telehandle"],
            chat_id=d["chatId"],
            venue=d["venue"],
            date_start=date.fromisoformat(d["date_start"]),
            time_start=time.fromisoformat(d["time_start"]),
            date_end=date.fromisoformat(d["date_end"]),
            time_end=time.fromisoformat(d["time_end"]),
        )
        r.id = doc.id
        return r

    # ── string representations ────────────────────────────────────────────────

    def cancel_string(self) -> str:
        return (
            f"Booking for {self.venue} on {self.date_start.strftime('%d-%m-%Y')} "
            f"({self.time_start.strftime('%H:%M')} - {self.time_end.strftime('%H:%M')}) cancelled"
        )
    def __str__(self) -> str:
        ts = self.time_start.strftime("%H:%M")
        te = self.time_end.strftime("%H:%M")
        ds = self.date_start.strftime("%d-%m-%Y")
        de = self.date_end.strftime("%d-%m-%Y")
        if self.date_start == self.date_end:
            return f"{self.venue} booked on {ds}: {ts} - {te}"
        return f"{self.venue} booked {ds} {ts} to {de} {te}"
