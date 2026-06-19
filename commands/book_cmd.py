from __future__ import annotations
from datetime import timedelta

from commands.cmd import Cmd
from model.reservation import Reservation
from util import parse_message, parse_time

USAGE = "Usage: /book <venue> <date> <start> <end>\nExample: /book 13L tomorrow 2pm 4pm"


class BookCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        args = self.parse_args(text)
        parts = args.split()
        if len(parts) < 4:
            await self.send_text(chat_id, USAGE)
            return

        start = parse_time.parse(parts[-2])
        end = parse_time.parse(parts[-1])
        book_args = self.parse_cancel_book_args(parts)

        if book_args is None or start is None or end is None or not (end > start):
            await self.send_text(
                chat_id,
                self.build_error_message(
                    book_args.venue if book_args else None,
                    book_args.date if book_args else None,
                    start,
                    end,
                ),
            )
            return

        # overnight inference: if end <= start, the booking spans into the next day
        date_end = book_args.date + timedelta(days=1) if end <= start else book_args.date

        res = Reservation(
            tele_handle=tele_handle,
            chat_id=chat_id,
            venue=book_args.venue,
            date_start=book_args.date,
            time_start=start,
            date_end=date_end,
            time_end=end,
        )

        try:
            if self.res_svc.has_conflict(res):
                await self.send_text(chat_id, "This slot clashes with an existing booking.")
                return
            self.res_svc.create(res)
            await self.send_text(
                chat_id,
                parse_message.parse_booked(book_args.venue, book_args.date, start, end, tele_handle),
            )
        except Exception as ex:
            print(f"/book save failed: {ex}")
            await self.send_text(chat_id, "Something went wrong, please try again.")
