from __future__ import annotations
from commands.cmd import Cmd
from util import parse_message


class MineCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        try:
            response = parse_message.parse_mine(tele_handle, self.res_svc.find_by_user(tele_handle))
            await self.send_text(chat_id, response)
        except Exception as e:
            print(f"/mine failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again")
