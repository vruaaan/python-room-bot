from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from telegram import Bot as TelegramBot
from telegram.constants import ParseMode

from service.reservation_svc import ReservationSvc
from util import parse_date, parse_venue

DATEISSUE = "I couldn't understand the date"
TIMEISSUE = "I couldn't understand the time. Try formats like 2pm, 14:00 or 1400."
TIMELOGIC = "End time must be after the start time."
VENUEDATEISSUE = "I couldn't understand the venue or time, refer to the proper formatting under /help"


@dataclass
class VenueDate:
    venue: str
    date: date


class Cmd(ABC): 
    def __init__(self, bot: TelegramBot, res_svc: ReservationSvc):
        self.bot = bot
        self.res_svc = res_svc

    @abstractmethod
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        ...

    #send helpers
    async def send_text(self, chat_id: str, text: str) -> None:
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"[{type(self).__name__}] Failed to send message: {e}")

    async def send_markdown(self, chat_id: str, markdown: str) -> None:
        try:
            await self.bot.send_message(chat_id=chat_id, text=markdown, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"[{type(self).__name__}] Failed to send message: {e}")

    #parsing helpers
    def parse_args(self, text: Optional[str]) -> str:
        if text is None:
            return ""
        trimmed = text.strip()
        first_space = trimmed.find(" ")
        if first_space == -1:
            return ""
        return trimmed[first_space + 1:].strip()

    def build_error_message(
        self,
        venue: Optional[str],
        d: Optional[date],
        start: Optional[time],
        end: Optional[time],
    ) -> str:
        if venue is None and d is None:
            return VENUEDATEISSUE
        elif d is None:
            return DATEISSUE
        elif start is None:
            return TIMEISSUE
        elif end is None:
            return TIMEISSUE
        elif start is not None and end is not None and end <= start:
            return TIMELOGIC
        return "Invalid input."

    def parse_cancel_book_args(self, parts: list[str]) -> Optional[VenueDate]:
        date_end_exclusive = len(parts) - 2
        for venue_end_exclusive in range(1, date_end_exclusive):
            venue_text = self.join(parts, 0, venue_end_exclusive)
            date_text = self.join(parts, venue_end_exclusive, date_end_exclusive)
            venue = parse_venue.parse(venue_text)
            d = parse_date.parse(date_text)
            if venue is not None and d is not None:
                return VenueDate(venue, d)
        return None

    def join(self, parts: list[str], frm: int, to: int) -> str:
        return " ".join(parts[frm:to])
