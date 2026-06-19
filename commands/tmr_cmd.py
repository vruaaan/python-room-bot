from __future__ import annotations
from datetime import date, timedelta
from commands.cmd import Cmd
from util import parse_message


class TmrCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        tmr = date.today() + timedelta(days=1)
        try:
            response = parse_message.parse_date(tmr, self.res_svc.find_by_date(tmr))
            await self.send_text(chat_id, response)
        except Exception as e:
            print(f"/tmr failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again")
