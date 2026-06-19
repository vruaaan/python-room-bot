from __future__ import annotations
from commands.cmd import Cmd
from util import parse_date, parse_message


class DateCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        args = self.parse_args(text)
        try:
            d = parse_date.parse(args)
            if d is None:
                raise ValueError("Invalid date / date format")
            response = parse_message.parse_date(d, self.res_svc.find_by_date(d))
            await self.send_text(chat_id, response)
        except ValueError as e:
            await self.send_text(chat_id, str(e))
        except Exception as e:
            print(f"/date failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again")
