from __future__ import annotations
from commands.cmd import Cmd

HELP_STRING = """*Venue Booking Bot*
Book and manage room reservations right from Telegram.

*Commands*

/book <venue> <date> <start> <end>
Create a booking. Fails if it clashes with an existing one.
  _e.g. /book 13L tomorrow 2pm 4pm_

/cancel <venue> <date> <start> <end>
Cancel a booking you made. Must match exactly, and you must be the one who made it.
  _e.g. /cancel 13L tomorrow 2pm 4pm_

/rooms <venue>
View all bookings for a venue.
  _e.g. /rooms 13L_

/date <date>
View all bookings for a specific date.
  _e.g. /date next fri_

/tdy — view today's bookings
/tmr — view tomorrow's bookings
/mine — view your own upcoming bookings

/help, /start — show this message

*Accepted venues*
12L recognised as : "12", "12l", "12 lounge", "level 12 lounge", "lvl 12 lounge"
13L recognised as : "13", "13l", "13 lounge", "level 13 lounge", "lvl 13 lounge"
14L recognised as : "14", "14l", "14 lounge", "level 14 lounge", "lvl 14 lounge"
12 study room recognised as : "study room", "12 study room", "level 12 study room", "12 study rm", "level 12 study rm"

*Accepted dates*
today, tdy, tonight, tomorrow, tmr, mon, next fri, next next mon, 15 jun, jun 15, 15-06-2026, 15062026

*Accepted times*
2pm, 2:30pm, 14:00, 1400, noon, midnight

*Notes*
- Times must have an end after the start, or the booking is treated as overnight if the end time is earlier in the day.
- Numeric dates are read as day-month-year, not year-month-year.
- You can only cancel bookings made under your own Telegram username.
- Times and venues are all case insensitive
"""


class HelpCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        await self.send_markdown(chat_id, HELP_STRING)
