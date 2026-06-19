from __future__ import annotations
from typing import Optional

from commands.cmd import Cmd, VenueDate
from model.reservation import Reservation
from util import parse_time

USAGE = "Usage: /cancel <venue> <date> <start> <end>\nExample: /cancel 13L tomorrow 2pm 4pm"
NOT_FOUND = "No matching bookings found"
NOT_YOURS = "Booking found not made by you"


class CancelCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        args = self.parse_args(text)
        parts = args.split()
        if len(parts) < 4:
            await self.send_text(chat_id, USAGE)
            return

        start = parse_time.parse(parts[-2])
        end = parse_time.parse(parts[-1])
        cancel_args = self.parse_cancel_book_args(parts)

        if cancel_args is None or start is None or end is None or not (end > start):
            await self.send_text(
                chat_id,
                self.build_error_message(
                    cancel_args.venue if cancel_args else None,
                    cancel_args.date if cancel_args else None,
                    start,
                    end,
                ),
            )
            return

        try:
            match = self._find_match(cancel_args, start, end)
            if match is None:
                await self.send_text(chat_id, NOT_FOUND)
                return
            if match.tele_handle != tele_handle:
                await self.send_text(chat_id, NOT_YOURS)
                return
            self.res_svc.delete(match.id)
            await self.send_text(chat_id, match.cancel_string())
        except Exception as e:
            print(f"/cancel failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again.")

    def _find_match(self, venue_date: VenueDate, start, end) -> Optional[Reservation]:
        candidates = self.res_svc.find_by_venue(venue_date.venue)
        for r in candidates:
            if r.matches(venue_date.venue, venue_date.date, start, end):
                return r
        return None
