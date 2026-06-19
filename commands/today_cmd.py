from __future__ import annotations
from datetime import date
from commands.cmd import Cmd
from util import parse_message


class TodayCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        tdy = date.today()
        try:
            response = parse_message.parse_date(tdy, self.res_svc.find_by_date(tdy))
            await self.send_text(chat_id, response)
        except Exception as e:
            print(f"/tdy failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again")
